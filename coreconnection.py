# coding=utf8
import socket, struct, select
from settings import *

requestpacketid=1

class RequestPacket:

    global requestpacketid

    #attributes список параметров
    def __init__(self, code, address):
        requestpacketid=1
        self.reqcode=code
        self.connection=CoreConnection(address)
        self.data=[]


    def getreply(self,pack):
        # requestpacketid | code | lengthpacket
        self.attrlen=len(pack)
        print "attrlen=%d" % self.attrlen
        self.lengthpacket=self.attrlen+7
        header=struct.pack("!LBH",requestpacketid, self.reqcode, self.lengthpacket)
        attr=struct.pack("!%ds" % self.attrlen, pack)
        if self.connection.senddata(header+attr):
            return self.connection.recvdata()


   	def __getitem__(self, key):
   	    return self.data[key]

    def __setitem__(self, key, item):
		self.data[key]=item

class CoreConnection:

    def __init__(self, address):
        self.address=address
        self.CreateConnection()


    def CreateConnection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect(self.address)

    def recvdata(self):
              #(rlist, wlist, xlist) = select.select(self.sock, [], self.sock)
              (data, addrport) = self.sock.recvfrom(8192)
              return data

    def senddata(self,data):
        #(rlist, wlist, xlist) = select.select([] ,self.sock, [])
        return self.sock.send(data)
