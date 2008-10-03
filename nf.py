#-*-coding=utf-8-*-

import socket, select, struct, datetime, time, sys, os
if os.name!='nt':
    os.chdir("/opt/ebs/data")
from IPy import IP
try:
    import mx.DateTime
except:
    print "cannot inport mx"
import settings
import psycopg2
import ConfigParser
config = ConfigParser.ConfigParser()


#from logger import redirect_std

#redirect_std("nf", redirect=config.get("stdout", "redirect"))

import threading
import gc
#from DBUtils.PooledDB import PooledDB

trafficclasses_pool = []
dcache   = {}
nascache = {}
ipncache = {}
vpncache = {}
dcacheLock = threading.Lock()
#nascache = []
#tdMinute = datetime.timedelta(seconds=60)
sleepTime = 291.0
aggrTime = 120.0
aggrNum = 1500


class Flow(object):
    # Virtual base class
    LENGTH = 0
    def __init__(self, data):
        if len(data) != self.LENGTH:
            raise ValueError, "Short flow"

    def _int_to_ipv4(self, addr):
        return ".".join(map(str, struct.unpack("BBBB", addr)))
        #return "%d.%d.%d.%d" % (addr >> 24 & 0xff, addr >> 16 & 0xff, addr >> 8 & 0xff, addr & 0xff)

class Header(object):
    # Virtual base class
    LENGTH = 0
    def __init__(self, data):
        if len(data) != self.LENGTH:
            raise ValueError, "Short flow header"

class Header5(Header):
    LENGTH = struct.calcsize("!HHIIIIBBH")
    def __init__(self, data):
        if len(data) != self.LENGTH:
            raise ValueError, "Short flow header"

        _nh = struct.unpack("!HHIIIIBBH", data)
        self.version = _nh[0]
        self.num_flows = _nh[1]
        self.sys_uptime = _nh[2]
        self.time_secs = _nh[3]
        self.time_nsecs = _nh[4]

    def __str__(self):
        ret  = "NetFlow Header v.%d containing %d flows\n" % \
             (self.version, self.num_flows)
        ret += "    Router uptime: %d\n" % self.sys_uptime
        ret += "    Current time:  %d.%09d\n" % \
            (self.time_secs, self.time_nsecs)

        return ret

class Flow5(Flow):


    LENGTH = struct.calcsize("!4s4s4sHHIIIIHHBBBBHHBBH")
    #print LENGTH
    def __init__(self, data):
        if len(data) != self.LENGTH:
            raise ValueError, "Short flow: data length: %d; LENGTH: %d" % (len(data), self.LENGTH)

        _ff = struct.unpack("!4s4s4sHHIIIIHHBBBBHHBBH", data)
        self.src_addr = self._int_to_ipv4(_ff[0])
        self.dst_addr = self._int_to_ipv4(_ff[1])
        self.next_hop = self._int_to_ipv4(_ff[2])
        self.in_index = _ff[3]
        self.out_index = _ff[4]
        self.packets = _ff[5]
        self.octets = _ff[6]
        self.start = _ff[7]
        self.finish = _ff[8]
        self.src_port = _ff[9]
        self.dst_port = _ff[10]
        # pad
        self.tcp_flags = _ff[12]
        self.protocol = _ff[13]
        self.tos = _ff[14]
        self.source_as = _ff[15]
        self.dst_as = _ff[16]
        self.src_netmask_length = _ff[17]
        self.dst_netmask_length = _ff[18]

class NetFlowPacket:
    FLOW_TYPES = {
        5 : (Header5, Flow5),
    }
    def __init__(self, data, addrport, flowCache):
        self.fc = flowCache
        if len(data) < 16:
            raise ValueError, "Short packet"

        nas_id = nascache.get(addrport[0])
        if not nas_id:
            cur.execute("""SELECT id from nas_nas WHERE  ipaddress='%s'""" % addrport[0])
            #print "after_nas", time.clock()-a
            try:
                nas_id = cur.fetchone()[0]
                nascache[addrport[0]] = nas_id
            except Exception, e:
                print e
                return
        flows=[]
        if nas_id!=None:	    
            _nf = struct.unpack("!H", data[:2])
            self.version = _nf[0]
            if not self.version in self.FLOW_TYPES.keys():
                raise RuntimeWarning, \
                      "NetFlow version %d is not yet implemented" % \
                      self.version
            hdr_class = self.FLOW_TYPES[self.version][0]
            flow_class = self.FLOW_TYPES[self.version][1]
            self.hdr = hdr_class(data[:hdr_class.LENGTH])
            # получаем классы трафика
            global ipncache
            global vpncache
            if not ipncache:
                print 'reset ipn'
                #cur.execute("SELECT array(SELECT ipn_ip_address FROM billservice_account);")
                cur.execute("SELECT ipn_ip_address FROM billservice_account;")
                ipncache = ipncache.fromkeys([x[0] for x in cur.fetchall()], 1)
            if not vpncache:
                print 'reset vpn'
                cur.execute("SELECT vpn_ip_address FROM billservice_account;")
                vpncache = vpncache.fromkeys([x[0] for x in cur.fetchall()], 1)
            
            '''cur.execute("SELECT ipn_ip_address FROM billservice_account;")
            accounts_ipn = [x[0] for x in cur.fetchall()]
            
            cur.execute("SELECT vpn_ip_address FROM billservice_account;")
            accounts_vpn =  [x[0] for x in cur.fetchall()]'''
            #print "111",accounts_ipn, accounts_vpn
            for n in range(self.hdr.num_flows):
                offset = self.hdr.LENGTH + (flow_class.LENGTH * n)
                flow_data = data[offset:offset + flow_class.LENGTH]
                flow=flow_class(flow_data)
                flow.nas_id = nas_id
                #if flow.src_addr in accounts_ipn or flow.src_addr in accounts_vpn or flow.dst_addr in accounts_ipn or flow.dst_addr in accounts_vpn:
                if vpncache.has_key(flow.src_addr) or vpncache.has_key(flow.dst_addr) or ipncache.has_key(flow.src_addr) or ipncache.has_key(flow.dst_addr):
                    self.fc.addflow5(flow)


class FlowCache:

    def __init__(self):
        dcache = {}
        nascache = {}
        self.keylist = []
        self.stime = time.time()
        #print "gc threshold", gc.get_threshold()
        #gc.set_threshold(700, 1000, 100)
        #self.cMonitor = threading.Timer(sleepTime, monitorCache)
        #self.cMonitor.start()

    def addflow(self, version, flow):
        method = getattr(self, "addflow" + str(version), None)
        return method(flow)

    def addflow5(self, flow):
        #assert isinstance(flow, Flow5)
        key = (flow.src_addr, flow.dst_addr, flow.next_hop, flow.src_port, flow.dst_port, flow.protocol)
        #key = ''.join([str(var) for var in (flow.src_addr, flow.dst_addr, flow.next_hop, flow.src_port, flow.dst_port, flow.protocol)])
        val = dcache.get(key)
        if not val:
            flow.cur = cur.connection.cursor()
            #self.stime = time.time()
            dcacheLock.acquire()
            i = 1
            j = 0
            try:
                dcache[key] = flow
                i=0
                dcacheLock.release()
                self.keylist.append(key)
                if (len(self.keylist) > aggrNum) or ((self.stime + 10.0) < time.time()):
                    tmr = threading.Timer(aggrTime, applyFlow, (self.keylist,))
                    tmr.start()
                    self.keylist = []
                    self.stime = time.time()
                    nascache = {}
                    ipncache = {}
                    vpncache = {}
                    print 'reset'
            except Exception, ex:
                if i:
                    dcacheLock.release()
                print "create rec ex: ", ex
                
        else:
            dcacheLock.acquire()
            i = 1
            try:
                dflow= dcache[key]
                dflow.octets  += flow.octets
                dflow.packets += flow.packets
                dflow.finish = flow.finish
                i = 0;
                dcacheLock.release()
            except Exception, ex:
                if i:
                    dcacheLock.release()

            
def monitorCache():    
    while True:
        #popList = []
        for k, v in dcache.items():
            #if (v.stime + tdMinute) <  datetime.datetime.now():
            '''if (v.stime + aggrTime + 11) <  time.time():
                popList.append(k)
            try:
                dcacheLock.acquire()                
                for dkey in popList:
                    try:
                        flow = dcache.pop(dkey)
                    except Exception, ex:
                        print "monitor pop ", ex 
                    else:
                        flow.cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (flow.nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
            except Exception, ex:
                print "monitor exception ", ex
            finally:
                    dcacheLock.release()'''

            if (v.stime + aggrTime + 11) <  time.time():
                try:
                    dcacheLock.acquire()
                    try:
                        flow = dcache.pop(k)
                    except Exception, ex:
                        print "monitor pop ", ex
                    else:
                        flow.cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (flow.nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
                    finally:
                        dcacheLock.release()
                    #print "monitor pop"
                except Exception, ex:
                    print "monitor exception ", ex
        nascache = {}
        print "monitor len dcache ", len(dcache)
        #print "time", time.clock()
        time.sleep(sleepTime)
        
def applyFlow(keylist):
    print "len keylist", len(keylist)
    #TO-DO: переделать на execute_many
    for key in keylist:
        dcacheLock.acquire()
        i = 1
        try:
            flow = dcache.pop(key)
            dcacheLock.release()
            i = 0
            flow.cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (flow.nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
            #print flow.cur.fetchone()
        except Exception, ex:
            if i:
                dcacheLock.release()
                #print "pop exception", ex
            #finally:
                #dcacheLock.release()
                



def main ():
    addrs = socket.getaddrinfo(settings.NF_HOST, settings.NF_PORT, socket.AF_UNSPEC,
                               socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
    socks = []
    for addr in addrs:
        sock = socket.socket(addr[0], addr[1])
        sock.bind(addr[4])
        socks.append(sock)
        print "listening on [%s]:%d" % (addr[4][0], addr[4][1])
    
    tFC = FlowCache()
    
    #TestSuite
    #===============================================================================
    #f = file('nf_data2.dat', "rb")
    #packets = f.read()
    #plist = packets.split('======')
    #addrport=('10.10.1.100', 9996)
    #plist.pop()
     
    #a=time.clock()
    #ff = 0
    i = 0
    #for i in range(1000):
        #for data in plist:

    while True:
        (rlist, wlist, xlist) = select.select(socks, [], socks)
        for sock in rlist:
            (data, addrport) = sock.recvfrom(8192)            

        if (i % 50) == 0:
            #if ff == 100:
                #ff = 0
                #print i
                #print "len dcache ", len(dcache)
                #print "time", time.clock()
                #print nascache
            print ipncache
            print vpncache
            cur.connection.commit()
        try:
            NetFlowPacket(data, addrport, tFC)
        except Exception, ex:
            print "NFP exception %d: %s" % (i, ex)
            #raise ex
            #ff += 1
            #time.sleep(0.1)
        i += 1
        #sys.exit()
    cur.connection.commit()
    #print "after_nfpacket", time.clock()-a

    return



import socket
if socket.gethostname() not in ['dolphinik','sserv.net','sasha','medusa', 'kail','billing', 'Billing.NemirovOnline']:
    import sys
    print "License key error. Exit from application."
    sys.exit(1)

if __name__=='__main__':
    if os.name!='nt':
        os.chdir("/opt/ebs/data")
        config.read("/opt/ebs/data/ebs_config.ini")
    else:
        config.read("ebs_config.ini")
    try:
        db_connection = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"),
                                                                                           config.get("db", "username"),
                                                                                           config.get("db", "host"),
                                                                                           config.get("db", "password")))
        cur = db_connection.cursor()
    except Exception, ex:
        print "Unable to connect to the database ", ex
        sys.exit()
    main()



