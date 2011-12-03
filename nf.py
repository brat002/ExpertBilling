#-*-coding=utf-8-*-

from __future__ import with_statement

import gc
import copy
import glob
import random
import signal
import os, sys
import marshal
import utilites

import psycopg2
import threading
import traceback
import ConfigParser
import socket, select, struct, datetime, time
import string, glob, types

try:
    import codecs
except ImportError:
    codecs = None

import isdlogger
import saver
import IPy

from threading import Thread, Lock, Event
from daemonize import daemonize
from IPy import IP, IPint, parseAddress
from collections import deque, defaultdict
from saver import graceful_loader, graceful_saver, allowedUsersChecker, setAllowedUsers
import logging
from logging.handlers import TimedRotatingFileHandler, BaseRotatingHandler, _MIDNIGHT

import twisted.internet

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
FLOW_NAME = 'flow'
MAX_PACKET_INDEX = 2147483647L

NOT_TRASMITTED = 0
WRITE_OK = 1

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
        self.consumer = None
        
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
            if self.PAUSED or not self.consumer:
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
        logger.info('SENDER: Connection failed. Reason: %s', reason)
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

def find_account_by_port(nasses,flow):
    #global caches
    caches = cacheMaster.cache
    if not caches.nas_port_cache.by_nas_id: 
        logger.debug("Nas ports cache is empty return", ())
        return None, None, None
    acc_data_src,acc_data_dst = None, None
    for nasitem in nasses:
        logger.debug("Checking flow port for nas_id=: %s. Nas-Port. In index=%s, out index=%s. cache len=%s", (nasitem.id, flow.in_index,flow.out_index, len(caches.nas_port_cache.by_nas_id)))
        if not acc_data_src:
            acc_data_src = caches.nas_port_cache.by_nas_id.get(nasitem.id,{}).get(flow.in_index,None)
            logger.debug("Search for flow src port  account=%s", (acc_data_src, ))
            nas_id = nasitem.id
        if not acc_data_dst: 
            acc_data_dst = caches.nas_port_cache.by_nas_id.get(nasitem.id,{}).get(flow.out_index,None)
            logger.debug("Search for flow dst port account=%s", (acc_data_dst, ))
            nas_id = nasitem.id
        if acc_data_dst and acc_data_src: return caches.account_cache.by_id.get(acc_data_src) if acc_data_src is not None else None,caches.account_cache.by_id.get(acc_data_dst) if acc_data_dst is not None else None, nas_id
    return caches.account_cache.by_id.get(acc_data_src) if acc_data_src is not None else None,caches.account_cache.by_id.get(acc_data_dst) if acc_data_dst is not None else None, nas_id

def find_account_by_ip(nasses,flow,src=False, dst=False):
    acc_data_src,acc_data_dst, nas_id = None, None, None
    caches = cacheMaster.cache
    for nasitem in nasses:

        logger.debug("Checking flow for nas_id=: %s Account-id", (nasitem.id, ))
        if src:
            if not acc_data_src:
                #Если нашли - больше не проверяем
                acc_data_src = caches.account_cache.vpn_ips.get((flow.src_addr, nasitem.id))
                if acc_data_src:
                    nas_id = nasitem.id
        if dst:
            if not acc_data_dst:
                #Если нашли - больше не проверяем
                acc_data_dst = caches.account_cache.vpn_ips.get((flow.dst_addr, nasitem.id))
                if acc_data_dst:
                    nas_id = nasitem.id
        if acc_data_dst and acc_data_src:  return caches.account_cache.by_id.get(acc_data_src), caches.account_cache.by_id.get(acc_data_dst), nas_id
    if src:
        if not acc_data_src:
            #Если не нашли аккаунта с привязкой к серверу доступа - выбираем без сервера
            acc_data_src = caches.account_cache.vpn_ips.get((flow.src_addr, None))
            if nasses:
                nas_id = nasses[0].id
            else:
                nas_id = None
    if dst:
        if not acc_data_dst:
            #Если не нашли аккаунта с привязкой к серверу доступа - выбираем без сервера
            acc_data_dst = caches.account_cache.vpn_ips.get((flow.dst_addr, None))
            if nasses:
                nas_id = nasses[0].id
            else:
                nas_id = None
            
    logger.debug("VPN Account without nas for flow src(%s) dst(%s) nas_id(%s)", (acc_data_src, acc_data_dst,nas_id,))
    return acc_data_src,acc_data_dst, nas_id


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
    nasses = caches.nas_cache.by_ip.get(addrport[0], [])
    if not caches: return
    if not nasses: logger.warning("NAS %s not found in our beautiful system. Mybe it hackers?", repr(addrport)); return      
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
        logger.debug("New flow arrived. src_ip=%s dst_ip=%s in_index=%s, out_index=%s: ", (IPy.intToIp(flow.src_addr, 4),IPy.intToIp(flow.dst_addr, 4), flow.in_index, flow.out_index))
        #look for account for ip address
        if vars.SKIP_INDEX_CHECK==False and (flow.out_index == 0 or flow.in_index == flow.out_index):
            logger.debug("flow int index==flow out index %s==%s or out index==0 rejecting", (flow.in_index,flow.out_index,))
            continue
        acc_data_src = None
        acc_data_dst = None
        nas_id = None
        nasses_list=[nasitem.id for nasitem in nasses]

        acc_data_src,acc_data_dst, nas_id = find_account_by_port(nasses, flow)
        acc_data_src_ip, acc_data_dst_ip, nas_id_ip=None,None,None
        
        if acc_data_src:
            src=False
        else:
            src=True
        
        if acc_data_dst:
            dst=False
        else:
            dst=True

            
        if not (acc_data_src and acc_data_dst):
            acc_data_src_ip,acc_data_dst_ip, nas_id_ip = find_account_by_ip(nasses, flow, src, dst)
            
        if  acc_data_src:
            acc_data_src=acc_data_src
        else:
            acc_data_src=acc_data_src_ip
            
        if  acc_data_dst:
            acc_data_dst=acc_data_dst
        else:
            acc_data_dst=acc_data_dst_ip
        
        if  nas_id:
            nas_id=nas_id
        else:
            nas_id=nas_id_ip

        logger.debug("VPN Account with nas for flow src(%s) dst(%s) default nas(%s)", (acc_data_src, acc_data_dst, nas_id, ))
        #Проверка на IPN сеть
        if not acc_data_src and caches.account_cache.ipn_range:
            for src_ip, src_mask, acc_nas_id, account_data in caches.account_cache.ipn_range:
                if (acc_nas_id in nasses_list or acc_nas_id is None) and (flow.src_addr & src_mask) == src_ip:
                    acc_data_src = account_data
                    nas_id=acc_nas_id
                    break
        if not acc_data_dst and caches.account_cache.ipn_range:
            for dst_ip, dst_mask, acc_nas_id, account_data in caches.account_cache.ipn_range:
                if (acc_nas_id in nasses_list  or acc_nas_id is None) and (flow.dst_addr & dst_mask) == dst_ip:
                    acc_data_dst = account_data
                    nas_id=acc_nas_id
                    break
        logger.debug("IPN Account for flow src(%s) dst(%s)", (acc_data_src, acc_data_dst, ))
        local = bool(acc_data_src and acc_data_dst)
        if local:
            logger.debug("Flow is local",())
        acc_acct_tf = (acc_data_src, acc_data_dst) if local else (acc_data_src or acc_data_dst,)
        #print repr(acc_acct_tf)
            
        if acc_acct_tf[0]:            
            flow.nas_id = nas_id
            #acc_id, acctf_id, tf_id = (acc_acct_tf)
            flow.padding = local
#            if vars.WRITE_FLOW:
#                flow.datetime = time.time()
#                ips = map(lambda ip: IPy.intToIp(ip, 4), flow.getAddrSlice())
#                for acc_flow in acc_acct_tf:
#                    flow.account_id = acc_flow[0]
#                    queues.flowSynchroBox.appendData(ips + flow.getBaseSlice())
#                queues.flowSynchroBox.checkData()
            flow.account_id = acc_acct_tf
            flow.node_direction = None
            if vars.CHECK_CLASSES:
                break_outer = False
                for nclass, nnodes in caches.class_cache.classes:                        
                    for nnode in nnodes:
                        if 0: assert isinstance(nnode,ClassData)
                        if (flow.src_addr & nnode.src_mask) != nnode.src_ip:continue
                        if (flow.dst_addr & nnode.dst_mask) != nnode.dst_ip:continue
                        if ((flow.protocol != nnode.protocol) and nnode.protocol): continue
                        if ((flow.src_port != nnode.src_port) and nnode.src_port):continue
                        if ((flow.dst_port != nnode.dst_port) and nnode.dst_port):continue
                        if ((flow.in_index != nnode.in_index) and nnode.in_index):continue
                        if ((flow.out_index != nnode.out_index) and nnode.out_index):continue
                        if ((flow.next_hop != nnode.next_hop) and (nnode.next_hop and nnode.next_hop!='0.0.0.0')):continue
                        if ((flow.src_as != nnode.src_as) and nnode.src_as):continue
                        if ((flow.dst_as != nnode.dst_as) and nnode.dst_as):continue
                                                    
                         #======================================================
                         # if (((flow.src_addr & nnode.src_mask) == nnode.src_ip) and \
                         #   ((flow.dst_addr & nnode.dst_mask) == nnode.dst_ip) and \
                         #   ((flow.next_hop == nnode.next_hop) or (not nnode.next_hop)) and \
                         #   ((flow.src_port == nnode.src_port) or (not nnode.src_port)) and \
                         #   ((flow.dst_port == nnode.dst_port) or (not nnode.dst_port)) and \
                         #   ((flow.in_index == nnode.in_index) or (not nnode.in_index)) and \
                         #   ((flow.out_index == nnode.out_index) or (not nnode.out_index)) and \
                         #   ((flow.src_as == nnode.src_as) or (not nnode.src_as)) and \
                         #   ((flow.dst_as == nnode.dst_as) or (not nnode.dst_as)) and \
                         #   ((flow.protocol == nnode.protocol) or (not nnode.protocol))):
                         #======================================================
                            
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
                nfwrite_list=[]
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
                                if (flow.src_addr & nnode.src_mask) != nnode.src_ip:continue
                                if (flow.dst_addr & nnode.dst_mask) != nnode.dst_ip:continue
                                if ((flow.protocol != nnode.protocol) and nnode.protocol): continue
                                if ((flow.src_port != nnode.src_port) and nnode.src_port):continue
                                if ((flow.dst_port != nnode.dst_port) and nnode.dst_port):continue
                                if ((flow.in_index != nnode.in_index) and nnode.in_index):continue
                                if ((flow.out_index != nnode.out_index) and nnode.out_index):continue
                                if ((flow.next_hop != nnode.next_hop) and (nnode.next_hop and nnode.next_hop!='0.0.0.0')):continue
                                if ((flow.src_as != nnode.src_as) and nnode.src_as):continue
                                if ((flow.dst_as != nnode.dst_as) and nnode.dst_as):continue
                                    
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
                                nfwrite_list.append(flow)
                                break                   
                        #traversed all the nodes
                        else:
                            if classLst:
                                self.add_classes_groups(flow, classLst, fnode, acc.acctf_id, has_groups, tarifGroups)
                                nfwrite_list.append(flow)
                            else: 
                                nfwrite_list.append(flow)
                                continue
                            
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
                if vars.WRITE_FLOW:
                    for flow in nfwrite_list:
                        ips = map(lambda ip: IPy.intToIp(ip, 4), flow.getAddrSlice())
                        queues.flowSynchroBox.appendData(ips + flow.getBaseSlice())
                    queues.flowSynchroBox.checkData()
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
                           
                        #print repr(cacheMaster.cache)
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
    

class MyTimedRotatingFileHandler(BaseRotatingHandler):
    """
    Handler for logging to a file, rotating the log file at certain timed
    intervals.

    If backupCount is > 0, when rollover is done, no more than backupCount
    files are kept - the oldest ones are deleted.
    """
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None):
        self.when = string.upper(when)
        self.backupCount = backupCount
        
        currentTime = int(time.time())
        if self.when == 'S':
            self.interval = 1 # one second
            self.suffix = "%Y-%m-%d_%H-%M-%S"
        elif self.when == 'M':
            self.interval = 60 # one minute
            self.suffix = "%Y-%m-%d_%H-%M"
        elif self.when == 'H':
            self.interval = 60 * 60 # one hour
            self.suffix = "%Y-%m-%d_%H"
        elif self.when == 'D' or self.when == 'MIDNIGHT':
            self.interval = 60 * 60 * 24 # one day
            self.suffix = "%Y-%m-%d"
        elif self.when.startswith('W'):
            self.interval = 60 * 60 * 24 * 7 # one week
            if len(self.when) != 2:
                raise ValueError("You must specify a day for weekly rollover from 0 to 6 (0 is Monday): %s" % self.when)
            if self.when[1] < '0' or self.when[1] > '6':
                raise ValueError("Invalid day specified for weekly rollover: %s" % self.when)
            self.dayOfWeek = int(self.when[1])
            self.suffix = "%Y-%m-%d"
        else:
            raise ValueError("Invalid rollover interval specified: %s" % self.when)

        self.interval = self.interval * interval # multiply by units requested
        self.rolloverAt = currentTime - (currentTime % self.interval) + self.interval
        if self.when == 'MIDNIGHT' or self.when.startswith('W'):
            # This could be done with less code, but I wanted it to be clear
            t = time.localtime(currentTime)
            currentHour = t[3]
            currentMinute = t[4]
            currentSecond = t[5]
            # r is the number of seconds left between now and midnight
            r = _MIDNIGHT - ((currentHour * 60 + currentMinute) * 60 +
                    currentSecond)
            self.rolloverAt = currentTime + r
            if when.startswith('W'):
                day = t[6] # 0 is Monday
                if day != self.dayOfWeek:
                    if day < self.dayOfWeek:
                        daysToWait = self.dayOfWeek - day
                    else:
                        daysToWait = 6 - day + self.dayOfWeek + 1
                    self.rolloverAt = self.rolloverAt + (daysToWait * (60 * 60 * 24))
        t = self.rolloverAt - self.interval
        timeTuple = time.localtime(t)
        open_fname = filename + "." + time.strftime(self.suffix, timeTuple)         
        BaseRotatingHandler.__init__(self, open_fname, 'a', encoding)
        self.baseFilename = os.path.abspath(filename)
        



        #print "Will rollover at %d, %d seconds from now" % (self.rolloverAt, self.rolloverAt - currentTime)

    def shouldRollover(self, record):
        """
        Determine if rollover should occur

        record is not used, as we are just comparing times, but it is needed so
        the method siguratures are the same
        """
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        #print "No need to rollover: %d, %d" % (t, self.rolloverAt)
        return 0

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        self.stream.close()
        # get the time that this sequence started at and make it a TimeTuple
        '''
        t = self.rolloverAt - self.interval
        timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)
        '''
        t = self.rolloverAt
        timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if self.backupCount > 0:
            # find the oldest log file and delete it
            s = glob.glob(self.baseFilename + ".20*")
            if len(s) > self.backupCount:
                s.sort()
                os.remove(s[0])
        #print "%s -> %s" % (self.baseFilename, dfn)
        if self.encoding:
            self.stream = codecs.open(dfn, 'a', self.encoding)
        else:
            self.stream = open(dfn, 'a')
        self.rolloverAt = self.rolloverAt + self.interval



class SynchroPacket(object):
    __slots__ = ('getDataPLZ', 'gotDataKTX', 'dataList', 'maxCount', 'maxTimeout',\
                  'dataCount', 'dataTime', 'SYNCHRO')
    
    def __init__(self, count = 1, timeout = 5):
        self.getDataPLZ = Event()
        self.gotDataKTX = Event()
        self.dataList = []
        self.maxCount = count
        self.maxTimeout = timeout
        self.dataCount = 0
        self.dataTime = 0
        self.SYNCHRO = True if self.dataCount == 1 else False
            
    def checkData(self):
        if (self.dataCount >= self.maxCount or (time.clock() - self.dataTime) > self.maxTimeout)\
          and not self.isDataEmpty() and self.gotDataKTX.isSet() == False:
            self.getDataPLZ.set()
            
    def isDataEmpty(self):
        return not bool(self.dataList)
    
    def waitForData(self):
        self.gotDataKTX.clear()
        #maybe timeout here?
        self.getDataPLZ.wait()
        #sys.setcheckinterval(0)
        data = self.dataList if not self.SYNCHRO else self.dataList[0]
        self.dataList = []
        self.dataTime = time.clock()
        self.getDataPLZ.clear()
        self.gotDataKTX.set()
        #sys.setcheckinterval(1000)
        return data
        
        
    def appendData(self, data):
        self.dataList.append(data)
        self.dataCount += 1
        if self.SYNCHRO:
            self.getDataPLZ.set()
            self.gotDataKTX.wait()

def simpleCSV(csvList):
    return ','.join([str(csvV) for csvV in csvList])

class FlowLoggerThread(Thread):
    def __init__(self, errorLogger, synchroBox, dieCondition, dataTransformer, fHandler, fVars):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        #create notifier
        self.synchroBox = synchroBox
        self.dieCondition = dieCondition
        self.errorLogger = errorLogger
        self.dataTranformer = dataTransformer
        self.fVars = fVars
        try:
            self.fileLogger = logging.getLogger('filelogger')
            self.fileLogger.setLevel(logging.DEBUG)
            #flHdlr = TimedRotatingFileHandler('/'.join((fVars.FLOW_DIR, fVars.FLOW_PREFIX)), when = fVars.FLOW_WHEN, interval = fVars.FLOW_INTERVAL)
            #currentTime = int(time.time())
            #flHdlr.rolloverAt = currentTime - (currentTime % flHdlr.interval) + flHdlr.interval
            flHdlr = fHandler('/'.join((fVars.FLOW_DIR, fVars.FLOW_PREFIX)), when = fVars.FLOW_WHEN, interval = fVars.FLOW_INTERVAL)
            flHdlr.setFormatter(logging.Formatter("%(message)s"))
            self.fileLogger.addHandler(flHdlr)
        except Exception, ex:
            self.errorLogger.error("Flowlogger creation exception: %s %s | %s", (self.getName(), repr(ex), traceback.format_exc()))
            print "Flowlogger creation exception: flow logging didn't start. See log."
            self.notifyError("Flowlogger creation exception: %s %s | %s" % (self.getName(), repr(ex), traceback.format_exc()))
    
    def notifyError(self, error):
        #maybe e-mail?
        pass
    
    def heuristics(self):
        pass
    
    def statistics(self):
        pass
    
    def run(self):
        #base on events
        while True:
            if self.dieCondition[self.__class__.__name__]:
                try:
                    for handler in self.fileLogger.handlers:
                        handler.flush()
                        handler.close()
                    self.errorLogger.info('Flowlogger terminated without errors.', ())
                except Exception, ex:
                    self.errorLogger.error("Flowlogger close exception: %s %s | %s", (self.getName(), repr(ex), traceback.format_exc()))
                break
            
            data = self.synchroBox.waitForData()
            try:
                for dataPiece in data:
                    dataString = self.dataTranformer(dataPiece)
                    self.fileLogger.log(logging.INFO, dataString)
                #heuristics
                #statistics
                for handler in self.fileLogger.handlers:
                    handler.flush()
            except Exception, ex:
                #write exception
                self.errorLogger.error("Flowlogger write exception: %s %s | %s", (self.getName(), repr(ex), traceback.format_exc()))
                #heuristics
                if self.fVars.FLOW_MAIL_WARNING:
                    self.notifyError(ex)
                    
            
    
def get_file_names():
    global vars,queues
    try:
        fllist = glob.glob(''.join((vars.READ_DIR, '/', vars.PREFIX + '*.dmp')))
        if fllist:
            with queues.databaseQueue.file_lock:
                queues.databaseQueue.file_queue.clear()
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
    file_lock.acquire()
    queues.databaseQueue.file_queue = deque()
    file_lock.release()
    db_lock.acquire()
    queues.fqueueLock.acquire()
    queues.nfqLock.acquire()
    graceful_saver([['nfFlowCache'], ['flowQueue', 'dcaches'], ['databaseQueue'], ['nfQueue']],
                   queues, vars.PREFIX, vars.SAVE_DIR)
    queues.nfqLock.release()
    queues.fqueueLock.release()

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
 
def file_test(ddir, prefix=''):
    try:
        tfname = ''.join((ddir,'/',prefix, str(time.time()), '.dmp'))
        dfile = open(tfname, 'wb')
        dfile.write("testtesttesttesttest")
        dfile.close()
        os.remove(tfname)
    except Exception, ex:
        raise Exception("Dump directory '"+ddir+ 
                        "' is not accesible/writable: errors were encountered upon"+\
                        "executing test operations with filenames like '" +tfname+ "'!")
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
    
    thrnames = [(FlowDequeThread, 'NfFlowDequeThread'), (nfDequeThread, 'nfDequeThread'), (nfDequeThread, 'nfDequeThread')]
    for thClass, thName in thrnames:
        threads.append(thClass())
        threads[-1].setName(thName)

    senderThread = SendPacketStream(queues.databaseQueue, queues.dbLock, vars.NFR_DELIMITER)
    senderThread.setName('SenderStream')
    threads.append(senderThread)
    
    if vars.WRITE_FLOW:
        flowWriterThr = FlowLoggerThread(logger, queues.flowSynchroBox, suicideCondition, simpleCSV, MyTimedRotatingFileHandler, vars)
        flowWriterThr.setName('FlowWriter')
        threads.append(flowWriterThr)
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
        psyco.full(memory=100)
        psyco.profile(0.05, memory=100)
        psyco.profile(0.2)

        vars.get_vars(config=config, name=NAME, db_name=DB_NAME, net_name=NET_NAME, flow_name=FLOW_NAME)
        #print repr(vars)
        
        
        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file) 
        saver.log_adapt = logger.log_adapt
        utilites.log_adapt = logger.log_adapt
        install_logger(logger)
        queues = NfQueues(dcacheNum=vars.CACHE_DICTS)
        queues.databaseQueue.post_init('NF_SEND_FSD', vars.DUMP_DIR, vars.PREFIX, vars.FILE_PACK, vars.MAX_SENDBUF_LEN, queues.dbLock, logger)
        queues.nfFlowCache = FlowCache()
        queues.flowSynchroBox = SynchroPacket(vars.FLOW_COUNT, vars.FLOW_TIME)
        logger.info("Config variables: %s", repr(vars))
        logger.lprint('Nf start')
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)

        #write profiling info predicate
        flags.writeProf = logger.writeInfoP()
        file_test(vars.DUMP_DIR, vars.PREFIX)
        if vars.WRITE_FLOW:
            try:
                os.mkdir(vars.FILE_DIR)
            except: pass
            file_test(vars.FLOW_DIR)
            
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
    
    
    