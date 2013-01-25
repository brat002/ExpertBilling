#-*-coding=utf-8-*-

from __future__ import with_statement
import site
site.addsitedir('/opt/ebs/venv/lib/python2.6/site-packages')
site.addsitedir('/opt/ebs/venv/lib/python2.7/site-packages')
import sys
sys.path.insert(0, "modules")
sys.path.append("cmodules")
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
from threading import Thread, Lock
from copy import copy, deepcopy
from collections import deque, defaultdict
from period_utilities import in_period_info
from saver import graceful_loader, graceful_saver
from db import traffictransaction, TraftransTableException, GpstTableException
from bisect import bisect_left


from decimal import Decimal
from classes.nfroutine_cache import *
from classes.common.Flow5Data import Flow5Data
from classes.cacheutils import CacheMaster
from classes.flags import NfrFlags
from classes.vars import NfrVars, NfrQueues, install_logger
from utilites import renewCaches, savepid, rempid, get_connection, getpid, check_running, \
                     STATE_NULLIFIED, STATE_OK, NFR_PACKET_HEADER_FMT
from utilites import settlement_period_info
#from dirq.QueueSimple import QueueSimple
#from saver import RedisQueue

from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall
from kombu import Connection
from queues import nf_out

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

NFR_PACKET_HEADER_LEN  = 16
TCP_PACKET_SIZE_HEADER = 5
NAME = 'nfroutine'
DB_NAME = 'db'
NET_NAME = 'nfroutine_nf'
MEGABYTE =1048576 
INT_ME_FN = lambda xt, y: (xt[0] + (ord(y) - 48) * xt[1], xt[1] * 10)

  
class Worker(ConsumerMixin):

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=nf_out,
                         callbacks=[self.process_task])]

    def process_task(self, body, message):
        data = body['data']
        try:
            queues.nfIncomingQueue.append(data)
        except Exception, ex:
            logger.error("NFR exception: %s \n %s", (repr(ex), traceback.format_exc()))
        finally:
            message.ack()
            
class groupDequeThread(Thread):
    '''Тред выбирает и отсылает в БД статистику по группам-пользователям'''
    def __init__ (self, retarificate=False, date_start=None, date_end=None):
        Thread.__init__(self)
        self.retarificate = retarificate
        self.date_start = date_start
        self.date_end = date_end
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

    def get_prepaid_octets(self, octets_in, prepInf, queues, force_db=False):
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
                    
                self.cur.execute("""UPDATE billservice_accountprepaystrafic SET size=size-(%s) WHERE id=%s""", (prep_octets, prepaid_id,))
                #self.connection.commit()
                if force_db==False:
                    with queues.prepaidLock:
                        prepInf[1] -= prep_octets
        return octets, prepaid_left    

    def tarificate(self, account_id, acctf_id, acctd_datetime,  tariff_id, traffic_transmit_service_id, group_id, octets, gdate, force_db=False):
        if not traffic_transmit_service_id: return
        octets_summ = 0
        #loop throungh classes in 'classes' tuple
        tarif_edges = self.caches.tarifedge_cache.by_tarif.get(tariff_id)
        group_edge = {}
        if tarif_edges:
            group_edge = tarif_edges.group_edges

        #get a record from prepays cache
        if force_db==True:
            self.cur.execute("""
                    SELECT prepais.id, prepais.size
                    FROM billservice_accountprepaystrafic as prepais
                     JOIN billservice_prepaidtraffic as prepaidtraffic ON prepaidtraffic.id=prepais.prepaid_traffic_id
                      WHERE prepais.size>0 and account_tarif_id=%s and prepaidtraffic.group_id=%s and current=True;
            """, (acctf_id, group_id))
            prepInf = self.cur.fetchone()
        else:
            prepInf = self.caches.prepays_cache.by_tts_acctf_group.get((traffic_transmit_service_id, acctf_id, group_id))                            
        octets, prepaid_left = self.get_prepaid_octets(octets, prepInf, queues, force_db)
        traffic_cost = 0
        summ = 0
        if octets > 0:
            #if group_id in group_edge:
            if False:
                logger.warning("Group id in group_edge")
                account_bytes = None
                try:
                    sys.setcheckinterval(sys.maxint)    
                    account_bytes = queues.accountbytes_cache.by_acctf.get(acctf_id)
                    if not account_bytes:
                        account_bytes = AccountGroupBytesData._make(account_id, tariff_id, acctf_id, acctd_datetime, {}, Lock(), datetime.datetime.now())
                        queues.accountbytes_cache.by_acctf[acctf_id] = account_bytes
                finally:
                    sys.setcheckinterval(100)
                if not account_bytes:
                    logger.warning("Account_bytes not resolved for acc %s", account_id)
                    return
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
                cur_edge_pos = bisect_left(group_edges, tg_bytes)
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
                    nodes = self.caches.nodes_cache.by_tts_group_edge.get((traffic_transmit_service_id, group_id, edge_fval))
                    trafic_cost = self.get_actual_cost(pay_fbytes, gdate, nodes) if nodes else 0
                    summ += (trafic_cost * pay_fbytes) / MEGABYTE    
                    
            else:        
                nodes = self.caches.nodes_cache.by_tts_group.get((traffic_transmit_service_id, group_id))
                trafic_cost = self.get_actual_cost(octets_summ, gdate, nodes) if nodes else 0
                summ = (trafic_cost * octets) / MEGABYTE
                
        logger.info("traffic_transmit_service_id=%s acctf_id=%s account_id=%s bytes=%s traffic_cost=%s summ=%s", (traffic_transmit_service_id, acctf_id, account_id, octets, trafic_cost, summ))
        if summ <> 0:
            logger.debug("Tarificate group bytes traffic_transmit_service_id=%s, acctf_id=%s, account_id=%s, summ=%s, created=%s",  (traffic_transmit_service_id, acctf_id, account_id, summ, gdate,))
            return traffictransaction(self.cur, traffic_transmit_service_id, acctf_id, account_id, summ=summ, created=gdate)

    def run(self):
        global CacheMaster, queues, flags, vars
        dateAT = datetime.datetime(2000, 1, 1)
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

                if cacheMaster.date > dateAT:
                    cacheMaster.lock.acquire()
                    try:
                        self.caches = cacheMaster.cache
                        dateAT = deepcopy(cacheMaster.date)
                    except Exception, ex:
                        logger.error("%s: cache exception: %s", (self.getName, repr(ex)))
                    finally:
                        cacheMaster.lock.release()

                if self.retarificate:
                    add_prepaid = []

                    #Делаем выборку статистики, попавшей в диапазон
                    self.cur.execute("""
                    SELECT id, group_id, account_id, bytes, datetime, 
                    COALESCE(accounttarif_id, (SELECT id FROM billservice_accounttarif WHERE account_id=gpst.account_id and datetime<gpst.datetime ORDER by datetime DESC limit 1)), transaction_id
                    FROM billservice_groupstat as gpst WHERE datetime between %s and %s ORDER BY account_id, datetime;
                      """, (self.date_start, self.date_end))
                    for item in self.cur.fetchall():
                        #print item
                        _id, _group_id, _account_id, _bytes, _datetime, _accounttarif_id, _transaction_id = item
                        gdate = _datetime
                        gkey = None
                        accsdata = self.caches.accounttariff_traf_service_cache.by_accounttariff.get(_accounttarif_id)
                        if _accounttarif_id not in add_prepaid:
                            print "delete transactions"
                            self.cur.execute("DELETE from billservice_traffictransaction WHERE created between %s and %s and  accounttarif_id=%s", (self.date_start, self.date_end, _accounttarif_id, ))
                            #Сбросили предоплаченный трафик товарищам, попавшим в указанный диапазон
                            print "select prepaistraffic"
                            self.cur.execute("SELECT id, datetime from billservice_accountprepaystrafic WHERE current=True and account_tarif_id=%s", (_accounttarif_id, ))
                            d = self.cur.fetchone()
                            if d:
                                prep_id, prep_date=d
                                print "delete prepaistraffic"
                                self.cur.execute("DELETE from billservice_accountprepaystrafic WHERE account_tarif_id=%s", (_accounttarif_id, ))
                                #начисляем предоплаченный трафик
                                print "add prepaid"
                                delta_coef=1
                                acc = self.caches.account_cache.by_account.get(_account_id)
                                sp = self.caches.settlement_cache.by_id.get(acc.settlement_period_id)

                                time_start = acc.datetime if sp.autostart else sp.time_start
                                period_start, period_end, delta = fMem.settlement_period_(time_start, sp.length_in, sp.length, _datetime)
                                if period_end and ((period_end-acc.datetime).days*86400+(period_end-acc.datetime).seconds)<delta and vars.USE_COEFF_FOR_PREPAID==True:
                                    delta_coef=float((period_end-acc.datetime).days*86400+(period_end-acc.datetime).seconds)/float(delta)                                
                                self.cur.execute("SELECT shedulelog_tr_credit_fn(%s, %s, %s, %s, %s, %s::timestamp without time zone);", 
                                        (_account_id, _accounttarif_id, accsdata.traffic_transmit_service_id, True, delta_coef, prep_date))
                            add_prepaid.append(_accounttarif_id)

                        
                        transaction_id = self.tarificate(_account_id, _accounttarif_id, accsdata.tariff_id, accsdata.traffic_transmit_service_id, _group_id, _bytes, _datetime, force_db=True)
                        if transaction_id:
                            self.cur.execute("UPDATE billservice_groupstat SET transaction_id=%s WHERE id=%s ", (transaction_id, _id))
                        elif _transaction_id:
                            self.cur.execute("UPDATE billservice_groupstat SET transaction_id=NULL WHERE id=%s ", (_id, ))

                    self.cur.connection.commit()

                    
                    sys.exit()
                gkey, gkeyTime, groupData = None, None, None
                with queues.groupLock:
                    #check whether double aggregation time passed - updates are rather costly
                    if len(queues.groupDeque) > 0 and (queues.groupDeque[0][1] + vars.GROUP_AGGR_TIME*2 < time.time()):
                        gkey, gkeyTime  = queues.groupDeque.popleft()

                if not gkey: time.sleep(10); continue

                #get data
                accounttarif_id, kgroup_id, gtime = gkey 
                dkey = (int(gtime / 667) + accounttarif_id) % vars.GROUP_DICTS
                #получить account_id Для вставки!!!
                aggrgDict = queues.groupAggrDicts[dkey]
                aggrgLock = queues.groupAggrLocks[dkey]
                with aggrgLock:
                    groupData = aggrgDict.pop(gkey, None)
                    
                if not groupData:
                    logger.info('%s: no groupdata for key: %s', (self.getName(), gkey))
                    continue
                
                accsdata = self.caches.accounttariff_traf_service_cache.by_accounttariff.get(accounttarif_id)
                if not accsdata: continue
                account_id = accsdata.account_id
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
                #if group_type == 2:
                if True:             
                    """
                    Место, где определяется максимальный класс
                    """           
                    if group_type==2:
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
                    elif group_type == 1:
                        for class_, gdict in groupItems.iteritems():
                            octs = gop(gdict)
                            octets += octs
                            classes.append(class_)
                            octlist.append(octs)
                                      
                    transaction_id = self.tarificate(accsdata.account_id, accsdata.id, None, accsdata.tariff_id, accsdata.traffic_transmit_service_id, group_id, octets, gdate, force_db=True)
                    try:
                        self.cur.execute("""INSERT INTO gpst%s""" % gdate.strftime("%Y%m01")+""" (group_id, account_id, bytes, datetime, classes, classbytes, max_class, accounttarif_id, transaction_id) 
                        VALUES (%s, %s, %s, %s, %s, %s , %s, %s, %s);""", (group_id, account_id, octets, gdate, classes, octlist, max_class, accsdata.id, transaction_id))
                    except psycopg2.ProgrammingError, e:
                        if e.pgcode=='42P01':
                            raise GpstTableException()

                        else:
                            self.connection.rollback()
                            raise e
                    self.connection.commit()

                
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
            except TraftransTableException, ex:
                logger.info("%s : traftrans table not exists. Creating", (self.getName(),  )) 
                self.connection.rollback()
                try:
                    self.cur.execute("SELECT traftrans_crt_pdb(%s::date)", (gdate,))
                    self.connection.commit()
                except Exception, ex:
                    logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc())) 
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
            except GpstTableException, ex:
                logger.info("%s : gpst table not exists. Creating", (self.getName(),  )) 
                self.connection.rollback()
                try:
                    self.cur.execute("SELECT gpst_crt_pdb(%s::date)", (gdate,))
                    self.connection.commit()
                except Exception, ex:
                    logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc())) 
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
        global queues, flags, vars, CacheMaster, queues

        dateAT = datetime.datetime(2000, 1, 1)
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
                if cacheMaster.date > dateAT:
                    cacheMaster.lock.acquire()
                    try:
                        self.caches = cacheMaster.cache
                        dateAT = deepcopy(cacheMaster.date)
                    except Exception, ex:
                        logger.error("%s: cache exception: %s", (self.getName, repr(ex)))
                    finally:
                        cacheMaster.lock.release()                    
                skey, skeyTime, statData = None, None, None
                with queues.statLock:
                    #check whether double aggregation time passed - updates are rather costly
                    if len(queues.statDeque) > 0 and (queues.statDeque[0][1] + vars.STAT_AGGR_TIME*2 < time.time()):
                        skey, skeyTime  = queues.statDeque.popleft()

                if not skey: time.sleep(10); continue
                
                accounttarif_id, stime = skey 
                dkey = (int(stime / 667) + accounttarif_id) % vars.STAT_DICTS
                #получить account_id Для вставки в БД!!!
                aggrsDict = queues.statAggrDicts[dkey]
                aggrsLock = queues.statAggrLocks[dkey]
                with aggrsLock:
                    statData = aggrsDict.pop(skey, None)
                    
                if not statData:
                    logger.info('%s: no statdata for key: %s', (self.getName(), skey))
                    continue
                
                accsdata = self.caches.accounttariff_traf_service_cache.by_accounttariff.get(accounttarif_id)
                if not accsdata: continue
                account_id = accsdata.account_id
                
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
                                    VALUES(%s, %s, %s, %s::timestamp without time zone, %s, %s::bigint[], %s::bigint[]);""" , (account_id, octets_in, octets_out, sdate, nas_id, classes, octlist))
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
                                 
                if len(queues.nfIncomingQueue) > 0:        
                    with queues.nfQueueLock:
                        if len(queues.nfIncomingQueue) > 0:
                            fpacket= queues.nfIncomingQueue.popleft()
                            
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
                    logger.info("Packet consumer: peer: %s Bad packet (marshalling problems):%s ; ",(repr(ex)))
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
                                                LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif WHERE account_id=%s and datetime<%s  ORDER BY datetime DESC LIMIT 1)
                                                LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id;
                                             """, (flow.account_id, stream_date,))
                            acc = self.cur.fetchone()
                            self.connection.commit()
                            if not acc: 
                                logger.info("Account for packet %s by date %s not found ",(str(flow),str(stream_date),))
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
                            gkey = (flow.acctf_id, group_id, gtime)
                            dgkey = (int(gtime / 667) + flow.acctf_id) % vars.GROUP_DICTS
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
                    skey  = (flow.acctf_id, stime)
                    dskey = (int(stime / 667) + flow.acctf_id) % vars.STAT_DICTS
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

                    #WTF??? tarif_mode = caches.period_cache.in_period.get(acc.traffic_transmit_service_id, False) if acc.traffic_transmit_service_id else False
                    

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
    __slots__ = ('periodCache', 'settlementCache')
    def __init__(self):
        self.periodCache = {}
        self.settlementCache ={}
        
    def in_period_(self, time_start, length, repeat_after, date_):
        res = self.periodCache.get((time_start, length, repeat_after, date_))
        if res==None:
            res = in_period_info(time_start, length, repeat_after, date_)
            self.periodCache[(time_start, length, repeat_after, date_)] = res
        return res
    
    def settlement_period_(self, time_start, length, repeat_after, stream_date):
        res = self.settlementCache.get((time_start, length, repeat_after, stream_date))
        if res is None:
            res = settlement_period_info(time_start, length, repeat_after, stream_date)
            self.settlementCache[(time_start, length, repeat_after, stream_date)] = res
        return res
    
class AccountServiceThread(Thread):
    '''Handles simultaniously updated READ ONLY caches connected to account-tarif tables'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
    
    def run(self):
        global suicideCondition, cacheMaster, flags, vars, queues, threads, cacheThr, in_dirq
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
            

class nfDequeThread(Thread):
    '''Thread that gets packets received by the server from nfQueue queue and puts them onto the conveyour
    that gets flows and caches them.'''
    
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
    

    def run(self):
        while True:
            global in_dirq
            #TODO: make connection with SimpleReconnectionStrategy
            try:


                with Connection(vars.kombu_dsn) as conn:
                    Worker(conn).run()
                
                time.sleep(0.5)
            except IndexError, ierr:
                time.sleep(3); continue  
            except Exception, ex:
                logger.error("NFP exception: %s \n %s", (repr(ex), traceback.format_exc()))

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
        
        
def ddict_IO():
    return {'INPUT':0, 'OUTPUT':0}

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

    suicideCondition[cacheThr.tname] = True
    logger.lprint("About to exit gracefully.")
    st_time = time.time()

    for thr in threads:
            suicideCondition[thr.tname] = True
    time.sleep(2)
    

    queues.groupLock.acquire()
    queues.statLock.acquire()
    #graceful_saver([['depickerQueue'], ['nfIncomingQueue'], ['groupDeque', 'groupAggrDicts'], ['statDeque', 'statAggrDicts']],
    #               queues, 'nfroutine_', vars.SAVE_DIR)

    queues.statLock.release()
    queues.groupLock.release()

    rempid(vars.piddir, vars.name)
    logger.lprint(vars.name + " stopping gracefully.")
    print vars.name + " stopping gracefully."

def graceful_recover():
    global queues, vars
    #graceful_loader(['depickerQueue','nfIncomingQueue', ['groupDeque', 'groupAggrDicts'], ['statDeque', 'statAggrDicts']],
    #                queues, 'nfroutine_', vars.SAVE_DIR)
    

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
    if os.path.exists("/opt/ebs/data/retarificate.ini"):
        print "Retarificate instructions file found /opt/ebs/data/retarificate.ini"
        print "parsing"
        import ConfigParser
        import datetime
        config = ConfigParser.ConfigParser()
        config.read("/opt/ebs/data/retarificate.ini")
        print dir(datetime)
        
        date_start = datetime.datetime(*(time.strptime(config.get("data", "date_start"), "%d.%m.%Y %H:%M:%S")[0:6]))
        date_end = datetime.datetime(*(time.strptime(config.get("data", "date_end"), "%d.%m.%Y %H:%M:%S")[0:6]))
        print "from %s to %s" % (date_start, date_end)
        grdqTh = groupDequeThread(retarificate=True, date_start=date_start, date_end=date_end)
        grdqTh.setName('GDT:#%i: groupDequeThread' %1)
        threads.append(grdqTh)
    else:
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

    
    cacheThr = AccountServiceThread()
    cacheThr.setName('AST: AccountServiceThread')
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.start()
    time.sleep(2)
    dThr = nfDequeThread()
    dThr.setName('INPUT The: QueueProcessThread')
    suicideCondition[dThr.__class__.__name__] = False
    dThr.start()
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
    
    try:
        signal.signal(signal.SIGINT, SIGSIGINT_handler)
    except: logger.lprint('NO SIGINT!')
    
    print "ebs: nfroutine: started"
    savepid(vars.piddir, vars.name)
    #reactor.run(installSignalHandlers=False)

#===============================================================================

    
if __name__ == "__main__":

    cacheMaster = CacheMaster()
    
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")
    
    suicideCondition = {}
    Watcher()
    try:
        import psyco
        psyco.full(memory=100)
    except:
        print "psyco not available. programm will run slowly" 
    try:
        #psyco.log()
        
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
        
        
        #function that returns number of allowed users
        #create allowedUsers
        if not globals().has_key('_1i'):
            _1i = lambda: ''

        fMem = pfMemoize()    
    
        #-------------------
        print "ebs: nfroutine: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nfroutine, exiting: ', repr(ex)
        logger.error('Exception in nfroutine, exiting: %s \b %s', (repr(ex), traceback.format_exc()))