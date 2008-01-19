# coding=utf8
import socket, struct
from settings import *
import tools
requestpacketid=1

class RequestPacket:

    global requestpacketid

    #attributes список параметров
    def __init__(self, code, address, nasip):
        requestpacketid=1
        self.reqcode=code
        self.nasip=nasip
        self.connection=CoreConnection(address)
        self.data=[]


    def getreply(self,pack):
        # requestpacketid | code | lengthpacket
        self.attrlen=len(pack)
        self.lengthpacket=self.attrlen+11
        header=struct.pack("!LB4sH",requestpacketid, self.reqcode, tools.EncodeAddress(self.nasip), self.lengthpacket)
        attr=struct.pack("!%ds" % self.attrlen, pack)
        if self.connection.senddata(header+attr):
            return self.connection.recvdata()


   	def __getitem__(self, key):
   	    return self.data[key]

    def __setitem__(self, key, item):
		self.data[key]=item

class CoreConnection:
    """
    Неудачная попытка реализовать нормальный клиент для работы с ядром.
    """
    def __init__(self, address):
        self.address=address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(5)
        #self.sock.bind(('10.20.3.111',2227))
        self.sock.connect(self.address)

    def recvdata(self):
              #(rlist, wlist, xlist) = select.select(self.sock, [], self.sock)
          (data, addrport) = self.sock.recvfrom(8192)
          #self.sock.close()
          self.sock.shutdown(1)
          self.sock.close()
          return data

    def senddata(self,data):
        #(rlist, wlist, xlist) = select.select([] ,self.sock, [])
        return self.sock.send(data)

        
