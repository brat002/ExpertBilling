#-*-coding=utf-8-*-
import os, sys
from daemonize import daemonize
import socket, select, struct, datetime, time
import asyncore
from IPy import IP, IPint, parseAddress
try:
    import mx.DateTime
except:
    print "cannot inport mx"
    

from collections import deque
import psycopg2
from DBUtils.PooledDB import PooledDB
import ConfigParser
config = ConfigParser.ConfigParser()
import threading
from threading import Thread
import marshal
import gc

#from logger import redirect_std

#redirect_std("nf", redirect=config.get("stdout", "redirect"))



#aggregation cache
dcache   = {}
#caches for Nas data, account IPN, VPN address indexes
global ipncache, vpncache
nascache = {}
ipncache = {}
vpncache = {}
#locks
dcacheLock = threading.Lock()
fqueueLock = threading.Lock()
dbLock = threading.Lock()

nfFlowCache = None
packetCount = None

#binary strings lengthes
flowLENGTH = struct.calcsize("!LLLHHIIIIHHBBBBHHBBH")
headerLENGTH = struct.calcsize("!HHIIIIBBH")

class reception_server(asyncore.dispatcher):
    '''
    Asynchronous server that recieves datagrams with NetFlow packets
    and appends them to 'nfQueue' queue.
    '''
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind( (host, port) )
        
    def handle_connect(self):
        #print 'New packet'
        pass
    
    
    def handle_read(self):        
        data, addrport = self.recvfrom(8192)        
        try:
            assert len(data)<=8192
            #NetFlowPacket(data, addrport, nfFlowCache, None)
            #nfPacketHandle(data, addrport, nfFlowCache)
            nfQueue.append((data, addrport))
        except Exception, ex:
            print "NF server exception: %s" % (repr(ex),)
        
    def writable(self):
        return (0)


def flow5(data):
    """
    Function that unpacks Flow binary string into a list.
    data legend:
        _ff= struct.unpack("!LLLHHIIIIHHBBBBHHBBH", data)
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
        [11] - nas_id
        self.tcp_flags = _ff[12]
        self.protocol = _ff[13]
        self.tos = _ff[14]
        self.source_as = _ff[15]
        self.dst_as = _ff[16]
        self.src_netmask_length = _ff[17]
        self.dst_netmask_length = _ff[18]
        [19]- 
        #added_later
        [20] - account_id
        [21] - CURRENT_TIMESTAMP
        [22] - nas_traficclass_id
        [23] - nas_trafficnode.direction
        [24] - nas_trafficclass.store
        [25] - nas.trafficclass.passthrough
    """
    if len(data) != flowLENGTH:
        raise ValueError, "Short flow: data length: %d; LENGTH: %d" % (len(data), flowLENGTH)
    #must turn tuples into lists because they are to be modified
    return list(struct.unpack("!LLLHHIIIIHHBBBBHHBBH", data))


def header5(data):
    """
    Function that unpacks Netflow packet header binary string into a tuple.
    data legend:
        _nh = struct.unpack("!HHIIIIBBH", data)
        self.version = _nh[0]
        self.num_flows = _nh[1]
        self.sys_uptime = _nh[2]
        self.time_secs = _nh[3]
        self.time_nsecs = _nh[4]
    """
    if len(data) != headerLENGTH:
        raise ValueError, "Short flow header"
    return struct.unpack("!HHIIIIBBH", data)

def nfPacketHandle(data, addrport, flowCache):
    '''
    Function receiving a binary Netflow packet, sender addrport and FlowCache reference.
    Gets, unpacks and checks flows from packets.
    Approved packets are added to FlowCache.
    '''
    if len(data) < 16:
        raise ValueError, "Short packet"

    nas_id = nascache.get(addrport[0])
    if not nas_id:
        return
          
    flows=[]
    if nas_id!=None:	    
        _nf = struct.unpack("!H", data[:2])
        pVersion = _nf[0]
        if not pVersion in nfFLOW_TYPES.keys():
            raise RuntimeWarning, \
                  "NetFlow version %d is not yet implemented" % \
                  pVersion
        hdr_class = nfFLOW_TYPES[pVersion][0]
        flow_class = nfFLOW_TYPES[pVersion][1]
        hdr = hdr_class(data[:headerLENGTH])
        #======
        #runs through flows
        for n in range(hdr[1]):
            offset = headerLENGTH + (flowLENGTH * n)
            flow_data = data[offset:offset + flowLENGTH]
            flow=flow_class(flow_data)
            #checks for account
            acc_id = (vpncache.has_key(flow[0]) and vpncache[flow[0]]) or (vpncache.has_key(flow[1]) and vpncache[flow[1]]) or (ipncache.has_key(flow[0]) and ipncache[flow[0]]) or (ipncache.has_key(flow[1]) and ipncache[flow[1]])
            if acc_id:
                flow[11] = nas_id
                flow.append(acc_id)
                passthr = True
                #checks classes
                #classLst = {'INPUT':[], 'OUTPUT':[]}
                direction=None
                fnode=None
                classLst = []
                #Направление берёт из первого пройденного нода
                for nclass, nnodes in nodesCache:                    
                    for nnode in nnodes:
                        if (((flow[0] & nnode[1]) == nnode[0]) and ((flow[2] & nnode[3]) == nnode[2]) and ((flow[3] == nnode[4]) or (not nnode[4])) and ((flow[9] == nnode[5]) or (not nnode[5])) and ((flow[10] == nnode[6]) or (not nnode[6])) and ((flow[13] == nnode[7]) or (not nnode[7]))):
                            '''wrflow = flow[:]
                            wrflow.append(time.time())
                            wrflow.append(nclass)
                            wrflow.append(nnode[9])
                            wrflow.append(nnode[10])
                            wrflow.append(nnode[8])
                            if not wrflow[-1]:
                                passthr = False
                            flowCache.addflow5(wrflow)'''
                            if not classLst:
                                direction = nnode[9]
                                fnode = nnode
                            classLst.append(nclass)
                            if not nnode[8]:
                                passthr = False
                            break
                    
                    if not passthr:

                        wrflow = flow[:]
                        wrflow.append(time.time())
                        wrflow.append(tuple(classLst))
                        wrflow.append(nnode[9])
                        wrflow.append(nnode[10])
                        wrflow.append(nnode[8])
                        flowCache.addflow5(wrflow)
                        break
               
                else:
                    if classLst:
                        wrflow = flow[:]
                        wrflow.append(time.time())
                        wrflow.append(tuple(classLst))
                        wrflow.append(nnode[9])
                        wrflow.append(nnode[10])
                        wrflow.append(nnode[8])
                        flowCache.addflow5(wrflow)


class FlowCache:
    '''
    Aggregates flows.
    '''
    def __init__(self):
        dcache = {}
        #nascache = {}
        #list for keeping keys
        self.keylist = []
        self.stime = time.time()

    def addflow(self, version, flow):
        method = getattr(self, "addflow" + str(version), None)
        return method(flow)

    def addflow5(self, flow):
        global ipncache, vpncache, nascache
        #key = (flow.src_addr, flow.dst_addr, flow.next_hop, flow.src_port, flow.dst_port, flow.protocol)
        #constructs a key
        key = (flow[0], flow[1], flow[2], flow[9], flow[10], flow[13])
        val = dcache.get(key)
        #no such value, must add
        if not val:
            dcacheLock.acquire()
            i = 1
            j = 0
            try:
                #adds
                dcache[key] = flow
                i=0
                dcacheLock.release()
                #stores key in a list
                self.keylist.append(key)
                #time to start over?
                if (len(self.keylist) > aggrNum) or ((self.stime + 10.0) < time.time()):
                    #-----------------
                    #appends keylist to flowQueue
                    fqueueLock.acquire()
                    flowQueue.append((self.keylist, time.time()))
                    fqueueLock.release()
                    #-----------------
                    #nullifies keylist
                    self.keylist = []
                    self.stime = time.time()
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
                #appends flows
                dflow= dcache[key]
                '''dflow.octets  += flow.octets
                dflow.packets += flow.packets
                dflow.finish = flow.finish'''
                dflow[6] += flow[6]
                dflow[5] += flow[5]
                dflow[8] = flow[8]
                i = 0;
                dcacheLock.release()
            except Exception, ex:
                if i:
                    dcacheLock.release()


class nfDequeThread(Thread):
    '''
    Thread that gets packets recieved by the server from nfQueue queue and puts them onto the conveyour
    that gets flows and caches them.
    '''
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        global nfFlowCache
        while True:
            #TODO: add locks if deadlocking issues arise
            try:
                data, addrport = nfQueue.popleft()
            except Exception, ex:
                #print "empty nfdq queue"
                time.sleep(3)
                continue
            try:
                nfPacketHandle(data, addrport, nfFlowCache)
            except Exception, ex:
                print "NFP exception: %s" % (repr(ex),)
                
class FlowDequeThread(Thread):
    '''
    Gets a keylist with keys to flows that are to be aggregated, waits for aggregation time, pops them from aggregation cache,
    constructs small lists of flows and appends them to 'databaseQueue'.
    '''
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        j = 0
        while True:
            fqueueLock.acquire()
            try:
                #get keylist and time
                keylist, stime = flowQueue.popleft()
                fqueueLock.release()
            except Exception, ex:
                fqueueLock.release()
                #print "empty flow queue"
                #print "len nfqueue: ", len(nfQueue)
                time.sleep(5)
                continue
            
            print "len keylist ", len(keylist)
            print "len queue ", len(flowQueue)
            print "len dbQueue: ", len(databaseQueue)
            print "len fnameQueue: ", len(fnameQueue)
            print "len nfqueue: ", len(nfQueue)
            
            #if aggregation time was still not reached -> sleep
            wtime = time.time() - aggrTime - stime
            if wtime < 0:
                time.sleep(abs(wtime))
            
            #TO-DO: переделать на execute_many
            fcnt = 0
            flst = []
            #ftime = time.time()
            for key in keylist:
                dcacheLock.acquire()
                i = 1
                try:
                    flow = dcache.pop(key)
                    dcacheLock.release()
                    i = 0
                    #construct a list
                    flst.append(tuple(flow))
                    fcnt += 1
                    
                    ##TODO: add time check!!!
                    #append to databaseQueue
                    if fcnt == 37:
                        dbLock.acquire()
                        databaseQueue.append(flst)
                        dbLock.release()
                        flst = []
                        fcnt = 0
                        #ftime = time.time()
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
            del keylist
            gc.collect()
            
 

                
class NfUDPSenderThread(Thread):
    '''
    Thread that gets packet lists from databaseQueue, marshals them and sends to Core module
    If there are errors, flow data are written to a file. When connection is established again, NfFileReadThread to clean up that files and resend data is started.
    '''
    def __init__(self):        
        #self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.outbuf = []
        #self.addrport = coreAddr
        #self.errflag = 0
        self.hpath = ''.join((dumpDir,'/','nf_'))
        Thread.__init__(self)
        
    def run(self):
        addrport = coreAddr
        nfsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        nfsock.settimeout(0.01)
        errflag = 0
        flnumpack = 0
        dfile = None
        fname = None
        while True:
            dbLock.acquire()
            try:
                flst = marshal.dumps(databaseQueue.popleft())
                dbLock.release()
            except Exception, ex:
                dbLock.release()
                #print "empty dbqueue"
                time.sleep(1)
                continue
            
            try:
                #send data
                nfsock.sendto(flst,addrport)
                #print addrport
                #recover reply
                dtrc, addr = nfsock.recvfrom(128)
                print dtrc, addr
                #if wrong length (probably zero reply) - raise exception
                if (dtrc == None) or (len(flst) != int(dtrc)):
                    raise Exception("Unequal sizes!")
                
                #if the connection is OK but there were errors earlier
                if errflag:
                    print "errflag detected"
                    dfile.close()
                    #use locks is deadlocking  arise
                    fnameQueue.append(fname)
                    
                    errflag = 0
                    #run a cleanup thread
                    nfFileThread = NfFileReadThread()
                    nfFileThread.start()                  
                
            except Exception, ex:
                #if no errors were detected earlier
                if not errflag:
                    try:
                        errflag = 1
                        print "open a new file"
                        #open a new file
                        fname = ''.join((self.hpath, str(time.clock()), '.dmp'))
                        dfile = open(fname, 'ab')
                    except Exception, ex:
                        print "NFUDPSenderThread file creation exception: ", repr(ex)
                        continue
                    
                try:   
                    #append data
                    dfile.write(flst)
                    dfile.write('\n')
                    #dfile.close()
                    flnumpack += 1
                    #if got enough packets - open a new file
                    if flnumpack == 300:
                        flnumpack = 0
                        dfile.close()
                        #use locks is deadlockind arise
                        fnameQueue.append(fname)
                        fname = ''.join((self.hpath, str(time.clock()), '.dmp'))
                        dfile = open(fname, 'ab')
                except Exception, ex:
                        print "NFUDPSenderThread file write exception: ", repr(ex)
                        continue
            del flst
            
class NfFileReadThread(Thread):
    '''
    Thread that reads previously written data dumps and resends data.
    '''
    def __init__(self):
        Thread.__init__(self)
        self.hpath = ''.join((dumpDir,'/','nf_'))
    
    def run(self):
        fname = None
        addrport = coreAddr
        nfsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        dfile = None
        while True:
            #get a file name
            fnameLock.acquire()
            try:
                fname = fnameQueue.popleft()
                fnameLock.release()
            except Exception, ex:
                fnameLock.release()
                return
            #open file and read data
            try:
                dfile = open(fname, 'rb')
                flows = dfile.readlines()
                dfile.close()
                fcnt = 0
                #send data
                try:
                    for flow in flows:
                        nfsock.sendto(flow[:-1],addrport)                    
                        dtrc, addr = nfsock.recvfrom(128)
                        if len(flow) - 1 != int(dtrc):
                            raise Exception("Unequal sizes!")
                        fcnt += 1
                        time.sleep(0.01)
                except Exception, ex:
                    #if errors - write data to another file
                    print "NfFileReadThread flowsend exception: ", repr(ex)
                    flows = flows[fcnt:]
                    newfname = ''.join((self.hpath, str(time.clock()), '.dmp'))
                    dfile = open(fname, 'ab')
                    for flow in flows:
                        dfile.write(flow)
                    dfile.close()
                    #use locks is deadlocking issues arise
                    fnameQueue.appendleft(newfname)
                    os.remove(fname)
                    return
                
            except Exception, ex:
                print "NfFileReadThread fileread exception: ", repr(ex)
                #use locks is deadlocking issues arise
                fnameQueue.append(fname)
                return
                        
            os.remove(fname)                      
                           
                    
class ServiceThread(Thread):
    '''
    Thread that forms and renews caches.

    nnode final structure:
    [0]  - src_ip
    [1]  - src_mask
    [2]  - dst_ip
    [3]  - dst_mask
    [4]  - next_hop
    [5]  - src_port
    [6]  - dst_port
    [7]  - protocol
    [8]  - passthrough
    [9]  - direction
    [10] - store
    [11] - traffic_class_id
    [12] - weight
        
    '''
    def __init__(self):
        
        self.connection = pool.connection()
        #self.connection._con._con.set_isolation_level(0)
        self.connection._con._con.set_client_encoding('UTF8')
        self.cur = self.connection.cursor()
        Thread.__init__(self)
        
    def run(self):
        #TODO: перенести обновления кешей нас, ипн, впн, а также проверку на переполнение словаря
        global nascache
        global ipncache
        global vpncache
        #global databaseQueue
        global nodesCache
        while True:
            #print "Servicethread"
            try:
                self.cur.execute("""SELECT ipaddress, id from nas_nas;""")
                self.connection.commit()
                nasvals = self.cur.fetchall()
                self.cur.close()
                self.cur = self.connection.cursor()
                nascache = dict(nasvals)
                del nasvals
            except Exception, ex:
                print "Servicethread nascache exception: ", repr(ex)
                try:
                    self.cur = self.connection.cursor()
                except Exception, ex:
                    print repr(ex)
                    time.sleep(5)
                    try:
                        self.connection = pool.connection()
                        self.connection._con._con.set_client_encoding('UTF8')
                    except Exception, ex:
                        print repr(ex)
                        time.sleep(10)
                        continue
                
            try:
                self.cur.execute("SELECT id,ipn_ip_address FROM billservice_account WHERE ipn_ip_address <> inet '0.0.0.0';")
                self.connection.commit()
                ipns = self.cur.fetchall()
                self.cur.close()
                self.cur = self.connection.cursor()
                icTmp = {}
                #ipncache = icTmp.fromkeys([parseAddress(x[0])[0] for x in self.cur.fetchall()], 1)
                #turn IP strings into long integers
                for ipn in ipns:
                    icTmp[parseAddress(ipn[1])[0]] = ipn[0]
                if icTmp:
                    ipncache = icTmp
                del icTmp
            except Exception, ex:
                print "Servicethread ipncache exception: ", repr(ex)
                
            try:
                self.cur.execute("SELECT id,vpn_ip_address FROM billservice_account WHERE vpn_ip_address <> inet '0.0.0.0';")
                self.connection.commit()
                vpns = self.cur.fetchall()
                self.cur.close()
                self.cur = self.connection.cursor()
                vcTmp = {}
                #turn IP strings into long integers
                for vpn in vpns:
                    vcTmp[parseAddress(vpn[1])[0]] = vpn[0]
                if vcTmp:
                    vpncache = vcTmp
                del vcTmp
                #vpncache = vcTmp.fromkeys([parseAddress(x[0])[0] for x in self.cur.fetchall()], 1)
            except Exception, ex:
                print "Servicethread vpncache exception: ", repr(ex)
             
            #forms a class-nodes structure
            try:
                self.cur.execute("SELECT weight, traffic_class_id, store, direction, passthrough, protocol, dst_port, src_port, src_ip, dst_ip, next_hop FROM nas_trafficnode AS tn JOIN nas_trafficclass AS tc ON tn.traffic_class_id=tc.id ORDER BY tc.weight, tc.passthrough;")
                self.connection.commit()
                nnodes = self.cur.fetchall()
                self.cur.close()
                self.cur = self.connection.cursor()
                ndTmp = [[0, []]]
                tc_id = nnodes[0][1]
                for nnode in nnodes:
                    if nnode[1] != tc_id:
                        ndTmp.append([0, []])
                    nclTmp = ndTmp[-1]
                    nclTmp[0] = nnode[1]
                    tc_id = nnode[1]
                    nlist = list(nnode)
                    n_hp = parseAddress(nlist.pop())[0]
                    d_ip = IPint(nlist.pop())
                    s_ip = IPint(nlist.pop())
                    nlist.append(n_hp)
                    nlist.append(d_ip.netmask())
                    nlist.append(d_ip.int())
                    nlist.append(s_ip.netmask())
                    nlist.append(s_ip.int())
                    nlist.reverse()
                    nclTmp[1].append(tuple(nlist))
                if ndTmp[0][0]:
                    nodesCache = ndTmp
                    #print ndTmp
                del ndTmp
            except Exception, ex:
                print "Servicethread trafficnodes exception: ", repr(ex)
                               
            try:
                self.cur.close()
                self.cur = self.connection.cursor()
            except: pass
                
            gc.collect()
            time.sleep(300)
               
            
        
def main ():        
    global packetCount
    global nfFlowCache
    packetCount = 0
    nfFlowCache = FlowCache()
    
    #-----
    svcThread = ServiceThread()
    svcThread.start()
    usThread = NfUDPSenderThread()
    usThread.start()
    #~~~~~~
    fdqThread = FlowDequeThread()
    fdqThread.start()
    #-----
    nfdqThread = nfDequeThread()
    nfdqThread.start()

    reception_server(config.get("nf", "host"), int(config.get("nf", "port")))            
    while 1: 
        asyncore.poll(0.010)
        
    return



import socket
if socket.gethostname() not in ['dolphinik','kenny','sserv.net','sasha','medusa', 'kail','billing', 'Billing.NemirovOnline', 'iserver']:
    import sys
    print "License key error. Exit from application."
    sys.exit(1)

if __name__=='__main__':
    if "-D" not in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
    
    config.read("ebs_config.ini")

    pool = PooledDB(
        mincached=2,
        maxcached=9,
        blocking=True,
        creator=psycopg2,
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"),
                                                               config.get("db", "username"),
                                                               config.get("db", "host"),
                                                               config.get("db", "password"))
    )
    #get socket parameters. AF_UNIX support
    if config.get("core_nf", "usock") == '0':
        coreHost = config.get("core_nf_inet", "host")
        corePort = int(config.get("core_nf_inet", "port"))
        coreAddr = (coreHost, corePort)
    elif config.get("core_nf", "usock") == '1':
        coreHost = config.get("core_nf_unix", "host")
        corePort = 0
        coreAddr = (coreHost,)
    else:
        raise Exception("Config '[core_nf] -> usock' value is wrong, must be 0 or 1")
    
    #get a dump' directrory string and check whethet it's writable
    dumpDir = config.get("core_nf", "dump_dir")
    try:
        tfname = ''.join((dumpDir,'/','nf_', str(time.clock()), '.dmp'))
        dfile = open(tfname, 'wb')
        dfile.write("testtesttesttesttest")
        dfile.close()
        os.remove(tfname)
    except Exception, ex:
        raise Exception("Dump directory '"+ dumpDir+ "' is not accesible/writable: operations with filename like '" +tfname+ "' were not executed properly!")

    #queues
    flowQueue = deque()
    databaseQueue = deque()
    fnameQueue = deque()
    fnameLock = threading.Lock()
    nodesCache = []
    nfQueue = deque()
    nfqLock = threading.Lock()
    nfFLOW_TYPES = {
        5 : (header5, flow5),
      }
    
    #numeric values
    sleepTime = 291.0
    aggrTime = 120.0
    #aggrTime = 60.0
    aggrNum = 666
    try:
        sleepTime = float(config.get("nf", "sleeptime"))
        aggrTime  = float(config.get("nf", "aggrtime"))
        aggrNum   = float(config.get("nf", "aggrnum"))
    except:
        pass
    main()



