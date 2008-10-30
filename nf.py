#-*-coding=utf-8-*-
import os, sys
from daemonize import daemonize
import socket, select, struct, datetime, time, sys, os

from IPy import IP
try:
    import mx.DateTime
except:
    print "cannot inport mx"
    

import psycopg2
from DBUtils.PooledDB import PooledDB
import ConfigParser
config = ConfigParser.ConfigParser()

from SocketServer import ThreadingUDPServer
from SocketServer import DatagramRequestHandler
from threading import Thread
import gc

#from logger import redirect_std

#redirect_std("nf", redirect=config.get("stdout", "redirect"))

import threading
import gc
from DBUtils.PooledDB import PooledDB

trafficclasses_pool = []
dcache   = {}
global ipncache, vpncache
nascache = {}
ipncache = {}
vpncache = {}
dcacheLock = threading.Lock()
fqueueLock = threading.Lock()
dbLock = threading.Lock()
#nascache = []
#tdMinute = datetime.timedelta(seconds=60)
nfFlowCache = None
packetCount = None


class Starter(Thread):
        def __init__ (self, address, handler):
            self.address=address
            self.handler=handler
            Thread.__init__(self)

        def run(self):
            server = ThreadingUDPServer(self.address, self.handler)
            #server.allow_reuse_address = True
            #server.conn = pool.connection()
            #server.conn._con._con.set_isolation_level(0)
            server.serve_forever()

            
class BaseHandle(DatagramRequestHandler):
    def handle(self):
        pass
    
class NetFlowCollectHandle(BaseHandle):
    def handle(self):
        #global packetCount
        global nfFlowCache
        #print self.server.conn
        data=self.request[0] # or recv(bufsize, flags)
        assert len(data)<=8192
        addrport=self.client_address
        #print repr(addrport[0])
        #print "gotpacket: ", addrport
        #if (packetCount % 50) == 0:
            #cur.connection.commit()
        try:
            #========
            #NetFlowPacket(data, addrport, nfFlowCache, self.server.conn.cursor())
            NetFlowPacket(data, addrport, nfFlowCache, None)
        except Exception, ex:
            print "NFP exception: %s" % (repr(ex),)
        #packetCount += 1
        #del data
        #del addrport
        
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
    def __init__(self, data, addrport, flowCache, sCur):
        
        #self.connection = pool.connection()
        #self.connection._con._con.set_isolation_level(0)
        #self.cur = self.connection.cursor()
        #self.cur = sCur
        #self.fc = flowCache
        if len(data) < 16:
            raise ValueError, "Short packet"
        
        #print nascache
        nas_id = nascache.get(addrport[0])
        if not nas_id:
            #======
            print "Nas_id not found: ", addrport[0]
            return
            #======
            
        #self.cur.execute("""SELECT id from nas_nas WHERE  ipaddress='%s'""" % addrport[0])
        '''
        try:
            nas_id = self.cur.fetchone()[0]
            nascache[addrport[0]] = nas_id
        except Exception, e:
            print "Error na_id: %s, %s" % (addrport[0], repr(e))
            self.cur.close()
            #self.connection.close()
            return
        '''
            
        flows=[]
        if nas_id!=None:	    
            _nf = struct.unpack("!H", data[:2])
            self.version = _nf[0]
            if not self.version in self.FLOW_TYPES.keys():
                #====
                #self.cur.close()
                #self.connection.close()
                raise RuntimeWarning, \
                      "NetFlow version %d is not yet implemented" % \
                      self.version
            hdr_class = self.FLOW_TYPES[self.version][0]
            flow_class = self.FLOW_TYPES[self.version][1]
            self.hdr = hdr_class(data[:hdr_class.LENGTH])
            #======
            """
            # получаем классы трафика
            global ipncache, vpncache

            if not ipncache:
                self.cur.execute("SELECT ipn_ip_address FROM billservice_account;")
                ipncache = ipncache.fromkeys([x[0] for x in self.cur.fetchall()], 1)
            if not vpncache:
                #print 'reset vpn'
                self.cur.execute("SELECT vpn_ip_address FROM billservice_account;")
                vpncache = vpncache.fromkeys([x[0] for x in self.cur.fetchall()], 1)
            self.cur.close()
            #self.connection.close()
            """
            for n in range(self.hdr.num_flows):
                offset = self.hdr.LENGTH + (flow_class.LENGTH * n)
                flow_data = data[offset:offset + flow_class.LENGTH]
                flow=flow_class(flow_data)
                flow.nas_id = nas_id
                #if flow.src_addr in accounts_ipn or flow.src_addr in accounts_vpn or flow.dst_addr in accounts_ipn or flow.dst_addr in accounts_vpn:
                if vpncache.has_key(flow.src_addr) or vpncache.has_key(flow.dst_addr) or ipncache.has_key(flow.src_addr) or ipncache.has_key(flow.dst_addr):
                    #self.fc.addflow5(flow)
                    flowCache.addflow5(flow)


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
        global ipncache, vpncache, nascache
        #assert isinstance(flow, Flow5)
        #print "addflow"
        key = (flow.src_addr, flow.dst_addr, flow.next_hop, flow.src_port, flow.dst_port, flow.protocol)
        #key = ''.join([str(var) for var in (flow.src_addr, flow.dst_addr, flow.next_hop, flow.src_port, flow.dst_port, flow.protocol)])
        val = dcache.get(key)
        if not val:
            #+++++++
            #flow.cur = cur.connection.cursor()
            #+++++++
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
                    #++++
                    #tmr = threading.Timer(aggrTime, applyFlow, (self.keylist,))
                    #tmr.start()
                    #++++
                    #-----------------
                    fqueueLock.acquire()
                    flowQueue.append((self.keylist, time.time()))
                    fqueueLock.release()
                    #-----------------
                    
                    self.keylist = []
                    self.stime = time.time()
                    #=====
                    '''
                    nascache = {}
                    ipncache = {}
                    vpncache = {}
                    '''
                    #=====
                    gc.collect()
                    #print 'reset'
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
            #print "executed"
            #print flow.cur.fetchone()
            del flow
            flow.cur.connection.commit()
        except Exception, ex:
            print "applyFlow exception: ", repr(ex)
            del flow
            if i:
                dcacheLock.release()

                
class FlowDequeThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        #self.connection = pool.connection()
        #self.connection._con._con.set_isolation_level(0)
        #self.connection._con._con.set_client_encoding('UTF8')
        #self.cur = self.connection.cursor()
        
    def run(self):
        j = 0
        while True:
            fqueueLock.acquire()
            try:
                keylist, stime = flowQueue.pop(0)
                fqueueLock.release()
            except Exception, ex:
                fqueueLock.release()
                print "empty queue"
                time.sleep(5)
                continue
            
            print "len keylist ", len(keylist)
            print "len queue ", len(flowQueue)
            print "len dbQueue: ", len(databaseQueue)
            wtime = time.time() - aggrTime - stime
            print wtime
            if wtime < 0:
                time.sleep(abs(wtime))
            
            #TO-DO: переделать на execute_many
            fcnt = 0
            flst = []
            for key in keylist:
                dcacheLock.acquire()
                i = 1
                try:
                    flow = dcache.pop(key)
                    dcacheLock.release()
                    i = 0
                    #fcur = cur.connection.cursor()
                    #self.cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (flow.nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
                    #flow.cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (flow.nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
                    #del flow
                    #fcur.close()
                    #flow.cur.connection.commit()
                    flst.append(flow)
                    fcnt += 1
                    if fcnt == 37:
                        dbLock.acquire()
                        databaseQueue.append(flst)
                        dbLock.release()
                        flst = []
                        fcnt = 0
                except Exception, ex:
                    print "fdqThread exception: ", repr(ex)
                    #del flow
                    if i:
                        dcacheLock.release()
            if len(flst) > 0:
                dbLock.acquire()
                databaseQueue.append(flst)
                dbLock.release()
                flst = []
            '''try:
                #cur.connection.commit()
                self.cur.connection.commit()
            except Exception, ex:
                print "fdqThread commit error: ", repr(ex)'''
            del keylist
            gc.collect()
            
 
class DatabaseThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.connection = pool.connection()
        self.connection._con._con.set_isolation_level(0)
        self.connection._con._con.set_client_encoding('UTF8')
        self.cur = self.connection.cursor()
    def run(self):
        while True:
            dbLock.acquire()
            try:
                flst = databaseQueue.pop(0)
                dbLock.release()
            except Exception, ex:
                dbLock.release()
                #print "empty dbqueue"
                time.sleep(2)
                continue
            
            #print "dbqueue len: ", len(databaseQueue)
            try:
                for flow in flst:
                    self.cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (flow.nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
                    #print self.cur.fetchone()
                    print "flow src: %s ---- dst %s" % (flow.src_addr, flow.dst_addr)
                    del flow
                '''for ifl in range(len(flst)):
                    flow = flst.pop()
                    self.cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (flow.nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
                    del flow''' 
                
                self.cur.connection.commit()
            except Exception, ex:
                print "dbThread error: ", repr(ex)
                if isinstance(ex, psycopg2.OperationalError) or isinstance(ex, psycopg2.InterfaceError):
                    #dbLock.acquire()
                    #databaseQueue.insert(0, flst)
                    #dbLock.release()
                    print "dbQueue len: ", len(databaseQueue)
                    time.sleep(10)
            del flst
                
class ServiceThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.connection = pool.connection()
        self.connection._con._con.set_isolation_level(0)
        self.connection._con._con.set_client_encoding('UTF8')
        self.cur = self.connection.cursor()
    def run(self):
        #TODO: перенести обновления кешей нас, ипн, впн, а также проверку на переполнение словаря
        global nascache
        global ipncache
        global vpncache
        global databaseQueue
        while True:
            try:
                self.cur.execute("""SELECT ipaddress, id from nas_nas;""")
                nasvals = self.cur.fetchall()
                nascache = dict(nasvals)
                #print nascache
                del nasvals
            except Exception, ex:
                print "Servicethread nascache exception: ", repr(ex)
                
            try:
                self.cur.execute("SELECT ipn_ip_address FROM billservice_account;")
                icTmp = {}
                ipncache = icTmp.fromkeys([x[0] for x in self.cur.fetchall()], 1)
            except Exception, ex:
                print "Servicethread ipncache exception: ", repr(ex)
                
            try:
                self.cur.execute("SELECT vpn_ip_address FROM billservice_account;")
                vcTmp = {}
                vpncache = vcTmp.fromkeys([x[0] for x in self.cur.fetchall()], 1)
            except Exception, ex:
                print "Servicethread vpncache exception: ", repr(ex)
             
            try: 
                if len(databaseQueue) > 1000000:
                    databaseQueue = databaseQueue[10000:]
            except Exception, ex:
                print "Servicethread dbQueue exception: ", repr(ex)    
                
            gc.collect()
            time.sleep(60)
            
        
def main ():
    if "-D" not in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
        
        
    global packetCount
    global nfFlowCache
    packetCount = 0
    nfFlowCache = FlowCache()
    
    #-----
    svcThread = ServiceThread()
    svcThread.start()
    dbThread = DatabaseThread()
    dbThread.start()
    #~~~~~~
    #dbThread2 = DatabaseThread()
    #dbThread2.start()
    #dbThread3 = DatabaseThread()
    #dbThread3.start()
    #dbThread4 = DatabaseThread()
    #dbThread4.start()
    #~~~~~~
    fdqThread = FlowDequeThread()
    fdqThread.start()
    #-----
    
    server_nf = Starter((config.get("nf", "host"), int(config.get("nf", "port"))), NetFlowCollectHandle)
    server_nf.start()
    
    cur.connection.commit()
    """'''addrs = socket.getaddrinfo(config.get("nf", "host"), config.get("nf", "port"), socket.AF_UNSPEC,
                               socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
    socks = []
    for addr in addrs:
        sock = socket.socket(addr[0], addr[1])
        sock.bind(addr[4])
        socks.append(sock)
        print "listening on [%s]:%d" % (addr[4][0], addr[4][1])'''
    
    #tFC = FlowCache()
    
    #TestSuite
    #===============================================================================
    #f = file('nf_data2.dat', "rb")
    #packets = f.read()
    #plist = packets.split('======')
    #addrport=('10.10.1.100', 9996)
    #plist.pop()
     
    #a=time.clock()
    #ff = 0
    #i = 0
    #for i in range(1000):
        #for data in plist:

    '''while True:
        (rlist, wlist, xlist) = select.select(socks, [], socks)
        for sock in rlist:
            (data, addrport) = sock.recvfrom(8192)            

        if (i % 50) == 0:
            #if ff == 100:
                #ff = 0
                #print "len dcache ", len(dcache)
                #print "time", time.clock()
            db_connection.commit()
        #try:
        NetFlowPacket(data, addrport, tFC)
        #except Exception, ex:
        #    print "NFP exception %d: %s" % (i, ex)
        i += 1
    cur.connection.commit()'''"""

    return



import socket
if socket.gethostname() not in ['dolphinik','kenny','sserv.net','sasha','medusa', 'kail','billing', 'Billing.NemirovOnline', 'iserver']:
    import sys
    print "License key error. Exit from application."
    sys.exit(1)

if __name__=='__main__':
    config.read("ebs_config.ini")
    '''try:
        pool = PooledDB(
            mincached=1,
            maxcached=2,
            blocking=True,
            #maxusage=20, 
            creator=psycopg2,
            dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"),
                                                                   config.get("db", "username"),
                                                                   config.get("db", "host"),
                                                                   config.get("db", "password"))
           )        
        db_connection = pool.connection()
        db_connection._con._con.set_client_encoding('UTF8')
        cur = db_connection.cursor()
    except Exception, ex:
        print "Unable to connect to the database ", ex
        sys.exit()'''
    pool = PooledDB(
        mincached=3,
        maxcached=9,
        blocking=True,
        creator=psycopg2,
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"),
                                                               config.get("db", "username"),
                                                               config.get("db", "host"),
                                                               config.get("db", "password"))
    )
    db_connection = pool.connection() 
    cur = db_connection.cursor()
    flowQueue = []
    databaseQueue = []
    sleepTime = 291.0
    aggrTime = 120.0
    aggrNum = 666
    try:
        sleepTime = float(config.get("nf", "sleeptime"))
        aggrTime  = float(config.get("nf", "aggrtime"))
        aggrNum   = float(config.get("nf", "aggrnum"))
    except:
        pass
    main()



