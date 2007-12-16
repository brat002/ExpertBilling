# -*- Mode: Python; tab-width: 4 -*-


import styacklessasyncore
import socket
import string

class proxy_server (styacklessasyncore.dispatcher):

    def __init__ (self, host, port):
        asyncore.dispatcher.__init__ (self)
        self.create_socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.there = (host, port)
        #here = ('', port + 8000)
        self.bind (self.there)
        #self.listen (5)

    def handle_accept (self):
        proxy_receiver (self, self.accept())


