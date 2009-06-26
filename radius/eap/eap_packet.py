import struct, types, random, md5
import copy


PW_MD5_CHALLENGE  = 1
PW_MD5_RESPONSE	  = 2
PW_MD5_SUCCESS	  = 3
PW_MD5_FAILURE	  = 4
PW_MD5_MAX_CODES  = 4

MD5_HEADER_LEN 	  = 4
MD5_CHALLENGE_LEN = 16 

PW_EAP_REQUEST   = 1
PW_EAP_RESPONSE  = 2
PW_EAP_SUCCESS   = 3
PW_EAP_FAILURE   = 4
PW_EAP_MAX_CODES = 4


PW_EAP_IDENTITY       = 1
PW_EAP_NOTIFICATION   = 2
PW_EAP_NAK            = 3
PW_EAP_MD5            = 4
PW_EAP_OTP            = 5
PW_EAP_GTC            = 6
PW_EAP_TLS            = 13
PW_EAP_LEAP           = 17
PW_EAP_SIM            = 18
PW_EAP_TTLS           = 21
PW_EAP_PEAP           = 25
PW_EAP_MSCHAPV2       = 26
PW_EAP_CISCO_MSCHAPV2 = 49
PW_EAP_TNC            = 38
PW_EAP_IKEV2          = 49
PW_EAP_MAX_TYPES      = 9

EAP_HEADER_LEN  = 4
EAP_TYPE_LEN    = 1

EAP_START = 2
NAME_LEN  = 32

EAP_HEADER = "!BBH"
EAP_TYPE = "!B"

# struct.pack('!B') == chr

class EAPError(Exception):
    pass


class EAP_Packet(object):
    __slots__ = ('code', 'identifier', 'length', 'type', 'type_data', 'raw_packet')

    def __init__(self):
        self.code = 0
        self.identifier = 0
        self.length = 0
        self.type = None
        self.type_data = None
        self.raw_packet = ''


    def unpack_header(self, raw_packet):
        self.raw_packet = raw_packet
        try:
            self.code, self.identifier, self.length = struct.unpack(EAP_HEADER, self.raw_packet[:EAP_HEADER_LEN])
        except struct.error:
            raise EAPError("EAP message header is corrupt!: " + repr(struct.error))
        if self.code in (PW_EAP_REQUEST, PW_EAP_RESPONSE):
            self.type, = struct.unpack(EAP_TYPE, self.raw_packet[EAP_HEADER_LEN:EAP_HEADER_LEN + EAP_TYPE_LEN])
            
    def unpack(self, raw_packet):
        self.raw_packet = raw_packet
        try:
            self.code, self.identifier, self.length = struct.unpack(EAP_HEADER, self.raw_packet[:EAP_HEADER_LEN])
        except struct.error:
            raise EAPError("EAP message header is corrupt!")
        
        if len(self.raw_packet) != self.length:
            raise EAPError("EAP message wrong length!")
        
        if self.code in (PW_EAP_REQUEST, PW_EAP_RESPONSE) and len(raw_packet) > EAP_HEADER_LEN:
            try:
                self.type, = struct.unpack(EAP_TYPE, self.raw_packet[EAP_HEADER_LEN:EAP_HEADER_LEN + EAP_TYPE_LEN])
                self.type_data = self.raw_packet[EAP_HEADER_LEN + EAP_TYPE_LEN:]
            except struct.error:
                raise EAPError("EAP type field is corrupt!")
            except IndexError:
                raise EAPError("EAP type data retrieval error!")
            
    def packs(self, code, identifier, ptype = None, type_data = None):
        self.code = code
        self.identifier = identifier
        self.type = ptype
        self.type_data = type_data
        if ptype is None:
            self.length = EAP_HEADER_LEN
        elif type_data is not None:
            self.length = EAP_HEADER_LEN + EAP_TYPE_LEN + len(type_data)
        else:
            raise EAPError("EAP error: either TYPE or TYPE-Data are not present!")
        
        self._pack()
            
    def _pack(self):
        if self.type is None:            
            try:
                self.length = EAP_HEADER_LEN
                self.raw_packet = struct.pack(EAP_HEADER, self.code, self.identifier, self.length)
            except struct.error:
                raise EAPError("EAP error: problems with packing!")
        elif self.type_data is not None:
            try:
                self.length = EAP_HEADER_LEN + EAP_TYPE_LEN + len(self.type_data)
                self.raw_packet  = struct.pack(EAP_HEADER, self.code, self.identifier, self.length)
                self.raw_packet += struct.pack(EAP_TYPE, self.type)
                self.raw_packet += self.type_data
            except struct.error:
                raise EAPError("EAP error: problems with packing!")
        else:
            raise EAPError("EAP packing error: either TYPE or TYPE-Data are not present!")
        
    @staticmethod
    def get_success_packet(id):
        eap_packet = EAP_Packet()
        eap_packet.packs(PW_EAP_SUCCESS, id)
        return eap_packet.raw_packet
    
    @staticmethod
    def get_failure_packet(id):
        eap_packet = EAP_Packet()
        eap_packet.packs(PW_EAP_FAILURE, id)
        return eap_packet.raw_packet
    
    def __repr__(self):
        return ' ;'.join((field + ': ' + repr(getattr(self,field)) for field in self.__slots__))
    
class EAP_MD5(EAP_Packet):
    __slots__ = ('value', 'value_length', 'name')
    
    def __init__(self):
        super(EAP_MD5, self).__init__()
        self.value_length = 0
        self.value = None
        self.name = ''
        
    def unpack(self, raw_packet):
        super(EAP_MD5, self).unpack(raw_packet)
        if not self.type_data:
            raise EAPError("EAP-MD5 error: no type data found!")
        try:
            self.value_length = struct.unpack("!B", self.type_data[:1])[0]
            self.value = self.type_data[1:self.value_length + 1]
            self.name  = self.type_data[self.value_length+1:]
        except struct.error:
            raise EAPError("EAP type field is corrupt! - " + repr(struct.error))
        except IndexError:
            raise EAPError("EAP type data retrieval error! - " + repr(IndexError))
    
    def set_challenge(self):
        self.type = PW_EAP_MD5
        value = ''
        for i in xrange(MD5_CHALLENGE_LEN):
            value += chr(i)
        #MD5_CHALLENGE_LEN + 1
        self.type_data = struct.pack("!B", MD5_CHALLENGE_LEN) + value + self.name
        
    @staticmethod
    def get_challenge_reply(old_eap_packet):
        eap_packet = copy.deepcopy(old_eap_packet)
        eap_packet.type = PW_EAP_MD5
        value = ''
        for i in xrange(MD5_CHALLENGE_LEN):
            value += chr(random.randint(0,255))
            
        #MD5_CHALLENGE_LEN + 1
        eap_packet.type_data = struct.pack("!B", MD5_CHALLENGE_LEN) + value
        eap_packet._pack()
        return eap_packet.raw_packet, value
    
    def check_response(self, password, challenge, id):
        return self.value == md5.md5(''.join((struct.pack("!B", id), password, challenge))).digest()
    
    def __repr__(self):
        return '; '.join((field + ': ' + repr(getattr(self,field)) for field in super(EAP_MD5, self).__slots__ + self.__slots__))

    
EAP_HANDLERS = {PW_EAP_IDENTITY: EAP_Packet, PW_EAP_MD5: EAP_MD5}


    