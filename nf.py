#-*-coding=utf-8-*-


import gc
import glob
import random
import signal
import os, sys
import marshal
import asyncore
import psycopg2
import threading
import traceback
import ConfigParser
import socket, select, struct, datetime, time

import isdlogger
import log_adapter


from threading import Thread
from daemonize import daemonize
from DBUtils.PooledDB import PooledDB
from IPy import IP, IPint, parseAddress
from collections import deque, defaultdict
from saver import graceful_loader, graceful_saver, allowedUsersChecker, setAllowedUsers

try:    import mx.DateTime
except: pass

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
        pass    
    
    def handle_read(self):        
        data, addrport = self.recvfrom(8192)
        try:
            assert len(data)<=8192
            nfQueue.append((data, addrport))
        except Exception, ex:
            logger.error("NF server exception: %s",(repr(ex),))
        
    def writable(self):
        return 0
    
class nfDequeThread(Thread):
    '''Thread that gets packets received by the server from nfQueue queue and puts them onto the conveyour
    that gets flows and caches them.'''
    
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
        
    def run(self):
        global nfFlowCache
        while True:
            if suicideCondition[self.tname]: break
            #TODO: add locks if deadlocking issues arise
            try:
                data, addrport = nfQueue.popleft()        
                nfPacketHandle(data, addrport, nfFlowCache)
            except IndexError, ierr:
                time.sleep(3); continue    
            except Exception, ex:
                logger.error("NFP exception: %s", (repr(ex),))


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
        [26] - accounttarif.id
        [27] - hasgroups
        [28] - groups
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
        #raise ValueError, "Short packet"
        return

    nas_id = nascache.get(addrport[0])
    if not nas_id:
        return
          
    flows=[]
    if nas_id!=None:	    
        _nf = struct.unpack("!H", data[:2])
        pVersion = _nf[0]
        if not pVersion in nfFLOW_TYPES.keys():
            raise RuntimeWarning, "NetFlow version %d is not yet implemented" % pVersion
        hdr_class  = nfFLOW_TYPES[pVersion][0]
        flow_class = nfFLOW_TYPES[pVersion][1]
        hdr = hdr_class(data[:headerLENGTH])
        #======
        #runs through flows
        for n in xrange(hdr[1]):
            offset = headerLENGTH + (flowLENGTH * n)
            flow_data = data[offset:offset + flowLENGTH]
            flow=flow_class(flow_data)
            #look for account for ip address
            acc_acct_tf = (vpncache.has_key(flow[0]) and vpncache[flow[0]]) or (vpncache.has_key(flow[1]) and vpncache[flow[1]]) or (ipncache.has_key(flow[0]) and ipncache[flow[0]]) or (ipncache.has_key(flow[1]) and ipncache[flow[1]])
            if acc_acct_tf:
                flow[11] = nas_id
                #acc_id, acctf_id, tf_id = (acc_acct_tf)
                flow.append(acc_acct_tf)
                if checkClasses:
                    break_outer = False
                    for nclass, nnodes in nodesCache:                        
                        for nnode in nnodes:
                            if (((flow[0] & nnode[1]) == nnode[0]) and ((flow[1] & nnode[3]) == nnode[2]) and ((flow[2] == nnode[4]) or (not nnode[4])) and ((flow[9] == nnode[5]) or (not nnode[5])) and ((flow[10] == nnode[6]) or (not nnode[6])) and ((flow[13] == nnode[7]) or (not nnode[7]))):
                                flowCache.addflow5(flow)
                                break_outer = True
                                break
                        if break_outer: break
                    continue
                
                flowCache.addflow5(flow)         
                
                        

class FlowCache(object):
    '''Aggregates flows.'''
    def __init__(self):
        dcache = {}
        #list for keeping keys
        self.keylist = []
        self.stime = time.time()

    def addflow(self, version, flow):
        method = getattr(self, "addflow" + str(version), None)
        return method(flow)

    def reset(self):
        if ((self.stime + 60.0) < time.time()) and self.keylist:
            #appends keylist to flowQueue
            fqueueLock.acquire()
            flowQueue.append((self.keylist, time.time()))
            fqueueLock.release()
            #-----------------
            #nullifies keylist
            self.keylist = []
            self.stime = time.time()
            
    def addflow5(self, flow):
        global ipncache, vpncache, nascache
        #key = (flow.src_addr, flow.dst_addr, flow.next_hop, flow.src_port, flow.dst_port, flow.protocol)
        #constructs a key
        key = (flow[0], flow[1], flow[2], flow[9], flow[10], flow[13])
        val = dcache.get(key)
        #no such value, must add
        if not val:
            dcacheLock.acquire()
            #adds
            dcache[key] = flow
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
        else:
            dcacheLock.acquire()
            #appends flows
            dflow= dcache[key]
            dflow[6] += flow[6]
            dflow[5] += flow[5]
            dflow[8] = flow[8]
            dcacheLock.release()




                
class FlowDequeThread(Thread):
    '''Gets a keylist with keys to flows that are to be aggregated, waits for aggregation time, pops them from aggregation cache,
    constructs small lists of flows and appends them to 'databaseQueue'.'''
    
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)        
    
    def isect_classes(self, groups_rec, class_list):
        '''Calculates intersection of group classes and flow classes.
           Returns a tuple.'''
        groups_rec[1].intersection_update(class_list)
        groups_rec[1] = tuple(groups_rec[1])
        return tuple(groups_rec)
    
    def add_classes_groups(self, flow, classLst, nnode, acctf_id, has_groups, tarifGroups):
        ptime =  time.time()
        ptime = ptime - (ptime % 20)
        flow.append(ptime)
        #flow.append(test_now)
        flow.append(tuple(classLst))
        flow.append(nnode[9])
        flow.append(nnode[10])
        flow.append(nnode[8])
        flow.append(acctf_id)
        flow.append(has_groups)
        #add groups, check if any
        if has_groups:
            dr = 0
            flow_dir = nnode[9]
            if flow_dir == 'INPUT':
                dr = 2
            elif flow_dir == 'OUTPUT':
                dr = 1
            groupLst = []
            fcset = set(classLst)
            for tgrp in tarifGroups:
                if (tgrp[2] == dr) or (tgrp[0] == 0):
                    continue
                group_cls = fcset.intersection(tgrp[1])
                if group_cls:
                    group_add = tgrp[:]
                    group_add[1] = tuple(group_cls)
                    groupLst.append(tuple(group_add))
            flow.append(tuple(groupLst))

    def run(self):
        j = 0
        while True:
            if suicideCondition[self.tname]: break
            try:                
                fqueueLock.acquire()
                iqueue = 1
                #get keylist and time
                keylist, stime = flowQueue.popleft()
                fqueueLock.release()
                iqueue = 0                
                #if aggregation time was still not reached -> sleep
                wtime = time.time() - aggrTime - stime
                if wtime < 0: time.sleep(abs(wtime))
                
                #TO-DO: переделать на execute_many
                fcnt = 0
                flst = []
                for key in keylist:
                    dcacheLock.acquire()
                    flow = dcache.pop(key, None)
                    dcacheLock.release()
                    if not flow: continue                        
                    #get id's
                    acc_id, acctf_id, tf_id = flow.pop()
                    flow.append(acc_id)
                    has_groups = False
                    #get groups for tarif
                    tarifGroups = tarif_groupsCache.get(tf_id)
                    if tarifGroups: 
                        has_groups = True
                    
                    passthr = True
                    #checks classes
                    direction=None
                    fnode=None
                    classLst = []
                    
                    #Direction is taken from the first approved node
                    for nclass, nnodes in nodesCache:                    
                        for nnode in nnodes:
                            if (((flow[0] & nnode[1]) == nnode[0]) and ((flow[1] & nnode[3]) == nnode[2]) and ((flow[2] == nnode[4]) or (not nnode[4])) and ((flow[9] == nnode[5]) or (not nnode[5])) and ((flow[10] == nnode[6]) or (not nnode[6])) and ((flow[13] == nnode[7]) or (not nnode[7]))):
                                if not classLst:
                                    #direction = nnode[9]
                                    fnode = nnode
                                elif nnode[9] != fnode[9]:
                                    continue
                                classLst.append(nclass)
                                if not nnode[8]:
                                    passthr = False
                                break
                        #found passthrough=false
                        if not passthr:
                            self.add_classes_groups(flow, classLst, fnode, acctf_id, has_groups, tarifGroups)
                            break                   
                    #traversed all the nodes
                    else:
                        if classLst:
                            self.add_classes_groups(flow, classLst, fnode, acctf_id, has_groups, tarifGroups)
                        else: continue
                        
                    #construct a list
                    flst.append(tuple(flow))
                    fcnt += 1                    
                    #append to databaseQueue
                    if fcnt == 37:
                        dbLock.acquire()
                        databaseQueue.append(flst)
                        dbLock.release()
                        flst = []
                        fcnt = 0
                        #ftime = time.time()
                if len(flst) > 0:
                    dbLock.acquire()
                    databaseQueue.append(flst)
                    dbLock.release()
                    flst = []
                del keylist
            except IndexError, ierr:
                if iqueue:
                    fqueueLock.release()
                    time.sleep(5)
                continue
            except Exception, ex:
                    logger.error("fdqThread exception: %s", repr(ex))
            
            
class NfUDPSenderThread(Thread):
    '''Thread that gets packet lists from databaseQueue, marshals them and sends to Core module
    If there are errors, flow data are written to a file. When connection is established again, NfFileReadThread to clean up that files and resend data is started.
    '''
    def __init__(self): 
        self.tname = self.__class__.__name__
        self.outbuf = []
        self.hpath = ''.join((dumpDir,'/','nf_'))
        Thread.__init__(self)
        
    def run(self):
        addrport = coreAddr
        nfsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        nfsock.settimeout(sockTimeout)
        errflag   = 0
        flnumpack = 0
        dfile = None
        fname = None
        while True:     
            try:
                if suicideCondition[self.tname]:
                    if errflag: dfile.close(); fnameQueue.append(fname)
                    break
                #get a bunch of packets
                dbLock.acquire()
                dqueue  = 1            
                fpacket = databaseQueue.popleft()
                dbLock.release()
                flst   = marshal.dumps(fpacket)
                dqueue = 0
                #send data
                nfsock.sendto(flst,addrport)
                #recover reply
                dtrc, addr = nfsock.recvfrom(128)

                #if wrong length (probably zero reply) - raise exception
                if (dtrc == None):
                    raise Exception("Empty!")
                
                if dtrc[:4] == 'SLP!':
                    print "sleepFlag detected!"
                    time.sleep(10)
                    continue
                    
                if (len(flst) != int(dtrc)):
                    raise Exception("Sizes not equal!")
                
                #if the connection is OK but there were errors earlier
                if errflag:
                    logger.info('NFUDPSenderThread errflag detected - time %d', time.time())
                    dfile.close()
                    #use locks is deadlocking  arise
                    fnameQueue.append(fname)
                    #clear errflag
                    errflag = 0
                    
            except IndexError, ierr:
                if dqueue:
                    dbLock.release()
                    time.sleep(5)
                continue    
            except Exception, ex:
                logger.debug('NFUDPSenderThread exp: %s', repr(ex))
                if dqueue: continue
                #if no errors were detected earlier
                if not errflag:
                    try:
                        errflag = 1                        
                        #open a new file
                        fname = ''.join((self.hpath, str(time.time()), '_', str(random.random()), '.dmp'))
                        dfile = open(fname, 'ab')
                        logger.info('NFUDPSenderThread open a new file: %s', fname)
                    except Exception, ex:
                        logger.error("NFUDPSenderThread file creation exception: %s", repr(ex))
                        continue
                    
                try:   
                    #append data
                    dfile.write(flst)
                    dfile.write('!FLW')
                    #dfile.close()
                    flnumpack += 1
                    #if got enough packets - open a new file
                    if flnumpack == 300:
                        flnumpack = 0
                        dfile.close()
                        #use locks is deadlockind arise
                        fnameQueue.append(fname)
                        fname = ''.join((self.hpath, str(time.time()), '_', str(random.random()), '.dmp'))
                        dfile = open(fname, 'ab')
                except Exception, ex:
                        logger.error("NFUDPSenderThread file write exception: ", repr(ex))
                        continue
            del flst
            
class NfFileReadThread(Thread):
    '''Thread that reads previously written data dumps and resends data.'''
    def __init__(self, tsleep=0, tcount=0):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        self.hpath  = ''.join((dumpDir,'/','nf_'))
        self.tsleep = tsleep
        self.tcount = tcount
    
    def run(self):
        #filename
        fname = None
        addrport = coreAddr
        nfsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        nfsock.settimeout(sockTimeout)
        dfile = None
        while True:
            try:
                if suicideCondition[self.tname]: break
                
                #get a file name from a queue
                fnameLock.acquire()
                fqueue = 1
                fname  = fnameQueue.popleft()
                fnameLock.release()
                fqueue = 0
                #open the file
                dfile = open(fname, 'rb')
                #read flows
                flows = dfile.read()
                dfile.close()
                #create/open counter file
                fcname  = fname + 'c'
                flows  = flows.split('!FLW')[:-1]
                if os.path.exists(fcname):
                    cfile = open(fcname, 'rb')
                    fwrt = len(cfile.read())
                    flows = flows[fwrt:]
                    cfile.close()
                    cfile = open(fcname, 'ab')
                else:
                    cfile = open(fcname, 'wb')
                fcnt = 0
                try:
                    #send flows
                    for flow in flows:
                        nfsock.sendto(flow,addrport)                    
                        dtrc, addr = nfsock.recvfrom(128)
                        if (dtrc == None):
                            raise Exception("Empty!")
                
                        if dtrc[:4] == 'SLP!':
                            logger.lprint("NfFileReadThread: sleepFlag detected!")
                            time.sleep(10)
                    
                        elif (len(flow) != int(dtrc)):
                            raise Exception("Sizes not equal!")                        
                        fcnt += 1
                        cfile.write('\n')
                        #flush every 4 packets
                        if fcnt % 4 == 0:
                            cfile.flush()
                        time.sleep(0.1)
                    cfile.close()
                    os.remove(fname)
                    os.remove(fcname)
                    logger.info("NfFileReadThread: file processed: %s", (fname,))
                except Exception, ex:
                    #if errors - write data to another file
                    logger.error("NfFileReadThread flowsend exception: %s", (repr(ex),))
                    dfile.close(); cfile.close()
                    #append file again
                    #use locks is deadlocking issues arise
                    fnameQueue.appendleft(fname)
                    #run a cleanup thread
                    time.sleep(60)
                    continue
            except IndexError, ierr:
                if fqueue:
                    fnameLock.release()
                    time.sleep(240)
                continue    
            except Exception, ex:
                logger.error("NfFileReadThread fileread exception: %s", (repr(ex),))
                traceback.print_exc(file=sys.stderr)
                #use locks is deadlocking issues arise
                fnameQueue.append(fname)
                return                   
                           
                    
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
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        
    def run(self):
        #TODO: перенести обновления кешей нас, ипн, впн, а также проверку на переполнение словаря
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global nascache, ipncache, vpncache, cachesRead
        global nodesCache, groupsCache
        global class_groupsCache, tarif_groupsCache
        global nfFlowCache, allowedUsers
        while True:
            if suicideCondition[self.tname]: break
            cur = connection.cursor()
            a = time.clock()
            nfFlowCache.reset()
            try:
                cur.execute("SELECT ipaddress, id from nas_nas;")                
                nasvals = cur.fetchall()
                cur.execute("SELECT ba.id,ba.vpn_ip_address,ba.ipn_ip_address, bacct.id, bacct.tarif_id FROM billservice_account AS ba JOIN billservice_accounttarif AS bacct ON bacct.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1);", (datetime.datetime.now(),))
                accts = cur.fetchall()
                cur.execute("SELECT weight, traffic_class_id, store, direction, passthrough, protocol, dst_port, src_port, src_ip, dst_ip, next_hop FROM nas_trafficnode AS tn JOIN nas_trafficclass AS tc ON tn.traffic_class_id=tc.id ORDER BY tc.weight, tc.passthrough;")
                nnodes = cur.fetchall()
                cur.execute("SELECT id, ARRAY(SELECT trafficclass_id from billservice_group_trafficclass as bgtc WHERE bgtc.group_id = bsg.id) AS trafficclass, direction, type FROM billservice_group AS bsg;")
                groups = cur.fetchall()
                #cur.execute("SELECT tarif_id, int_array_aggregate(group_id) AS group_ids FROM (SELECT tarif_id, group_id FROM billservice_trafficlimit UNION SELECT bt.id, btn.group_id FROM billservice_tariff AS bt JOIN billservice_traffictransmitnodes AS btn ON bt.traffic_transmit_service_id=btn.traffic_transmit_service_id WHERE btn.group_id IS NOT NULL) AS tarif_group GROUP BY tarif_id;")
                cur.execute("SELECT id, ARRAY(SELECT id FROM billservice_group) FROM billservice_tariff;")
                tarif_groups = cur.fetchall()
                connection.commit()
                cur.close()
                allowedUsersChecker(allowedUsers, lambda: len(accts))
                #nas cache creation
                nascache = dict(nasvals)
                del nasvals            

                #vpn-ipn caches creation
                icTmp = {}
                vcTmp = {}
                for acct in accts:
                    vpn_ip, ipn_ip = acct[1:3]
                    if vpn_ip != '0.0.0.0':
                        vcTmp[parseAddress(vpn_ip)[0]] = (acct[0], acct[3], acct[4])
                    if ipn_ip != '0.0.0.0':
                        icTmp[parseAddress(ipn_ip)[0]] = (acct[0], acct[3], acct[4]) 

                ipncache = icTmp           
                vpncache = vcTmp
                del icTmp, vcTmp
                
                #forms a class->nodes structure                
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
                del ndTmp       
                #print nodesCache
                #id, trafficclass, in_direction, out_direction, type
                gpcTmp = defaultdict(set)
                groups_ = {}
                for group in groups:
                    if not group[1]: continue
                    lgroup = list(group)
                    #lgroup[1] = set(lgroup[1])
                    groups_[group[0]] = lgroup
        
                groupsCache = groups_
                class_groupsCache = gpcTmp
                del gpcTmp
                
                tg_ = defaultdict(list)
                for tarif_id, groups__ in tarif_groups:
                    for grp in set(groups__):
                        tg_[tarif_id].append(groupsCache.get(grp, [0,[]]))
                    
                tarif_groupsCache = tg_                
                cachesRead = True
                
                
                #reread runtime config options
                config.read("ebs_config_runtime.ini")
                logger.setNewLevel(int(config.get("nf", "log_level")))
                logger.info("nf time : %s", time.clock() - a)
                global writeProf
                writeProf = logger.writeInfoP()
                if writeProf:
                    logger.info("len flowQueue %s", len(flowQueue))
                    logger.info("len dbQueue: %s", len(databaseQueue))
                    logger.info("len fnameQueue: %s", len(fnameQueue))
                    logger.info("len nfqueue: %s", len(nfQueue))
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    logger.error("%s: database connection is down: %s", (self.getName(),repr(ex)))
                else:
                    logger.error("%s: exception: %s", (self.getName(),repr(ex)))  
            gc.collect()
            time.sleep(300)
               
            
        

class RecoveryThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        global dumpDir, fnameQueue
        try:
            fllist = glob.glob(''.join((dumpDir, '/', 'nf_*.dmp')))
            if fllist:
                for fl in fllist:
                    fnameQueue.appendleft(fl)
        except Exception, ex:
            logger.error("%s: exception: %s", (self.getName(),repr(ex)))  

def SIGTERM_handler(signum, frame):
    graceful_save()

def graceful_save():
    global cacheThr, threads, suicideCondition
    asyncore.close_all()
    suicideCondition[cacheThr.tname] = True
    for thr in threads:
            suicideCondition[thr.tname] = True
    time.sleep(10)
    
    graceful_saver([['dcache','nfFlowCache'], ['flowQueue'], ['databaseQueue']],
                   globals(), 'nf_', saveDir)
    
    pool.close()
    time.sleep(2)
    sys.exit()
        
def graceful_recover():
    graceful_loader(['dcache','nfFlowCache','flowQueue','databaseQueue'],
                    globals(), 'nf_', saveDir)
                
def main ():        
    global packetCount, nfFlowCache, threads, cacheThr
    global recover, cachesRead
    packetCount = 0
    nfFlowCache = FlowCache()
    
    graceful_recover()
    #recover leftover dumps?
    if recover:
        recThr = RecoveryThread()
        recThr.setName('Recovery thread')
        recThr.start()
        time.sleep(0.5)
        
    threads = []
    thrnames = [(NfFileReadThread, 'NfFileReadThread'), (NfUDPSenderThread, 'NfUDPSenderThread'), \
                (FlowDequeThread, 'NfFlowDequeThread'), (nfDequeThread, 'nfDequeThread')]
    
    for thClass, thName in thrnames:
        threads.append(thClass())
        threads[-1].setName(thName)

    #-----
    cacheThr = ServiceThread()
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.setName('NfCacheThread')
    cacheThr.start()
    
    #sleep until all caches are read
    while not cachesRead:
        time.sleep(0.2)
        if not cacheThr.isAlive:
            sys.exit()
            
    for th in threads:
        suicideCondition[th.__class__.__name__] = False
        th.start()
        time.sleep(0.5)
        
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')    
    reception_server(config.get("nf", "host"), int(config.get("nf", "port"))) 
    
    print "ebs: nf: started"
    while 1: 
        asyncore.poll(0.010)


if socket.gethostname() not in ['dolphinik','kenny','sserv.net','sasha','medusa', 'kail','billing', 'Billing.NemirovOnline', 'iserver']:
    import sys
    print "License key error. Exit from application."
    sys.exit(1)

if __name__=='__main__':
    if "-D" in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
        

    config = ConfigParser.ConfigParser()

    #binary strings lengthes
    flowLENGTH   = struct.calcsize("!LLLHHIIIIHHBBBBHHBBH")
    headerLENGTH = struct.calcsize("!HHIIIIBBH")
    
    config.read("ebs_config.ini")


    logger = isdlogger.isdlogger(config.get("nf", "log_type"), loglevel=int(config.get("nf", "log_level")), ident=config.get("nf", "log_ident"), filename=config.get("nf", "log_file")) 
    log_adapter.log_adapt = logger.log_adapt
    logger.lprint('Nf start')
    
    try:
        #write profiling info predicate
        writeProf = logger.writeInfoP()
        
        pool = PooledDB(
        mincached=1,  maxcached=9,
        blocking=True,creator=psycopg2,
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"),
                                                               config.get("db", "host"), config.get("db", "password")))
    
            
        #get socket parameters. AF_UNIX support
        if config.get("nfroutine_nf", "usock") == '0':
            coreHost = config.get("nfroutine_nf_inet", "host")
            corePort = int(config.get("nfroutine_nf_inet", "port"))
            coreAddr = (coreHost, corePort)
            
        elif config.get("nfroutine_nf", "usock") == '1':
            coreHost = config.get("nfroutine_nf_unix", "host")
            corePort = 0
            coreAddr = (coreHost,)
        else:
            raise Exception("Config '[nfroutine_nf] -> usock' value is wrong, must be 0 or 1")
        
        sockTimeout = float(config.get("nfroutine_nf", "sock_timeout"))
        recover    = (config.get("nfroutine_nf", "recover") == '1')
        recoverAtt = (config.get("nfroutine_nf", "recoverAttempted") == '1')
        saveDir = config.get("nf", "save_dir")
        
        checkClasses = (config.get("nf", "checkclasses") == '1')
        #get a dump' directrory string and check whethet it's writable
        dumpDir = config.get("nfroutine_nf", "dump_dir")
        try:
            tfname = ''.join((dumpDir,'/','nf_', str(time.time()), '.dmp'))
            dfile = open(tfname, 'wb')
            dfile.write("testtesttesttesttest")
            dfile.close()
            os.remove(tfname)
        except Exception, ex:
            raise Exception("Dump directory '"+ dumpDir+ "' is not accesible/writable: errors were encountered upun executing test operations with filenames like '" +tfname+ "'!")
    
        suicideCondition = {}
        cachesRead = False
        #aggregation cache
        dcache   = {}
        #caches for Nas data, account IPN, VPN address indexes
        nascache = {}
        ipncache = {}
        vpncache = {}
        
        #cache for groups data
        groupsCache = {}
        #cache for group->classes
        class_groupsCache = defaultdict(set)
        #cache for tarif->groups
        tarif_groupsCache = {}
        #locks
        dcacheLock = threading.Lock()
        fqueueLock = threading.Lock()
        dbLock = threading.Lock()
        
        nfFlowCache = None
        packetCount = None
        #queues
        flowQueue = deque()
        databaseQueue = deque()
        fnameQueue = deque()
        fnameLock = threading.Lock()
        
        #cache for class->nodes
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
        aggrNum = 667
        try:
            sleepTime = float(config.get("nf", "sleeptime"))
            aggrTime  = float(config.get("nf", "aggrtime"))
            aggrNum   = float(config.get("nf", "aggrnum"))
        except:
            pass
        
        allowedUsers = setAllowedUsers(pool.connection(), "license.lic")        
        allowedUsers()
        test_now = time.time()
        #-------------------
        print "ebs: nf: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nf, exiting: ', repr(ex)
        logger.error('Exception in nf, exiting: %s', repr(ex))
    
    
    
