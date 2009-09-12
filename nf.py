#-*-coding=utf-8-*-

from __future__ import with_statement

#REWRITE SENDER

import gc
import copy
import glob
import random
import signal
import os, sys
import marshal
import utilites
#import asyncore
import psycopg2
import threading
import traceback
import ConfigParser
import socket, select, struct, datetime, time

import isdlogger
import saver


from threading import Thread, Lock
from daemonize import daemonize
from DBUtils.PooledDB import PooledDB
from IPy import IP, IPint, parseAddress
from collections import deque, defaultdict
from saver import graceful_loader, graceful_saver, allowedUsersChecker, setAllowedUsers

import twisted.internet
#import twisted.protocols.ftp
from twisted.protocols.basic import implements, interfaces, defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.protocol import Protocol, ReconnectingClientFactory

try:
    from twisted.internet import pollreactor
    pollreactor.install()
except:
    print 'No poll(). Using select() instead.'
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator, ClientFactory

from classes.nf_cache import *
from classes.common.Flow5Data import Flow5Data
from classes.cacheutils import CacheMaster
from classes.flags import NfFlags
from classes.vars import NfVars, NfQueues, install_logger
from utilites import renewCaches, savepid, rempid, get_connection, getpid, check_running, \
                     STATE_NULLIFIED, STATE_OK, NFR_PACKET_HEADER_FMT


MIN_NETFLOW_PACKET_LEN = 16
HEADER_FORMAT = "!HHIIIIBBH"
FLOW_FORMAT   = "!LLLHHIIIIHHBBBBHHBBH"
FLOWCACHE_OVER_TIME  = 10
FLOWCACHE_RESET_TIME = 60

NAME = 'nf'
DB_NAME = 'db'
NET_NAME = 'nfroutine_nf'
MAX_PACKET_INDEX = 2147483647L

NOT_TRASMITTED = 0
WRITE_OK = 1

try:    import mx.DateTime
except: pass

class Reception_UDP(DatagramProtocol):
    '''
    Twisted Asynchronous server that recieves datagrams with NetFlow packets
    and appends them to 'nfQueue' queue.
    '''
    def datagramReceived(self, data, addrport):
        if len(data) <= vars.MAX_DATAGRAM_LEN:
            queues.nfQueue.append((data, addrport))
        else:
            logger.error("NF server exception: packet %s <= %s", (len(data), vars.MAX_DATAGRAM_LEN))
            
class SendPacketProducer(object):

    implements(interfaces.IPullProducer)

    def __init__(self, packet_queue, packet_lock, consumer, delimeter):
        
        self.packet_queue = packet_queue
        self.packet_lock = packet_lock
        self.consumer = consumer
        self.consumer.registerProducer(self, False)
        self.delimeter = delimeter
        self.delim_len = len(self.delimeter)
        
    def pauseProducing(self):
        pass

    def stopProducing(self):
        logger.warning("Sender consumer asked producer to stop!", ())
        
    def resumeProducing(self):
        send_packet = False
        packet_status = 0

        if len(self.packet_queue) > 0:
            with self.packet_lock:
                if len(self.packet_queue) > 0:
                    send_packet = self.packet_queue.popleft()
        if not send_packet:
            self.pauseProducing()
            #return
            #self.consumer.write('')
        else:        
            packet_len = len(send_packet) + 5 + self.delim_len
            str_len = str(packet_len)[:5]
            formatted_packet = '0' * (len(str_len) - 5) + str_len + send_packet + self.delimeter
            if self.consumer.write(formatted_packet) == NOT_TRASMITTED:
                with self.packet_lock:
                    self.packet_queue.appendleft(send_packet)         
        ''''''

class SendPacketStream(Thread):

    implements(interfaces.IProducer)
    structFormat = "!I"
    prefixLength = struct.calcsize(structFormat)
    
    def __init__(self, packet_queue, packet_lock, delimeter):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
        
        self.packet_queue = packet_queue
        self.packet_lock = packet_lock

        self.delimeter = delimeter
        self.delim_len = len(self.delimeter)
        self.PAUSED = True
        #self 
        
    def registerConsumer_(self, consumer):
        self.consumer = consumer
        self.consumer.registerProducer(self, True)
        self.resumeProducing()
        
    def pauseProducing(self):
        self.PAUSED = True

    def stopProducing(self):
        self.PAUSED = True
        logger.warning("Sender consumer asked producer to stop!", ())
        
    def resumeProducing(self):
        self.PAUSED = False
        
    def run(self):
        while True:
            if suicideCondition[self.tname]: break
            if self.PAUSED:
                time.sleep(0.3); continue
            send_packet = False
            packet_status = 0
            if len(self.packet_queue) > 0:
                with self.packet_lock:
                    if len(self.packet_queue) > 0:
                        send_packet = self.packet_queue.popleft()
            if not send_packet: 
                time.sleep(1)
                continue
            #print len(send_packet)
            #packet_len = len(send_packet)
            #str_len = str(packet_len)[:5]
            #formatted_packet = '0' * (5 - len(str_len)) + str_len + send_packet + self.delimeter
            if self.consumer.write(struct.pack(self.structFormat, len(send_packet)) + send_packet) == NOT_TRASMITTED:
                with self.packet_lock:
                    self.packet_queue.appendleft(send_packet)

class TCPSender(Protocol):
    implements(interfaces.IConsumer)
    
    isConnected = False
    
    def __init__(self, producer):
        #super(TCPSender, self).__init__()
        self.producer = producer

    def connectionMade(self):
        self.isConnected = True
        self.transport.bufferSize = 512000
        #self.producer_ = self.producer(queues.databaseQueue, queues.dbLock, self, vars.NFR_DELIMITER)
        self.producer.registerConsumer_(self)
        
    def connectionLost(self, reason):
        self.isConnected = False
    def dataReceived(self, data):
        #print 'datarecieved'
        if data == '!SLP':
            time.sleep(30)
            
    def registerProducer(self, producer, streaming):
        return self.transport.registerProducer(producer, streaming)

    def unregisterProducer(self):
        self.transport.unregisterProducer()
        self.transport.loseConnection()

    def write(self, formatted_packet):
        if self.isConnected:
            #print 'SENT LINE: ', formatted_packet[:6], '|', formatted_packet[-6:]
            self.transport.write(formatted_packet)

        else:
            return NOT_TRASMITTED


    def resumeProducing(self):
        self.transport.resumeProducing()

    def pauseProducing(self):
        self.transport.pauseProducing()

    def stopProducing(self):
        self.transport.stopProducing()

    
            
class TCPSender_ClientFactory(ReconnectingClientFactory):
    protocol = TCPSender
    factor = 1.6180339887498948
    maxDelay = 600
    def __init__(self, producer):
        #super(TCPSender_ClientFactory, self).__init__()
        self.Producer = producer
        
    def startedConnecting(self, connector):
        logger.info('SENDER: Started connecting.', ())

    def buildProtocol(self, addr):
        logger.info('SENDER: Connected.', ())
        self.resetDelay()
        return TCPSender(self.Producer)
        #tcs.producer = self.producer
        #return tcs

    def clientConnectionLost(self, connector, reason):
        logger.info('SENDER: Lost connection.  Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        logger.info('SENDER: Connection failed. Reason:', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)

class nfDequeThread(Thread):
    '''Thread that gets packets received by the server from nfQueue queue and puts them onto the conveyour
    that gets flows and caches them.'''
    
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
        
    def run(self):
        while True:
            if suicideCondition[self.tname]: break
            #TODO: add locks if deadlocking issues arise
            try:
                data, addrport = queues.nfQueue.popleft()        
                nfPacketHandle(data, addrport, queues.nfFlowCache)
            except IndexError, ierr:
                time.sleep(3); continue  
            except Exception, ex:
                logger.error("NFP exception: %s \n %s", (repr(ex), traceback.format_exc()))


def flow5(data):
    if len(data) != vars.flowLENGTH:
        raise ValueError, "Short flow: data length: %d; LENGTH: %d" % (len(data), vars.flowLENGTH)
    #must turn tuples into lists because they are to be modified
    return Flow5Data(False, *struct.unpack(FLOW_FORMAT, data))


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
    if len(data) != vars.headerLENGTH:
        raise ValueError, "Short flow header"
    return struct.unpack(HEADER_FORMAT, data)

def nfPacketHandle(data, addrport, flowCache):
    '''
    Function receiving a binary Netflow packet, sender addrport and FlowCache reference.
    Gets, unpacks and checks flows from packets.
    Approved packets are added to FlowCache.
    '''    
    if len(data) < MIN_NETFLOW_PACKET_LEN:
        #raise ValueError, "Short packet"
        logger.warning("Small packet, discarded: %s", repr(addrport))
        return
    caches = cacheMaster.cache
    if 0: assert isinstance(caches, NfCaches)
    nas_id = caches.nas_cache.ip_id.get(addrport[0])
    if not nas_id: return
          
    flows=[]
    _nf = struct.unpack("!H", data[:2])
    pVersion = _nf[0]
    if not pVersion in vars.FLOW_TYPES.keys():
        raise RuntimeWarning, "NetFlow version %d is not yet implemented" % pVersion
    hdr_class, flow_class  = vars.FLOW_TYPES[pVersion]
    hdr = hdr_class(data[:vars.headerLENGTH])
    #======
    #runs through flows
    for n in xrange(hdr[1]):
        offset = vars.headerLENGTH + (vars.flowLENGTH * n)
        flow_data = data[offset:offset + vars.flowLENGTH]
        flow = flow_class(flow_data)
        if 0: assert isinstance(flow, Flow5Data)
        #look for account for ip address

        acc_data_src = caches.account_cache.vpn_ips.get(flow.src_addr) or caches.account_cache.ipn_ips.get(flow.src_addr)
        acc_data_dst = caches.account_cache.vpn_ips.get(flow.dst_addr) or caches.account_cache.ipn_ips.get(flow.dst_addr)
        local = bool(acc_data_src and acc_data_dst)
        acc_acct_tf = (acc_data_src, acc_data_dst) if local else (acc_data_src or acc_data_dst,)
        if acc_acct_tf[0]:            
            flow.nas_id = nas_id
            #acc_id, acctf_id, tf_id = (acc_acct_tf)
            flow.padding = local
            flow.account_id = acc_acct_tf
            flow.node_direction = None
            if vars.CHECK_CLASSES:
                break_outer = False
                for nclass, nnodes in caches.class_cache.classes:                        
                    for nnode in nnodes:
                        if 0: assert isinstance(nnode,ClassData)
                        if (((flow.src_addr & nnode.src_mask) == nnode.src_ip) and \
                            ((flow.dst_addr & nnode.dst_mask) == nnode.dst_ip) and \
                            ((flow.next_hop == nnode.next_hop) or (not nnode.next_hop)) and \
                            ((flow.src_port == nnode.src_port) or (not nnode.src_port)) and \
                            ((flow.dst_port == nnode.dst_port) or (not nnode.dst_port)) and \
                            ((flow.protocol == nnode.protocol) or (not nnode.protocol))):
                            
                            flowCache.addflow5(flow)
                            break_outer = True
                            break
                    if break_outer: break
                continue
            
            flowCache.addflow5(flow)         
                
                        

class FlowCache(object):
    '''Aggregates flows.'''
    def __init__(self):
        #queues.dcache = {}
        #list for keeping keys
        self.keylist = []
        self.stime = time.time()
        
    def __len__(self):
        return len(self.keylist)

    def addflow(self, version, flow):
        method = getattr(self, "addflow" + str(version), None)
        return method(flow)

    def reset(self):
        if ((self.stime + FLOWCACHE_RESET_TIME) < time.time()) and self.keylist:
            #appends keylist to flowQueue
            with queues.fqueueLock:
                queues.flowQueue.append((self.keylist, time.time()))
            #-----------------
            #nullifies keylist
            self.keylist = []
            self.stime = time.time()
            
    def addflow5(self, flow):
        global queues, vars
        if 0: assert isinstance(flow, Flow5Data)
        #constructs a key
        key = (flow.src_addr, flow.dst_addr, flow.next_hop, flow.src_port, flow.dst_port, flow.protocol)
        dhkey   = (flow.src_addr + flow.dst_addr + flow.src_port) % vars.CACHE_DICTS
        dhcache = queues.dcaches[dhkey]
        dhlock  = queues.dcacheLocks[dhkey]
        dhlock.acquire()
        dflow = dhcache.get(key)
        #no such value, must add        
        if dflow:
            dflow.octets  += flow.octets
            dflow.packets += flow.packets
            dflow.finish = flow.finish
            dhlock.release()
        else:
            dhcache[key] = flow            
            #stores key in a list
            self.keylist.append(key)
            dhlock.release()
            #time to start over?
            if (len(self.keylist) > vars.AGGR_NUM) or ((self.stime + FLOWCACHE_OVER_TIME) < time.time()):
                #appends keylist to flowQueue
                with queues.fqueueLock:
                    queues.flowQueue.append((self.keylist, time.time()))
                #nullifies keylist
                self.keylist = []
                self.stime = time.time()            
                
class FlowDequeThread(Thread):
    '''Gets a keylist with keys to flows that are to be aggregated, waits for aggregation time, pops them from aggregation cache,
    constructs small lists of flows and appends them to 'databaseQueue'.'''
    
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
    
    def add_classes_groups(self, flow, classLst, nnode, acctf_id, has_groups, tarifGroups):
        ptime =  time.time()
        if vars.NF_TIME_MOD:
            ptime = ptime - (ptime % vars.NF_TIME_MOD)
        if 0: assert isinstance(flow, Flow5Data); assert isinstance(nnode, ClassData)
        flow.datetime = ptime; flow.class_id = tuple(classLst)
        flow.node_direction = nnode.direction; flow.class_store = nnode.store
        flow.class_passthrough = nnode.passthrough; flow.acctf_id = acctf_id
        flow.groups = None; flow.has_groups = has_groups
        #add groups, check if any
        if has_groups:
            dr = 0
            if   nnode.direction == 'INPUT' : dr = 2
            elif nnode.direction == 'OUTPUT': dr = 1
            groupLst = []
            fcset = set(classLst)
            for tgrp in tarifGroups:
                if 0: assert isinstance(tgrp, GroupsData)
                if (not tgrp.trafficclass) or (tgrp.direction == dr):
                    continue
                group_cls = fcset.intersection(tgrp.trafficclass)
                if group_cls:
                    group_add = tgrp[:]
                    group_add[1] = tuple(group_cls)
                    groupLst.append(tuple(group_add))
            flow.groups = tuple(groupLst)

    def run(self):
        j = 0
        while True:
            if suicideCondition[self.tname]: break
            try:       
                stime = 0
                queues.fqueueLock.acquire()
                try:
                    #get keylist and time
                    keylist, stime = queues.flowQueue.popleft()
                except Exception, ex:
                    logger.debug("fdqThread indexerror exception: %s", repr(ex))
                finally:
                    queues.fqueueLock.release()
                if not stime: time.sleep(5); continue
                
                #if aggregation time was still not reached -> sleep
                wtime = time.time() - vars.AGGR_TIME - stime
                if wtime < 0: time.sleep(abs(wtime))

                fcnt = 0
                flst = []
                for key in keylist:
                    #src_addr, dst_addr, src_port
                    dhkey   = (key[0] + key[1] + key[3]) % vars.CACHE_DICTS
                    dhcache = queues.dcaches[dhkey]
                    dhlock  = queues.dcacheLocks[dhkey]
                    with dhlock:
                        qflow = dhcache.pop(key, None)
                    if not qflow: continue
                    #get id's
                    acc_data = qflow.account_id
                    qflow.account_id = None
                    local = qflow.padding
                    src = True
                    for acc in acc_data:
                        flow = copy.copy(qflow) if (local and src) else qflow
                        if 0: assert isinstance(flow, Flow5Data)
                        flow.account_id = acc.account_id
                        flow.acctf_id = acc.acctf_id
                        #get groups for tarif
                        tarifGroups = cacheMaster.cache.tfgroup_cache.by_tarif.get(acc.tarif_id)
                        has_groups = True if tarifGroups else False
                        direction = ((src and 'INPUT') or 'OUTPUT') if local else None
                        passthr = True
                        #checks classes                    
                        fnode = None; classLst = []                    
                        #Direction is taken from the first approved node
                        for nclass, nnodes in cacheMaster.cache.class_cache.classes:                    
                            for nnode in nnodes:
                                if 0: assert isinstance(nnode, ClassData)
                                if (((flow.src_addr & nnode.src_mask) == nnode.src_ip) and \
                                    ((flow.dst_addr & nnode.dst_mask) == nnode.dst_ip) and \
                                    ((flow.next_hop == nnode.next_hop) or (not nnode.next_hop)) and \
                                    ((flow.src_port == nnode.src_port) or (not nnode.src_port)) and \
                                    ((flow.dst_port == nnode.dst_port) or (not nnode.dst_port)) and \
                                    ((flow.protocol == nnode.protocol) or (not nnode.protocol))):
                                    
                                    if not classLst and (not direction or (nnode.direction == direction)):
                                        fnode = nnode
                                    elif not fnode:
                                        continue
                                    elif nnode.direction != fnode.direction:
                                        continue
                                    classLst.append(nclass)
                                    if not nnode.passthrough:
                                        passthr = False
                                    break
                            #found passthrough=false
                            if not passthr:
                                self.add_classes_groups(flow, classLst, fnode, acc.acctf_id, has_groups, tarifGroups)
                                break                   
                        #traversed all the nodes
                        else:
                            if classLst:
                                self.add_classes_groups(flow, classLst, fnode, acc.acctf_id, has_groups, tarifGroups)
                            else: continue
                            
                        #construct a list
                        flst.append(tuple(flow)); fcnt += 1                    
                        #append to databaseQueue
                        if fcnt == vars.PACKET_PACK:
                            flpack = marshal.dumps(flst)
                            with queues.dbLock:
                                queues.databaseQueue.append(flpack)
                            flst = []; fcnt = 0
                            
                        src = False
                        
                if len(flst) > 0:
                    flpack = marshal.dumps(flst)
                    with queues.dbLock:
                        queues.databaseQueue.append(flpack)
                    flst = []
                del keylist
            except Exception, ex:
                    logger.error("fdqThread exception: %s \n %s", (repr(ex), traceback.format_exc()))
            
            
class NfUDPSenderThread(Thread):
    '''Thread that gets packet lists from databaseQueue, marshals them and sends to Core module
    If there are errors, flow data are written to a file. When connection is established again, NfFileReadThread to clean up that files and resend data is started.
    '''
    def __init__(self): 
        self.tname = self.__class__.__name__
        self.outbuf = []
        self.hpath = ''.join((vars.DUMP_DIR,'/',vars.PREFIX))
        Thread.__init__(self)
        self.last_packet = None
        self.err_count   = 0
        
    def run(self):
        addrport = vars.NFR_ADDR
        nfsock = get_socket()
        errflag, flnumpack = 0, 0
        dfile, fname = None, None
        while True:     
            try:
                if suicideCondition[self.tname]:
                    break
                #get a bunch of packets
                flst = None

                with queues.dbLock:
                    if len(queues.databaseQueue) > 0:
                        flst = queues.databaseQueue.popleft()
                if not flst: time.sleep(5); continue
                
                nfsock.sendto(struct.pack(NFR_PACKET_HEADER_FMT, *get_index_state()) + flst, vars.NFR_ADDR)
                #recover reply
                dtrc, addr = nfsock.recvfrom(128)
                #if wrong length (probably zero reply) - raise exception
                if dtrc is None or len(dtrc) < 4: raise Exception("Empty!")
                
                if dtrc[4] != '!' and (len(flst) != int(dtrc)): raise Exception("Sizes not equal!")
                
                with queues.packetIndexLock:
                    queues.packetIndex += 1
                  
                if   dtrc[:4] == 'BAD!':
                    raise Exception("Bad packet flag detected!")
                
                self.last_packet = flst
                self.err_count   = 0
                
                if dtrc[:4] == 'SLP!':
                    logger.lprint("sleepFlag detected!")
                    time.sleep(30); continue
                elif dtrc[:4] == 'DUP!':
                    logger.lprint("Duplicate packet flag detected!")
                    continue
                elif dtrc[:4] == 'ERR!':
                    logger.lprint("Error packet flag detected!")
                    continue     
                    
            except Exception, ex:
                logger.debug('%s exp: %s \n %s', (self.getName(), repr(ex), traceback.format_exc()))
                #if no errors were detected earlier
                if self.last_packet == flst and not isinstance(ex, socket.timeout):
                    self.err_count += 1
                else:
                    self.last_packet = flst
                    self.err_count = 0
                if flst and self.err_count < 5:
                    #self.err_count == 0
                    with queues.dbLock:
                        queues.databaseQueue.appendleft(flst)
                elif flst:
                    logger.warning("%s: Packet dropped!", self.getName())

 
def get_index_state():
    state = STATE_OK
    index = 0
    with queues.packetIndexLock:
        if queues.packetIndex > MAX_PACKET_INDEX:
            queues.packetIndex = 0
            state = STATE_NULLIFIED
        index = queues.packetIndex
    return (index, state, time.time())

class NfFileReadThread(Thread):
    '''Thread that reads previously written data dumps and resends data.'''
    def __init__(self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        self.hpath  = ''.join((vars.READ_DIR,'/',vars.PREFIX))
        self.prev_ps  = 1.0
        #self.pprev_ps = 1.0
        self.cur_ps   = 1.0
        self.file_ps  = vars.FILE_PACK / float(vars.MAX_SENDBUF_LEN)
        self.allow_recover = 0
        self.allow_dump    = 0
    
    def run(self):
        fname, dfile = None, None
        while True:
            try:
                if suicideCondition[self.tname]: break
                #get a file name from a queue
                fname = None
                self.allow_recover = 0
                self.allow_dump    = 0
                dbqueue_len = 0
                #with queues.dbLock:
                dbqueue_len = len(queues.databaseQueue)
                self.cur_ps = dbqueue_len / vars.MAX_SENDBUF_LEN
                #logger.info('PPrevious dbqueue len/max percentage: %s', self.pprev_ps)
                logger.info('Previous dbqueue len/max percentage: %s', self.prev_ps)
                logger.info('Current dbqueue len/max percentage: %s', self.cur_ps) 
                if self.cur_ps > 1:
                    if self.cur_ps < 1 + self.file_ps:
                        pass
                    elif self.prev_ps < 1 and self.cur_ps - 1 / self.file_ps < 3:
                        self.allow_dump = 1
                    else:
                        self.allow_dump = int(self.cur_ps - 1 / self.file_ps)
                elif self.cur_ps < 1 and len(queues.fnameQueue) > 0:
                    if self.cur_ps > 1 - self.file_ps:
                        pass
                    elif self.prev_ps > 1 and  1 - self.cur_ps / self.file_ps < 3:
                        self.allow_recover = 1
                    else:
                        self.allow_recover = int(1 - self.cur_ps / self.file_ps)
                        
                self.prev_ps = self.cur_ps
                if self.allow_dump:
                    dump_queue = None
                    dump_index = -1 * self.allow_dump * vars.FILE_PACK
                    with queues.dbLock:
                        dump_queue = queues.databaseQueue[dump_index:]
                        queues.databaseQueue = queues.databaseQueue[:dump_index]
                    if dump_queue:
                        for i in xrange(self.allow_dump):
                            dump_out = dump_queue[:vars.FILE_PACK]
                            dump_queue = dump_queue[vars.FILE_PACK:]
                            if dump_out:
                                try:
                                    fname = ''.join((self.hpath, str(time.time()), '_', str(random.random()), '.dmp'))
                                    dump_file = open(fname, 'wb')
                                    marshal.dump(dump_out, dump_file)
                                    dump_file.close()
                                except Exception, ex:
                                    logger.error("NfFileReadThread filewrite exception: %s \n %s", (repr(ex), traceback.format_exc()))
                                else:
                                    with queues.fnameLock:
                                        queues.fnameQueue.append(fname)
                                    logger.info("NfFileReadThread dumped %s packets to file %s", (len(dump_out), fname))
                elif self.allow_recover:
                    recover_list = []
                    for i in xrange(self.allow_recover):
                        fname = None
                        with queues.fnameLock:
                            if len(queues.fnameQueue) > 1:
                                fname = queues.fnameQueue.popleft()
                        if not fname: break
                        try:
                            rec_file = open(fname, 'rb')
                            recover_list = marshal.load(rec_file)
                        except Exception, ex:
                            logger.error("NfFileReadThread fileread exception: %s \n %s", (repr(ex), traceback.format_exc()))
                        finally:
                            rec_file.close()
                        if recover_list:
                            with queues.dbLock:
                                queues.databaseQueue.extend(recover_list)
                            logger.info("NfFileReadThread read %s packets from file %s", (len(recover_list), fname))             
                
            except Exception, ex:
                logger.error("NfFileReadThread fileread exception: %s \n %s", (repr(ex), traceback.format_exc()))
                 
            time.sleep(240)
                           
    
            
class ServiceThread(Thread):
    '''Thread that forms and renews caches.'''
    
    def __init__(self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        
    def run(self):
        #connection = pool.connection()
        #connection._con._con.set_client_encoding('UTF8')
        global suicideCondition, cacheMaster, flags, queues, vars
        self.connection = get_connection(vars.db_dsn)
        counter = 0; now = datetime.datetime.now
        while True:
            if suicideCondition[self.__class__.__name__]:
                try:    self.connection.close()
                except: pass
                break
            a = time.clock()
            queues.nfFlowCache.reset()
            try: 
                time_run = (now() - cacheMaster.date).seconds > vars.CACHE_TIME
                if flags.cacheFlag or time_run:
                    run_time = time.clock()                    
                    cur = self.connection.cursor()
                    renewCaches(cur, cacheMaster, NfCaches, 11)
                    cur.close()
                    if counter % 5 == 0 or time_run:
                        allowedUsersChecker(allowedUsers, lambda: len(cacheMaster.cache.account_cache.data), ungraceful_save, flags)
                        if not flags.allowedUsersCheck: continue
                        counter = 0
                        #flags.allowedUsersCheck = True
                        flags.writeProf = logger.writeInfoP()
                        if flags.writeProf:
                            #logger.info("len flowCache %s", len(queues.dcache))
                            logger.info("len flowQueue %s", len(queues.flowQueue))
                            logger.info("len dbQueue: %s", len(queues.databaseQueue))
                            logger.info("len fnameQueue: %s", len(queues.databaseQueue.file_queue))
                            logger.info("len nfqueue: %s", len(queues.nfQueue))
                            
                        if not cacheMaster.cache.class_cache.data:
                            logger.warning("NO CLASSES/CLASSNODES FOUND! THE DAEMON IS IDLE!", ())
                            
                        queues.databaseQueue.sui_check()
                    counter += 1
                    if flags.cacheFlag:
                        with flags.cacheLock: flags.cacheFlag = False
                    
                    logger.info("ast time : %s", time.clock() - run_time)
            except Exception, ex:
                logger.error("%s : #30110004 : %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(ex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(20)
    

def ungraceful_save():
    global suicideCondition
    global cacheThr, threads, suicideCondition, vars
    from twisted.internet import reactor
    reactor.callFromThread(reactor.disconnectAll)
    reactor.callFromThread(reactor.stop)
    reactor._started = False
    suicideCondition[cacheThr.tname] = True
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    rempid(vars.piddir, vars.name)
    print "NF: exiting"
    logger.lprint("NF exiting.")
    sys.exit()
    
class RecoveryThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        get_file_names()
    
def get_file_names():
    global vars,queues
    try:
        fllist = glob.glob(''.join((vars.READ_DIR, '/', vars.PREFIX + '*.dmp')))
        if fllist:
            with queues.databaseQueue.file_lock:
                for fl in fllist: queues.databaseQueue.file_queue.appendleft(fl)
    except Exception, ex:
        logger.error("get_files_names exception: %s", (repr(ex),))
        
def get_socket():
    global vars
    nfsock = None
    if vars.SOCK_TYPE   == 0:
        nfsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        nfsock.settimeout(vars.SOCK_TIMEOUT)
    elif vars.SOCK_TYPE == 1:
        nfsock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        nfsock.settimeout(vars.SOCK_TIMEOUT)
    return nfsock

def SIGTERM_handler(signum, frame):
    logger.lprint("SIGTERM recieved")
    graceful_save()

def SIGHUP_handler(signum, frame):
    global config
    logger.lprint("SIGHUP recieved")
    try:
        config.read("ebs_config.ini")
        logger.setNewLevel(int(config.get("nf", "log_level")))
        flags.writeProf = logger.writeInfoP()
    except Exception, ex:
        logger.error("SIGHUP config reread error: %s", repr(ex))
    else:
        logger.lprint("SIGHUP config reread OK")

def SIGUSR1_handler(signum, frame):
    global flags
    logger.lprint("SIGUSR1 recieved")
    with flags.cacheLock: flags.cacheFlag = True
    
def graceful_save():
    global cacheThr, threads, suicideCondition, vars
    from twisted.internet import reactor
    reactor.callFromThread(reactor.disconnectAll)
    reactor.callFromThread(reactor.stop)
    reactor._started = False
    suicideCondition[cacheThr.tname] = True
    for thr in threads:
        suicideCondition[thr.tname] = True
    logger.lprint("About to stop gracefully.")
    time.sleep(8)
    #pool.close()
    #time.sleep(1)
    db_lock = queues.databaseQueue.LOCK
    file_lock = queues.databaseQueue.file_lock
    queues.databaseQueue.LOCK = None
    queues.databaseQueue.file_lock = None
    time.sleep(2)
    db_lock.acquire()
    file_lock.acquire()
    queues.fqueueLock.acquire()
    queues.nfqLock.acquire()
    graceful_saver([['nfFlowCache'], ['flowQueue', 'dcaches'], ['databaseQueue'], ['nfQueue']],
                   queues, vars.PREFIX, vars.SAVE_DIR)
    queues.nfqLock.release()
    queues.fqueueLock.release()
    file_lock.release()
    db_lock.release()
    
    time.sleep(1)
    rempid(vars.piddir, vars.name)
    logger.lprint(vars.name + " stopping gracefully.")
    print vars.name + " stopping gracefully."
        
def graceful_recover():
    global vars, queues
    graceful_loader(['nfFlowCache',['flowQueue', 'dcaches'],'databaseQueue' ,'nfQueue'],
                    queues, vars.PREFIX, vars.SAVE_DIR)
    queues.databaseQueue.post_init('NF_SEND_FSD', vars.DUMP_DIR, vars.PREFIX, vars.FILE_PACK, vars.MAX_SENDBUF_LEN, queues.dbLock, logger)
                
def main ():        
    global flags, queues, cacheMaster, threads, cacheThr, caches
    if vars.RECOVER:
        graceful_recover()
    #recover leftover dumps?
    if vars.RECOVER_DUMP:
        get_file_names()
        '''
        recThr = RecoveryThread()
        recThr.setName('Recovery thread')
        recThr.start()
        time.sleep(0.5)'''
        
    threads = []
    '''thrnames = [(NfFileReadThread, 'NfFileReadThread'), (NfUDPSenderThread, 'NfUDPSenderThread'), \
                (FlowDequeThread, 'NfFlowDequeThread'), (nfDequeThread, 'nfDequeThread')]'''
    
    thrnames = [(FlowDequeThread, 'NfFlowDequeThread'), (nfDequeThread, 'nfDequeThread')]
    for thClass, thName in thrnames:
        threads.append(thClass())
        threads[-1].setName(thName)

    senderThread = SendPacketStream(queues.databaseQueue, queues.dbLock, vars.NFR_DELIMITER)
    senderThread.setName('SenderStream')
    threads.append(senderThread)
    #-----
    cacheThr = ServiceThread()
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.setName('NfCacheThread')
    cacheThr.start()
    
    #sleep until all caches are read
    time.sleep(2)
    while cacheMaster.read is False:        
        if not cacheThr.isAlive:
            print 'Exception in cache thread: exiting'
            sys.exit()
        time.sleep(10)
        if not cacheMaster.read: 
            print 'caches still not read, maybe you should check the log'
      
    print 'caches ready'
    
    if 0: assert isinstance(cacheMaster.cache, NfCaches)  
    for th in threads:
        suicideCondition[th.__class__.__name__] = False
        th.start()
        time.sleep(0.5)
        

    try:
        signal.signal(signal.SIGHUP, SIGHUP_handler)
    except: logger.lprint('NO SIGHUP!')
    try:
        signal.signal(signal.SIGUSR1, SIGUSR1_handler)
    except: logger.lprint('NO SIGUSR1!')
    
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')

    #add "listenunixdatagram!"
    #listenUNIXDatagram(self, address, protocol, maxPacketSize=8192,
    
    
    reactor.listenUDP(vars.PORT, Reception_UDP())
    
    sender_factory = TCPSender_ClientFactory(senderThread)
    if vars.SOCK_TYPE == 0:
        reactor.connectTCP(vars.NFR_HOST, vars.NFR_PORT, sender_factory)
    elif vars.SOCK_TYPE == 1:
        reactor.connectUNIX(vars.NFR_HOST, sender_factory)
    else: 
        raise Exception("Unknown socket type!")
    #
    savepid(vars.piddir, vars.name)
    print "ebs: nf: started"    
    reactor.run(installSignalHandlers=False)


if __name__=='__main__':
    if "-D" in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
        
    flags = NfFlags()
    vars  = NfVars()
    
    cacheMaster = CacheMaster()
    caches = None
    
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")
    
    try:
        import psyco
        psyco.log()
        psyco.full(memory=100)
        psyco.profile(0.05, memory=100)
        psyco.profile(0.2)

        vars.get_vars(config=config, name=NAME, db_name=DB_NAME, net_name=NET_NAME)
        
        
        
        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file) 
        saver.log_adapt = logger.log_adapt
        utilites.log_adapt = logger.log_adapt
        install_logger(logger)
        queues = NfQueues(dcacheNum=vars.CACHE_DICTS)
        queues.databaseQueue.post_init('NF_SEND_FSD', vars.DUMP_DIR, vars.PREFIX, vars.FILE_PACK, vars.MAX_SENDBUF_LEN, queues.dbLock, logger)
        queues.nfFlowCache = FlowCache()
        logger.info("Config variables: %s", repr(vars))
        logger.lprint('Nf start')
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)

        #write profiling info predicate
        flags.writeProf = logger.writeInfoP()

        try:
            tfname = ''.join((vars.DUMP_DIR,'/',vars.PREFIX, str(time.time()), '.dmp'))
            dfile = open(tfname, 'wb')
            dfile.write("testtesttesttesttest")
            dfile.close()
            os.remove(tfname)
        except Exception, ex:
            raise Exception("Dump directory '"+ vars.DUMP_DIR+ "' is not accesible/writable: errors were encountered upun executing test operations with filenames like '" +tfname+ "'!")
    
        suicideCondition = {}    
        vars.FLOW_TYPES = {5 : (header5, flow5)}        

        if not globals().has_key('_1i'):
            _1i = lambda: ''
        allowedUsers = setAllowedUsers(_1i())         
        allowedUsers()
        #-------------------
        print "ebs: nf: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nf, exiting: ', repr(ex)
        logger.error('Exception in nf, exiting: %s \n %s', (repr(ex), traceback.format_exc()))
    
    
    
