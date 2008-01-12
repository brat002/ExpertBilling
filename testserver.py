#-*-coding=utf-8-*-
import socket, time, packet
import dictionary, pickle

from threading import Thread
dict=dictionary.Dictionary("dicts\dictionary","dicts\dictionary.microsoft")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
f=open('request','r')
u = pickle.Unpickler(f)
data = u.load()

f.close()
addr=('10.20.3.111',1812)
class AuthRequest(Thread):
      def __init__ (self):
          Thread.__init__(self)

      def run(self):
          sock.connect(addr)
          while True:
                sock.send(data)
                a=sock.recv(8192)
                time.sleep(0.01)
          
          
a=AuthRequest()
a.start()