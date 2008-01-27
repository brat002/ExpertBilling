#-*-coding=utf-8-*-
import dictionary
import packet
import auth
from time import clock
import settings
from coreconnection import RequestPacket
import corepacket
#import utilites
from SocketServer import ThreadingUDPServer, DatagramRequestHandler
from threading import Thread

RequireLogin=1
LoginAllowed=2
LoginDisabled=3

dict=dictionary.Dictionary("dicts\dictionary","dicts\dictionary.microsoft")

class handle_auth(DatagramRequestHandler):
      def handle(self):
        t = clock()
        bufsize=4096
        data,socket=self.request # or recv(bufsize, flags)
        addrport=self.client_address
        reqpack=RequestPacket(1,(settings.core_host, settings.core_auth), self.client_address[0])
        corereply=reqpack.getreply(data)
        packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
        packetobject=packet.Packet(secret=packetfromcore.secret, dict=dict,packet=data)
        authobject=auth.Auth(Packet=packetobject, plainpassword=packetfromcore.password, plainusername=packetfromcore.username, code=packetfromcore.code, attrs=packetfromcore._PktEncodeAttributes())
        returndata=authobject.ReturnPacket()
        self.socket.sendto(returndata,addrport)
        del reqpack
        del corereply
        del packetfromcore
        del packetobject
        print "AUTH:%.20f" % (clock()-t)

class handle_acct(DatagramRequestHandler):
      def handle(self):
        t = clock()
        bufsize=4096
        data,socket=self.request # or recv(bufsize, flags)
        addrport=self.client_address
        reqpack=RequestPacket(1,(settings.core_host, settings.core_acct), self.client_address[0])
        corereply=reqpack.getreply(data)
        requestpacket=packet.AcctPacket(dict=dict,packet=data)
        packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
        print packetfromcore.code
        if packetfromcore.code==5:
            
            replyobj=packet.AcctPacket( id=requestpacket.id, code=packetfromcore.code, secret=packetfromcore.secret, authenticator=requestpacket.authenticator, dict=dict)
            returndat=replyobj.ReplyPacket()
            self.socket.sendto(returndat,addrport)
            print "ACC:%.20f" % (clock()-t)
            del reqpack
            del corereply
            del packetfromcore
            del replyobj
        else:
            pass
          

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
