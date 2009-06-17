# coding=utf8
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
from radius.eap.eap_packet import EAP_Packet, get_failure_packet, get_success_packet, EAP_HANDLERS

class Auth:
    """
    Класс предназначен для реализации проверки авторизации для механизмов
    PAP,CHAP,MSCHAP2 и генерации ответного пакета.
    Для проверки имени и пароля конструктором вызывается функция _CheckAuth с параметрами username, plainpassword, secret
    """

    def __init__(self, packetobject, username, password, secret, access_type):
        self.packet=packetobject
        self.secret = secret
        self.access_type = access_type
        self.extensions = {}


        self.typeauth=self._DetectTypeAuth()

        self.plainusername=username
        self.plainpassword=password


        self.ident=''
        self.NTResponse=''
        self.PeerChallenge=''
        self.AuthenticatorChallenge=''

        self.attrs = None




    def ReturnPacket(self, packetfromcore):
        self.attrs=packetfromcore._PktEncodeAttributes()

        self.Reply=self.packet.CreateReply()
        self.Reply.secret = self.secret
        if self._CheckAuth(code = self.code):
            self.Reply.code=self.code
            if (self.typeauth=='MSCHAP2') and (self.code!=3):
                self.Reply.AddAttribute((311,26),self._MSchapSuccess())
            return self.Reply.ReplyPacket(self.attrs)
        elif self.typeauth == 'EAP':
            #self.packet.
            return self.Reply.ReplyPacket()
        else:
            self.Reply.code=packet.AccessReject
            return self.Reply.ReplyPacket()

    def _DetectTypeAuth(self):
        if self.packet.has_key('User-Password') and self.access_type!='DHCP':
            return 'PAP'
        elif self.packet.has_key('CHAP-Password') and self.access_type!='DHCP':
            return 'CHAP'
        elif self.packet.has_key('MS-CHAP-Challenge') and self.access_type!='DHCP':
            return 'MSCHAP2'
        elif self.packet.has_key('EAP-Message') and self.access_type!='DHCP':
            self.extensions['eap-packet'] = EAP_Packet().unpack_header(self.packet['EAP-Message'])
            return 'EAP'
        else:
            return 'UNKNOWN'

    def _HandlePacket(self):
        pass

    def _ProcessPacket(self):
        pass

    def EAP_Reply(self):
        if self.code == packet.AccessAccept:
            return get_success_packet(self.extensions['eap-packet'].identifier)


    def set_code(self, code):
        self.code = code

    def check_auth(self):
        return self._CheckAuth()


    def _CheckAuth(self, code= packet.AccessReject):
        """
        Функция, в зависимости от типа авторизации, вызывает разные методы для определения правильности
        логина и пароля.
        To Do: Если ядро ответило: доступ запретить-пропускаем.
        """
        if self.access_type=='DHCP':
            return True
        if code not in (packet.AccessReject, packet.AccessChallenge):
            if self.typeauth=='PAP':
                #print self._PwDecrypt()
                if self._PwDecrypt():
                    #print 'pap=', True
                    return True
            elif self.typeauth=='CHAP':
                if self._CHAPDecrypt():
                    return True
            elif self.typeauth=='MSCHAP2':
                #print "mschap2"
                if self._MSCHAP2Decrypt():
                    return True
        return False



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

