#-*-coding=utf-8-*-

from __future__ import with_statement
import site
site.addsitedir('/opt/ebs/venv/lib/python2.6/site-packages')
site.addsitedir('/opt/ebs/venv/lib/python2.7/site-packages')
import sys
sys.path.insert(0, "modules")
sys.path.append("cmodules")
import gc
import copy

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
from IPy import IP, IPint, parseAddress
from collections import deque, defaultdict
from saver import graceful_loader, graceful_saver
import logging
from logging.handlers import TimedRotatingFileHandler, BaseRotatingHandler, _MIDNIGHT


from classes.nf_cache import *
from classes.common.Flow5Data import Flow5Data
from classes.cacheutils import CacheMaster
from classes.flags import NfFlags
from classes.vars import NfFilterVars, NfQueues, install_logger
from utilites import renewCaches, savepid, rempid, get_connection, getpid, check_running, \
                     STATE_NULLIFIED, STATE_OK, NFR_PACKET_HEADER_FMT

#from dirq.QueueSimple import QueueSimple
#from saver import RedisQueue

from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall
from kombu import Connection
from kombu.common import maybe_declare
from kombu.pools import producers

from queues import nf_out, nf_in, task_exchange

MIN_NETFLOW_PACKET_LEN = 16
HEADER_FORMAT = "!HHIIIIBBH"
FLOW_FORMAT   = "!LLLHHIIIIHHBBBBHHBBH"
FLOWCACHE_OVER_TIME  = 10
FLOWCACHE_RESET_TIME = 60

NAME = 'nffilter'
DB_NAME = 'db'
FLOW_NAME = 'flow'
MAX_PACKET_INDEX = 2147483647L

NOT_TRASMITTED = 0
WRITE_OK = 1


class Worker(ConsumerMixin):

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=nf_in,
                         callbacks=[self.process_task])]

    def process_task(self, body, message):
        body = body['data']
        data_bulk = body.split("_|_|_")
        for data in data_bulk:
            try:
                data, addr = data.split("|<>|")
            
                nfPacketHandle(data, addr, queues.nfFlowCache)
            except Exception, ex:
                logger.error("NFF exception: %s \n %s", (repr(ex), traceback.format_exc()))

        message.ack()


def send_as_task(connection, data, routing_key):
    payload = {'data': data}


    with producers[connection].acquire(block=True) as producer:
        maybe_declare(task_exchange, producer.channel)
        producer.publish(payload, serializer='pickle',
                                  compression='bzip2',
                                  exchange=task_exchange, 
                                  routing_key=routing_key)
        
                    
class nfDequeThread(Thread):
    '''Thread that gets packets received by the server from nfQueue queue and puts them onto the conveyour
    that gets flows and caches them.'''
    
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
        
    def run(self):
        
        while True:
            try:
                with Connection(vars.kombu_dsn) as conn:
                    Worker(conn).run()

            except IndexError, err:
                time.sleep(3); continue  
            except Exception, ex:
                logger.error("NFF exception: %s \n %s", (repr(ex), traceback.format_exc()))


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
        #logger.debug("Nas ports cache is empty return", ())
        return None, None, None
    acc_data_src,acc_data_dst = None, None
    for nasitem in nasses:
        #logger.debug("Checking flow port for nas_id=: %s. Nas-Port. In index=%s, out index=%s. cache len=%s", (nasitem.id, flow.in_index,flow.out_index, len(caches.nas_port_cache.by_nas_id)))
        if not acc_data_src:
            acc_data_src = caches.nas_port_cache.by_nas_id.get(nasitem.id,{}).get(flow.in_index,None)
            #logger.debug("Search for flow src port  account=%s", (acc_data_src, ))
            nas_id = nasitem.id
        if not acc_data_dst: 
            acc_data_dst = caches.nas_port_cache.by_nas_id.get(nasitem.id,{}).get(flow.out_index,None)
            #logger.debug("Search for flow dst port account=%s", (acc_data_dst, ))
            nas_id = nasitem.id
        if acc_data_dst and acc_data_src: return caches.account_cache.by_id.get(acc_data_src) if acc_data_src is not None else None,caches.account_cache.by_id.get(acc_data_dst) if acc_data_dst is not None else None, nas_id
    return caches.account_cache.by_id.get(acc_data_src) if acc_data_src is not None else None,caches.account_cache.by_id.get(acc_data_dst) if acc_data_dst is not None else None, nas_id

def find_account_by_ip(nasses,flow,src=False, dst=False):
    acc_data_src,acc_data_dst, nas_id = None, None, None
    caches = cacheMaster.cache
    for nasitem in nasses:

        #logger.debug("Checking flow for nas_id=: %s Account-id", (nasitem.id, ))
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
        if acc_data_dst and acc_data_src:  
            #logger.debug(" Account with nas for flow src(%s) dst(%s) nas_id(%s)", (acc_data_src, acc_data_dst,nas_id,))
            return caches.account_cache.by_id.get(acc_data_src), caches.account_cache.by_id.get(acc_data_dst), nas_id
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
            
    #logger.debug(" Account without nas for flow src(%s) dst(%s) nas_id(%s)", (acc_data_src, acc_data_dst,nas_id,))
    return acc_data_src,acc_data_dst, nas_id


def nfPacketHandle(data, addr, flowCache):
    '''
    Function receiving a binary Netflow packet, sender addr and FlowCache reference.
    Gets, unpacks and checks flows from packets.
    Approved packets are added to FlowCache.
    '''    
    if len(data) < MIN_NETFLOW_PACKET_LEN:
        #raise ValueError, "Short packet"
        logger.warning("Small packet, discarded: %s", repr(addr))
        return
    caches = cacheMaster.cache
    if 0: assert isinstance(caches, NfCaches)
    nasses = caches.nas_cache.by_ip.get(addr, [])
    if not caches: return
    if not nasses: logger.warning("NAS %s not found in our beautiful system. May be it hackers?", repr(addr)); return      
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
        #logger.debug("New flow arrived. src_ip=%s dst_ip=%s in_index=%s, out_index=%s: ", (IPy.intToIp(flow.src_addr, 4),IPy.intToIp(flow.dst_addr, 4), flow.in_index, flow.out_index))
        #look for account for ip address
        if vars.SKIP_INDEX_CHECK==False and (flow.out_index == 0 or flow.in_index == flow.out_index):
            logger.debug("flow int index==flow out index %s==%s or out index==0 rejecting", (flow.in_index,flow.out_index,))
            continue
        acc_data_src = None
        acc_data_dst = None
        nas_id = None
        #nasses_list=[nasitem.id for nasitem in nasses]

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
            pass
            
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

        logger.debug("Account with nas for flow src(%s) dst(%s) default nas(%s)", (acc_data_src, acc_data_dst, nas_id, ))
        #Проверка на IPN сеть
        #=======================================================================
        # if not acc_data_src and caches.account_cache.ipn_range:
        #    for src_ip, src_mask, acc_nas_id, account_data in caches.account_cache.ipn_range:
        #        if (acc_nas_id in nasses_list or acc_nas_id is None) and (flow.src_addr & src_mask) == src_ip:
        #            acc_data_src = account_data
        #            nas_id=acc_nas_id
        #            break
        # if not acc_data_dst and caches.account_cache.ipn_range:
        #    for dst_ip, dst_mask, acc_nas_id, account_data in caches.account_cache.ipn_range:
        #        if (acc_nas_id in nasses_list  or acc_nas_id is None) and (flow.dst_addr & dst_mask) == dst_ip:
        #            acc_data_dst = account_data
        #            nas_id=acc_nas_id
        #            break
        # logger.debug("IPN Account for flow src(%s) dst(%s)", (acc_data_src, acc_data_dst, ))
        #=======================================================================
        local = bool(acc_data_src and acc_data_dst)
        if local:
            logger.debug("Flow is local",())
        acc_acct_tf = (acc_data_src, acc_data_dst) if local else (acc_data_src or acc_data_dst,)
        #print repr(acc_acct_tf)
            
        if acc_acct_tf[0]:            
            flow.nas_id = nas_id
            #acc_id, acctf_id, tf_id = (acc_acct_tf)
            flow.padding = local
            flow.account_id = acc_acct_tf
            flow.node_direction = 'INPUT' if acc_data_dst else 'OUTPUT'
            
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
        """
        Функция добавляет в очередь новый flow и агрегирует пришедшие пакеты
        """
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
    constructs small lists of flows and appends them to 'databaseQueue'.
    В этом трэде присходит классификация трафика и определение прнадлежности к группам.
    Каждому flow применяется дата - 20 секунд от текущего времени - бред...
    '''
    
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
    
    def add_classes_groups(self, flow, classLst, nnode, acctf_id, has_groups, tarifGroups):
        ptime =  time.time()
        if vars.NF_TIME_MOD:
            ptime = ptime - (ptime % vars.NF_TIME_MOD)
        if 0: assert isinstance(flow, Flow5Data); assert isinstance(nnode, ClassData)
        flow.datetime = ptime; flow.class_id = tuple(classLst)
        
        flow.class_passthrough = nnode.passthrough; flow.acctf_id = acctf_id
        flow.groups = None; flow.has_groups = has_groups
        #add groups, check if any
        #print tarifGroups
        if has_groups:
            dr = 0
            if   flow.node_direction == 'INPUT' : dr = 0
            elif flow.node_direction == 'OUTPUT': dr = 1
            groupLst = []
            fcset = set(classLst)
            for tgrp in tarifGroups:
                if 0: assert isinstance(tgrp, GroupsData)
                #print tgrp.direction, dr
                if (not tgrp.trafficclass) or (int(tgrp.direction) != int(dr) and tgrp.direction!=2):
                #if (not tgrp.trafficclass):
                    # Если у группы нет классров или направление группы равно направлению трафика
                    #print "skip", tgrp, dr
                    continue
                group_cls = fcset.intersection(tgrp.trafficclass) # ищем пересечение классов
                if group_cls:
                    group_add = tgrp[:]
                    group_add[1] = tuple(group_cls)
                    groupLst.append(tuple(group_add))
            flow.groups = tuple(groupLst)

    def run(self):
        """
        Что здесь происходит:
        Каждому flow определяется класс, в который он попал
        Каждому flow определяется группа, под которую он попал
        """
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
                                if flow.node_direction == 'INPUT':
                                    
                                    if (flow.src_addr & nnode.dst_mask) != nnode.dst_ip:continue
                                    
                                else:
                                    
                                    if (flow.dst_addr & nnode.dst_mask) != nnode.dst_ip:
                                        continue
                                    if (flow.src_addr & nnode.src_mask) != nnode.src_ip:
                                        continue                                    
                                    
                                if ((flow.protocol != nnode.protocol) and nnode.protocol): continue
                                if ((flow.src_port != nnode.src_port) and nnode.src_port):continue
                                if ((flow.dst_port != nnode.dst_port) and nnode.dst_port):continue
                                if ((flow.in_index != nnode.in_index) and nnode.in_index):continue
                                if ((flow.out_index != nnode.out_index) and nnode.out_index):continue
                                if ((flow.next_hop != nnode.next_hop) and (nnode.next_hop and nnode.next_hop!='0.0.0.0')):continue
                                if ((flow.src_as != nnode.src_as) and nnode.src_as):continue
                                if ((flow.dst_as != nnode.dst_as) and nnode.dst_as):continue
                                
                                if not classLst:
                                    fnode = nnode
                                elif not fnode:
                                    continue
                                classLst.append(nclass)
                                if not nnode.passthrough:
                                    passthr = False
                                break
                            #found passthrough=false
                            if not passthr:

                                self.add_classes_groups(flow, classLst, fnode, acc.acctf_id, has_groups, tarifGroups)
                                if nnode.store==True:
                                    nfwrite_list.append(flow)
                                break                   
                        #traversed all the nodes
                        else:
                            if classLst:
                                self.add_classes_groups(flow, classLst, fnode, acc.acctf_id, has_groups, tarifGroups)
                                if nnode.store==True:
                                    nfwrite_list.append(flow)
                            else: 
                                if nnode.store==True:
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
            
            
class NfroutinePushThread(Thread):
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
                    self.connection.close()
                    break
                #get a bunch of packets
                flst = None

                with queues.dbLock:
                    if len(queues.databaseQueue) > 0:
                        flst = queues.databaseQueue.popleft()
                if not flst: time.sleep(5); continue
                

                send_as_task(out_connection, flst, 'nf_out')
                    
            except Exception, ex:
                logger.debug('%s exp: %s \n %s', (self.getName(), repr(ex), traceback.format_exc()))
                try:

                    with queues.dbLock:
                        queues.databaseQueue.appendleft(flst)
                except:
                    logger.warning("%s: Packet dropped!", self.getName())

            
class ServiceThread(Thread):
    '''Thread that forms and renews caches.'''
    
    def __init__(self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        
    def run(self):
        #connection = pool.connection()
        #connection._con._con.set_client_encoding('UTF8')
        global suicideCondition, cacheMaster, flags, queues, vars, in_dirq, out_dirq
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

    suicideCondition[cacheThr.tname] = True
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    rempid(vars.piddir, vars.name)
    print "NF: exiting"
    logger.lprint("NF exiting.")
    sys.exit()
    

class MyTimedRotatingFileHandler(BaseRotatingHandler):
    """
    Handler for logging to a file, rotating the log file at certain timed
    intervals.

    If backupCount is > 0, when rollover is done, no more than backupCount
    files are kept - the oldest ones are deleted.
    """
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None):
        global vars
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
        folder = os.path.abspath(os.path.join(vars.FLOW_DIR,time.strftime('%Y-%m-%d', timeTuple)))
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        open_fname = os.path.join(folder, filename + "." + time.strftime(self.suffix, timeTuple))      
           
        BaseRotatingHandler.__init__(self, open_fname, 'a', encoding)

        self.baseFilename = os.path.abspath(open_fname)
        



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
            flHdlr = fHandler(fVars.FLOW_PREFIX, when = fVars.FLOW_WHEN, interval = fVars.FLOW_INTERVAL)
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
                    
            
class Watcher:
    """this class solves two problems with multithreaded
    programs in Python, (1) a signal might be delivered
    to any thread (which is just a malfeature) and (2) if
    the thread that gets the signal is waiting, the signal
    is ignored (which is a bug).

    The watcher is a concurrent process (not thread) that
    waits for a signal and the process that contains the
    threads.  See Appendix A of The Little Book of Semaphores.
    http://greenteapress.com/semaphores/

    I have only tested this on Linux.  I would expect it to
    work on the Macintosh and not work on Windows.
    """
    
    def __init__(self):
        """ Creates a child thread, which returns.  The parent
            thread waits for a KeyboardInterrupt and then kills
            the child thread.
        """
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            # I put the capital B in KeyBoardInterrupt so I can
            # tell when the Watcher gets the SIGINT
            print 'KeyBoardInterrupt'
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError: pass
        
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

def SIGINT_handler(signum, frame):
    logger.lprint("SIGINT recieved")
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

    suicideCondition[cacheThr.tname] = True
    for thr in threads:
        suicideCondition[thr.tname] = True

    logger.lprint("About to stop gracefully.")
    #pool.close()
    #time.sleep(1)

    db_lock = queues.databaseQueue.LOCK
    file_lock = queues.databaseQueue.file_lock
    queues.databaseQueue.LOCK = None
    queues.databaseQueue.file_lock = None
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
    

    rempid(vars.piddir, vars.name)
    logger.lprint(vars.name + " stopping gracefully.")
    print vars.name + " stopping gracefully."
    sys.exit()
        
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
    global flags, queues, cacheMaster, threads, cacheThr, caches, script
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
    '''thrnames = [ (NfroutinePushThread, 'NfroutinePushThread'), \
                (FlowDequeThread, 'NfFlowDequeThread'), (nfDequeThread, 'nfDequeThread')]'''
    
    thrnames = [(FlowDequeThread, 'NfFlowDequeThread'), (nfDequeThread, 'nfDequeThread'), ]
    for thClass, thName in thrnames:
        threads.append(thClass())
        threads[-1].setName(thName)

    senderThread = NfroutinePushThread()
    senderThread.setName('NfroutinePushThread')
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
      
    #print 'caches ready'
    
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

    try:
        signal.signal(signal.SIGINT, SIGINT_handler)
    except:
        print "nosigint" 
        logger.lprint('NO SIGINT!')
    
    #add "listenunixdatagram!"
    #listenUNIXDatagram(self, address, protocol, maxPacketSize=8192,
    
    

    
    #
    savepid(vars.piddir, vars.name)
    print "ebs: nffilter: started"    
    

    
    


if __name__=='__main__':
        
    flags = NfFlags()
    vars  = NfFilterVars()
    
    cacheMaster = CacheMaster()
    caches = None
    
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")
    Watcher()
    try:
        
        import psyco
        psyco.full(memory=100)
        psyco.profile(0.05, memory=100)
        psyco.profile(0.2)
    except:
        print "Can`t optimize"
        
    try:
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME, flow_name=FLOW_NAME)
        #print repr(vars)
        #in_dirq = QueueSimple(vars.QUEUE_IN)
        #in_dirq = RedisQueue("in_queue", host=vars.REDIS_HOST, port=vars.REDIS_PORT, db=vars.REDIS_DB)
        
        #out_dirq = RedisQueue("out_queue", host=vars.REDIS_HOST, port=vars.REDIS_PORT, db=vars.REDIS_DB)
        #out_dirq = QueueSimple(vars.QUEUE_OUT)
        
        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file) 
        saver.log_adapt = logger.log_adapt
        utilites.log_adapt = logger.log_adapt
        install_logger(logger)
        queues = NfQueues(dcacheNum=vars.CACHE_DICTS)
        queues.databaseQueue.post_init('NF_SEND_FSD', vars.DUMP_DIR, vars.PREFIX, vars.FILE_PACK, vars.MAX_SENDBUF_LEN, queues.dbLock, logger)
        queues.nfFlowCache = FlowCache()
        queues.flowSynchroBox = SynchroPacket(vars.FLOW_COUNT, vars.FLOW_TIME)
        logger.info("Config variables: %s", repr(vars))
        logger.lprint('Nf Filter start')
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)
        
        out_connection = Connection(vars.kombu_dsn)
        
        
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


        #-------------------
        print "ebs: nffilter: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nffilter, exiting: ', repr(ex)
        print "Exception in nffilter, exiting: %s \n %s'" % (repr(ex), traceback.format_exc())
    
    
    
