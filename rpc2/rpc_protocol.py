from hashlib import md5
from Crypto.Cipher import Blowfish
from functools import partial
import time
import marshal, cPickle, zlib, struct, random, traceback
from twisted.protocols.basic import implements, interfaces
BLOCK_SIZE = 8
CHALLENGE_LEN = 16
KEY_LEN = 16
import random
import os, datetime

from types import InstanceType, StringType, UnicodeType

logger = None

def install_logger(lgr):
    global logger
    logger = lgr
    
    
def format_update (x,y):
    #print 'y', y, type(y)
    if y!=u'Null' and y!=u'None':
        if type(y)==StringType or type(y)==UnicodeType:
            #print True
            y=y.replace('\'', '\\\'').replace('"', '\"').replace("\\","\\\\")
            #print 'y', y
        return "%s='%s'" % (x,y)
    else:
        return "%s=%s" % (x,'Null')

def format_insert(y):
    if y==u'Null' or y ==u'None':
        return 'Null'
    elif type(y)==StringType or type(y)==UnicodeType:
        #print True
        return y.replace('\'', '\\\'').replace('"', '\"').replace("\\","\\\\")
    else:
        return y
    
class Object(object):
    def __init__(self, result=[], *args, **kwargs):
        for key in result:
            setattr(self, key, result[key])
        """
        if result[key]!=None:
            setattr(self, key, result[key])
        else:
            setattr(self, key, 'Null')
        """


        for key in kwargs:
            setattr(self, key, kwargs[key])  

        #print dir(self)          

    def _toTuple(self):        
        return tuple(self.__dict__.items().append(self.__class__.__name__))
    
    @staticmethod
    def _fromTuple(tpl):
        return Object(dict(tpl))

    def save(self, table):
        fields=[]
        for field in self.__dict__:
            if type(field)!=InstanceType:
                if self.__dict__[field]=='now()':
                    self.__dict__[field] = datetime.datetime.now()
                fields.append(field)

        try:
            self.__dict__['id']
            sql=u"UPDATE %s SET %s WHERE id=%d RETURNING id;" % (table, " , ".join([format_update(x, unicode(self.__dict__[x])) for x in fields ]), self.__dict__['id'])
        except Exception, e:
            #print e
            sql=u"INSERT INTO %s (%s) VALUES('%s') RETURNING id;" % (table, ",".join([x for x in fields]), ("%s" % "','".join([format_insert(unicode(self.__dict__[x])) for x in fields ])))
            sql = sql.replace("'None'", 'Null')
            sql = sql.replace("'Null'", 'Null')
        return sql
    
    def delete(self, table):
        fields=[]
        for field in self.__dict__:
            if type(field)!=InstanceType:
                # and self.__dict__[field]!=None
                fields.append(field)
        
        sql = u"DELETE FROM %s WHERE %s" % (table, " AND ".join([format_update(x, unicode(self.__dict__[x])) for x in fields ]))
        
        return sql
        
    def get(self, fields, table):
        return "SELECT %s FROM %s WHERE id=%d" % (",".join([fields]), table, int(self.id))

    def __call__(self):
        return self.id

    def hasattr(self, attr):
        if attr in self.__dict__:
            return True
        return False

    def isnull(self, attr):
        if self.hasattr(attr):
            if self.__dict__[attr]!=None and self.__dict__[attr]!='Null':
                return False

        return True
    
class ProtocolException(Exception):
    pass

class AuthenticationException(Exception):
    pass

class BasicClientConnection(object):
    implements(interfaces.IProducer)
    
    STATUS_ = ('none', False)
    def __init__(self, protocol):
        self.protocol = protocol
        self.consumer = None
        self.mailbox = None
        self.notifier = None
        
    def registerConsumer_(self, consumer):
        self.consumer = consumer
        self.consumer.registerProducer(self, True)
        self.resumeProducing()
        
    def pauseProducing(self):
        #self.PAUSED = True
        pass

    def stopProducing(self):
        pass
        #self.PAUSED = True
        logger.warning("Sender consumer asked producer to stop!", ())
        
    def resumeProducing(self):
        pass
        #self.PAUSED = False
        
    def authenticate(self, login, password):
        return self.process_send('AUTH', login, password)
    
        
    def process_get(self, *args):
        idx, header, body = self.protocol._preprocess(args[0])
        if idx in self.protocol._qprocess:
            packet = self.protocol.get_qprocess(idx, header, body)
        else:
            packet = self.protocol.get_process(idx, header, body)
            
        if packet[0] == 'to_send':
            return self.process_send(idx, header, body, packet)
        else:
            data = packet[1]
            if isinstance(data, tuple) and len(data) == 1:
                data = data[0]
            return data
    
    #check_all + fails + fallbacks!
    def process_send(self, idx, *args, **kwargs):
        try:
            if idx in self.protocol._qprocess:
                packet = self.protocol.send_qprocess(idx, *args)
            else:
                if kwargs:
                    kwargs['kwargs'] = ''
                    args = args + (kwargs,)
                logger.debug('RPC: basic client args: %s', (args,))
                packet = self.protocol.send_process(idx, *args)
            if packet[0] == 'send':
                return self.consumer.write(packet[1])
            else:
                #print packet[0]
                self.STATUS_ = ('OK', True)
                return ('OK', True)
        except Exception, ex:
            logger.error('Exception detected: %s | %s', (repr(ex), traceback.format_exc()))
            #if self.notifier:
            #    self.notifier(str(ex))
            raise ex
            
    def process_outer(self, idx, *args):
        self.process_send(idx, *args)
        return self.mailbox
    
    def __getattr__(self, *args, **kwargs):
        return partial(self.process_send,'DATA', args[0])

class RPCProtocol(object):
    structFormat = "!I"
    prefixLength = struct.calcsize(structFormat)
    _qprocess = ['AUTH',]
    _encrypt = True
    _compress  = 'Z'
    _idxes = ['AUTH', 'DATA', 'RCNT']
    _len_size = 16
    _INDEX_LENGTH = 4
    _IDX_LEN = 4
    _HEADER_LEN = 16
    _STATUS_CODE = '00'
    _FAIL_CODE   = '00'
    _OBJECT_FLAG = False
    _FAIL_CODES  = {'DB_ERROR': '09', 'DB_DISCONNECT': '13', 'PROTOCOL_ERROR' : '17'}
    _compression = {'Z': {'compress': zlib.compress, 'decompress': zlib.decompress}}
    _serializer = {'P': {'dumps': lambda x: cPickle.dumps(x, cPickle.HIGHEST_PROTOCOL), 'loads': cPickle.loads},\
                  'M': {'dumps': marshal.dumps, 'loads': marshal.loads}}
    _object_name = {'Object': 'O'}
    _allowed_objects = (Object,)
    _object = {'Object': {'tuplify': lambda x: x._toTuple, 'detuplify': lambda x: Object._fromTuple}}
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.identity = None
        self.index = '0000'
        
    def _check_status(self):
        return self.authenticator.status == 'OK'
    
    def _preprocess(self, packet):
        '''
        plen = packet[16:32]
        if str(plen) != len(packet):
            raise ProtocolException("Wrong packet length %s | %s" % (plen, len(packet)))'''
        idx = packet[:4]
        if idx not in self._idxes:
            raise ProtocolException("Unknown index %s" % (idx,))
        if not idx in self._qprocess:
            header = packet[4:16]
            packet = packet[16:]
            '''
            if header[2:4] != '00':
                raise ProtocolException("Fail code detected %s" % (header, ))
            '''
        else:
            header = packet[4:8]
            packet = packet[8:]
        return idx, header, packet
    
    def get_qprocess(self, idx, header, body, *args):
        return self.authenticator.process('get', header, body)
    
    def send_qprocess(self, idx, *args, **kwargs):
        type, packet = self.authenticator.process('send', *args, **kwargs)
        if type == 'send':
            return (type, ''.join((struct.pack(self.structFormat, len(packet)), packet)))
        else: 
            return (type, packet)
        
    def get_process(self, idx, header, body, *args):
        if idx == 'DATA':
            return self.get_process_data(header, body, *args)
        else:
            raise ProtocolException('UNIMPLEMENTED IDX: %s' % idx)
        
    def get_process_data(self, header, body, *args):
        data = body
        self.index = header[:4]
        encrypt, compress, serialize, object_ = header[4:8]
        process_time = time.clock()
        if encrypt != '0':
            data = self.authenticator._decrypt(self.authenticator.sess_crypter, data)
        logger.debug('RPC: get_process_data: encrypt time: %s', time.clock() - process_time)
        process_time = time.clock()
        if compress != '0':
            compressor = self._compression.get(compress)
            if not compressor:
                raise ProtocolException("NO COMPRESSOR FOUND: %s" % header)
            data = compressor['decompress'](data)
        logger.debug('RPC: get_process_data: compress time: %s', time.clock() - process_time)
        process_time = time.clock()
        if serialize != '0':
            serializer = self._serializer.get(serialize)
            if not serializer:
                raise ProtocolException("NO serializer FOUND: %s" % header)
            data = serializer['loads'](data)
        logger.debug("RPC: loaded data: %s", (data,))
        logger.debug('RPC: get_process_data: serialize time: %s', time.clock() - process_time)
        process_time = time.clock()
        if object_ != '0':
            '''objectifier = self._object.get(object_)
            if not objectifier:
                raise ProtocolException("NO objectifier FOUND: %s" % header)'''
            n_data = []
            for elt in data[1]:
                if isinstance(elt, list):
                    elt = map(self.objectifier_fn, elt)
                elif isinstance(elt, tuple):
                    elt = tuple(map(self.objectifier_fn, elt))
                else:
                    elt = self.objectifier_fn(elt)
                n_data.append(elt)
            data = (data[0], tuple(n_data))
            #data[1] = ((objectifier['detuplify'](data[1][0][0]) + data[1][0][1:]), data[1][1])
            #data = (data[0], (objectifier['detuplify'](data[1][0]),) + data[1][1:])
        logger.debug('RPC: get_process_data: objectify time: %s', time.clock() - process_time)
        if data[1] and isinstance(data[1][0], Exception):
            raise data[1][0]
        return data
    
    def send_process(self, idx, f_name, *args):
        if idx == 'DATA':
            return self.send_process_data(idx, f_name, *args)
        else:
            raise ProtocolException('UNIMPLEMENTED IDX: %s' % idx)
        
    def deobjectifier_fn(self, elt):
        if isinstance(elt, self._allowed_objects):
            self._OBJECT_FLAG = True
            return self._object[elt.__class__.__name__]['tuplify'](elt)
        else: 
            return elt
        
    def objectifier_fn(self, elt):
        if isinstance(elt, tuple) and isinstance(elt[-1], str) and self._object.has_key(elt[-1]):
            return self._object[elt[-1]]['detuplify'](elt[:-1])
        else:
            return elt
            
    def send_process_data(self, idx, f_name, *args):
        #f_name = args[0]
        #data = args[1]
        #data = (args, kwargs)
        encrypt, compress, serialize, object_ = '0000'
        self._OBJECT_FLAG = False
        process_time = time.clock()
        if args:
            n_args = []
            for elt in args:
                if isinstance(elt, list):
                    elt = map(self.deobjectifier_fn, elt)
                elif isinstance(elt, tuple):
                    elt = tuple(map(self.deobjectifier_fn, elt))
                else:
                    elt = self.deobjectifier_fn(elt)
                n_args.append(elt)
            n_args = tuple(n_args)
           
        packet = (f_name, args)
        #print repr(packet)
        logger.debug('RPC: send_process_data: objectify time: %s', time.clock() - process_time)
        process_time = time.clock()
        try:
            packet = marshal.dumps(packet)
            serialize = 'M'
        except Exception, ex:
            packet = cPickle.dumps(packet, cPickle.HIGHEST_PROTOCOL)
            serialize = 'P'
        '''
        packet = cPickle.dumps(packet, cPickle.HIGHEST_PROTOCOL)
        serialize = 'P'
        '''
        logger.debug('RPC: send_process_data: serialize time: %s', time.clock() - process_time)
        process_time = time.clock()
        if self._compress:
            packet = self._compression[self._compress]['compress'](packet)
            compress = self._compress
        logger.debug('RPC: send_process_data: compress time: %s', time.clock() - process_time)
        process_time = time.clock()
        if self._encrypt:
            packet = self.authenticator._encrypt(self.authenticator.sess_crypter, packet)
            encrypt = 'E'
        logger.debug('RPC: send_process_data: encrypt time: %s', time.clock() - process_time)
        process_time = time.clock()
        index = str(int(self.index) + 1)
        if len(index) > self._INDEX_LENGTH:
            index = '0000'
        elif len(index) < self._INDEX_LENGTH:
            index = '0'*(self._INDEX_LENGTH - len(index)) + index
        header = ''.join((idx, self._STATUS_CODE, self._FAIL_CODE, encrypt, compress, serialize, object_, index))
        self._STATUS_CODE = '00'
        self._FAIL_CODE   = '00'
        length__ = struct.pack(self.structFormat, self._HEADER_LEN + len(packet))
        logger.debug('RPC: send_process_data: pack time: %s', time.clock() - process_time)
        return ('send', ''.join((length__, header, packet))) 
    
    def log_packet(self, packet):
        return 'Packet header: %s' % (packet[:16],)
    
    def get_len(self, plen):
        s_len = str(plen)
        return '0'* (self._len_size - len(s_len)) + s_len
    
    def process(self):
        pass
    
    def reset(self):
        self.authenticator.reset()
        
class Authenticator(object):
    _state = {}
    
    def __init__(self):
        pass
    
    def process(self, *args, **kwargs):
        pass
    
    def process_packet(self, *args, **kwargs):
        pass
    
    def client_send_process(self, *args, **kwargs):
        pass
    
    def client_get_process(self, *args, **kwargs):
        pass
    
    def server_send_process(self, *args, **kwargs):
        pass
    
    def server_get_process(self, *args, **kwargs):
        pass
    
class MD5_Authenticator(Authenticator):
    _state = {}
    _FAIL_CODES = {'01':'NO SUCH USER!', '02':'Challenge check failed!', '03':'Wrong AUTH get status!', '04':''}
    def __init__(self, identity, code, check_user = None, addr = None):
        self.identity = identity
        self.status = None
        self.code = code
        self.session_key = None
        self.login = None
        self.password = None
        self.challenge = None
        self.pass_crypter = None
        self.sess_crypter = None
        self.check_user = check_user
        self.addr = addr
        self.fail_code = '00'
        
    def reset(self):
        self.status = None
        self.session_key = None
        self.login = None
        self.password = None
        self.challenge = None
        self.pass_crypter = None
        self.sess_crypter = None
        self.fail_code = '00'
        
    def _encrypt(self, crypter, data):
        data_mod = len(data) % BLOCK_SIZE
        pad_char = "=" if data[-1] != '='  else "-"
        #data_mod = BLOCK_SIZE if not data_mod else data_mod
        crypt_str = data + pad_char*(BLOCK_SIZE - data_mod)
        return crypter.encrypt(crypt_str)
    
    def _decrypt(self, crypter, cdata):
        ddata = crypter.decrypt(cdata)
        return ddata.rstrip(ddata[-1])
        
    def process(self, type, *args, **kwargs):
        if args[0][0] == '9': self.reset
        method = getattr(self, '_'.join((self.identity, type, 'process')), None)
        if method:
            return method(*args, **kwargs)
        else:
            raise Exception("Unknown identity/type: %s / %s" % (self.identity, type))
    
    def process_packet(self, *args, **kwargs):
        if not self.session_key:
            raise Exception('no sess key')
        packet = args[0]
        if   args[1] == 'encrypt':
            return self._encrypt(self.sess_crypter, packet)
        elif args[1] == 'decrypt':
            return self._decrypt(self.sess_crypter, packet)
        #encrypt with a session_key
        else:
            raise ProtocolException("Unknown process packet type %s" % args[1])
    
    #9000 - login sent
    #1100 - challenge replied
    def client_send_process(self, *args, **kwargs):
        if not self.status:
            self.login = args[0]
            self.password = args[1]
            self.status = 'init'
            return ('send', ''.join((self.code, '9000', '0'*8, '-ln-', str(self.login), '-ln-')))
        elif self.status == 'replied':
            #self.challenge = args[0]
            self.status = 'ch_sent'
            return ('send', ''.join((self.code,'1100', '0'*8, '-cr-',  md5(self.password + self.challenge).digest(), '-cr-')))
        else:
            raise Exception("Wrong AUTH send status: %s" % self.status)
        '''
        elif self.status == 'sk_rcvd':
            self.'''
            
            
    
    def client_get_process(self, *args, **kwargs):
        if not self.status:
            raise Exception('empty status')
        header = args[0]
        if header[2:4] != '00':
            raise Exception('Exception detected: %s!' % self._FAIL_CODES.get(header[2:4], 'Unknown error'))
        #print repr(args)
        if self.status == 'init':
            '''
            header = args[0]
            if header[2] == '1':
                raise Exception('No such user')
            elif header[2] != '0':
                raise Exception('Unknown error')
            '''
            self.challenge = args[1].split('-ch-')[1]
            if not self.challenge:
                raise Exception('No challenge')
            self.status = 'replied'
            return ('to_send',)
        elif self.status == 'ch_sent':
            header = args[0]
            '''
            if header[2] == '1':
                raise Exception('No such user')
            '''
            self.pass_crypter = Blowfish.new(self.password)
            self.session_key = self._decrypt(self.pass_crypter, args[1].split('-sk-')[1])
            self.sess_crypter = Blowfish.new(self.session_key)
            #print self.session_key
            self.status ='OK'
            return ("OK", True)
        else:
            raise Exception("Wrong AUTH get status: %s" % self.status)
            
    
    def server_send_process(self, *args, **kwargs):
        if self.fail_code != '00':
            return_packet = ('send', ''.join((self.code,'99', self.fail_code)))
            self.reset()
            return return_packet
        if self.status == 'user_ok':
            self.challenge = self.issue_challenge(CHALLENGE_LEN)
            self.status = 'ch_sent'
            return ('send', ''.join((self.code,'10', self.fail_code, '-ch-', self.challenge, '-ch-')))
        elif self.status == 'chr_got':
            self.session_key = self.issue_challenge(KEY_LEN)
            #print self.session_key
            self.sess_crypter = Blowfish.new(self.session_key)
            self.status = 'OK'
            return ('send', ''.join((self.code,'12', self.fail_code, '-sk-', self._encrypt(self.pass_crypter, self.session_key), '-sk-')))
    
    def server_get_process(self, *args, **kwargs):
        if args[1][4:8] == '9000':
            self.reset()
        if not self.status:
            try:
                self.login = args[1].split('-ln-')[1]
                if not self.login:
                    raise Exception("No login!")
                login_status = self.check_user(self.login)
                if not login_status:
                    raise Exception("No such user!")
            except Exception, ex:
                logger.error("AUTH SGP login exception: %s ; %s", (args, repr(ex)))
                self.fail_code = '01'
                #raise ex
            self.password = str(login_status[0][1])
            self.pass_crypter = Blowfish.new(self.password)
            self.status = 'user_ok'
            #self.challenge = self.issue_challenge(CHALLENGE_LEN)
            #return ('send', ''.join((self.code,'1000', '-ch-', self.challenge, '-ch-')))
            return ('to_send',)
        elif self.status == 'ch_sent':
            ch_status = md5(self.password + self.challenge).digest() == args[1].split('-cr-')[1]
            if not ch_status:
                self.fail_code = '02'
                logger.error("AUTH SGP Challenge check failed!: %s", (args,))
                #raise Exception("Challenge check failed!")
            self.status = 'chr_got'
            #sess_key = self.issue_challenge(KEY_LEN)
            #self.sess_crypter = Blowfish.new(sess_key)
            return ('to_send',)
        else:
            self.fail_code = '03'
            logger.error("AUTH SGP: Wrong AUTH get status %s:  %s", (self.status, args,))
            #raise Exception("Wrong AUTH get status: %s" % self.status)
            
                
                
    def issue_challenge(self, ch_len):
        value = ''
        for i in xrange(ch_len):
            value += chr(random.randint(1,255))
        return value
    
