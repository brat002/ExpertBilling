import socket, select,struct, md5
from socket import AF_INET, SOCK_DGRAM
import dictionary
import packet
import auth
import time
import settings
from coreconnection import *
import corepacket
import utilites

#значения поля code
RequireLogin=1
LoginAllowed=2
LoginDisabled=3

addrs = socket.getaddrinfo('10.20.3.111', 1812, socket.AF_UNSPEC, socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)

socks = []

for addr in addrs:
	sock = socket.socket(addr[0], addr[1])
	sock.bind(addr[4])
	socks.append(sock)
##Accounting
addrs = socket.getaddrinfo('10.20.3.111', 1813, socket.AF_UNSPEC, socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
for addr in addrs:
	sock = socket.socket(addr[0], addr[1])
	sock.bind(addr[4])
	socks.append(sock)


print "listening on [%s]:%d" % (addr[4][0], addr[4][1])

dict=dictionary.Dictionary("dicts\dictionary","dicts\dictionary.microsoft")

data=''
while 1:
	(rlist, wlist, xlist) = select.select(socks, [], socks)
	for sock in rlist:
	    (data, addrport) = sock.recvfrom(4096)
        t = time.time()
        (code, packetid, length, authenticator)=struct.unpack("!BBH16s", data[0:20])
        if code==1:
            reqpack=RequestPacket(1,('10.20.3.111',2224))
            #Отправляем ядру копию пакета, полученного от NAS
            #Ядро должно вернуть закодированный объект corepacket.CorePacket c установленными атрибутами
            corereply=reqpack.getreply(data)
            packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
            #print " After parsing packet from core %.40f" % (time.time()-t)
            #Получили объект ответа. Сейчас мы можем изменять или считывать его атрибуты
            #packetfromcore=packetobject['User-Name']
            #А вот таким образом можем взять уже готовую для отправки строку аргументов attrs=packetfromcore._PktEncodeAttributes()
            #
            packetobject=packet.Packet(secret=packetfromcore.secret, authenticator=authenticator, dict=dict,packet=data)
            authobject=auth.Auth(packetobject, packetfromcore.password, packetfromcore.username, code=packetfromcore.code, attrs=packetfromcore._PktEncodeAttributes())
            returndata=authobject.ReturnPacket()
            sock.sendto(returndata,addrport)
        elif code==4:
            reqpack=RequestPacket(1,('10.20.3.111',2225))
            corereply=reqpack.getreply(data)
            requestpacket=packet.AcctPacket(dict=dict,packet=data)
            packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
            replyobj=packet.AcctPacket( id=requestpacket.id, code=packetfromcore.code, secret=packetfromcore.secret, authenticator=authenticator, dict=dict)
            returndat=replyobj.ReplyPacket()
            sock.sendto(returndat,addrport)
            print "%.40f" % (time.time()-t)