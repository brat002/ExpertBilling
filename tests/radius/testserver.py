#-*-coding=utf-8-*-
import socket, time, packet
import dictionary, pickle

from threading import Thread
dict=dictionary.Dictionary("dicts\dictionary","dicts\dictionary.microsoft")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
f=open('request','rb')
#u = pickle.Unpickler(f)
data = f.read()
n=0
f.close()
addr=('10.10.1.2',1812)
class AuthRequest(Thread):
      def __init__ (self):
          Thread.__init__(self)

      def run(self):
          sock.connect(addr)
          global n
          while True:
                sock.send(data)
                n+=1
                a=sock.recv(8192)
                #time.sleep(0.01)
          
          
#a=AuthRequest()
#a.start()

b=[]
for i in xrange(0,1):
    #print
    a=AuthRequest()
    b.append(a.start())

time.sleep(20)
print n
for i in b:
    i.join()
    
print n