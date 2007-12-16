# coding=utf8
"""
Модуль содержит класс для проверки прав на авторизацию
"""
import packet
import md5,struct
import sha as SHA
import md4
import pyDes as DES
from pyDes import ECB

class Auth:
    """
    Класс предназначен для реализации механизма проверки авторизации для механизмов
    PAP,CHAP,MSCHAP2 и генерации ответного пакета.
    Для проверки имени и пароля конструктором вызывается функция _CheckAuth с параметрами username, plainpassword, secret
    """

    def __init__(self, Packet, plainpassword, plainusername, code, attrs):
        self.Packet=Packet
        self.code=code
        self.typeauth=self._DetectTypeAuth(self.Packet)
        self.plainusername=plainusername
        self.plainpassword=plainpassword
        self.ident=''
        self.AccessAccept=False
        self.NTResponse=''
        self.PeerChallenge=''
        self.AuthenticatorChallenge=''
        self._CheckAuth()
        self.attrs=attrs

        
    def ReturnPacket(self):
            self.Reply=self.Packet.CreateReply()
            self.Reply.code=self.code
            if (self.typeauth=='MSCHAP2') and (self.code!=3):
                  self.Reply.AddAttribute((311,26),self._MSchapSuccess())
            return self.Reply.ReplyPacket(self.attrs)
        
    def _DetectTypeAuth(self, Packet):
        if Packet.has_key('User-Password'):
            self.typeauth='PAP'
        elif Packet.has_key('CHAP-Password'):
               self.typeauth='CHAP'
        elif Packet.has_key('MS-CHAP-Challenge'):
               self.typeauth='MSCHAP2'
        else:
            self.typeauth='UNKNOWN'
        return self.typeauth
    
    def _CheckAuth(self):
        """
        Функция, в зависимости от типа авторизации, вызывает разные методы для определения правильности
        логина и пароля.
        To Do: Если ядро ответило: доступ запретить-пропускаем.
        """
        if self.code!=3:
           if self.typeauth=='PAP':
             if self._PwDecrypt(password=self.Packet['User-Password'][0], authenticator=self.Packet.authenticator, secret=self.Packet.secret):
                 print "PAP Authorisation Ok"
                 self.AccessAccept=True
           if self.typeauth=='CHAP':
             if self._CHAPDecrypt():
                  print "CHAP Authorisation Ok"
                  self.AccessAccept=True
           if self.typeauth=='MSCHAP2':
             if self._MSCHAP2Decrypt(self.plainusername, self.plainpassword):
                print "MSCHAP2 Authorisation Ok"
                self.AccessAccept=True
               
    def _MSCHAP2Decrypt(self, username, plainpassword):
        (self.ident, var, self.PeerChallenge, reserved, self.NTResponse)=struct.unpack("!BB16s8s24s",self.Packet['MS-CHAP2-Response'][0])
        self.AuthenticatorChallenge=self.Packet['MS-CHAP-Challenge'][0]
        if self.NTResponse==self._GenerateNTResponse(self.AuthenticatorChallenge, self.PeerChallenge, username, plainpassword):
            return True
        else:
            return False

        
    def _CHAPDecrypt(self):
        (ident , password)=struct.unpack('!B16s',self.Packet['CHAP-Password'][0])
        pck="%s%s%s" % (struct.pack('!B',ident),self.plainpassword,self.Packet['CHAP-Challenge'][0])
        if md5.new(pck).digest()==password:
            return True
        else:
            return False
        

    def _PwDecrypt(self, password, authenticator, secret):
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
		pw=""
		print password, authenticator, secret

		while password:
			hash=md5.new(secret+authenticator).digest()
			print "%s; len=%s" % (hash, str(len(hash)))
			for i in range(16):
				pw+=chr(ord(hash[i]) ^ ord(password[i]))

			(authenticator,password)=(password[:16], password[16:])

		while pw.endswith("\x00"):
			pw=pw[:-1]
			
		if pw==self.plainpassword:
		    return True
		else:
		    return False
        
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
        response = self._ChallengeResponse(challenge, passwordhash)
        return response

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
    		desk=DES.des(self._convert_key(pwhash[i*7:(i+1)*7]), ECB)
    		resp+=desk.encrypt(challenge)
    	return resp
    
    def _MSchapSuccess(self):
        return struct.pack("!BBB42s", 26,45, self.ident, self._GenerateAuthenticatorResponse())


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

