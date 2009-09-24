from __future__ import with_statement

from threading import Thread, Lock
from twisted.protocols.basic import implements, interfaces, defer, Int32StringReceiver
from twisted.internet.protocol import Factory
from collections import deque
import time, traceback
logger = None

def install_logger(lgr):
    global logger
    logger = lgr

class DBDisconnectException(Exception):
    pass

class DBFailException(Exception):
    pass

class PersistentDBConnection(object):
    
    def __init__(self, driver, dsn, cursor_factory = None, encoding = 'UTF8'):
        self.driver = driver
        self.dsn = dsn
        self.connected = None
        self.connection = None
        self.cursor_ = None
        self.encoding = encoding
        self.cursor_factory = cursor_factory
        
    def connect(self):
        try:
            self.connection = self.driver.connect(self.dsn)
            self.connection.set_client_encoding('UTF8')
            if self.cursor_factory:
                self.cursor_ = self.connection.cursor(cursor_factory=self.cursor_factory)
            else:
                self.cursor_ = self.connection.cursor()
            self.connected = True
        except Exception, ex:
            self.connected = False
            logger.error('Database connect failed: %s', (repr(ex),))
            raise DBDisconnectException(str(ex))
        
    def execute(self, query, args = ()):
        if not self.connected or self.connection.closed:
            self.connect()
            
        if args:
            self.cursor_.execute(query, args)
        else:
            self.cursor_.execute(query)
        
    def fetchone(self):
        return self.cursor_.fetchone()
    
    def fetchall(self):
        return self.cursor_.fetchall()
    
    def commit(self):
        self.connection.commit()
        
    def rollback(self):
        self.connection.rollback()
        
    def cursor(self):
        return self.connection.cursor()
        
    def close(self):
        pass
    
        
    

class TCP_IntStringReciever(Int32StringReceiver):    
    producer = None
    protocol_ = None
    send_queue = None
    send_lock  = None
    producer_started = False
    
    def __init__(self, build_producer):
        #super(TCPSender, self).__init__()
        self.build_producer = build_producer
        
    def connectionMade(self):
        logger.info("SERVER: connectionMade: host: %s | peer: %s", (self.transport.getHost(), self.transport.getPeer()))
        self.peer__ = self.transport.getPeer()
        self.producer = self.build_producer(self.peer__)
        self.protocol_ = self.producer.protocol
        self.send_queue = self.producer.send_queue
        self.send_lock = self.producer.send_lock
        
    def stringReceived(self, packet):
        logger.debug("SERVER: incoming packet: host: %s | peer: %s | %s", (self.transport.getHost(), self.transport.getPeer(), packet[:self.protocol_._HEADER_LEN]))
        print 'incoming: ', packet
        idx, header, body = self.protocol_._preprocess(packet)
        if idx in self.protocol_._qprocess:
            packet = self.protocol_.get_qprocess(idx, header, body)
            if packet[0] == 'to_send':            
                s_packet = self.protocol_.send_qprocess(idx, header, body, packet)
                if s_packet[0] == 'send':
                    self.write(s_packet[1])
            if self.protocol_._check_status():
                self.producer.start()
                self.producer_started = True
                self.producer.registerConsumer_(self)
        else:
            if not self.producer_started:
                self.transport.loseConnection()
                return
            with self.send_lock:
                self.send_queue.append((idx, header, body, packet))
        
    def registerProducer(self, producer, streaming):
        return self.transport.registerProducer(producer, streaming)

    def unregisterProducer(self):
        self.transport.unregisterProducer()
        self.transport.loseConnection()

    def write(self, formatted_packet):
        print 'write packet: ', formatted_packet 
        self.transport.write(formatted_packet)


    def resumeProducing(self):
        self.transport.resumeProducing()

    def pauseProducing(self):
        self.transport.pauseProducing()

    def stopProducing(self):
        self.transport.stopProducing()

    
            
            
#FALLBACK DB ON RECONNECT!
class DBProcessingThread(Thread):

    implements(interfaces.IProducer)
    '''when too long self.transport.unregisterProducer()
        self.transport.loseConnection()'''
    
    def __init__(self, protocol, db_conn, RPC):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
        
        self.protocol = protocol
        self.send_queue = deque()
        self.send_lock = Lock()
        self.PAUSED = True
        self.suicideCondition = False
        #self.connection = self.protocol.get_connection()
        self.connection = db_conn
        self.RPC = RPC
        self.RUNNING = True
        
    def registerConsumer_(self, consumer):
        self.consumer = consumer
        self.consumer.registerProducer(self, True)
        self.resumeProducing()
        
    def pauseProducing(self):
        self.PAUSED = True

    def stopProducing(self):
        self.PAUSED = True
        self.RUNNING = False
        logger.warning("Sender consumer asked producer to stop!", ())
        
    def resumeProducing(self):
        self.PAUSED = False
        
    def process(self, fn_name, args):
        method = getattr(self.RPC, fn_name)
        if not callable(method):
            logger.error('METHOD %s IS NOT CALLABLE', fn_name)
            self.protocol._FAIL_CODE = self.protocol._FAIL_CODES['PROTOCOL_ERROR']
            return(fn_name, (Exception('Method not found')))
        
        if len(args) > 0 and isinstance(args[-1], dict) and args[-1].has_key('kwargs'):
            kwargs = args[-1]
            args = args[:-1]
            del kwargs['kwargs']
        else:
            kwargs = {}
        kwargs['connection'] = self.connection
        kwargs['cur'] = self.connection
        print repr(args), repr(kwargs)
        try:
            result = method(*args, **kwargs)
            '''
            if not isinstance(result, tuple):
                result = (result,)'''
        except Exception, ex:
            print repr(ex)
            print traceback.format_exc()
            logger.error('Execution exception: %s', repr(ex))
            self.protocol._FAIL_CODE = self.protocol._FAIL_CODES['PROTOCOL_ERROR']
            return (fn_name, (Exception('Execution exception'),))
        else:
            return (fn_name, result)
        
    def run(self):
        while self.RUNNING:
            if self.suicideCondition: break
            if self.PAUSED:
                time.sleep(1); continue
            input_packet = False
            packet_status = 0
            if len(self.send_queue) > 0:
                with self.send_lock:
                    if len(self.send_queue) > 0:
                        input_packet = self.send_queue.popleft()
            if not input_packet: 
                time.sleep(1)
                continue
            print 'inpyt: ', repr(input_packet)
            try:
                get_processed = self.protocol.get_process(*input_packet)
                print 'processed', repr(get_processed)
            except Exception, ex:
                logger.error('PROTOCOL ERROR: %s', repr(ex))
                self.protocol._FAIL_CODE = self.protocol._FAIL_CODES['PROTOCOL_ERROR']
                rpc_processed = (input_packet[0], 'error', (Exception('Protocol error'),))
            else:
                rpc_processed = (input_packet[0],) + self.process(*get_processed)
            snd_processed = self.protocol.send_process(*rpc_processed)
            self.consumer.write(snd_processed[1])
            #print len(send_packet)
          
class RPCFactory(Factory):
    def __init__(self, factory_class, build_producer):
        #super(TCPSender_ClientFactory, self).__init__()
        self.factory_class = factory_class
        self.build_producer = build_producer
        

    def buildProtocol(self, addr):
        logger.info('RPC: Connected.', ())
        return self.factory_class(self.build_producer)
            