from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.protocols.basic import implements, interfaces
import socket, time,struct, errno

logger = None

def install_logger(lgr):
    global logger
    logger = lgr

class TCPException(Exception):
    pass

class BlockingTcpClient(object):

    maxRetry = 600
    maxRetries = 5
    factor = 1.7
    buffer = ''
    readBytes = 60000
    structFormat = "!I"
    prefixLength = struct.calcsize(structFormat)
    MAX_LENGTH = 5000000
    recvd = ""
    needed_length = 0

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.setsockopt ( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1 )
        except:
            pass
        self.connected = False
        self.retries = 0
        self.retryTime = 2
        self.producer = None

    def registerProducer(self, producer, streaming):
        self.producer = producer

    def connect(self):
        self.retries = 0
        self.retryTime = 2
        self.retry()

    def retry(self):
        if self.retries >= self.maxRetries:
            raise TCPException('REACHED MAX RETRIES! STILL NO CONNECTION!')

        logger.info('TCP CLIENT CONNECTING: %s', ((self.host, self.port),))
        try:
            self.socket.connect((self.host, self.port))
        except Exception, ex:
            logger.error('TCP CLIENT CONNECTING FAILED: %s', (self.host, self.port))
            time.sleep(self.retryTime)
            self.retries += 1
            self.retryTime **= self.factor
            self.retry()

        self.connectionMade()


    def close(self):
        pass

    def connectionMade(self):
        self.connected = True
        self.retries = 0
        self.retryTime = 2
        logger.info('TCP CLIENT CONNECTED: sock: %s peer: %s', (self.socket.getsockname(), self.socket.getpeername()))
        return True

    def connectionLost(self):
        self.retry()

    def read(self):

        read_buffer = ''
        while True:
            recd = ''
            try:
                recd = self.socket.recv(self.readBytes)
            except socket.timeout:
                raise TimeoutError("connection timeout receiving")
            except socket.error, ex:
                if ex.args[0] == errno.EINTR or (hasattr(errno, 'WSAEINTR') and ex.args[0] == errno.WSAEINTR):
                    # interrupted system call, just retry
                    continue
                logger.error('TCP Client recovery error : %s', repr(ex))
                #self.connectionLost()
                raise TCPException('READ FAILED!')

            self.recvd = self.recvd + recd
            if len(self.recvd) >= self.prefixLength:
                if not self.needed_length:
                    self.needed_length,= struct.unpack(
                        self.structFormat, self.recvd[:self.prefixLength])
                if len(self.recvd) > self.MAX_LENGTH:
                    logger.error('LINE LENGTH %s > MAX_LENGTH: %s', (len(self.recvd), self.MAX_LENGTH))
                    return
                if len(self.recvd) < self.needed_length + self.prefixLength:
                    continue
                packet = self.recvd[self.prefixLength:self.needed_length + self.prefixLength]
                self.recvd = self.recvd[self.needed_length + self.prefixLength:]
                self.needed_length = 0
                return packet


    def write(self, data):
        try:
            sdata = data
            while True:
                total = self.socket.send(sdata)
                if total != len(sdata):
                    sdata = sdata[total:]
                    continue
                break
        except Exception, ex:
            logger.error('TCP Client send error : %s', repr(ex))
            self.connectionLost()
        return self.producer.process_get(self.read())

class TCPSender(Protocol):
    implements(interfaces.IConsumer)

    isConnected = False

    def __init__(self, producer, bufsize = None):
        #super(TCPSender, self).__init__()
        self.producer = producer
        self.bufsize = bufsize

    def connectionMade(self):
        self.isConnected = True
        if self.bufsize:
            self.transport.bufferSize = self.bufsize
        #self.producer_ = self.producer(queues.databaseQueue, queues.dbLock, self, vars.NFR_DELIMITER)
        self.producer.registerConsumer_(self)

    def connectionLost(self, reason):
        self.isConnected = False

    def dataReceived(self, data):
        if data == '!SLP':
            time.sleep(30)

    def registerProducer(self, producer, streaming):
        return self.transport.registerProducer(producer, streaming)

    def unregisterProducer(self):
        self.transport.unregisterProducer()
        self.transport.loseConnection()

    def write(self, formatted_packet):
        if self.isConnected:
            #print 'SENT LINE: ', formatted_packet[:6], '|', formatted_packet[-6:]
            self.transport.write(formatted_packet)

        else:
            return NOT_TRASMITTED


    def resumeProducing(self):
        self.transport.resumeProducing()

    def pauseProducing(self):
        self.transport.pauseProducing()

    def stopProducing(self):
        self.transport.stopProducing()



class TCPSender_ClientFactory(ReconnectingClientFactory):
    protocol = TCPSender
    def __init__(self, producer):
        #super(TCPSender_ClientFactory, self).__init__()
        self.Producer = producer        

    def startedConnecting(self, connector):
        logger.info('SENDER: Started connecting.', ())

    def buildProtocol(self, addr):
        logger.info('SENDER: Connected.', ())
        self.resetDelay()
        return TCPSender(self.Producer)
        #tcs.producer = self.producer
        #return tcs

    def clientConnectionLost(self, connector, reason):
        logger.info('SENDER: Lost connection.  Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        logger.info('SENDER: Connection failed. Reason:', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
