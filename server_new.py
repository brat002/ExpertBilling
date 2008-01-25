#-*-coding=utf-8-*-
import dictionary
import packet
import auth
import time
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
        #РћС‚РїСЂР°РІР»СЏРµРј СЏРґСЂСѓ РєРѕРїРёСЋ РїР°РєРµС‚Р°, РїРѕР»СѓС‡РµРЅРЅРѕРіРѕ РѕС‚ NAS
        #РЇРґСЂРѕ РґРѕР»Р¶РЅРѕ РІРµСЂРЅСѓС‚СЊ Р·Р°РєРѕРґРёСЂРѕРІР°РЅРЅС‹Р№ РѕР±СЉРµРєС‚ corepacket.CorePacket c СѓСЃС‚Р°РЅРѕРІР»РµРЅРЅС‹РјРё Р°С‚СЂРёР±СѓС‚Р°РјРё
        corereply=reqpack.getreply(data)
        packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
        #print " After parsing packet from core %.40f" % (time.time()-t)
        #РџРѕР»СѓС‡РёР»Рё РѕР±СЉРµРєС‚ РѕС‚РІРµС‚Р°. РЎРµР№С‡Р°СЃ РјС‹ РјРѕР¶РµРј РёР·РјРµРЅСЏС‚СЊ РёР»Рё СЃС‡РёС‚С‹РІР°С‚СЊ РµРіРѕ Р°С‚СЂРёР±СѓС‚С‹
        #packetfromcore=packetobject['User-Name']
        #Рђ РІРѕС‚ С‚Р°РєРёРј РѕР±СЂР°Р·РѕРј РјРѕР¶РµРј РІР·СЏС‚СЊ СѓР¶Рµ РіРѕС‚РѕРІСѓСЋ РґР»СЏ РѕС‚РїСЂР°РІРєРё СЃС‚СЂРѕРєСѓ Р°СЂРіСѓРјРµРЅС‚РѕРІ attrs=packetfromcore._PktEncodeAttributes()
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
