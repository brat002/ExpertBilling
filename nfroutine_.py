#-*-coding=utf-8-*-

from __future__ import with_statement

import cPickle
import random
import signal
import asyncore
import threading
import ConfigParser
import psycopg2, psycopg2.extras
import time, datetime, os, sys, gc, traceback
import socket


import isdlogger
import saver_ as saver, utilites

from IPy import intToIp
from marshal import dumps, loads
from daemonize import daemonize
from threading import Thread, Lock
from copy import copy, deepcopy
from DBUtils.PooledDB import PooledDB
from DBUtils.PersistentDB import PersistentDB
from collections import deque, defaultdict
from period_utilities import in_period_info
from db import delete_transaction, dbRoutine
from saver_ import allowedUsersChecker, setAllowedUsers, graceful_loader, graceful_saver
from db import transaction, transaction_noret, traffictransaction, get_last_checkout, time_periods_by_tarif_id, set_account_deleted

import twisted.internet
from twisted.internet.protocol import DatagramProtocol
try:
    from twisted.internet import pollreactor
    pollreactor.install()
except:
    print 'No poll(). Using select() instead.'
from twisted.internet import reactor

from classes.nfroutine_cache import *
from classes.common.Flow5Data import Flow5Data
from classes.cacheutils import CacheMaster
from classes.flags import NfrFlags
from classes.vars import NfrVars, NfrQueues
from utilites import renewCaches, savepid

try:    import mx.DateTime
except: print 'cannot import mx'

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)



class Picker(object):
    __slots__= ('data',)
    def __init__(self):
        self.data = defaultdict(float)      

    def add_summ(self, tts_id, acctf_id, account_id, summ):
        self.data[(tts_id, acctf_id, account_id)] += summ

    def get_list(self):
        while len(self.data) > 0:
            #yield {'account':key, 'tarif':self.data[key]['tarif'], 'summ': self.data[key]['summ']}
            yield self.data.popitem()
            
    def get_data(self):
        return self.data.items()

#try to save data - ticket 31
class DepickerThread(Thread):
    '''Thread that takes a Picker object and executes transactions'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        
    def run(self):        
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        cur = connection.cursor()
        global queues, flags, suicideCondition
        while True:
            if suicideCondition[self.tname]: break
            try:
                picker = None
                
                with queues.depickerLock:
                    if len(queues.depickerQueue) > 0:
                        picker = queues.depickerQueue.popleft()
                if not picker: time.sleep(10); continue              
                
                a = time.clock()
                now = datetime.datetime.now()
                icount = 0
                ilist = picker; ilen = len(picker)
                for (tts,acctf,acc), summ in ilist:
                    #debit accounts
                    traffictransaction(cur, tts, acctf, acc, summ=summ, created=now)
                    connection.commit()
                    icount += 1
                if flags.writeProf:
                    logger.info("DPKALIVE: %s icount: %s run time: %s", (self.getName(), icount, time.clock() - a))
            except IndexError, ierr:
                if not picker:
                    try: queues.depickerLock.release()
                    except: pass
                logger.debug("%s : indexerror : %s", (self.getName(), repr(ierr))) 
                time.sleep(10)
                continue             
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))    
                if isinstance(ex, psycopg2.OperationalError) or isinstance(ex, psycopg2.ProgrammingError) or isinstance(ex, psycopg2.InterfaceError):
                    if picker:
                        with queues.depickerLock:
                            queues.depickerQueue.appendleft(ilist[icount:])
                    #try: cur = connection.cursor()
                    #except: pass
                    try: 
                        time.sleep(3)
                        cur = connection.cursor()
                    except: 
                        time.sleep(20)
                        try:
                            connection = pool.connection()
                            connection._con.set_client_encoding('UTF8')
                            cur = connection.cursor()
                            continue
                        except:
                            time.sleep(10)
                time.sleep(10)
  
class groupDequeThread(Thread):
    '''Тред выбирает и отсылает в БД статистику по группам-пользователям'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__

    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        cur = connection.cursor()
        global queues, flags
        #direction type->operations
        #gops = {1: lambda xdct: xdct['INPUT'], 2: lambda xdct: xdct['OUTPUT'] , 3: lambda xdct: xdct['INPUT'] + xdct['OUTPUT'], 4: lambda xdct: max(xdct['INPUT'], xdct['OUTPUT'])}
        gops = [lambda xdct: xdct['INPUT'], lambda xdct: xdct['OUTPUT'], lambda xdct: xdct['INPUT'] + xdct['OUTPUT'], lambda xdct: max(xdct['INPUT'], xdct['OUTPUT'])]
        icount = 0; timecount = 0
        a = time.clock()
        while True:
                #gdata[1] - group_id, group_dir, group_type
                #gkey[0] - account_id, gkey[2] - date
            try:
                if suicideCondition[self.tname]: break
                if flags.writeProf: 
                    a = time.clock()
                    
                gkey, gkeyTime, groupData = None, None, None
                with queues.groupLock:
                    #check whether double aggregation time passed - updates are rather costly
                    if len(queues.groupDeque) > 0 and (queues.groupDeque[0][1] + vars.groupAggrTime*2 < time.time()):
                        gkey, gkeyTime  = queues.groupDeque.popleft()

                if not gkey: time.sleep(30); continue

                #get data
                account_id, kgroup_id, gtime = gkey 
                dkey = (int(gtime) + account_id) % vars.groupDicts
                aggrgDict = queues.groupAggrDicts[dkey]
                aggrgLock = queues.groupAggrLocks[dkey]
                with aggrgLock:
                    groupData = aggrgDict.pop(gkey, None)
                    
                if not groupData:
                    logger.info('%s: no groupdata for key: %s', (self.getName(), gkey))
                    continue
                
                groupItems, groupInfo = groupData[0:2]
                #get needed method
                group_id, group_dir, group_type = groupInfo
                gdate = datetime.datetime.fromtimestamp(gtime)
                #gop = gops[group_dir]
                gop = gops[group_dir - 1]
                octlist, classes = [], []             
                max_class = None
                octets = 0               
                
                #second type groups
                if   group_type == 2:                        
                    max_oct = 0
                    #get class octets, calculate with direction method, find maxes
                    for class_, gdict in groupItems.iteritems():                            
                        octs = gop(gdict)
                        classes.append(class_)
                        octlist.append(octs)
                        if octs > max_oct:
                            max_oct = octs
                            max_class = class_                            
                        
                    octets = max_oct                        
                    if not max_class: continue
                    cur.execute("""SELECT group_type2_fn(%s, %s, %s, %s::timestamp without time zone, %s::int[], %s::int[], %s);""" , (group_id, account_id, octets, gdate, classes, octlist, max_class))
                    connection.commit()
                #first type groups
                elif group_type == 1:
                    #get class octets, calculate sum with direction method
                    for class_, gdict in groupItems.iteritems():
                        octs = gop(gdict)
                        octets += octs
                    cur.execute("""SELECT group_type1_fn(%s, %s, %s, %s::timestamp without time zone, %s::int[], %s::int[], %s);""" , (group_id, account_id, octets, gdate, classes, octlist, max_class))
                    connection.commit()
                else:
                    continue
                
                #write profiling infos
                if flags.writeProf:
                    icount += 1
                    timecount += time.clock() - a
                    if icount == 10:                        
                        logger.info("%s run time(10): %s", (self.getName(), timecount))
                        icount = 0; timecount = 0
            except IndexError, ierr:
                if not gkey:
                    try:    queues.groupLock.release()
                    except: pass
                logger.debug("%s : indexerror : %s", (self.getName(), repr(ierr))) 
                continue
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc())) 
                if isinstance(ex, psycopg2.OperationalError) or isinstance(ex, psycopg2.ProgrammingError) or isinstance(ex, psycopg2.InterfaceError):
                    if gkey and gkeyTime and groupData:
                        with aggrgLock:
                            grec = aggrgDict.get(gkey)
                            if not grec:
                                aggrgDict[gkey] = groupData
                                with queues.groupLock:
                                    queues.groupDeque.appendleft((gkey, gkeyTime))
                            else:
                                for gclass, class_io in groupItems.iteritems():
                                    grec[0][gclass]['INPUT']  += class_io['INPUT']
                                    grec[0][gclass]['OUTPUT'] += class_io['OUTPUT']
                        
                    #try: cur = connection.cursor()
                    #except: time.sleep(20)
                    try: 
                        time.sleep(3)
                        cur = connection.cursor()
                    except: 
                        time.sleep(20)
                        try:
                            connection = pool.connection()
                            connection._con.set_client_encoding('UTF8')
                            cur = connection.cursor()
                        except:
                            time.sleep(20)
                            
                
                
class statDequeThread(Thread):
    '''Thread picks out and sends to the DB global statistics'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__

    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        cur = connection.cursor()
        global queues, flags
        icount = 0; timecount = 0
        a = time.clock()
        while True:
                #gdata[1] - group_id, group_dir, group_type
                #gkey[0] - account_id, gkey[2] - date
            try:
                if suicideCondition[self.tname]: break
                if flags.writeProf:
                    a = time.clock()
                    
                skey, skeyTime, statData = None, None, None
                with queues.statLock:
                    #check whether double aggregation time passed - updates are rather costly
                    if len(queues.statDeque) > 0 and (queues.statDeque[0][1] + vars.statAggrTime*2 < time.time()):
                        skey, skeyTime  = queues.statDeque.popleft()

                if not skey: time.sleep(30); continue
                
                account_id, stime = skey 
                dkey = (int(stime) + account_id) % vars.statDicts
                aggrsDict = queues.statAggrDicts[dkey]
                aggrsLock = queues.statAggrLocks[dkey]
                with aggrsLock:
                    statData = aggrsDict.pop(skey, None)
                    
                if not statData:
                    logger.info('%s: no statdata for key: %s', (self.getName(), skey))
                    continue

                statItems, statInfo = statData
                nas_id, sum_bytes   = statInfo
                octets_in  = sum_bytes['INPUT']
                octets_out = sum_bytes['OUTPUT']
                sdate = datetime.datetime.fromtimestamp(stime)
                octlist, classes = [], []
                       
                #get octets for every class
                for class_, sdict in statItems.iteritems():                            
                    classes.append(class_)
                    octlist.append([sdict['INPUT'], sdict['OUTPUT']])              
                    
                cur.execute("""SELECT global_stat_fn(%s, %s, %s, %s::timestamp without time zone, %s, %s::int[], %s::bigint[]);""" , (account_id, octets_in, octets_out, sdate, nas_id, classes, octlist))
                connection.commit()
                
                if flags.writeProf:
                    icount += 1
                    timecount += time.clock() - a
                    if icount == 10:                        
                        logger.info("%s run time(10): %s", (self.getName(), timecount))
                        icount = 0; timecount = 0
                        
            except IndexError, ierr:
                if not skey:
                    try:    queues.statLock.release()
                    except: pass
                logger.debug("%s : indexerror : %s", (self.getName(), repr(ierr))) 
                continue
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc())) 
                if isinstance(ex, psycopg2.OperationalError) or isinstance(ex, psycopg2.ProgrammingError) or isinstance(ex, psycopg2.InterfaceError):
                    if skey and skeyTime and statData:
                        with aggrsLock:
                            srec = aggrsDict.get(skey)
                            if not srec:
                                aggrsDict[gkey] = statData
                                with queues.statLock:
                                    queues.statDeque.appendleft((skey, skeyTime))
                            else:
                                for sclass, class_io in statItems.iteritems():
                                    srec[0][sclass]['INPUT']  += class_io['INPUT']
                                    srec[0][sclass]['OUTPUT'] += class_io['OUTPUT']
                                srec[1][1]['INPUT']  += octets_in
                                srec[1][1]['OUTPUT'] += octets_out
                        
                    try: 
                        time.sleep(3)
                        cur = connection.cursor()
                    except: 
                        time.sleep(20)
                        try:
                            connection = pool.connection()
                            connection._con.set_client_encoding('UTF8')
                            cur = connection.cursor()
                        except:
                            time.sleep(20)
                            
                
            
       
class NetFlowRoutine(Thread):
    '''Thread that handles NetFlow statistic packets and bills according to them'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        
    def get_actual_cost(self, octets_summ, stream_date, nodes):
        """Метод возвращает актуальную цену для направления трафика для пользователя:"""
        #TODO: check whether differentiated traffic billing us used <edge_start>=0; <edge_end>='infinite'
        cost, min_from_start = 0, 0
        for node in nodes:
            if 0: assert isinstance(node, NodesData)
            tnc, tkc, from_start, result = fMem.in_period_(node.time_start, node.length, node.repeat_after, stream_date)
            if result:
                """
                Зачем здесь было это делать:
                Если в тарифном плане с оплатой за трафик в одной ноде указана цена за "круглые сутки", 
                но в другой ноде указана цена за какой-то конкретный день (к пр. праздник), 
                который так же попадает под круглые сутки, но цена в "праздник" должна быть другой, 
                значит смотрим у какой из нод помимо класса трафика попал расчётный период и выбираем из всех нод ту, 
                у которой расчётный период начался как можно раньше к моменту попадения строки статистики в БД.
                """
                if from_start < min_from_start or min_from_start == 0:
                    min_from_start = from_start
                    cost = node.traffic_cost
                    
        return cost


    
    def run(self):
        connection = persist.connection()
        connection._con.set_client_encoding('UTF8')
        global cacheMaster, vars, flags, queues
        caches = None
        dateAT = datetime.datetime(2000, 1, 1)
        oldAcct = defaultdict(list)
        cur = connection.cursor()
        icount, timecount = 0, 0
        while True:
            try:   
                if suicideCondition[self.tname]: break
                if flags.writeProf:
                    a = time.clock()
                    
                fpacket = None
                if cacheMaster.date > dateAT:
                    cacheMaster.lock.acquire()
                    try:
                        caches = cacheMaster.cache
                        dateAT = deepcopy(cacheMaster.date)
                    except Exception, ex:
                        logger.error("%s: cache exception: %s", (self.getName, repr(ex)))
                    finally:
                        cacheMaster.lock.release()
                    oldAcct = defaultdict(list)
                    
                if not caches:
                    time.sleep(3)
                    continue
                
                if 0: assert isinstance(caches, NfroutineCaches)  
                
                #time to pick
                if (time.time() > queues.pickerTime + 300.0):
                    #add picker to a depicker queue
                    with queues.pickerLock:
                        queues.depickerQueue.append(queues.picker.get_data())
                        queues.picker = Picker()
                        queues.pickerTime = time.time()                    

                fpacket = queues.nfIncomingQueue.popleft()
                flows = loads(fpacket)
                #iterate through them
                for pflow in flows:
                    flow = Flow5Data(False, *pflow)
                    #get account id and get a record from cache based on it
                    acc = caches.account_cache.by_account.get(flow.account_id)
                    if not acc: continue
                    if 0: assert isinstance(acc, AccountData)
                    stream_date = datetime.datetime.fromtimestamp(flow.datetime)

                    #if no line in cache, or the collection date is younger then accounttarif creation date
                    #get an acct record from teh database
                    if  (acc.acctf_id  != flow.acctf_id) or (not acc.datetime <= stream_date):
                        acc = oldAcct.get(flow.acctf_id)
                        if not acc:
                            cur.execute("""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, FALSE, ba.created, ba.disabled_by_limit, ba.balance_blocked, ba.nas_id, ba.vpn_ip_address, ba.ipn_ip_address,ba.ipn_mac_address, ba.assign_ipn_ip_from_dhcp, ba.ipn_status, ba.ipn_speed, ba.vpn_speed, ba.ipn_added, bt.ps_null_ballance_checkout, bt.deleted, bt.allow_express_pay, ba.status, ba.allow_vpn_null, ba.allow_vpn_block, ba.username
                                           FROM billservice_account as ba
                                           JOIN billservice_accounttarif AS act ON act.id=%s AND ba.id=act.account_id
                                           LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id;
                                        """, (flow.account_id,))
                            acc = cur.fetchone()
                            connection.commit()
                            if not acc: continue
                            acc = AccountData(*acc)
                            oldAcct[flow.acctf_id] = acc                           
                    
                    #if no tarif_id, tarif.active=False and don't store, account.active=false and don't store    
                    if (acc.tarif_id == None) or (not (acc.tarif_active or flags.store_na_tarif)) \
                       or (not (acc.account_status or flags.store_na_account)): continue                    
                    
                    '''Статистика по группам: 
                    аггрегируется в словаре по структурам типа {класс->{'INPUT':0, 'OUTPUT':0}}
                    Ключ - (account_id, group_id, gtime)
                    Ключ затем добавляется в очередь.'''
                    if flow.has_groups and flow.groups:                        
                        gtime = flow.datetime - (flow.datetime % vars.groupAggrTime)                        
                        for group_id, group_classes, group_dir, group_type in flow.groups:
                            #group_id, group_classes, group_dir, group_type  = group
                            #calculate a key and check the dictionary
                            gkey = (flow.account_id, group_id, gtime)
                            dgkey = (int(gtime / 667) + flow.account_id) % vars.groupDicts
                            aggrgDict = queues.groupAggrDicts[dgkey]
                            aggrgLock = queues.groupAggrLocks[dgkey]
                            with aggrgLock:
                                grec = aggrgDict.get(gkey)
                                if not grec:
                                    #add new record to the queue and the dictionary
                                    grec = [defaultdict(ddict_IO), (group_id, group_dir, group_type)]
                                    aggrgDict[gkey] = grec
                                    with queues.groupLock:
                                        queues.groupDeque.append((gkey, time.time()))                      
                                #aggregate bytes for every class/direction
                                for class_ in group_classes:
                                    grec[0][class_][flow.node_direction] += flow.octets                     
                   
                                
                    #global statistics calculation
                    stime = flow.datetime - (flow.datetime % vars.statAggrTime)
                    skey  = (flow.account_id, stime)
                    dskey = (int(stime / 667) + flow.account_id) % vars.statDicts
                    aggrsDict = queues.statAggrDicts[dskey]
                    aggrsLock = queues.statAggrLocks[dskey]
                    with aggrsLock:
                        srec = aggrsDict.get(skey)
                        if not srec:                            
                            srec = [defaultdict(ddict_IO), [flow.nas_id, {'INPUT':0, 'OUTPUT':0}]]
                            aggrsDict[skey] = srec
                            with queues.statLock:
                                queues.statDeque.append((skey, time.time()))
                        #add for every class
                        for class_ in flow.class_id:
                            srec[0][class_][flow.node_direction] += flow.octets
                        #global data
                        srec[1][1][flow.node_direction] += flow.octets                        

                    tarif_mode = caches.period_cache.in_period.get(acc.traffic_transmit_service_id, False) if acc.traffic_transmit_service_id else False
                    store_classes = list(caches.storeclass_cache.classes.intersection(flow.class_id))
                    #if tarif_mode is False or tarif.active = False
                    #write statistics without billing it
                    if store_classes and not (tarif_mode and acc.tarif_active and acc.account_status):
                        #cur = connection.cursor()
                        cur.execute("""INSERT INTO billservice_netflowstream(
                                       nas_id, account_id, tarif_id, direction,date_start, src_addr, traffic_class_id,
                                       dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                                    """, (flow.nas_id, flow.account_id, acc.tarif_id, flow.node_direction, stream_date, \
                                          intToIp(flow.src_addr,4), store_classes, intToIp(flow.dst_addr,4), flow.octets, \
                                          flow.src_port, flow.dst_port, flow.protocol, False, False,))
                        connection.commit()
                        continue
                    
                    if acc.traffic_transmit_service_id and flow.has_groups and flow.groups:
                        octets_summ = 0
                        #loop throungh classes in 'classes' tuple
                            
                        for group_id, group_classes, group_dir, group_type in flow.groups:
                            nodes = caches.nodes_cache.by_tts_group.get((acc.traffic_transmit_service_id, group_id))
                            trafic_cost = self.get_actual_cost(octets_summ, stream_date, nodes) if nodes else 0

                            #get a record from prepays cache
                            prepInf = caches.prepays_cache.by_tts_acctf_group.get((acc.traffic_transmit_service_id, acc.acctf_id, group_id))                            
                            octets = flow.octets
                            if prepInf:
                                prepaid_id, prepaid = prepInf[0:2]
                                if prepaid > 0:                            
                                    if prepaid>=octets:
                                        prepaid, octets = prepaid-octets, 0
                                    elif octets>=prepaid:
                                        prepaid, octets = octets-prepaid, abs(prepaid-octets)
                                        
                                    cur.execute("""UPDATE billservice_accountprepaystrafic SET size=size-%s WHERE id=%s""", (prepaid, prepaid_id,))
                                    connection.commit()
            
                            summ = (trafic_cost * octets)/(1048576)
        
                            if summ > 0:
                                with queues.pickerLock:
                                    queues.picker.add_summ(acc.traffic_transmit_service_id, acc.acctf_id, acc.account_id, summ)
                                    
                    if store_classes:
                        cur.execute("""INSERT INTO billservice_netflowstream(
                                       nas_id, account_id, tarif_id, direction,date_start, src_addr, traffic_class_id,
                                       dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                                   """, (flow.nas_id, flow.account_id, acc.tarif_id, flow.node_direction, stream_date, \
                                         intToIp(flow.src_addr,4), store_classes, intToIp(flow.dst_addr,4), flow.octets, \
                                         flow.src_port, flow.dst_port, flow.protocol, True, False,))
                        connection.commit()
                 
                if flags.writeProf:
                    icount += 1
                    timecount += time.clock() - a
                    if icount == 100:                        
                        logger.info("%s run time: %s", (self.getName(), timecount))
                        icount = 0; timecount = 0
                        
            except IndexError, ierr:
                logger.debug("%s : indexerror : %s", (self.getName(), repr(ierr))) 
                if not fpacket: time.sleep(random.randint(10,20))                
                continue               
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc())) 
                if isinstance(ex, psycopg2.OperationalError) or isinstance(ex, psycopg2.ProgrammingError) or isinstance(ex, psycopg2.InterfaceError):
                    try: 
                        time.sleep(3)
                        cur = connection.cursor()
                    except: 
                        time.sleep(20)
                        try:
                            connection = persist.connection()
                            connection._con.set_client_encoding('UTF8')
                            cur = connection.cursor()
                        except:
                            time.sleep(20)
                time.sleep(1)
                    

#periodical function memoize class
class pfMemoize(object):
    __slots__ = ('periodCache')
    def __init__(self):
        self.periodCache = {}
        
    def in_period_(self, time_start, length, repeat_after, date_):
        res = self.periodCache.get((time_start, length, repeat_after, date_))
        if res==None:
            res = in_period_info(time_start, length, repeat_after, date_)
            self.periodCache[(time_start, length, repeat_after, date_)] = res
        return res
    
    
class AccountServiceThread(Thread):
    '''Handles simultaniously updated READ ONLY caches connected to account-tarif tables'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
    
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global suicideCondition, cacheMaster, flags, queues, threads, cacheThr
        counter = 0; now = datetime.datetime.now
        while True:
            if suicideCondition[self.__class__.__name__]: break
            a = time.clock()
            try: 
                time_run = (now() - cacheMaster.date).seconds > 180
                if flags.cacheFlag or time_run:
                    run_time = time.clock()                    
                    cur = connection.cursor()
                    renewCaches(cur, cacheMaster, NfroutineCaches, 21, (fMem,))
                    cur.close()
                    if counter == 0 or time_run:
                        allowedUsersChecker(allowedUsers, lambda: len(cacheMaster.cache.account_cache.data))
                        flags.writeProf = logger.writeInfoP()
                        if flags.writeProf:        
                            logger.info("incoming queue len: %s", len(queues.nfIncomingQueue))
                            #logger.info("groupDictLen: %s", len(queues.groupAggrDict))
                            logger.info("groupDequeLen: %s", len(queues.groupDeque))
                            #logger.info("statDictLen: %s", len(queues.statAggrDict))
                            logger.info("statDequeLen: %s", len(queues.statDeque))
                            
                    if counter == 5:
                        counter, fMem.periodCache = 0, {}
                        if (len(queues.nfIncomingQueue) > 1000) or (len(queues.statDeque) > len(cacheMaster.cache.account_cache.data) * 10):
                            if not vars.sendFlag or vars.sendFlag!='SLP!':
                                vars.sendFlag = 'SLP!'
                                logger.lprint('Sleep flag set!')                        
                        else:
                            if vars.sendFlag and vars.sendFlag=='SLP!':
                                vars.sendFlag = ''
                                logger.lprint('Sleep flag unset!')
                            
                        th_status = ';'.join((thrd.getName().split(' ')[0] + (thrd.isAlive() and 'OK') or 'NO' for thrd in threads + [cacheThr]))
                        logger.warning('THREAD STATUS: %s', th_status)

                    counter += 1
                    if flags.cacheFlag:
                        with flags.cacheLock: flags.cacheFlag = False
                    
                    logger.info("ast time : %s", time.clock() - run_time)
            except Exception, ex:
                logger.error("%s : #30210004 : %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                if isinstance(ex, psycopg2.OperationalError) or isinstance(ex, psycopg2.ProgrammingError) or isinstance(ex, psycopg2.InterfaceError):
                    time.sleep(5)
                    try:
                        connection = pool.connection()
                        connection._con.set_client_encoding('UTF8')
                    except:
                        time.sleep(10)
            gc.collect()
            time.sleep(20)
            
            
class NfTwistedServer(DatagramProtocol):
    '''
    Twisted Asynchronous server that recieves datagrams with NetFlow packets
    and appends them to 'nfQueue' queue.
    '''
    def datagramReceived(self, data, addrport):
        try:
            self.transport.write(vars.sendFlag + str(len(data)), addrport)
            #self.socket.sendto(vars.sendFlag + str(len(data)), addrport)
            queues.nfIncomingQueue.append(data)
        except:            
            logger.error("%s : #30210701 : %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))

class NfAsyncUDPServer(asyncore.dispatcher):
    ac_out_buffer_size = 16384*10
    ac_in_buffer_size = 16384*10
    
    def __init__(self, addr_):
        self.outbuf = []
        asyncore.dispatcher.__init__(self)

        self.host = addr_[0]
        self.port = addr_[1]
        self.dbconn = None
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)
        self.bind(addr_)
        self.set_reuse_addr()

    def handle_connect(self):
        pass    
    def handle_read_event (self):
        try:
            data, addr = self.socket.recvfrom(32768)
            self.socket.sendto(vars.sendFlag + str(len(data)), addr)
            queues.nfIncomingQueue.append(data)
        except:            
            logger.error("%s : #30210701 : %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))


    def handle_readfrom(self,data, address):
        pass
    def writable(self):
        return (0)

    def handle_error (self, *info):
        logger.error('Uncaptured python exception, closing channel %s \n %s', (repr(self), traceback.format_exc()))
        self.close()
    
    def handle_close(self):
        self.close()     


        

def ddict_IO():
    return {'INPUT':0, 'OUTPUT':0}

def SIGTERM_handler(signum, frame):
    logger.lprint("SIGTERM recieved")
    graceful_save()

def SIGHUP_handler(signum, frame):
    global config
    logger.lprint("SIGHUP recieved")
    try:
        config.read("ebs_config.ini")
        logger.setNewLevel(int(config.get("nfroutine", "log_level")))
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
    #asyncore.close_all()
    reactor.callFromThread(reactor.disconnectAll)
    reactor.callFromThread(reactor.stop)
    reactor._started = False
    suicideCondition[cacheThr.tname] = True
    logger.lprint("About to exit gracefully.")
    st_time = time.time()
    time.sleep(1)
    i = 0
    while True:
        if len(queues.nfIncomingQueue) > 300:  break
        if len(queues.nfIncomingQueue) == 0:   break
        if i == 4:                             break
        time.sleep(1)

    for thr in threads:
        if not isinstance(thr, DepickerThread):
            suicideCondition[thr.tname] = True
    time.sleep(1)
    
    for thr in threads:
            suicideCondition[thr.tname] = True
    time.sleep(2)
    pool.close()            
    time.sleep(1)
    
    queues.depickerLock.acquire()
    queues.groupLock.acquire()
    queues.statLock.acquire()
    graceful_saver([['depickerQueue'], ['nfIncomingQueue'], ['groupDeque', 'groupAggrDicts'], ['statDeque', 'statAggrDicts']],
                   queues, 'nfroutine_', vars.saveDir)
    time.sleep(3)
    queues.statLock.release()
    queues.groupLock.release()
    queues.depickerLock.release()
    logger.lprint(vars.name + " stopping gracefully.")
    print vars.name + " stopping gracefully."

def graceful_recover():
    global queues, vars
    graceful_loader(['depickerQueue','nfIncomingQueue','groupDeque', 'groupAggrDicts','statDeque', 'statAggrDicts'],
                    queues, 'nfroutine_', vars.saveDir)
    

def main():
    graceful_recover()
    global cacheMaster, suicideCondition
    global threads, cacheThr, NfAsyncUDPServer
    threads=[]
    for i in xrange(int(config.get("nfroutine", "routinethreads"))):
        newNfr = NetFlowRoutine()
        newNfr.setName('NFR:#%i: NetFlowRoutine' % i)
        threads.append(newNfr)
    for i in xrange(int(config.get("nfroutine", "groupstatthreads"))):
        grdqTh = groupDequeThread()
        grdqTh.setName('GDT:#%i: groupDequeThread' % i)
        threads.append(grdqTh)
    for i in xrange(int(config.get("nfroutine", "globalstatthreads"))):
        stdqTh = statDequeThread()
        stdqTh.setName('SDS:#%i: statDequeThread' % i)
        threads.append(stdqTh)
    for i in xrange(int(config.get("nfroutine", "depickerthreads"))):
        depTh = DepickerThread()
        depTh.setName('DET:#%i: depickerThread' % i)
        threads.append(depTh)
    
    cacheThr = AccountServiceThread()
    cacheThr.setName('AST: AccountServiceThread')
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.start()
    
    time.sleep(2)
    while cacheMaster.read is False:        
        if not cacheThr.isAlive:
            sys.exit()
        time.sleep(10)
        if not cacheMaster.read: 
            print 'caches still not read, maybe you should check the log'
      
    print 'caches ready'
    logger.info("NFR: cache read status: %s", cacheMaster.read)
    #i= range(len(threads))
    for th in threads:
        suicideCondition[th.__class__.__name__] = False
        th.start()        
        logger.info("NFR %s start", th.getName())
        time.sleep(0.1)
        
    logger.warning("THREADS=%s", repr([thrd.getName() for thrd in threads + [cacheThr]]))
    #logger.warning("CACHETH=%s", cacheThr.getName())
    time.sleep(5)    
    try:
        signal.signal(signal.SIGHUP, SIGHUP_handler)
    except: logger.lprint('NO SIGHUP!')
    
    try:
        signal.signal(signal.SIGUSR1, SIGUSR1_handler)
    except: logger.lprint('NO SIGUSR1!')
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')
    
    reactor.listenUDP(vars.port, NfTwistedServer(), maxPacketSize=32687)
    print "ebs: nfroutine: started"
    savepid(vars.piddir, vars.name)
    reactor.run(installSignalHandlers=False)
#===============================================================================

    
if __name__ == "__main__":
    if "-D" in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
        

    cacheMaster = CacheMaster()
    
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")

    flags = NfrFlags()
    vars  = NfrVars()
    
    if config.has_option("nfroutine", "groupdicts"): vars.groupDicts = config.getint("nfroutine", "groupdicts")
    if config.has_option("nfroutine", "statdicts"):  vars.statDicts  = config.getint("nfroutine", "statdicts")
    queues= NfrQueues(vars.groupDicts, vars.statDicts)
    
    logger = isdlogger.isdlogger(config.get("nfroutine", "log_type"), loglevel=int(config.get("nfroutine", "log_level")), ident=config.get("nfroutine", "log_ident"), filename=config.get("nfroutine", "log_file")) 
    saver.log_adapt = logger.log_adapt
    utilites.log_adapt = logger.log_adapt
    logger.lprint('Nfroutine start')
    try:
        
        if config.get("nfroutine_nf", "usock") == '0':
            vars.host = config.get("nfroutine_nf_inet", "host")
            vars.port = int(config.get("nfroutine_nf_inet", "port"))
            vars.addr = (vars.host, vars.port)
        elif config.get("nfroutine_nf", "usock") == '1':
            vars.host = config.get("nfroutine_nf_unix", "host")
            vars.port = 0
            vars.addr = (vars.host,)
        else:
            raise Exception("Config '[nfroutine_nf] -> usock' value is wrong, must be 0 or 1")
        #temp save on restart or graceful stop
        vars.saveDir = config.get("nfroutine", "save_dir")
        #store stat. for old tarifs and accounts?
        flags.store_na_tarif   = True if ((config.get("nfroutine", "store_na_tarif")   =='True') or (config.get("nfroutine", "store_na_tarif")  =='1')) else False
        flags.store_na_account = True if ((config.get("nfroutine", "store_na_account") =='True') or (config.get("nfroutine", "store_na_account")=='1')) else False
        
        #write profiling info?
        flags.writeProf = logger.writeInfoP()  
        
        pool = PooledDB(
            mincached=4,  maxcached=20,
            blocking=True,creator=psycopg2,
            dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"),
                                                                   config.get("db", "host"), config.get("db", "password")))
        persist = PersistentDB(
            setsession=["SET synchronous_commit TO OFF;"],
            creator=psycopg2,
            dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"), 
                                                                   config.get("db", "host"), config.get("db", "password")))
    
        #--------------------------------------------------------
        
        suicideCondition = {}

        #group statistinc an global statistics objects    
        #key = account, group id , time
        #[(1,2,3)][0][4]['INPUT']
        #[(1,2, )][1] = group info
        #lambda: [defaultdict(lambda: {'INPUT':0, 'OUTPUT':0}), None])
        #groupAggrDict = {}   
        #key - account_id, time
        #[(1,2,3)][0][4]['INPUT']
        #[(1,2, )][1] = nas etc
        #statAggrDict = {}   
        
        queues.picker = Picker()
        queues.pickerTime = time.time() + 5
        
        #function that returns number of allowed users
        #create allowedUsers
        if not globals().has_key('_1i'):
            _1i = lambda: ''
        allowedUsers = setAllowedUsers(pool.connection(), _1i())       
        allowedUsers()
        
        fMem = pfMemoize()    
    
    
        #-------------------
        print "ebs: nfroutine: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nfroutine, exiting: ', repr(ex)
        logger.error('Exception in nfroutine, exiting: %s \b %s', (repr(ex), traceback.format_exc()))