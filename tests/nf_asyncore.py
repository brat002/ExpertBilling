import sys, os, time
from socket import *
import asyncore

class reception_server(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(AF_INET, SOCK_DGRAM)
        self.bind( (host, port) )
        self.set_reuse_addr(True)
        #self.buffer=''

    def handle_connect(self):
        print 'New AUTH request'
        pass
    
    def handle_read(self):
        data_str, address = self.recvfrom(4096)
        #self.buffer=data_str
        print data_str
        
    #def writable(self):
    #    return len(self.buffer)

    #def handle_write(self):
    #    sent = self.send(self.buffer)
    #    self.buffer = self.buffer[sent:]


reception_server('10.10.1.2', 1812)

while 1: 
    #asyncore.poll()
    asyncore.poll2(0.01)
    #time.sleep(1)


