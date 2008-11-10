import sys, os
from socket import *
import asyncore

class reception_server(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.host = host
        self.port = port
        self.create_socket(AF_INET, SOCK_DGRAM)
        self.bind( (host, port) )
        self.set_reuse_addr()
        self.buffer=''

    def handle_connect(self):
        print "New Auth Request"
    
    def handle_read(self):
        data_str, address = self.recvfrom(8192)
        self.buffer = data_str
        
    def writable(self):
        return len(self.buffer)

    def handle_write(self):
        sent = self.sendto(self.buffer, (self.host, self.port))
        
        #self.send('123')
        #self.buffer=''
        self.buffer = self.buffer[sent:]

reception_server('10.10.1.2', 1812)

while 1: 
    asyncore.poll(0.010)


