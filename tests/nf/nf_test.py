import socket, time
import ConfigParser
config = ConfigParser.ConfigParser()
config.read("../../ebs_config.ini")
f = file('nf_data2.dat', "rb")
packets = f.read()
plist = packets.split('======')
hst = '0.0.0.0'
prt = 9996
addrs = socket.getaddrinfo(config.get("nf", "host"), config.get("nf", "port"), socket.AF_UNSPEC,
                               socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print addrs
s = socket.socket(addrs[0][0], addrs[0][1])
s.connect(addrs[0][4])

addrport=('10.10.1.100', 9996)

plist.pop()
print len(plist)
a=time.clock()
ff = 0
i = 0
for i in range(1000):
    a=time.clock()
    for data in plist:
        s.send(data)
        time.sleep(0.0005)
    print time.clock() - a