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



import traceback
import ConfigParser
import socket, struct, datetime, time
import  glob

import IPy

import msgpack


import isdlogger
import saver


from threading import Thread, Lock
from IPy import IP, IPint
from collections import deque
from saver import graceful_loader, graceful_saver
import logging



from classes.nf_cache import *
from classes.common.Flow5Data import Flow5Data
from classes.cacheutils import CacheMaster
from classes.flags import NfFlags
from classes.vars import NfFilterVars, NfQueues, install_logger
from utilites import renewCaches, savepid, rempid, get_connection,  \
                     STATE_NULLIFIED, NFR_PACKET_HEADER_FMT



#from dirq.QueueSimple import QueueSimple
#from saver import RedisQueue

from kombu.mixins import ConsumerMixin
from kombu import Connection
from kombu.common import maybe_declare
from kombu.pools import producers

from queues import  nf_in, task_exchange

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
                         callbacks=[self.on_message], accept=['msgpack'])]

    def on_message(self, body, message):
        #print body
        while queues.flowQueueSize >15000:
            time.sleep(1)
            
        #body = body['data']
        
        """
            Src_addr uint32
            Dst_addr uint32
            Nexthop uint32
            Snmp_in uint16
            Snmp_out uint16
            Packets_count uint32
            Bytes uint32
            Sysuptime uint32
            LastUptime uint32
            SrcPort uint16
            DstPort uint16
            A    uint8
            Tcpflags int8
            Protocol uint8
            Tos uint8
            SrcAs    uint16
            DstAs    uint16
            SrcMask    uint8
            DstMask    uint8
            B    int16
        """
        for item in body:
            try:
                flow = item.get('Flow')
                f = Flow5Data(
                    empty=False,
                    src_addr = flow.get('Src_addr'),
                    dst_addr = flow.get('Dst_addr'),
                    next_hop = flow.get('Nexthop'),
                    in_index = flow.get('Snmp_in'),
                    out_index = flow.get('Snmp_out'),
                    packets = flow.get('Packets_count'),
                    octets = flow.get('Bytes'),
                    start = flow.get('Sysuptime'),
                    finish = flow.get('LastUptime'),
                    src_port = flow.get('SrcPort'),
                    dst_port = flow.get('DstPort'),
                    nas_id = item.get('Nas_id'),
                    tcp_flags = flow.get('Tcpflags'),
                    protocol = flow.get('Protocol'),
                    tos = flow.get('Tos'),
                    src_as = flow.get('SrcAs'),
                    dst_as = flow.get('DstAs'),
                    src_netmask_length = flow.get('SrcMask'),
                    dst_netmask_length = flow.get('DstMask'),
                    account_id = item.get('Account').get('Account_id'),
                    node_direction = 'INPUT' if item.get('Direction')==0 else 'OUTPUT',
                    acctf_id = item.get('Account').get('AccountTarif_id'),
                    tariff_id = item.get('Account').get('Tarif_id')
                    )
                #print f
                queues.nfFlowCache.addflow5(f)
                #nfPacketHandle(data, addr, queues.nfFlowCache)
            except Exception, ex:
                logger.error("NFF exception: %s \n %s", (repr(ex), traceback.format_exc()))

        message.ack()


def send_as_task(connection, data, routing_key):
    payload = {'data': data}


    with producers[connection].acquire(block=True) as producer:
        maybe_declare(task_exchange, producer.channel)
        producer.publish(payload, serializer='pickle',
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
                queues.flowQueueSize +=1
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
                    queues.flowQueueSize+=1
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
    
    
    def add_classes_groups(self, flow, class_id, nnode, acctf_id, has_groups, tarifGroups):
        ptime =  time.time()
        if vars.NF_TIME_MOD:
            ptime = ptime - (ptime % vars.NF_TIME_MOD)

        flow.datetime = ptime; flow.class_id = tuple([class_id,])
        
        flow.acctf_id = acctf_id
        flow.groups = None; flow.has_groups = has_groups
        #add groups, check if any
        #print tarifGroups
        
        if has_groups:
            dr = 0
            if   flow.node_direction == 'INPUT' : dr = 0
            elif flow.node_direction == 'OUTPUT': dr = 1
            groupLst = []
            #fcset = set(classLst)
            for tgrp in tarifGroups:

                #print 'tgrp.direction, dr', tgrp.direction, dr
                if (not tgrp.trafficclass) or (int(tgrp.direction) != int(dr) and tgrp.direction!=2):
                #if (not tgrp.trafficclass):
                    # Если у группы нет классров или направление группы равно направлению трафика
                    #print "skip", tgrp, dr
                    continue
                group_cls = set([class_id,]).intersection(tgrp.trafficclass) # ищем пересечение классов
                #print 'group_cls', group_cls
                if group_cls:
                    group_add = tgrp[:]
                    group_add[1] = tuple(group_cls)
                    groupLst.append(tuple(group_add))
                    #print 'group_add', group_add
            #print 'groupLst', groupLst
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
                    queues.flowQueueSize-=1
                except Exception, ex:
                    #logger.debug("fdqThread indexerror exception: %s", repr(ex))
                    pass
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
                    #print key
                    #with dhlock:
                    qflow = dhcache.pop(key, None)
                    if not qflow: 
                        #print 'not', qflow
                        continue
                    #get id's
                    acc = qflow.account_id
                    qflow.account_id = None
                    local = qflow.padding
                    src = True
                    if not acc : 
                        #print 'not acc', qflow
                        continue
                    flow = qflow
                    if 0: assert isinstance(flow, Flow5Data)
                    #flow.account_id = acc.account_id
                    #flow.acctf_id = acc.accounttarif_id
                    #get groups for tarif
                    tarifGroups = cacheMaster.cache.tfgroup_cache.by_tarif.get(flow.tariff_id)
                    has_groups = True if tarifGroups else False
                    #direction = flow.node_direction
                    passthr = True
                    #checks classes                    
                    fnode = None; classLst = []                    
                    #Direction is taken from the first approved node
                    
                    nodes = cacheMaster.cache.class_cache.nodes
                    #print IPy.IPint(flow.src_addr) 
                    #print IPy.IPint(flow.dst_addr)
                    #for n in nodes:
                    #    if n[7]==0: 
                    #        print 'n7=0'
                    if flow.node_direction == 'INPUT':
                       
                        nodes = nodes[(((flow.src_addr & nodes[:,5])==nodes[:,4]) & 
                                       ((flow.dst_addr & nodes[:,3])==nodes[:,2])  &
                                       #(nodes[:,13]==0 | (nodes[:,13]==flow.protocol))
                                       #(nodes[:,7]==0 | (nodes[:,7]==flow.src_port )) &
                                       #(nodes[:,8]==0 | (nodes[:,8]==flow.dst_port )) 
                                       (nodes[:,12]==0 | (nodes[:,12]==flow.in_index )) &
                                       (nodes[:,13]==0 | (nodes[:,13]==flow.out_index )) 
                                       #(nodes[:,10]==0 | (nodes[:,10]==flow.src_as )) &
                                       #(nodes[:,11]==0 | (nodes[:,11]==flow.src_as )) 
                                       )
                                      ]
                    else:
                        nodes = nodes[(((flow.dst_addr & nodes[:,5])==nodes[:,4]) & 
                                       ((flow.src_addr & nodes[:,3])==nodes[:,2]) & 
                                       #(nodes[:,13]==0 | (nodes[:,13]==flow.protocol))
                                       #(nodes[:,7]==0 | (nodes[:,7]==flow.src_port )) &
                                       #(nodes[:,8]==0 | (nodes[:,8]==flow.dst_port )) 
                                       (nodes[:,12]==0 | (nodes[:,12]==flow.in_index )) &
                                       (nodes[:,13]==0 | (nodes[:,13]==flow.out_index )) 
                                       #(nodes[:,10]==0 | (nodes[:,10]==flow.src_as )) &
                                       #(nodes[:,11]==0 | (nodes[:,11]==flow.src_as )) 
                                       )
                                        ]
                    #print 'nodes', nodes
                    try:
                        #print nodes
                        if nodes[0][0]:
                            #if has_groups:
                                #print 'nodes[0][0]', nodes[0][0], has_groups, tarifGroups
                            self.add_classes_groups(flow, int(nodes[0][0]), [], acc.accounttarif_id, has_groups, tarifGroups)
                            #print nodes[0][1], nodes[0][1]==1
                            if nodes[0][1]==1:
                                nfwrite_list.append(tuple(flow))
                    except Exception, e:
                        #print e
                        pass
#===============================================================================
#                     for nclass, nnodes in cacheMaster.cache.class_cache.classes:        
#                         class_found = False            
#                         for nnode in nnodes:
# 
#                             if flow.node_direction == 'INPUT':
#                                 
#                                 if (flow.src_addr & nnode.dst_mask) != nnode.dst_ip:continue
#                                 if (flow.dst_addr & nnode.src_mask) != nnode.src_ip:continue
#                             else:
#                                 
#                                 if (flow.dst_addr & nnode.dst_mask) != nnode.dst_ip:
#                                     continue
#                                 if (flow.src_addr & nnode.src_mask) != nnode.src_ip:
#                                     continue
#                                 
#                             if ((flow.protocol != nnode.protocol) and nnode.protocol): continue
#                             if ((flow.src_port != nnode.src_port) and nnode.src_port):continue
#                             if ((flow.dst_port != nnode.dst_port) and nnode.dst_port):continue
#                             
#                             if ((flow.in_index != nnode.in_index) and nnode.in_index):continue
#                             if ((flow.out_index != nnode.out_index) and nnode.out_index):continue
#                             if ((flow.next_hop != nnode.next_hop) and (nnode.next_hop and nnode.next_hop!='0.0.0.0')):continue
#                             if ((flow.src_as != nnode.src_as) and nnode.src_as):continue
#                             if ((flow.dst_as != nnode.dst_as) and nnode.dst_as):continue
#                             
#                             
#                             class_found = True
#                             if not classLst:
#                                 fnode = nnode
#                             elif not fnode:
#                                 continue
#                             classLst.append(nclass)
# 
#                         #found passthrough=false
#                         if classLst:
#                             #logger.info("flow no pass: %s  classlst:%s nnode: %s tarifGroups: %s", (flow, classLst, nnode, tarifGroups))
#                             self.add_classes_groups(flow, classLst, fnode, acc.accounttarif_id, has_groups, tarifGroups)
#                             if nnode.store==True:
#                                 nfwrite_list.append(tuple(flow))
#                             break                   
#===============================================================================

                        
                    #construct a list
                    flst.append(tuple(flow)); fcnt += 1            

                    #append to databaseQueue
                    if fcnt == vars.PACKET_PACK:
                        flpack = flst #marshal.dumps(flst)
                        with queues.dbLock:
                            queues.databaseQueue.append(flpack)
                        flst = []; fcnt = 0
                        
                    src = False
                        
                if len(flst) > 0:
                    flpack = flst#marshal.dumps(flst)
                    with queues.dbLock:
                        queues.databaseQueue.append(flpack)
                    flst = []
                del keylist
                if vars.WRITE_FLOW and nfwrite_list:
                    #queues.flowSynchroBox.appendData(ips + flow.getBaseSlice())
                    try:
                        send_as_task(out_connection, nfwrite_list, 'nf_write')
                    except Exception, ex:
                        logger.error("fdqThread exception: Can not write to nfwriter queue \n %s %s", (repr(ex), traceback.format_exc()))
                #queues.flowSynchroBox.checkData()
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
                            logger.info("len flowQueueSize %s", queues.flowQueueSize)
                            
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

        logger.info("Config variables: %s", repr(vars))
        logger.lprint('Nf Filter start')
        #if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)
        
        out_connection = Connection(vars.kombu_dsn)
        
        
        #write profiling info predicate
        flags.writeProf = logger.writeInfoP()
        #file_test(vars.DUMP_DIR, vars.PREFIX)
        if vars.WRITE_FLOW:
            try:
                os.mkdir(vars.FILE_DIR)
            except: pass
            file_test(vars.FLOW_DIR)
            
        suicideCondition = {}    



        #-------------------
        print "ebs: nffilter: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nffilter, exiting: ', repr(ex)
        print "Exception in nffilter, exiting: %s \n %s'" % (repr(ex), traceback.format_exc())
    
    
    
