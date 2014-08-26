from __future__ import with_statement

from threading import Thread, Lock, Event
from twisted.protocols.basic import implements, interfaces, defer, Int32StringReceiver
from twisted.internet.protocol import Factory
from collections import deque
import time, traceback, datetime
import socket

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
        if self.connected and not self.connection.closed:
            self.connection.commit()
        
    def rollback(self):
        if self.connected and not self.connection.closed:
            self.connection.rollback()
        
    def cursor(self):
        return self.connection.cursor()
       
    def close_(self):
        self.connected = False
        self.connection.close()
        
    def close(self):
        pass
    
        
    

class TCP_IntStringReciever(Int32StringReceiver):    
    producer = None
    protocol_ = None
    send_queue = None
    send_lock  = None
    producer_started = False
    SINGLE_USER = False
    peer__ = None
    add_data = {}
    
    def __init__(self, build_producer):
        #super(TCPSender, self).__init__()
        self.build_producer = build_producer
        
    def connectionMade(self):
        logger.info("SERVER: connectionMade: host: %s | peer: %s", (self.transport.getHost(), self.transport.getPeer()))
        self.peer__ = self.transport.getPeer()
        try:
            sock = self.transport.getHandle()
            sock.setsockopt ( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1 )
            sock.setsockopt ( socket.SOL_TCP, socket.TCP_KEEPIDLE, 600 )
            sock.setsockopt ( socket.SOL_TCP, socket.TCP_KEEPCNT, 20 )
            sock.setsockopt ( socket.SOL_TCP, socket.TCP_KEEPINTVL, 60 )
        except Exception, ex:
            logger.warning("SERVER: socket options were not set due to exception: %s | %s", (repr(ex), traceback.format_exc()))
        self.producer = self.build_producer(self.peer__)
        self.protocol_ = self.producer.protocol
        self.send_queue = self.producer.send_queue
        self.send_lock = self.producer.send_lock
        self.SINGLE_USER = self.producer.SINGLE_THREADED
        self.post_login = self.producer.post_login
        self.add_data = self.producer.add_data
        
    def connectionLost(self, reason):
        logger.warning("SERVER: connection was lost: %s, reason: %s", (self.peer__, reason))
        self.producer.suicideCondition = True
        if self.SINGLE_USER:
            self.producer.dummy_run()
        else:
            self.producer.EVENT.set()
        
    def stringReceived(self, packet):
        logger.debug("SERVER: incoming packet: host: %s | peer: %s | %s", (self.transport.getHost(), self.transport.getPeer(), packet[:self.protocol_._HEADER_LEN]))
        idx, header, body = self.protocol_._preprocess(packet)
        if idx in self.protocol_._qprocess:
            packet = self.protocol_.get_qprocess(idx, header, body)
            if packet[0] == 'to_send':            
                s_packet = self.protocol_.send_qprocess(idx, header, body, packet)
                if s_packet[0] == 'send':
                    self.write(s_packet[1])
            status_result = self.protocol_._check_status()
            if status_result:
                self.post_login((self.protocol_._check_status(), self.transport.getPeer(), datetime.datetime.now(), self.add_data))
                if not self.SINGLE_USER:
                    self.producer.start()
                self.producer_started = True
                self.producer.registerConsumer_(self)
        else:
            if not self.producer_started:
                self.transport.loseConnection()
                return
            '''
            with self.send_lock:
                self.send_queue.append((idx, header, body, packet))
            '''
            if not self.SINGLE_USER:
                if self.producer.EVENT.isSet():
                    if self.producer.PAUSED:
                        time.sleep(2)
                        self.producer.resumeProducing()
                        with self.producer.MAILBOX_LOCK:
                            self.producer.MAILBOX = (idx, header, body, packet)
                            self.producer.EVENT.set()
                    else:
                        time.sleep(0.5)
                        with self.producer.MAILBOX_LOCK:
                            self.producer.MAILBOX = (idx, header, body, packet)
                            self.producer.EVENT.set()
                self.producer.MAILBOX = (idx, header, body, packet)
                self.producer.EVENT.set()
            else:
                self.producer.MAILBOX = (idx, header, body, packet)
                self.producer.dummy_run()
                    
        
    def registerProducer(self, producer, streaming):
        return self.transport.registerProducer(producer, streaming)

    def unregisterProducer(self):
        self.transport.unregisterProducer()
        self.transport.loseConnection()

    def write(self, formatted_packet):
        logger.debug('RPC Server producer: write packet: %s', formatted_packet)
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
    
    def __init__(self, protocol, db_conn, RPC, reactor_ = None, single_threaded = False, post_login = lambda x: 0):
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
        self.processing_server = RPC
        self.RUNNING = True
        self.MAILBOX = None
        self.MAILBOX_LOCK = Lock()
        self.EVENT = Event()
        self.reactor_ = reactor_
        self.SINGLE_THREADED = single_threaded
        self.post_login = post_login
        self.add_data = {}
        self.add_data['USER_ID'] = [None, None]
        
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
            return(fn_name, Exception('Method not found: %s' % fn_name))
        
        if len(args) > 0 and isinstance(args[-1], dict) and args[-1].has_key('kwargs'):
            kwargs = args[-1]
            args = args[:-1]
            del kwargs['kwargs']
        else:
            kwargs = {}
        kwargs['connection'] = self.connection
        kwargs['cur'] = self.connection
        kwargs['add_data'] = self.add_data
        #print repr(args), repr(kwargs)
        try:
            result = method(*args, **kwargs)
            '''
            if not isinstance(result, tuple):
                result = (result,)'''
        except Exception, ex:
            logger.error('Execution exception: %s, %s', (repr(ex), traceback.format_exc()))
            self.protocol._FAIL_CODE = self.protocol._FAIL_CODES['PROTOCOL_ERROR']
            return (fn_name, Exception('Execution exception: %s' % str(ex)))
        else:
            return (fn_name, result)
        
    def dummy_run(self):
            input_packet = self.MAILBOX
            self.MAILBOX = None
            total_time = time.clock()
            try:
                processed_time = time.clock()
                get_processed = self.protocol.get_process(*input_packet)
                logger.debug('RPC processing thread: get processing: time: %s processed: %s', (time.clock() - processed_time, get_processed,))
            except Exception, ex:
                logger.error('PROTOCOL ERROR: %s', repr(ex))
                self.protocol._FAIL_CODE = self.protocol._FAIL_CODES['PROTOCOL_ERROR']
                rpc_processed = (input_packet[0], 'error', (Exception('Protocol error'),))
            else:
                processed_time = time.clock()
                rpc_processed = (input_packet[0],) + self.process(*get_processed)
                logger.debug('RPC processing thread: prc processed time: %s', time.clock() - processed_time)
            processed_time = time.clock()
            snd_processed = self.protocol.send_process(*rpc_processed)
            logger.debug('RPC processing thread: snd processed time: %s', time.clock() - processed_time)
            self.consumer.write(snd_processed[1])
            logger.debug('RPC processing thread: total processed time: %s', time.clock() - total_time)
        
    def run(self):
        ta1 = time.clock()
        while self.RUNNING:
            self.EVENT.wait()
            if self.suicideCondition:
                try:
                    self.connection.close()
                except:
                    pass
                break
            if self.PAUSED:
                time.sleep(0.1); continue
            input_packet = self.MAILBOX
            with self.MAILBOX_LOCK:
                self.MAILBOX = None
                self.EVENT.clear()
                
            logger.debug('RPC: packet processing time: %s', time.clock() - ta1)
            ta1 = time.clock()
            total_time = time.clock()
            try:
                #processed_time = time.clock()
                get_processed = self.protocol.get_process(*input_packet)
                #logger.debug('RPC processing thread: get processing: time: %s processed: %s', (time.clock() - processed_time, get_processed,))
            except Exception, ex:
                logger.error('PROTOCOL ERROR: %s', repr(ex))
                self.protocol._FAIL_CODE = self.protocol._FAIL_CODES['PROTOCOL_ERROR']
                rpc_processed = (input_packet[0], 'error', (Exception('Protocol error'),))
            else:http://candygram.sourceforge.net
                #processed_time = time.clock()
                rpc_processed = (input_packet[0],) + self.process(*get_processed)
                #logger.debug('RPC processing thread: prc processed time: %s', time.clock() - processed_time)
            #processed_time = time.clock()
            snd_processed = self.protocol.send_process(*rpc_processed)
            #logger.debug('RPC processing thread: snd processed time: %s', time.clock() - processed_time)
            if self.reactor_:
                self.reactor_.callFromThread(self.consumer.write,snd_processed[1])                
            else:
                self.consumer.write(snd_processed[1])
            logger.debug('RPC processing thread: total processed time: %s', time.clock() - total_time)
            #print len(send_packet)
          
class RPCFactory(Factory):
    def __init__(self, factory_class, build_producer):
        #super(TCPSender_ClientFactory, self).__init__()
        self.factory_class = factory_class
        self.build_producer = build_producer
        

    def buildProtocol(self, addr):
        logger.info('RPC: Connected.', ())
        return self.factory_class(self.build_producer)
            