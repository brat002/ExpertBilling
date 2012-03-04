#-*-coding=utf-8-*-

from __future__ import with_statement

import cPickle
import random
import signal
import struct
import threading
import ConfigParser
import psycopg2, psycopg2.extras
import time, datetime, os, sys, gc, traceback
import socket


import isdlogger
import saver, utilites

from IPy import intToIp
from marshal import dumps, loads
from daemonize import daemonize
from threading import Thread, Lock
from copy import copy, deepcopy
from collections import deque, defaultdict
from period_utilities import in_period_info
from db import delete_transaction, dbRoutine
from saver import allowedUsersChecker, setAllowedUsers, graceful_loader, graceful_saver
from db import transaction, transaction_noret, traffictransaction, get_last_checkout, time_periods_by_tarif_id, set_account_deleted

import twisted.internet
from twisted.internet.protocol import DatagramProtocol, Factory
from twisted.protocols.basic import LineReceiver, Int32StringReceiver
try:
    from twisted.internet import pollreactor
    pollreactor.install()
except:
    print 'No poll(). Using select() instead.'
from twisted.internet import reactor

from decimal import Decimal
from classes.nfroutine_cache import *
from classes.common.Flow5Data import Flow5Data
from classes.cacheutils import CacheMaster
from classes.flags import NfrFlags
from classes.vars import NfrVars, NfrQueues, install_logger
from utilites import renewCaches, savepid, rempid, get_connection, getpid, check_running, \
                     STATE_NULLIFIED, STATE_OK, NFR_PACKET_HEADER_FMT

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

NFR_PACKET_HEADER_LEN  = 16
TCP_PACKET_SIZE_HEADER = 5
NAME = 'nfroutine'
DB_NAME = 'db'
NET_NAME = 'nfroutine_nf'
MEGABYTE =1048576 
INT_ME_FN = lambda xt, y: (xt[0] + (ord(y) - 48) * xt[1], xt[1] * 10)


class Picker(object):
    __slots__= ('data',)
    def __init__(self):
        self.data = defaultdict(Decimal)      

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
        global queues, flags, suicideCondition, vars
        self.connection = get_connection(vars.db_dsn)
        self.cur        = self.connection.cursor()
        while True:
            if suicideCondition[self.tname]:
                try: self.connection.close()
                except: pass
                break
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
                    traffictransaction(self.cur, tts, acctf, acc, summ=summ, created=now)
                    self.connection.commit()
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
                if ex.__class__ in vars.db_errors:
                    if picker:
                        with queues.depickerLock:
                            queues.depickerQueue.appendleft(ilist[icount:])
                    #try: cur = connection.cursor()
                    #except: pass
                    try: 
                        time.sleep(3)
                        if self.connection.closed():
                            try:
                                self.connection = get_connection(vars.db_dsn)
                                self.cur = self.connection.cursor()
                            except:
                                time.sleep(20)
                        else:
                            self.cur.connection.commit()
                            self.cur = self.connection.cursor()
                    except: 
                        time.sleep(10)
                        try:
                            self.connection.close()
                        except: pass
                        try:
                            self.connection = get_connection(vars.db_dsn)
                            self.cur = self.connection.cursor()
                        except:
                            time.sleep(20)
                time.sleep(20)
  
class groupDequeThread(Thread):
    '''Тред выбирает и отсылает в БД статистику по группам-пользователям'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__

    def run(self):
        global queues, flags, vars
        self.connection = get_connection(vars.db_dsn)
        self.cur = self.connection.cursor()
        #direction type->operations
        gops = [lambda xdct: xdct['INPUT'], lambda xdct: xdct['OUTPUT'], lambda xdct: xdct['INPUT'] + xdct['OUTPUT'], lambda xdct: max(xdct['INPUT'], xdct['OUTPUT'])]
        icount = 0; timecount = 0
        a = time.clock()
        while True:
                #gdata[1] - group_id, group_dir, group_type
                #gkey[0] - account_id, gkey[2] - date
            try:
                if suicideCondition[self.tname]:
                    try: self.connection.close()
                    except: pass
                    break
                #Записывать данные для профилирования
                if flags.writeProf: 
                    a = time.clock()
                    
                gkey, gkeyTime, groupData = None, None, None
                with queues.groupLock:
                    #check whether double aggregation time passed - updates are rather costly
                    if len(queues.groupDeque) > 0 and (queues.groupDeque[0][1] + vars.GROUP_AGGR_TIME*2 < time.time()):
                        gkey, gkeyTime  = queues.groupDeque.popleft()

                if not gkey: time.sleep(10); continue

                #get data
                account_id, kgroup_id, gtime = gkey 
                dkey = (int(gtime / 667) + account_id) % vars.GROUP_DICTS
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
                if group_type == 2:                        
                    max_oct = 0
                    #get class octets, calculate with direction method, find maxes
                    for class_, gdict in groupItems.iteritems():                            
                        octs = gop(gdict)
                        classes.append(class_)
                        octlist.append(octs)
                        if octs >= max_oct:
                            max_oct = octs
                            max_class = class_                            
                        
                    octets = max_oct                        
                    if not max_class: continue
                    self.cur.execute("""SELECT group_type2_fn(%s, %s, %s, %s::timestamp without time zone, %s::int[], %s, %s);""" , (group_id, account_id, octets, gdate, classes, octlist, max_class))
                    self.connection.commit()
                #first type groups
                elif group_type == 1:
                    #get class octets, calculate sum with direction method
                    for class_, gdict in groupItems.iteritems():
                        octs = gop(gdict)
                        octets += octs
                    self.cur.execute("""SELECT group_type1_fn(%s, %s, %s, %s::timestamp without time zone, %s::int[], %s, %s);""" , (group_id, account_id, octets, gdate, classes, octlist, max_class))
                    self.connection.commit()
                else:
                    continue
                
                #write profiling infos
                if flags.writeProf:
                    icount += 1
                    timecount += time.clock() - a
                    if icount == 100:                        
                        logger.info("%s run time(100): %s", (self.getName(), timecount))
                        icount = 0; timecount = 0
            except IndexError, ierr:
                if not gkey:
                    try:    queues.groupLock.release()
                    except: pass
                logger.debug("%s : indexerror : %s", (self.getName(), repr(ierr))) 
                continue
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc())) 
                if ex.__class__ in vars.db_errors:
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
                        
                    try: 
                        time.sleep(3)
                        if self.connection.closed():
                            try:
                                self.connection = get_connection(vars.db_dsn)
                                self.cur = self.connection.cursor()
                            except:
                                time.sleep(20)
                        else:
                            self.cur.connection.commit()
                            self.cur = self.connection.cursor()
                    except: 
                        time.sleep(10)
                        try:
                            self.connection.close()
                        except: pass
                        try:
                            self.connection = get_connection(vars.db_dsn)
                            self.cur = self.connection.cursor()
                        except:
                            time.sleep(20)
                            
                
                
class statDequeThread(Thread):
    '''Thread picks out and sends to the DB global statistics'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__

    def run(self):
        global queues, flags, vars
        self.connection = get_connection(vars.db_dsn)
        self.cur = self.connection.cursor()
        
        icount = 0; timecount = 0
        a = time.clock()
        while True:
                #gdata[1] - group_id, group_dir, group_type
                #gkey[0] - account_id, gkey[2] - date
            try:
                if suicideCondition[self.tname]:
                    try: self.connection.close()
                    except: pass
                    break
                if flags.writeProf:
                    a = time.clock()
                    
                skey, skeyTime, statData = None, None, None
                with queues.statLock:
                    #check whether double aggregation time passed - updates are rather costly
                    if len(queues.statDeque) > 0 and (queues.statDeque[0][1] + vars.STAT_AGGR_TIME*2 < time.time()):
                        skey, skeyTime  = queues.statDeque.popleft()

                if not skey: time.sleep(10); continue
                
                account_id, stime = skey 
                dkey = (int(stime / 667) + account_id) % vars.STAT_DICTS
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
                    
                self.cur.execute("""INSERT INTO billservice_globalstat(account_id, bytes_in, bytes_out, datetime, nas_id, classes, classbytes) 
                                    VALUES(%s, %s, %s, %s::timestamp without time zone, %s, %s::int[], %s::bigint[]);""" , (account_id, octets_in, octets_out, sdate, nas_id, classes, octlist))
                self.connection.commit()
                
                if flags.writeProf:
                    icount += 1
                    timecount += time.clock() - a
                    if icount == 100:                        
                        logger.info("%s run time(100): %s", (self.getName(), timecount))
                        icount = 0; timecount = 0
                        
            except IndexError, ierr:
                if not skey:
                    try:    queues.statLock.release()
                    except: pass
                logger.debug("%s : indexerror : %s", (self.getName(), repr(ierr))) 
                continue
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc())) 
                if ex.__class__ in vars.db_errors:
                    if skey and skeyTime and statData:
                        with aggrsLock:
                            srec = aggrsDict.get(skey)
                            if not srec:
                                aggrsDict[skey] = statData
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
                        if self.connection.closed():
                            try:
                                self.connection = get_connection(vars.db_dsn)
                                self.cur = self.connection.cursor()
                            except:
                                time.sleep(20)
                        else:
                            self.cur.connection.commit()
                            self.cur = self.connection.cursor()
                    except: 
                        time.sleep(10)
                        try:
                            self.connection.close()
                        except: pass
                        try:
                            self.connection = get_connection(vars.db_dsn)
                            self.cur = self.connection.cursor()
                        except:
                            time.sleep(20)
                            
                
            
       
class NetFlowRoutine(Thread):
    '''Thread that handles NetFlow statistic packets and bills according to them'''
    def __init__ (self):
        global vars
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        self.connection = get_connection(vars.db_dsn, vars.NFR_SESSION)
        
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

    def get_prepaid_octets(self, octets_in, prepInf, queues):
        octets = octets_in
        prepaid_left = False
        if prepInf:
            prepaid_id, prepaid = prepInf[0:2]
            if prepaid > 0:  
                prep_octets = 0
                prepaid_left = True
                if prepaid>=octets:
                    #prepaid, octets = prepaid-octets, 0
                    prep_octets, octets = octets, 0
                elif octets>=prepaid:
                    #prepaid, octets = octets-prepaid, abs(prepaid-octets)
                    prep_octets, octets = prepaid, octets-prepaid
                    
                self.cur.execute("""UPDATE billservice_accountprepaystrafic SET size=size-%s WHERE id=%s""", (prep_octets, prepaid_id,))
                self.connection.commit()
                with queues.prepaidLock:
                    prepInf[1] -= prep_octets
        return octets, prepaid_left
    
    def edge_bin_search(self, s_array, value):
        """
        функция производит поиск ближайшего значения в списке
        TODO: переписать!
        """
        if value >= s_array[-1]:
            return len(s_array) - 1
        elif len(s_array) == 1:
            return len(s_array) - 1
        else:
            #lookup_array = s_array
            start_pos = 0
            end_pos = len(s_array) - 1
            while True:
                bin_pos = (end_pos - start_pos) / 2
                if s_array[bin_pos] > value:
                    if (bin_pos - start_pos == 0) or ((bin_pos - 1 >= 0) and s_array[bin_pos - 1] <= value):
                        break
                    else:
                        end_pos = bin_pos
                else:
                    start_pos = bin_pos
        return bin_pos
                                    
            
    def run(self):
        #connection = persist.connection()
        #connection._con.set_client_encoding('UTF8')
        global cacheMaster, vars, flags, queues
        caches = None
        dateAT = datetime.datetime(2000, 1, 1)
        oldAcct = defaultdict(list)
        self.cur = self.connection.cursor()
        icount, timecount = 0, 0
        totaltime = time.clock()
        while True:
            try:   
                if suicideCondition[self.tname]:
                    try: self.connection.close()
                    except: pass
                    break
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
                with queues.pickerLock:
                    #add picker to a depicker queue
                    if (time.time() > queues.pickerTime + vars.PICKER_AGGR_TIME):
                        queues.depickerQueue.append(queues.picker.get_data())
                        queues.picker = Picker()
                        queues.pickerTime = time.time()                    
                if len(queues.nfIncomingQueue) > 0:        
                    with queues.nfQueueLock:
                        if len(queues.nfIncomingQueue) > 0:
                            fpacket, addr = queues.nfIncomingQueue.popleft()
                            
                #flows = loads(fpacket)
                if not fpacket: time.sleep(random.randint(1,10) / 10.0); continue
                '''
                recieved_len = len(fpacket)
                declared_len = reduce(INT_ME_FN, fpacket[:TCP_PACKET_SIZE_HEADER][::-1], (0,1))[0]
                if recieved_len != declared_len:
                    logger.warning('Packet consumer: peer: %s declared %s and recieved %s packet lengths do not match! Packet dropped!', (addr, declared_len, recieved_len))
                    continue
                '''
                try:
                    flows = loads(fpacket)
                    #
                except Exception, ex:
                    logger.info("Packet consumer: peer: %s Bad packet (marshalling problems):%s ; ",(addr, repr(ex)))
                    continue
                #flows = fpacket
                #iterate through them
                for pflow in flows:
                    flow = Flow5Data(False, *pflow)
                    logger.debug("Packet for processing: %s ; ",(repr(flow),))
                    #get account id and get a record from cache based on it
                    acc = caches.account_cache.by_account.get(flow.account_id)
                    if not acc: 
                        logger.info("Account for packet not found: %s ",(repr(flow)))
                        continue
                    if 0: assert isinstance(acc, AccountData)
                    stream_date = datetime.datetime.fromtimestamp(flow.datetime)

                    #if no line in cache, or the collection date is younger then accounttarif creation date
                    #get an acct record from teh database
                    if  (acc.acctf_id  != flow.acctf_id) or ( acc.datetime > stream_date):
                        acc = oldAcct.get(flow.acctf_id)
                        if not acc:
                            self.cur.execute("""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, ba.status   
                                                FROM billservice_account as ba
                                                LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif WHERE account_id=%s ORDER BY datetime DESC LIMIT 1)
                                                LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id;
                                             """, (flow.account_id,))
                            acc = self.cur.fetchone()
                            self.connection.commit()
                            if not acc: 
                                logger.info("Account for packet %s by date %s not found: %s ",(str(flow),str(stream_date),))
                                continue
                            acc = AccountData(*acc)
                            oldAcct[flow.acctf_id] = acc                           
                    
                    #if no tarif_id, tarif.active=False and don't store, account.active=false and don't store    
                    if (acc.tarif_id == None) or (not (acc.tarif_active or vars.STORE_NA_TARIF)) \
                       or (not (acc.account_status == 1 or vars.STORE_NA_ACCOUNT)): continue                    
                    
                    '''Статистика по группам: 
                    аггрегируется в словаре по структурам типа {класс->{'INPUT':0, 'OUTPUT':0}}
                    Ключ - (account_id, group_id, gtime)
                    Ключ затем добавляется в очередь.'''
                    if flow.has_groups and flow.groups:                        
                        gtime = flow.datetime - (flow.datetime % vars.GROUP_AGGR_TIME)                        
                        for group_id, group_classes, group_dir, group_type in flow.groups:
                            #group_id, group_classes, group_dir, group_type  = group
                            #calculate a key and check the dictionary
                            gkey = (flow.account_id, group_id, gtime)
                            dgkey = (int(gtime / 667) + flow.account_id) % vars.GROUP_DICTS
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
                    stime = flow.datetime - (flow.datetime % vars.STAT_AGGR_TIME)
                    skey  = (flow.account_id, stime)
                    dskey = (int(stime / 667) + flow.account_id) % vars.STAT_DICTS
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
                    
                    if acc.traffic_transmit_service_id and flow.has_groups and flow.groups:
                        octets_summ = 0
                        #loop throungh classes in 'classes' tuple
                        tarif_edges = caches.tarifedge_cache.by_tarif.get(acc.tarif_id)
                        group_edge = {}
                        if tarif_edges:
                            group_edge = tarif_edges.group_edges
                        for group_id, group_classes, group_dir, group_type in flow.groups:
                            #get a record from prepays cache
                            prepInf = caches.prepays_cache.by_tts_acctf_group.get((acc.traffic_transmit_service_id, acc.acctf_id, group_id))                            
                            octets, prepaid_left = self.get_prepaid_octets(flow.octets, prepInf, queues)
                            traffic_cost = 0
                            summ = 0
                            if octets > 0:
                                #if group_id in group_edge:
                                if False:
                                    logger.warning("Group id in group_edge")
                                    account_bytes = None
                                    try:
                                        sys.setcheckinterval(sys.maxint)    
                                        account_bytes = queues.accountbytes_cache.by_acctf.get(acc.acctf_id)
                                        if not account_bytes:
                                            account_bytes = AccountGroupBytesData._make(acc.account_id, acc.tarif_id, acc.acctf_id, acc.datetime, {}, Lock(), datetime.datetime.now())
                                            queues.accountbytes_cache.by_acctf[acc.acctf_id] = account_bytes
                                    finally:
                                        sys.setcheckinterval(100)
                                    if not account_bytes:
                                        logger.warning("Account_bytes not resolved for acc %s", acc)
                                        break
                                    tg_bytes = 0
                                    tg_datetime, tg_current, tg_next = None, None, None
                                    with account_bytes.lock:
                                        gbytes = account_bytes.group_data.get(group_id)
                                        if not gbytes:
                                            gbytes = GroupBytesDictData._make((0,))
                                            account_bytes.group_data[group_id] = gbytes
                                        if prepaid_left and gbytes.bytes != 0:
                                            gbytes.bytes = 0
                                        tg_bytes = gbytes.bytes
                                        gbytes.bytes += octets                                        
                                        #tg_datetime, tg_current, tg_next = gbytes.tg_current, gbytes.tg_next
                                        account_bytes.last_accessed = datetime.datetime.now()
                                        
                                    #get tarif info
                                    group_edges = group_edge[group_id]
                                    edge_octets = []
                                    pay_bytes = octets
                                    cur_edge_pos = self.edge_bin_search(group_edges, tg_bytes)
                                    while True:
                                        edge_val = group_edges[cur_edge_pos] * MEGABYTE
                                        if (pay_bytes + tg_bytes <= edge_val) or (cur_edge_pos + 1 >= len(group_edges)):
                                            edge_octets.append((group_edges[cur_edge_pos], pay_bytes))
                                            break
                                        else:
                                            pre_edge_bytes = edge_val - (pay_bytes + tg_bytes)
                                            tg_bytes += pre_edge_bytes
                                            pay_bytes -= pre_edge_bytes
                                            cur_edge_pos += 1
                                    for edge_fval, pay_fbytes in edge_octets:
                                        nodes = caches.nodes_cache.by_tts_group_edge.get((acc.traffic_transmit_service_id, group_id, edge_fval))
                                        trafic_cost = self.get_actual_cost(pay_fbytes, stream_date, nodes) if nodes else 0
                                        summ += (trafic_cost * pay_fbytes) / MEGABYTE    
                                        
                                else:        
                                    nodes = caches.nodes_cache.by_tts_group.get((acc.traffic_transmit_service_id, group_id))
                                    trafic_cost = self.get_actual_cost(octets_summ, stream_date, nodes) if nodes else 0
                                    summ = (trafic_cost * octets) / MEGABYTE
        
                            if summ != 0:
                                with queues.pickerLock:
                                    queues.picker.add_summ(acc.traffic_transmit_service_id, acc.acctf_id, acc.account_id, summ)

                if flags.writeProf:
                    icount += 1
                    timecount += time.clock() - a
                    if icount == 100:                        
                        logger.info("%s run time(100): %s, totaltime: %s", (self.getName(), timecount, time.clock() - totaltime))
                        icount = 0; timecount = 0
                        totaltime = time.clock()
                        
            except IndexError, ierr:
                logger.debug("%s : indexerror : %s, %s", (self.getName(), repr(ierr), traceback.format_exc())) 
                if not fpacket: 
                    time.sleep(random.randint(10,20))
                    logger.debug("%s : indexerror : %s", (self.getName(), repr(ierr))) 
                else:
                    logger.debug("%s : indexerror : %s, %s", (self.getName(), repr(ierr), traceback.format_exc())) 
                continue               
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc())) 
                if ex.__class__ in vars.db_errors:
                    try: 
                        time.sleep(3)
                        self.cur.connection.commit()
                        self.cur = self.connection.cursor()
                    except: 
                        time.sleep(10)
                        try:
                            self.connection.close()
                        except: pass
                        try:
                            self.connection = get_connection(vars.db_dsn, vars.NFR_SESSION)
                            self.cur = self.connection.cursor()
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
        global suicideCondition, cacheMaster, flags, vars, queues, threads, cacheThr
        self.connection = get_connection(vars.db_dsn)
        counter = 0; now = datetime.datetime.now
        while True:
            if suicideCondition[self.__class__.__name__]: 
                try:    self.connection.close()
                except: pass
                break
            a = time.clock()
            try: 
                time_run = (now() - cacheMaster.date).seconds > vars.CACHE_TIME
                if flags.cacheFlag or time_run:
                    run_time = time.clock()                    
                    cur = self.connection.cursor()
                    renewCaches(cur, cacheMaster, NfroutineCaches, 21, (fMem, cacheMaster.first_time))
                    cur.close()
                    if counter == 0 or time_run:
                        allowedUsersChecker(allowedUsers, lambda: len(cacheMaster.cache.account_cache.data), ungraceful_save, flags)
                        if not flags.allowedUsersCheck: continue
                        counter = 0
                        #flags.allowedUsersCheck = True
                        flags.writeProf = logger.writeInfoP()
                        if flags.writeProf:        
                            logger.info("incoming queue len: %s", len(queues.nfIncomingQueue))
                            logger.info("groupDictLen: %s", '('+ ', '.join((str(len(dct)) for dct in queues.groupAggrDicts)) + ')')
                            logger.info("groupDequeLen: %s", (len(queues.groupDeque)))
                            logger.info("statDictLen: %s", '('+ ', '.join((str(len(dct)) for dct in queues.statAggrDicts)) + ')')
                            logger.info("statDequeLen: %s", len(queues.statDeque))
                          
                    if cacheMaster.first_time:
                        cacheMaster.first_time = False
                        queues.accountbytes_cache = cacheMaster.cache.accountbytes_cache
                        
                    if counter == 5:
                        counter, fMem.periodCache = 0, {}
                        '''
                        if (len(queues.nfIncomingQueue) > 1000) or (len(queues.statDeque) > len(cacheMaster.cache.account_cache.data) * 10):
                            if not vars.sendFlag or vars.sendFlag!='SLP!':
                                vars.sendFlag = 'SLP!'
                                logger.lprint('Sleep flag set!')                        
                        else:
                            if vars.sendFlag and vars.sendFlag=='SLP!':
                                vars.sendFlag = ''
                                logger.lprint('Sleep flag unset!')
                        '''
                            
                        th_status = ';'.join((thrd.getName().split(' ')[0] + (thrd.isAlive() and 'OK') or 'NO' for thrd in threads + [cacheThr]))
                        logger.warning('THREAD STATUS: %s', th_status)

                    counter += 1
                    if flags.cacheFlag:
                        with flags.cacheLock: flags.cacheFlag = False
                    
                    logger.info("ast time : %s", time.clock() - run_time)
            except Exception, ex:
                logger.error("%s : #30210004 : %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(ex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(20)
            
            
class NfTwistedServer(DatagramProtocol):
    '''
    Twisted Asynchronous server that recieves datagrams with NetFlow packets
    and appends them to 'nfQueue' queue.
    '''
    def __init__(self):
        super(NfTwistedServer, self).__init__()
        self.last_addr  = None
        self.last_index = None
        self.last_timestamp = 0

    def datagramReceived(self, data, addrport):
        try:
            if not vars.ALLOWED_NF_IP_LIST or addrport[0] not in vars.ALLOWED_NF_IP_LIST:
                logger.info("IP not in list, packet discarded %s", str(addrport))
                self.transport.write('ERR!', addrport)
                return
            if len(data) < NFR_PACKET_HEADER_LEN:
                logger.info("Bad packet (too small) from %s", str(addrport))
                self.transport.write('BAD!', addrport)
                return
            try:
                cur_index, cur_state, cur_timestamp = struct.unpack(NFR_PACKET_HEADER_FMT, data[:NFR_PACKET_HEADER_LEN])
            except Exception, ex:
                logger.info("Bad packet (strange header) from %s ; " + repr(ex), str(addrport))
                self.transport.write('BAD!', addrport)
                return
            if self.last_addr != addrport[0]:
                queues.lastPacketInfo[self.last_addr] = (self.last_index, self.last_timestamp)
                self.last_addr = addrport[0]
                self.last_index, self.last_timestamp = queues.lastPacketInfo[self.last_addr]
            if self.last_index == cur_index or self.last_timestamp < cur_timestamp:
                logger.info("Duplicate packet from %s", str(addrport))
                self.transport.write('DUP!', addrport)
                return            
            try:
                flows = loads(data[NFR_PACKET_HEADER_LEN:])
            except Exception, ex:
                logger.info("Bad packet (marshalling problems) from %s ; " + repr(ex), str(addrport))
                self.transport.write('BAD!', addrport)
                return
                 
            
            self.last_index     = cur_index
            self.last_timestamp = cur_timestamp
            with queues.nfQueueLock:
                queues.nfIncomingQueue.append(flows)
            self.transport.write(vars.sendFlag + str(len(data) - NFR_PACKET_HEADER_LEN), addrport)
            #self.socket.sendto(vars.sendFlag + str(len(data)), addrport)
            
        except:            
            logger.error("Twisted Server Error : #30210701 : %s \n %s", (repr(ex), traceback.format_exc()))

class TCP_LineReciever(LineReceiver):
    delimiter = '--NFRP--'
    
    '''
    def connectionMade(self):
        print 'conn', self, self.transport.getHost(), self.transport.getPeer(), self.transport.hostname
    '''    
    def lineReceived(self, line):
        queues.nfIncomingQueue.append((line, self.transport.getPeer()))
        '''
        with queues.nfQueueLock:
            queues.nfIncomingQueue.append((flows, self.transport.getPeer()))'''
        '''    
        if vars.sendFlag:
            self.transport.write(vars.sendFlag)'''
        
class TCP_IntStringReciever(Int32StringReceiver):    
    peer__ = ''
    def connectionMade(self):
        logger.info("SERVER: connectionMade: host: %s | peer: %s", (self.transport.getHost(), self.transport.getPeer()))
        self.peer__ = self.transport.getPeer()
        
    def stringReceived(self, msg):
        queues.nfIncomingQueue.append((msg, self.peer__))
        
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

    for thr in threads:
            suicideCondition[thr.tname] = True
    time.sleep(2)
    
    queues.depickerLock.acquire()
    queues.groupLock.acquire()
    queues.statLock.acquire()
    graceful_saver([['depickerQueue'], ['nfIncomingQueue'], ['groupDeque', 'groupAggrDicts'], ['statDeque', 'statAggrDicts']],
                   queues, 'nfroutine_', vars.SAVE_DIR)
    time.sleep(3)
    queues.statLock.release()
    queues.groupLock.release()
    queues.depickerLock.release()
    time.sleep(16)
    rempid(vars.piddir, vars.name)
    logger.lprint(vars.name + " stopping gracefully.")
    print vars.name + " stopping gracefully."

def graceful_recover():
    global queues, vars
    graceful_loader(['depickerQueue','nfIncomingQueue', ['groupDeque', 'groupAggrDicts'], ['statDeque', 'statAggrDicts']],
                    queues, 'nfroutine_', vars.SAVE_DIR)
    

def ungraceful_save():
    global cacheThr, threads, suicideCondition, vars
    from twisted.internet import reactor
    reactor.callFromThread(reactor.disconnectAll)
    reactor.callFromThread(reactor.stop)
    reactor._started = False
    suicideCondition[cacheThr.tname] = True
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    rempid(vars.piddir, vars.name)
    print "NFR: exiting"
    logger.lprint("NFR exiting.")
    sys.exit()
    
def main():
    if vars.RECOVER:
        graceful_recover()
    global cacheMaster, suicideCondition
    global threads, cacheThr, NfAsyncUDPServer
    threads=[]
    for i in xrange(vars.ROUTINE_THREADS):
        newNfr = NetFlowRoutine()
        newNfr.setName('NFR:#%i: NetFlowRoutine' % i)
        threads.append(newNfr)
    for i in xrange(vars.GROUPSTAT_THREADS):
        grdqTh = groupDequeThread()
        grdqTh.setName('GDT:#%i: groupDequeThread' % i)
        threads.append(grdqTh)
    for i in xrange(vars.GLOBALSTAT_THREADS):
        stdqTh = statDequeThread()
        stdqTh.setName('SDS:#%i: statDequeThread' % i)
        threads.append(stdqTh)
    for i in xrange(vars.BILL_THREADS):
        depTh = DepickerThread()
        depTh.setName('DET:#%i: billThread' % i)
        threads.append(depTh)
    
    cacheThr = AccountServiceThread()
    cacheThr.setName('AST: AccountServiceThread')
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.start()
    
    time.sleep(2)
    while cacheMaster.read is False:        
        if not cacheThr.isAlive:
            print 'Exception in cache thread: exiting'
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
    
    if   vars.SOCK_TYPE == 0:
        #reactor.listenUDP(vars.PORT, NfTwistedServer(), maxPacketSize=vars.MAX_DATAGRAM_LEN)
        fact = Factory()
        #fact.protocol = TCP_LineReciever
        fact.protocol = TCP_IntStringReciever
        p = reactor.listenTCP(vars.PORT, fact)
        logger.info("Listening on: %s", p.getHost())
    elif vars.SOCK_TYPE == 1:
        #reactor.listenUNIXDatagram(vars.ADDR, NfTwistedServer(), maxPacketSize=vars.MAX_DATAGRAM_LEN)
        fact = Factory()
        #fact.protocol = TCP_LineReciever
        fact.protocol = TCP_IntStringReciever
        try:
            os.unlink(vars.HOST)
        except Exception, ex:
            logger.warning('NFR: previous unix socket removal status: %s', repr(ex))
        reactor.listenUNIX(vars.HOST, fact)
    else: 
        raise Exception("Unknown socket type!")
    
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
    
    suicideCondition = {}

    try:
        import psyco
        #psyco.log()
        psyco.full(memory=100)
        #psyco.profile(0.05, memory=100)
        #psyco.profile(0.2)

        flags = NfrFlags()
        vars  = NfrVars()
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME, net_name=NET_NAME)
        
        queues= NfrQueues(vars.GROUP_DICTS, vars.STAT_DICTS)
        
        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file)
        saver.log_adapt = logger.log_adapt
        utilites.log_adapt = logger.log_adapt
        install_logger(logger)
        logger.info("Config variables: %s", repr(vars))
        logger.lprint(vars.name + ' start')
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)
                

        #temp save on restart or graceful stop
        #store stat. for old tarifs and accounts?

        #write profiling info?
        flags.writeProf = logger.writeInfoP()         
        #--------------------------------------------------------  
        
        queues.picker = Picker()
        queues.pickerTime = time.time() + 5
        
        #function that returns number of allowed users
        #create allowedUsers
        if not globals().has_key('_1i'):
            _1i = lambda: ''
        allowedUsers = setAllowedUsers(_1i())       
        allowedUsers()
        
        fMem = pfMemoize()    
    
        #-------------------
        print "ebs: nfroutine: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nfroutine, exiting: ', repr(ex)
        logger.error('Exception in nfroutine, exiting: %s \b %s', (repr(ex), traceback.format_exc()))