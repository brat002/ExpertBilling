#!/usr/bin/python

import socket, sys
import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import time
from threading import Thread
a=time.clock()
srv=Client(server="localhost",
        secret="123",
	dict=Dictionary("dictionary"))

req=srv.CreateAuthPacket(code=pyrad.packet.AccessRequest,
                User_Name="dolphinik")

req["NAS-IP-Address"] = "10.10.1.100"
req["NAS-Port"] = 0
req["Service-Type"] = "Login-User"
req["NAS-Identifier"] = "MikroTik"
req["User-Password"]=req.PwCrypt("123456")

#req["Called-Station-Id"] = "00-04-5F-00-0F-D1"
#req["Calling-Station-Id"] = "00-01-24-80-B3-9C"
#req["Framed-IP-Address"] = "10.0.0.100"

req['NAS-Port-Type'] = 'Virtual'
req['Calling-Station-Id']='10.10.1.2'

#f=file("request", "wb")
#f.write(req.ReplyPacket())
#f.flush()

class AuthRequest(Thread):
      def __init__ (self):
            Thread.__init__(self)

      def run(self):
            #sock.connect(addr)
            for x in xrange(0,1000):
                try:
                    #print "Sending authentication request"
                    reply=srv.SendPacket(req)
                except pyrad.client.Timeout:
                    print "RADIUS server does not reply"
                    sys.exit(1)
                except socket.error, error:
                    print "Network error: " + error[1]
                    sys.exit(1)
                    
                #time.sleep(1)
                  

b=[]
zz=time.clock()
for i in xrange(0,100):
      #print
      a=AuthRequest()
      a.start()
      b.append(a)



for i in b:
    #print i
    i.join()
print time.clock()-zz      
    
#===============================================================================
#    if reply.code==pyrad.packet.AccessAccept:
#    	print "Access accepted"
#    else:
#    	print "Access denied"
#===============================================================================

print time.clock()-a
print "Attributes returned by server:"
print "Code:", reply.code
for i in reply.keys():
	print "%s: %s" % (i, reply[i])

