# coding=utf8
import socket, struct
from settings import *
import tools
requestpacketid=1

class RequestPacket:
    #attributes список параметров
    def __init__(self, code, address, nasip):
        self.reqcode=code
        self.nasip=nasip
        self.connection=CoreConnection(address)
        self.data=[]


    def getreply(self,pack):
        # requestpacketid | code | nasip | lengthpacket
        self.attrlen=len(pack)
        self.lengthpacket=self.attrlen+11
        header=struct.pack("!LB4sH",1, self.reqcode, tools.EncodeAddress(self.nasip), self.lengthpacket)
        attr=struct.pack("!%ds" % self.attrlen, pack)
        if self.connection.senddata(header+attr):
            return self.connection.recvdata()

class CoreConnection:
    """
    Неудачная попытка реализовать нормальный клиент для работы с ядром.
    """
    def __init__(self, address):
        self.address=address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(5)
        self.sock.connect(self.address)

    def recvdata(self):
          (data, addrport) = self.sock.recvfrom(8192)
          self.sock.shutdown(1)
          self.sock.close()
          return data

    def senddata(self,data):
        return self.sock.send(data)

        
