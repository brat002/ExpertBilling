import socket, time
import ConfigParser
import threading
import random
config = ConfigParser.ConfigParser()
config.read("../../ebs_config.ini")

f = file('nf_data2.dat', "rb")
packets = f.read()
plist = packets.split('======')
hst = '0.0.0.0'
prt = 9996
addrs = socket.getaddrinfo(config.get("nf", "host"), 1234, socket.AF_UNSPEC,
                               socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print addrs
print s.gettimeout()
#s = socket.socket(addrs[0][0], addrs[0][1])
#s.connect(('127.0.0.1', 9996))
print addrs[0][4]

#addrport=('10.10.1.100', 9996)

plist.pop()
print len(plist)
a=time.clock()
ff = 0
i = 0
for i in range(1000):
    a=time.clock()
    for data in plist:
        #s.send(data)
        s.sendto(data,('127.0.0.1', 9996))
        """try:
            dtrc, addr = s.recvfrom(128)
            #print dtrc
        except Exception, ex:
            pass"""
        time.sleep(0.0005)
    print time.clock() - a


"""class UDPThread(threading.Thread):
    def __init__(self, sendwrd):
        threading.Thread.__init__(self)
        self.sendwrd = sendwrd
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addrport = ('127.0.0.1', 9996)
        print self.sendwrd
    
    def run(self):
        while True:
            #print self.sendwrd
            self.sock.sendto(self.sendwrd,self.addrport)
            
            try:
                dtrc, addr = self.sock.recvfrom(128)
                print "Thread '" +self.sendwrd+ "' recover: " + dtrc
            except Exception, ex:
                print "Thread '" +self.sendwrd+ "' norecv"
             
            z = 1.0
            time.sleep(random.random())
            for i in range(random.randint(100, 10000)):
                z /= i + 1
            print z
            #time.sleep(0.5)"""
"""if __name__ == "__main__":
    print config.get("core_nf", "dump_dir")
    ttr1 = UDPThread("333")
    ttr2 = UDPThread("4444")
    ttr3 = UDPThread("55555")"""
    
    #ttr1.start()
    #ttr2.start()
    #ttr3.start()