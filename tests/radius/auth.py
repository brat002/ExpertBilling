#!/usr/bin/python

import socket, sys
import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import time
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
req["User-Password"]=req.PwCrypt("WUoKLf3n")

#req["Called-Station-Id"] = "00-04-5F-00-0F-D1"
#req["Calling-Station-Id"] = "00-01-24-80-B3-9C"
#req["Framed-IP-Address"] = "10.0.0.100"

req['NAS-Port-Type'] = 'Virtual'
req['Calling-Station-Id']='10.10.1.2'

f=file("request", "wb")
f.write(req.ReplyPacket())
f.flush()

for x in range(0,1000000):
    try:
    	#print "Sending authentication request"
    	reply=srv.SendPacket(req)
    except pyrad.client.Timeout:
    	print "RADIUS server does not reply"
    	sys.exit(1)
    except socket.error, error:
    	print "Network error: " + error[1]
    	sys.exit(1)
    
#===============================================================================
#    if reply.code==pyrad.packet.AccessAccept:
#    	print "Access accepted"
#    else:
#    	print "Access denied"
#===============================================================================

print time.clock()-a
print "Attributes returned by server:"
for i in reply.keys():
	print "%s: %s" % (i, reply[i])

