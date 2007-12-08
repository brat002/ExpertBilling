import socket, select,struct, md5
from socket import AF_INET, SOCK_DGRAM
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

##addrs = socket.getaddrinfo('10.20.3.111', 1812, socket.AF_UNSPEC, socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
##
##socks = []
##
##for addr in addrs:
##	sock = socket.socket(addr[0], addr[1])
##	sock.bind(addr[4])
##	socks.append(sock)
####Accounting
##addrs = socket.getaddrinfo('10.20.3.111', 1813, socket.AF_UNSPEC, socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
##for addr in addrs:
##	sock = socket.socket(addr[0], addr[1])
##	sock.bind(addr[4])
##	socks.append(sock)
##
##
##print "listening on [%s]:%d" % (addr[4][0], addr[4][1])

dict=dictionary.Dictionary("dicts\dictionary","dicts\dictionary.microsoft")

data=''
##while 1:
##	(rlist, wlist, xlist) = select.select(socks, [], socks)
##	for sock in rlist:
##	    (data, addrport) = sock.recvfrom(4096)
##        t = time.time()
##        (code, packetid, length, authenticator)=struct.unpack("!BBH16s", data[0:20])
##        if code==1:
##            reqpack=RequestPacket(1,('10.20.3.111',2224))
##            #Отправляем ядру копию пакета, полученного от NAS
##            #Ядро должно вернуть закодированный объект corepacket.CorePacket c установленными атрибутами
##            corereply=reqpack.getreply(data)
##            packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
##            #print " After parsing packet from core %.40f" % (time.time()-t)
##            #Получили объект ответа. Сейчас мы можем изменять или считывать его атрибуты
##            #packetfromcore=packetobject['User-Name']
##            #А вот таким образом можем взять уже готовую для отправки строку аргументов attrs=packetfromcore._PktEncodeAttributes()
##            #
##            packetobject=packet.Packet(secret=packetfromcore.secret, authenticator=authenticator, dict=dict,packet=data)
##            authobject=auth.Auth(packetobject, packetfromcore.password, packetfromcore.username, code=packetfromcore.code, attrs=packetfromcore._PktEncodeAttributes())
##            returndata=authobject.ReturnPacket()
##            sock.sendto(returndata,addrport)
##        elif code==4:
##            reqpack=RequestPacket(1,('10.20.3.111',2225))
##            corereply=reqpack.getreply(data)
##            requestpacket=packet.AcctPacket(dict=dict,packet=data)
##            packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
##            replyobj=packet.AcctPacket( id=requestpacket.id, code=packetfromcore.code, secret=packetfromcore.secret, authenticator=authenticator, dict=dict)
##            returndat=replyobj.ReplyPacket()
##            sock.sendto(returndat,addrport)
##            print "%.40f" % (time.time()-t)
            
class handle_auth(DatagramRequestHandler):
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
        reqpack=RequestPacket(1,('10.20.3.111',2224))
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
        authobject=auth.Auth(packetobject, packetfromcore.password, packetfromcore.username, code=packetfromcore.code, attrs=packetfromcore._PktEncodeAttributes())
        returndata=authobject.ReturnPacket()
        self.socket.sendto(returndata,addrport)
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
        reqpack=RequestPacket(1,('10.20.3.111',2225))
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


server_auth = serve_requests(("10.20.3.111", 1812), handle_auth)
server_auth.start()

server_acct = serve_requests(("10.20.3.111", 1813), handle_acct)
server_acct.start()
