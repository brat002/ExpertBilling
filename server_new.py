#import socket, select,struct, md5
#import pickle
#from socket import AF_INET, SOCK_DGRAM
import dictionary
import packet
import auth
import time
import settings
from coreconnection import *
import corepacket
import utilites
from SocketServer import ThreadingUDPServer, DatagramRequestHandler
from threading import Thread
#значения поля code
RequireLogin=1
LoginAllowed=2
LoginDisabled=3

dict=dictionary.Dictionary("dicts\dictionary","dicts\dictionary.microsoft")

data=''

class handle_auth(DatagramRequestHandler):
      def handle(self):
        #auth_logger = logging.getLogger("RADIUS SERVER")
        t = time.clock()
        # self.request is the socket object
        #print "%s I got an request from ip=%s port=%s" % (time.strftime("%Y-%m-%d %H:%M:%S"), self.client_address[0], self.client_address[1] )
        #auth_logger.info("nanana")
        #self.request.send("What is your name?\n")
        bufsize=4096
        data,socket=self.request # or recv(bufsize, flags)
        addrport=self.client_address
        reqpack=RequestPacket(1,('10.20.3.111',2224), self.client_address[0])
        #Отправляем ядру копию пакета, полученного от NAS
        #Ядро должно вернуть закодированный объект corepacket.CorePacket c установленными атрибутами
        corereply=reqpack.getreply(data)
        packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
        #print " After parsing packet from core %.40f" % (time.time()-t)
        #Получили объект ответа. Сейчас мы можем изменять или считывать его атрибуты
        #packetfromcore=packetobject['User-Name']
        #А вот таким образом можем взять уже готовую для отправки строку аргументов attrs=packetfromcore._PktEncodeAttributes()
        #
        packetobject=packet.Packet(secret=packetfromcore.secret, dict=dict,packet=data)
        #f=open('request','w')
        #x=pickle.Pickler(f)
        #x.dump(data)
        #f.close()
        authobject=auth.Auth(Packet=packetobject, plainpassword=packetfromcore.password, plainusername=packetfromcore.username, code=packetfromcore.code, attrs=packetfromcore._PktEncodeAttributes())
        returndata=authobject.ReturnPacket()
        self.socket.sendto(returndata,addrport)
        del reqpack
        del corereply
        del packetfromcore
        del packetobject
        print "%.20f" % (time.clock()-t)

class handle_acct(DatagramRequestHandler):
      def handle(self):
        t = time.clock()
        # self.request is the socket object
        print "%s I got an request from ip=%s port=%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S"),
            self.client_address[0],
            self.client_address[1]
            )
        #self.request.send("What is your name?\n")
        bufsize=4096
        data,socket=self.request # or recv(bufsize, flags)
        addrport=self.client_address
        reqpack=RequestPacket(1,('10.20.3.111',2225), self.client_address[0])
        corereply=reqpack.getreply(data)
        requestpacket=packet.AcctPacket(dict=dict,packet=data)
        packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
        replyobj=packet.AcctPacket( id=requestpacket.id, code=packetfromcore.code, secret=packetfromcore.secret, authenticator=requestpacket.authenticator, dict=dict)
        returndat=replyobj.ReplyPacket()
        self.socket.sendto(returndat,addrport)
        print "%.20f" % (time.clock()-t)

          

class serve_requests(Thread):
        def __init__ (self, address, handler):
            self.address=address
            self.handler=handler
            Thread.__init__(self)

        def run(self):
            server = ThreadingUDPServer(self.address, self.handler)
            server.allow_reuse_address = True
            server.serve_forever()


server_auth = serve_requests(("0.0.0.0", 1812), handle_auth)
server_auth.start()

server_acct = serve_requests(("0.0.0.0", 1813), handle_acct)
server_acct.start()
