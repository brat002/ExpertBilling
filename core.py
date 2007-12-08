# coding=utf8
import sys,time,os,datetime
from SocketServer import ThreadingTCPServer
from SocketServer import StreamRequestHandler
from threading import Thread
import dictionary
import packet
import struct
import corepacket
os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'
sys.path.append('c:\\Python25\\Scripts')
from mikrobill.radius.models import Session
from mikrobill.billing.models import Account, Tarif

dict=dictionary.Dictionary("dicts\dictionary","dicts\dictionary.microsoft")
t = time.clock()

class handle_auth(StreamRequestHandler):
    def handle(self):
        # self.request is the socket object
        print "%s I got an request from ip=%s port=%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S"),
            self.client_address[0],
            self.client_address[1]
            )
        #self.request.send("What is your name?\n")
        bufsize=4096
        response=self.request.recv(bufsize).strip() # or recv(bufsize, flags)
        (requestpacketid, code, length)=struct.unpack("!LBH",response[:7])
        packetobject=packet.Packet(dict=dict,packet=response[7:])
        ##Здесь нужно организовать проверку наличия в базе имени пользователя
        ##Если есть-подставляем в объект и ставим атрибут code=2, наче code=3
        replypacket=corepacket.CorePacket(secret='123', dict=dict)
        try:
            account=Account.objects.get(username=packetobject['User-Name'][0])
            if packetobject['User-Name'][0]==account.username:
               replypacket.code=2
               replypacket.username=account.username
               replypacket.password=account.password
               replypacket.AddAttribute('Service-Type',2)
               replypacket.AddAttribute('Framed-Protocol',1)
               replypacket.AddAttribute('Framed-IP-Address',account.ipaddress)
               replypacket.AddAttribute('Framed-Routing',0)

            else:
                replypacket.username='None'
                replypacket.password='None'
                replypacket.code=3
        except:
            replypacket.username='None'
            replypacket.password='None'
            replypacket.code=3

        data_to_send=replypacket.ReplyPacket()
        #data_to_send=replypacket._PktEncodeAttributes()
        self.request.sendto(data_to_send,self.client_address) # or send(data, flags)
        #print "%s connection finnished" % self.client_address[0]
        
class handle_acct(StreamRequestHandler):
        def handle(self):
        # self.request is the socket object
            #print "%s I got an request from ip=%s port=%s" % (
            #time.strftime("%Y-%m-%d %H:%M:%S"),
            #self.client_address[0],
            #self.client_address[1]
            #)
            #self.request.send("What is your name?\n")
            bufsize=8096
            response=self.request.recv(bufsize).strip() # or recv(bufsize, flags)
            (requestpacketid, code, length)=struct.unpack("!LBH",response[:7])
            packetobject=packet.Packet(dict=dict,packet=response[7:])
            ##Здесь нужно организовать проверку наличия в базе имени пользователя
            ##Если есть-подставляем в объект и ставим атрибут code=2, наче code=3
            sess=Session()
            if packetobject['Acct-Status-Type']==['Start']:
                sess.account=Account.objects.get(username=packetobject['User-Name'][0])
                sess.sessionid=packetobject['Acct-Session-Id'][0]
                sess.caller_id=packetobject['Calling-Station-Id'][0]
                sess.called_id=packetobject['Called-Station-Id'][0]
                sess.nas_id=packetobject['NAS-IP-Address'][0]
                sess.save()

            if packetobject['Acct-Status-Type']==['Alive']:
                sess=Session.objects.get(sessionid=packetobject['Acct-Session-Id'][0])
                sess.session_time=packetobject['Acct-Session-Time'][0]
                sess.bytes_in=packetobject['Acct-Input-Packets'][0]
                sess.bytes_out=packetobject['Acct-Output-Packets'][0]
                sess.save()

            if packetobject['Acct-Status-Type']==['Stop']:
                sess=Session.objects.get(sessionid=packetobject['Acct-Session-Id'][0])
                sess.session_time=packetobject['Acct-Session-Time'][0]
                sess.bytes_in=packetobject['Acct-Input-Packets'][0]
                sess.bytes_out=packetobject['Acct-Output-Packets'][0]
                sess.date_end=datetime.datetime.now()
                sess.save()

#            for key,value in packetobject.items():
#                print packetobject._DecodeKey(key),packetobject[packetobject._DecodeKey(key)]

            replypacket=corepacket.CorePacket(username="None",secret='123', password="None", dict=dict)
            replypacket.code=5
            
            data_to_send=replypacket.ReplyPacket()
            self.request.sendto(data_to_send,self.client_address) # or send(data, flags)

    
class serve_auth(Thread):
        def __init__ (self,address, handler):
            self.address=address
            self.handler=handler
            Thread.__init__(self)

        def run(self):
            server = ThreadingTCPServer(self.address, self.handler)
            server.serve_forever()


server_auth = serve_auth(("10.20.3.111", 2224), handle_auth)
server_auth.start()
		    
server_acct = serve_auth(("10.20.3.111", 2225), handle_acct)
server_acct.start()