#-*-coding=utf-8-*-

from __future__ import with_statement

"""
Модуль содержит класс для проверки прав на авторизацию
"""
import packet
import struct

from Crypto.Cipher import DES
from encodings import utf_16_le,hex_codec
from Crypto.Hash import MD4 as md4
from Crypto.Hash import SHA as SHA
from Crypto.Hash import MD5 as md5
import radius.eap.eap_packet as EAP
from radius.eap.eap_packet import EAP_Packet, EAP_MD5, EAP_HANDLERS, EAP_TLS, EAP_IDENTITY_CHECK_TYPES
from collections import defaultdict
from utilites import hex_bytestring


#EAP_IDENTITY_CHECK = lambda kwargs: (EAP.PW_EAP_MD5, EAP_MD5.get_challenge_reply)
EAP_IDENTITY_CHECK = lambda kwargs: (EAP.PW_EAP_TLS, EAP_TLS.get_tls_start)

def set_identity_check(identity_type):
    global EAP_IDENTITY_CHECK
    id_type = EAP_IDENTITY_CHECK_TYPES.get(identity_type)
    if not id_type:
        raise Exception("AUTH exception: Unknown EAP Identity Type: %s" % identity_type)
    id_check = lambda kwargs: id_type
    EAP_IDENTITY_CHECK = id_check
    

def get_eap_handlers():
    return EAP_HANDLERS.iterkeys()
class Auth:
    """
    Класс предназначен для реализации проверки авторизации для механизмов
    PAP,CHAP,MSCHAP2 и генерации ответного пакета.
    Для проверки имени и пароля конструктором вызывается функция _CheckAuth с параметрами username, plainpassword, secret
    """

    def __init__(self, packetobject, username, password, secret, access_type, challenges={}):
        self.packet=packetobject
        self.secret = secret
        self.packet.secret = secret
        self.access_type = access_type
        self.extensions = {}
        self.challenges = defaultdict(lambda:{'get': lambda x,d: None, 'set': lambda x,y: None, 'lock': None})
        for challenge_type in challenges:
            self.challenges[challenge_type] = challenges[challenge_type]

        self.typeauth=self._DetectTypeAuth()

        self.plainusername=username
        self.plainpassword=password

        self.code = 0
        self.ident=''
        self.NTResponse=''
        self.PeerChallenge=''
        self.AuthenticatorChallenge=''

        self.attrs = None

    def __repr__(self):
        return ', '.join((name + str(item) for name, item in (('code: ', self.code), ('access_type: ', self.access_type),\
                                                              ('secret: ', self.secret), ('auth: ', self.typeauth), \
                                                              ('username: ', self.plainusername), ('password: ', self.plainpassword), \
                                                              ('\n packet: ', self.packet), ('\n extensions: ', ' | '.join((str(key) +': ' + str(value) for key, value in self.extensions.iteritems())))))) 


    def ReturnPacket(self, packetfromcore):
        self.attrs=packetfromcore._PktEncodeAttributes()

        self.Reply=self.packet.CreateReply()
        self.Reply.secret = self.secret
        if self.typeauth == 'EAP':
            if self.code == packet.AccessReject:
                eap_packet = self.extensions.get('EAP-Packet')
                self.packet['EAP-Message'] = EAP_Packet.get_failure_packet(eap_packet.identifier)
            elif self.code == packet.AccessChallenge:
                self.Reply['State'] = self.packet['State'][0]
            self.Reply.code=self.code
            self.Reply['EAP-Message'] = self.packet['EAP-Message'][0]
            self.Reply['Message-Authenticator'] = self.packet['Message-Authenticator'][0]
            return self.Reply.ReplyPacket(), self.Reply

        elif self._CheckAuth(code = self.code):
            self.Reply.code=self.code
            if (self.typeauth=='MSCHAP2') and (self.code!=3):
                self.Reply.AddAttribute((311,26),self._MSchapSuccess())
            return self.Reply.ReplyPacket(self.attrs), self.Reply

        else:
            self.Reply.code=packet.AccessReject
            return self.Reply.ReplyPacket(), self.Reply

    def _DetectTypeAuth(self):
        if self.packet.has_key('User-Password') and self.access_type!='DHCP':
            return 'PAP'
        elif self.packet.has_key('CHAP-Password') and self.access_type!='DHCP':
            return 'CHAP'
        elif self.packet.has_key('MS-CHAP-Challenge') and self.access_type!='DHCP':
            return 'MSCHAP2'
        elif self.packet.has_key('EAP-Message') and self.access_type!='DHCP':
            eap_packet = EAP_Packet()
            eap_packet.unpack_header(self.packet['EAP-Message'][0])
            self.extensions['EAP-Packet'] = eap_packet
            return 'EAP'
        else:
            return 'UNKNOWN'

    def _HandlePacket(self, **kwargs):
        if self.typeauth == 'EAP':
            eap_packet = self.extensions.get('EAP-Packet')
            if not eap_packet:
                #self.code = packet.AccessReject
                return False, False, 'EAP error: No EAP-Message found: %s' % self.plainusername
            elif eap_packet.code not in (EAP.PW_EAP_RESPONSE,):
                #self.code = packet.AccessReject
                #self.packet['EAP-Message'] = EAP_Packet.get_failure_packet()
                return False, False, 'EAP error: Wrong code: %s/%s' % (self.plainusername, eap_packet.code)
            else:
                eap_handler = EAP_HANDLERS.get(eap_packet.type)
                if not eap_handler:
                    return False, False, 'EAP error: unknown type: %s/%s' % (self.plainusername, eap_packet.type)
                eap_packet = eap_handler()
                eap_packet.unpack(self.packet['EAP-Message'][0])
                self.extensions['EAP-Packet'] = eap_packet
                return True, True, ''

        else:
            return True, True, ''


    def _ProcessPacket(self, **kwargs):
        if self.typeauth == 'EAP':
            eap_packet = self.extensions.get('EAP-Packet')
            if not eap_packet:
                return False, False, 'EAP error: No EAP-Message found: %s' % self.plainusername
            if eap_packet.type == EAP.PW_EAP_IDENTITY:
                #assume that User-Name is checked as a radius attribute User-Name
                self.code = packet.AccessChallenge
                eap_packet.identifier = (eap_packet.identifier + 1)  % 255
                auth_name, auth_handler = EAP_IDENTITY_CHECK({})
                self.packet['EAP-Message'], challenge = auth_handler(eap_packet)
                state = self.plainusername[:3] + '00'
                self.packet['State'] = state
                if challenge:
                    with self.challenges[auth_name]['lock']:                    
                        self.challenges[auth_name]['set'](self.plainusername, (challenge, eap_packet.identifier, state))
                return False, True, 'EAP: challenge issued: %s' % self.plainusername
            elif eap_packet.type == EAP.PW_EAP_NAK:
                self.code = packet.AccessChallenge
                auth_name, auth_handler = EAP_IDENTITY_CHECK({})
                with self.challenges[auth_name]['lock']:                    
                    old_challenge, old_id, old_state = self.challenges[auth_name]['get'](self.plainusername, (None, None, None))
                if not old_id or not ((old_id == eap_packet.identifier) or (old_id == eap_packet.identifier - 1)):
                    return False, False, 'EAP error: wrong identifiers for user: %s old: %s new: %s' % (self.plainusername, old_id,eap_packet.identifier)
                eap_packet.identifier = (eap_packet.identifier + 1)  % 255
                eap_handler = EAP_HANDLERS.get(eap_packet.req_auth)
                if not eap_handler:
                    return False, False, 'EAP error: unknown requested auth method: %s %s' % (self.plainusername, eap_packet.req_auth)
                self.packet['EAP-Message'], challenge = eap_handler.get_challenge_reply(eap_packet)
                state = self.plainusername[:3] + '01'
                self.packet['State'] = state
                if challenge:
                    with self.challenges[eap_packet.req_auth]['lock']:                    
                        self.challenges[eap_packet.req_auth]['set'](self.plainusername, (challenge, eap_packet.identifier, state))
                return False, True, 'EAP: post NAK challenge issued: %s auth type %s' % (self.plainusername, eap_packet.req_auth)
            else:
                return True, True, ''

        else:
            return True, True, ''

    def _EAP_Check(self):
        eap_packet = self.extensions.get('EAP-Packet')
        if eap_packet.type == EAP.PW_EAP_MD5:
            with self.challenges[EAP.PW_EAP_MD5]['lock']:
                challenge, id, state = self.challenges[EAP.PW_EAP_MD5]['get'](self.plainusername, (None, None, None))
            if challenge is None:
                return False, 'EAP Password check: issued challenge not found: %s' % self.plainusername
            #print hex_bytestring(challenge)
            #print hex_bytestring(md5.new(''.join((struct.pack("!B", id), self.plainpassword, challenge))).digest())
            if eap_packet.check_response(self.plainpassword, challenge, id):
                self.code = packet.AccessAccept
                self.packet['EAP-Message'] = EAP_MD5.get_success_packet(eap_packet.identifier)
                return True, ''
            else:
                return False, 'EAP Password check: wrong password: %s' % self.plainusername

        else:
            return False, 'EAP Password check: type not implemented: %s/%s' % (self.plainusername, eap_packet.type)

    def EAP_Reply(self):
        if self.code == packet.AccessAccept:
            return get_success_packet(self.extensions['eap-packet'].identifier)


    def set_code(self, code):
        self.code = code

    def check_auth(self):
        return self._CheckAuth()


    def _CheckAuth(self, code= packet.AccessAccept, **kwargs):
        """
        Функция, в зависимости от типа авторизации, вызывает разные методы для определения правильности
        логина и пароля.
        To Do: Если ядро ответило: доступ запретить-пропускаем.
        """
        if self.access_type=='DHCP':
            return True, ''
        if code not in (packet.AccessReject, packet.AccessChallenge):
            if self.typeauth=='PAP':
                #print self._PwDecrypt()
                if self._PwDecrypt():
                    #print 'pap=', True
                    return True, ''
            elif self.typeauth=='CHAP':
                if self._CHAPDecrypt():
                    return True, ''
            elif self.typeauth=='MSCHAP2':
                #print "mschap2"
                if self._MSCHAP2Decrypt():
                    return True, ''
            elif self.typeauth == 'EAP':
                return self._EAP_Check()
        return False, 'Password check: bad password: %s' % self.plainusername



    def _MSCHAP2Decrypt(self):
        (self.ident, var, self.PeerChallenge, reserved, self.NTResponse)=struct.unpack("!BB16s8s24s",self.packet['MS-CHAP2-Response'][0])
        self.AuthenticatorChallenge=self.packet['MS-CHAP-Challenge'][0]
        return self.NTResponse==self._GenerateNTResponse(self.AuthenticatorChallenge, self.PeerChallenge, self.plainusername, self.plainpassword)

    def _CHAPDecrypt(self):
        (ident , password)=struct.unpack('!B16s',self.packet['CHAP-Password'][0])
        pck="%s%s%s" % (struct.pack('!B',ident),self.plainpassword,self.packet['CHAP-Challenge'][0])
        return md5.new(pck).digest()==password

    def _PwDecrypt(self):
        """
        Функция расшифровывает пароль из атрибута 2 (Password) с помощью секретного ключа, и аутентикатора
        Используется только в алгоритме PAP
        Unobfuscate a RADIUS password

        RADIUS hides passwords in packets by using an algorithm
        based on the MD5 hash of the pacaket authenticator and RADIUS
        secret. This function reverses the obfuscation process.

        @param password: obfuscated form of password
        @type password:  string
        @return:         plaintext password
        @rtype:          string
        """
        pw=''
        password=self.packet["User-Password"][0]
        authenticator=self.packet.authenticator
        while password:
            hash=md5.new(self.secret+authenticator).digest()
            for i in range(16):
                pw+=chr(ord(hash[i]) ^ ord(password[i]))

            (authenticator,password)=(password[:16], password[16:])

        while pw.endswith("\x00"):
            pw=pw[:-1]

        return pw==self.plainpassword

    #Функции для генерации MSCHAP2 response
    def _convert_key(self, key):
        """
        Converts a 7-bytes key to an 8-bytes key based on an algorithm.
        Функция для дополнения ключа до длины, кратной 8-ми
        """
        assert len(key) == 7, "NTLM convert_key needs 7-byte key"
        bytes = [key[0],
                 chr(((ord(key[0]) << 7) & 0xFF) | (ord(key[1]) >> 1)),
                 chr(((ord(key[1]) << 6) & 0xFF) | (ord(key[2]) >> 2)),
                 chr(((ord(key[2]) << 5) & 0xFF) | (ord(key[3]) >> 3)),
                 chr(((ord(key[3]) << 4) & 0xFF) | (ord(key[4]) >> 4)),
                 chr(((ord(key[4]) << 3) & 0xFF) | (ord(key[5]) >> 5)),
                 chr(((ord(key[5]) << 2) & 0xFF) | (ord(key[6]) >> 6)),
                 chr( (ord(key[6]) << 1) & 0xFF),
             ]
        return "".join([ self._set_odd_parity(b) for b in bytes ])

    def _set_odd_parity (self,byte):
        """
        Turns one-byte into odd parity. Odd parity means that a number in
        binary has odd number of 1's.
        Функция для дополнения ключа до длины, кратной 8-ми
        """
        assert len(byte) == 1
        parity = 0
        ordbyte = ord(byte)
        for dummy in range(8):
            if (ordbyte & 0x01) != 0:
                parity += 1
            ordbyte >>= 1
        ordbyte = ord(byte)
        if parity % 2 == 0:
            if (ordbyte & 0x01) != 0:
                ordbyte &= 0xFE
            else:
                ordbyte |= 0x01
        return chr(ordbyte)

    def _ChallengeHash(self, PeerChallenge, AuthenticatorChallenge, username):
        return SHA.new("%s%s%s" % (PeerChallenge, AuthenticatorChallenge, username)).digest()[0:8]

    def _NtPasswordHash(self, password, utf16=True):
        """Generate a NT password hash.

    	The NT password hash is a MD4 hash of the UTF-16 little endian
    	encoding of the password.
    	"""

        if utf16==True:
            pw=password.encode("utf-16-le")
        else:
            pw=password

        md4_context = md4.new()       #Эксперимент с нативной md4 библиотекой
        md4_context.update(pw)    #
        hash = md4_context.digest()   #
        return hash

    def _GenerateNTResponse(self, authchallenge, peerchallenge, username, password):
        """
        Генерируем 24-битное значение ответа клиента на challenge-запрос сервера
        чтобы сравнить с полученным от NAS значением. Если совпадают-авторизировать пользователя.
        """
        challenge = self._ChallengeHash(peerchallenge, authchallenge, username)
        passwordhash = self._NtPasswordHash(password)
        return self._ChallengeResponse(challenge, passwordhash)

    def _ChallengeResponse(self, challenge, pwhash):
        """Calculate a response to a password challenge.

    	The challenge-response algorithm is based on DES encoding:
    	the challenge is encoded three times with the three successive
    	7-byte blocks from the password hash.
    	"""
        # По алгоритму дополняем нолями MD4 хэш пароля до 21 символа
        pwhash+='\x00' * (21-len(pwhash))
        resp=''

        for i in range(3):
            desk=DES.new(self._convert_key(pwhash[i*7:(i+1)*7]), DES.MODE_ECB)
            resp+=desk.encrypt(challenge)
        return resp

    def _MSchapSuccess(self):
        return struct.pack("!BBB42s", 26, 45, self.ident, self._GenerateAuthenticatorResponse())


    def _GenerateAuthenticatorResponse(self):
        magic1= \
              "\x4D\x61\x67\x69\x63\x20\x73\x65" + \
              "\x72\x76\x65\x72\x20\x74\x6F\x20" + \
              "\x63\x6C\x69\x65\x6E\x74\x20\x73" + \
              "\x69\x67\x6E\x69\x6E\x67\x20\x63" + \
              "\x6F\x6E\x73\x74\x61\x6E\x74"

        magic2= \
              "\x50\x61\x64\x20\x74\x6F\x20\x6D" + \
              "\x61\x6B\x65\x20\x69\x74\x20\x64" + \
              "\x6F\x20\x6D\x6F\x72\x65\x20\x74" + \
              "\x68\x61\x6E\x20\x6F\x6E\x65\x20" + \
              "\x69\x74\x65\x72\x61\x74\x69\x6F" + \
              "\x6E"

        pwhash=self._NtPasswordHash(self.plainpassword)
        pwhashash=self._NtPasswordHash(pwhash,False)

        digest=SHA.new(pwhashash+self.NTResponse+magic1).digest()
        challenge=self._ChallengeHash(self.PeerChallenge, self.AuthenticatorChallenge, self.plainusername)
        digest=SHA.new(digest+challenge+magic2).digest()

        return "S="+digest.encode("hex").upper()

