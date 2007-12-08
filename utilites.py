import packet
import socket

def disconnect(code, secret, dict, nasIP, nasID, username, sessionID):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('10.20.3.111',24000))
    #sock.connect('10.20.3.1',1700)
    doc=packet.AcctPacket(code=code,secret=secret, dict=dict)
    doc.AddAttribute('NAS-IP-Address', nasIP)
    doc.AddAttribute('NAS-Identifier', nasID)
    doc.AddAttribute('User-Name',username)
    doc.AddAttribute('Acct-Session-Id', sessionID)
    doc_data=doc.RequestPacket()
    sock.sendto(doc_data,('10.20.3.1',1700))
    (data, addrport) = sock.recvfrom(8192)
    doc=packet.AcctPacket(secret=secret, dict=dict, packet=data)

    for key,value in doc.items():
        print doc._DecodeKey(key),doc[doc._DecodeKey(key)]
    sock.close()