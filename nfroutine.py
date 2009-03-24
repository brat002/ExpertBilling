#-*-coding=utf-8-*-


import cPickle
import signal
import asyncore
import threading
import ConfigParser
import psycopg2, psycopg2.extras
import time, datetime, os, sys, gc, traceback

import isdlogger
import saver

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
from saver import allowedUsersChecker, setAllowedUsers, graceful_loader, graceful_saver
from db import transaction, transaction_noret, ps_history, get_last_checkout, time_periods_by_tarif_id, set_account_deleted

try:    import mx.DateTime
except: print 'cannot import mx'

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)



class Picker(object):
    __slots__= ('data',)
    def __init__(self):
        self.data=defaultdict(int)      

    def add_summ(self, account, tarif, summ):
        self.data[(account, tarif)] += summ

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
        global depickerQueue, depickerLock, suicideCondition
        while True:
            if suicideCondition[self.tname]: break
            try:
                if len(depickerQueue) > 0:
                    depickerLock.acquire()
                    picker = depickerQueue.popleft()
                    depickerLock.release()
                else:
                    time.sleep(10)
                    continue                
                
                a = time.clock()
                now = datetime.datetime.now()
                icount = 0
                
                #ilist = picker.get_list()
                #ilen = len(picker.data)
                ilist = picker
                ilen = len(picker)
                for acc_tf_id, summ in ilist:
                    #debit accounts
                    transaction_noret(cursor=cur, type='NETFLOW_BILL', account=acc_tf_id[0], approved=True,
                                tarif=acc_tf_id[1], summ=summ, description=u"", created=now)
                    icount += 1
                    connection.commit()
                if writeProf:
                    logger.info("%s icount: %s run time: %s", (self.getName(), icount, time.clock() - a))
            except IndexError, ierr:
                try: depickerLock.release()
                except: pass
                time.sleep(60)
                logger.debug("%s : indexerror : %s", (self.getName(), repr(ierr))) 
                continue             
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError) or isinstance(ex, psycopg2.ProgrammingError) or isinstance(ex, psycopg2.InterfaceError):
                    try: cur = connection.cursor()
                    except: pass
                logger.error("%s : exception: %s", (self.getName(), repr(ex)))    
  
class groupDequeThread(Thread):
    '''Тред выбирает и отсылает в БД статистику по группам-пользователям'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__

    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        cur = connection.cursor()
        global groupAggrDict, groupAggrTime
        global groupDeque, groupLock
        #direction type->operations
        gops = {1: lambda xdct: xdct['INPUT'], 2: lambda xdct: xdct['OUTPUT'] , 3: lambda xdct: xdct['INPUT'] + xdct['OUTPUT'], 4: lambda xdct: max(xdct['INPUT'], xdct['OUTPUT'])}
        global writeProf
        icount = 0; timecount = 0
        while True:
                #gdata[1] - group_id, group_dir, group_type
                #gkey[0] - account_id, gkey[2] - date
            try:
                if suicideCondition[self.tname]: break
                if writeProf:
                    a = time.clock()
                groupLock.acquire()
                gqueue = 1
                

                #check whether double aggregation time passed - updates are rather costly
                if groupDeque and (groupDeque[0][1] + groupAggrTime*2 < time.time()):
                    gkey = groupDeque.popleft()[0]
                    groupLock.release()
                else:
                    groupLock.release()
                    time.sleep(30)
                    continue
                gqueue = 0
                #get data
                groupData = groupAggrDict.pop(gkey)
                groupInfo = groupData[1]
                #get needed method
                gop = gops[groupInfo[1]]
                octlist = []
                classes = []
                max_class = None
                octets = 0
                gdate = datetime.datetime.fromtimestamp(gkey[2])
                account_id = gkey[0]
                
                #second type groups
                if groupInfo[2] == 2:                        
                    max_oct = 0
                    #get class octets, calculate with direction method, find maxes
                    for class_, gdict in groupData[0].iteritems():                            
                        octs = gop(gdict)
                        classes.append(class_)
                        octlist.append(octs)
                        if octs > max_oct:
                            max_oct = octs
                            max_class = class_                            
                        
                    octets = max_oct                        
                    if not max_class: continue
                    cur.execute("""SELECT group_type2_fn(%s, %s, %s, %s, %s, %s, %s);""" , (groupInfo[0], account_id, octets, gdate, classes, octlist, max_class))
                    connection.commit()
                #first type groups
                elif groupInfo[2] == 1:
                    #get class octets, calculate sum with direction method
                    for class_, gdict in groupData[0].iteritems():
                        octs = gop(gdict)
                        octets += octs
                    cur.execute("""SELECT group_type1_fn(%s, %s, %s, %s, %s, %s, %s);""" , (groupInfo[0], account_id, octets, gdate, classes, octlist, max_class))
                    connection.commit()
                else:
                    continue
                
                #write profiling infos
                if writeProf:
                    icount += 1
                    timecount += time.clock() - a
                    if icount == 10:                        
                        logger.info("NFGroupdeque thread name: %s run time(10): %s", (self.getName(), timecount))
                        icount = 0; timecount = 0
            except IndexError, ierr:
                if gqueue:
                    groupLock.release()
                    time.sleep(30)
                logger.debug("%s : indexerror : %s", (self.getName(), repr(ierr))) 
                continue
            except KeyError, kerr:
                logger.info("%s : keyerror : %s", (self.getName(), repr(kerr)))                
            except psycopg2.OperationalError, p2oerr:
                logger.error("%s : database connection is down: %s", (self.getName(), repr(p2oerr)))
            except psycopg2.ProgrammingError, p2perr:
                logger.error("%s : cursor programming error: %s", (self.getName(), repr(p2perr)))
            except psycopg2.InterfaceError, p2ierr:
                logger.error("%s : cursor interface error: %s", (self.getName(), repr(p2ierr)))
                try: cur = connection.cursor()
                except: pass
            except Exception, ex:
                logger.error("%s : exception: %s", (self.getName(), repr(ex)))            
                
                
class statDequeThread(Thread):
    '''Thread picks out and sends to the DB global statistics'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__

    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        cur = connection.cursor()
        global statAggrDict, statAggrTime
        global statDeque, statLock
        global writeProf
        icount = 0
        timecount = 0
        while True:
                #gdata[1] - group_id, group_dir, group_type
                #gkey[0] - account_id, gkey[2] - date
                #ftm = open('routtmp', 'ab+')
            try:
                if suicideCondition[self.tname]: break
                if writeProf:
                    a = time.clock()
                    
                #check whether double aggregation time passed - updates are rather costly
                statLock.acquire()
                #if statDeque[0][1]:
                #if statDeque[0][1] + statAggrTime*2 < time.time():
                if statDeque and (statDeque[0][1] + statAggrTime*2 < time.time()):
                    #get a key                
                    skey = statDeque.popleft()[0]
                    statLock.release()
                else:
                    statLock.release()
                    time.sleep(30)
                    continue
                #get data
                statData = statAggrDict.pop(skey)
                
                statInfo = statData[1]
                nas_id = statInfo[0]
                #total octets
                sum_bytes = statInfo[1]
                
                octlist = []
                classes = []
                sdate = datetime.datetime.fromtimestamp(skey[1])
                account_id = skey[0]
                       
                #get octets for every class
                for class_, sdict in statData[0].iteritems():                            
                    classes.append(class_)
                    octlist.append([sdict['INPUT'], sdict['OUTPUT']])
                    
                octets_in  = sum_bytes['INPUT']
                octets_out = sum_bytes['OUTPUT']                  
                    
                cur.execute("""SELECT global_stat_fn(%s, %s, %s, %s, %s, %s, %s);""" , (account_id, octets_in, octets_out, sdate, nas_id, classes, octlist))
                connection.commit()
                
                if writeProf:
                    icount += 1
                    timecount += time.clock() - a
                    if icount == 10:                        
                        logger.info("NFStatDeque thread name: %s run time(10): %s", (self.getName(), timecount))
                        icount = 0; timecount = 0
                        
            except IndexError, ierr:
                statLock.release()
                time.sleep(30)
                logger.debug("%s : indexerror : %s", (self.getName(), repr(ierr))) 
                continue
            except KeyError, kerr:
                logger.info("%s : keyerror : %s", (self.getName(), repr(kerr)))                
            except psycopg2.OperationalError, p2oerr:
                logger.error("%s : database connection is down: %s", (self.getName(), repr(p2oerr)))
            except psycopg2.ProgrammingError, p2perr:
                logger.error("%s : cursor programming error: %s", (self.getName(), repr(p2perr)))
            except psycopg2.InterfaceError, p2ierr:
                logger.error("%s : cursor interface error: %s", (self.getName(), repr(p2ierr)))
                try: cur = connection.cursor()
                except: pass
            except Exception, ex:
                logger.error("%s : exception: %s", (self.getName(), repr(ex)))
       
class NetFlowRoutine(Thread):
    '''Thread that handles NetFlow statistic packets and bills according to them'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        
    def get_actual_cost(self, trafic_transmit_service_id, group_id, octets_summ, stream_date, cTRTRNodesCache):
        """
        Метод возвращает актуальную цену для направления трафика для пользователя:
        """
        #TODO: check whether differentiated traffic billing us used <edge_start>=0; <edge_end>='infinite'
        #print (octets_summ, octets_summ, octets_summ, trafic_transmit_service_id, traffic_class_id, d)
        #trafic_transmit_nodes=self.cur.fetchall()
        trafic_transmit_nodes = cTRTRNodesCache.get((trafic_transmit_service_id, group_id), [])
        cost=0
        min_from_start=0
        # [0] - ttsn.id, [1] - ttsn.cost, [2] - ttsn.edge_start, [3] - ttsn.edge_end, [4] - tpn.time_start, [5] - tpn.length, [6] - tpn.repeat_after
        for node in trafic_transmit_nodes:
            #'d': '9' - in_direction, '10' - out_direction
            #if node[d]:
            trafic_transmit_node_id=node[0]
            trafic_cost=node[1]
            trafic_edge_start, trafic_edge_end=node[2:4]    
            period_start, period_length, repeat_after=node[4:7]

            #tnc, tkc, from_start,result=in_period_info(time_start=period_start,length=period_length, repeat_after=repeat_after, now=stream_date)
            tnc, tkc, from_start,result=fMem.in_period_(period_start,period_length, repeat_after, stream_date)
            if result:
                """
                Зачем здесь было это делать:
                Если в тарифном плане с оплатой за трафик в одной ноде указана цена за "круглые сутки", 
                но в другой ноде указана цена за какой-то конкретный день (к пр. праздник), 
                который так же попадает под круглые сутки, но цена в "праздник" должна быть другой, 
                значит смотрим у какой из нод помимо класса трафика попал расчётный период и выбираем из всех нод ту, 
                у которой расчётный период начался как можно раньше к моменту попадения строки статистики в БД.
                """
                if from_start<min_from_start or min_from_start==0:
                    min_from_start=from_start
                    cost=trafic_cost
        #del trafic_transmit_nodes
        return cost


    
    def run(self):
        connection = persist.connection()
        #connection._con._con.set_client_encoding('UTF8')
        connection._con.set_client_encoding('UTF8')
        #connection._con._con.set_isolation_level(0)
        global curAT_acIdx
        global curAT_date,curAT_lock
        global nfIncomingQueue
        global tpnInPeriod, curSPCache, curTTSCache
        global prepaysCache, TRTRNodesCache, ClassesStore
        global store_na_tarif, store_na_account
        global groupAggrDict, statAggrDict
        global groupAggrTime, statAggrTime
        global groupDeque, statDeque
        global gPicker, pickerLock, pickerTime
        cacheAT = None
        dateAT = datetime.datetime(2000, 1, 1)
        oldAcct = defaultdict(list)
        cur = connection.cursor()
        icount = 0
        timecount = 0
        global writeProf
        while True:
            try:   
                if suicideCondition[self.tname]: break
                if writeProf:
                    a = time.clock()
                if curAT_date > dateAT:
                    try:
                        #if caches were renewed, renew local copies                    
                        curAT_lock.acquire()
                        #cacheAT = deepcopy(curATCache)
                        #account-tarif cach indexed by account_id
                        cacheAT = copy(curAT_acIdx)
                        #settlement_period cache
                        cacheSP  = copy(curSPCache)
                        #traffic_transmit_service
                        cacheTTS = copy(curTTSCache)
                        classesStore = copy(ClassesStore)
                        
                        c_TRTRNodesCache = copy(TRTRNodesCache)
                        c_tpnInPeriod    = copy(tpnInPeriod)
                        c_prepaysCache   = copy(prepaysCache)                        
                        oldAcct = defaultdict(list)
                        #date of renewal
                        dateAT = deepcopy(curAT_date)

                        curAT_lock.release()
                    except:
                        time.sleep(1)
                        continue
                
                #if deadlocks arise add locks
                #time to pick
                if (time.time() > pickerTime + 300.0):
                    #add picker to a depicker queue
                    pickerLock.acquire()
                    depickerQueue.append(gPicker.get_data())
                    del gPicker
                    gPicker = Picker()
                    pickerTime = time.time()
                    pickerLock.release()
                    
                #if deadlocks arise add locks
                #pop flows
                fqueue = 1
                fpacket = nfIncomingQueue.popleft()
                flows = loads(fpacket)
                fqueue = 0

                #print flows
                #iterate through them
                for flow in flows:
                    #get account id and get a record from cache based on it
                    acct = cacheAT.get(flow[20])
                    #get collection date
                    ftime = flow[21]
                    stream_date = datetime.datetime.fromtimestamp(ftime)
                    cur_actf_id = acct[12]
                    if not acct:
                        continue
                    
                    flow_actf_id = flow[26]                    
                    #print stream_date
                    #if no line in cache, or the collection date is younger then accounttarif creation date
                    #get an acct record from teh database
                    if  (cur_actf_id  != flow_actf_id) or (not acct[3] <= stream_date):
                        if oldAcct.has_key(flow_actf_id):
                            acct = oldAcct[flow_actf_id]
                        else:                        
                            cur.execute("""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, FALSE, ba.created, ba.disabled_by_limit, ba.balance_blocked, ba.nas_id, ba.vpn_ip_address, ba.ipn_ip_address,ba.ipn_mac_address, ba.assign_ipn_ip_from_dhcp, ba.ipn_status, ba.ipn_speed, ba.vpn_speed, ba.ipn_added, bt.ps_null_ballance_checkout, bt.deleted, bt.allow_express_pay, ba.status, ba.allow_vpn_null, ba.allow_vpn_block, ba.username
                            FROM billservice_account as ba
                            JOIN billservice_accounttarif AS act ON act.id=%s AND ba.id=act.account_id
                            LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id;""", (flow[26],))
                            acct = cur.fetchone()
                            connection.commit()
                            oldAcct[flow_actf_id] = acct                           
                        
                        if not acct:
                            continue
                    
                    tarif_id = acct[4]
                    #if no tarif_id, tarif.active=False and don't store, account.active=false and don't store    
                    if (tarif_id == None) or (not (acct[11] or store_na_tarif)) or (not (acct[13] or store_na_account)):
                        continue                    
                    
                    octets = flow[6]
                    flow_classes, flow_dir = flow[22:24]                    
                    account_id = flow[20]
                    nas_id = flow[11]
                    
                    has_groups = (len(flow) > 27) and flow[27]
                    #check for groups
                    '''Статистика по группам: 
                    аггрегируется в словаре по структурам типа {класс->{'INPUT':0, 'OUTPUT':0}}
                    Ключ - (account_id, group_id, gtime)
                    Ключ затем добавляется в очередь.'''
                    groups = []
                    if has_groups:                        
                        groups = flow[28]
                        gtime = ftime - (ftime % groupAggrTime)                        
                        for group in groups:
                            try:
                                group_id, group_classes, group_dir, group_type  = group
                                #calculate a key and check the dictionary
                                gkey = (account_id, group_id, gtime)
                                grec = groupAggrDict.get(gkey)
                                if not grec:
                                    #add new record to the queue and the dictionary
                                    groupDeque.append((gkey, time.time()))
                                    grec = [defaultdict(ddict_IO), (group_id, group_dir, group_type)]
                                    groupAggrDict[gkey] = grec
                                #aggregate bytes for every class/direction
                                for class_ in group_classes:
                                    grec[0][class_][flow_dir] += octets                     
                
                            except Exception, ex:
                                logger.info('%s groupstat exception: %s', (self.getName(), repr(ex)))
                                traceback.print_exc(file=sys.stderr)                    
                                
                    #global statistics calculation
                    stime = ftime - (ftime % statAggrTime)
                    skey  = (account_id, stime)
                    try:
                        srec = statAggrDict.get(skey)
                        if not srec:
                            statDeque.append((skey, time.time()))
                            srec = [defaultdict(ddict_IO), [nas_id, {'INPUT':0, 'OUTPUT':0}]]
                            statAggrDict[skey] = srec
                        #calculation for every class
                        for class_ in flow_classes:
                            srec[0][class_][flow_dir] += octets
                        #global data
                        srec[1][1][flow_dir] += octets                        
                    except Exception, ex:
                                logger.info('%s globalstat exception: %s', (self.getName(), repr(ex)))
                                traceback.print_exc(file=sys.stderr)
                    
                    
                    tarif_mode = False
                    
                    tts_id = acct[7]
                    #if traffic_transmit_service_id is OK
                    if tts_id:
                        tarif_mode = c_tpnInPeriod[tts_id]
                        
                    store_classes = list(classesStore.intersection(flow_classes))
                    #if tarif_mode is False or tarif.active = False
                    #write statistics without billing it
                    if store_classes and ( not (tarif_mode and acct[11] and acct[13])):
                        #cur = connection.cursor()
                        cur.execute("""INSERT INTO billservice_netflowstream(
                                    nas_id, account_id, tarif_id, direction,date_start, src_addr, traffic_class_id,
                                    dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s,
                                    %s, %s, %s, %s, %s, %s, %s);
                                    """, (nas_id, account_id, tarif_id, flow[23], stream_date,intToIp(flow[0],4), store_classes, intToIp(flow[1],4), flow[6],flow[9], flow[10], flow[13], False, False,))
                        connection.commit()
                        #cur.close()
                        continue
                    
                    s = False
                    #if traffic_transmit_service_id is OK
                    if tts_id and has_groups:
                        #if settlement_period_id is OK
                        setper_id = acct[10]
                        if setper_id:
                            #get a line from Settlement Period cache                            
                            #[0] - id, [1] - time_start, [2] - length, [3] - length_in, [4] - autostart
                            spInf = cacheSP[setper_id]
                            #if 'autostart'
                            if spInf[4]:
                                # Если у расчётного периода стоит параметр Автостарт-за начало расчётного периода принимаем
                                # дату привязки тарифного плана пользователю
                                #start = accounttarif.datetime
                                sp_time_start=acct[3]
                                
                            #stream_date = datetime.datetime.fromtimestamp(flow[20])
                            settlement_period_start, settlement_period_end, deltap = settlement_period_info(time_start=spInf[1], repeat_after=spInf[3], repeat_after_seconds=spInf[2], now=stream_date)
                            #Смотрим сколько уже наработал за текущий расчётный период по этому тарифному плану

                            octets_summ=0
                        else:
                            octets_summ=0
                            #loop throungh classes in 'classes' tuple
                        for group in groups:
                            tgroup = group[0]
                            #acct[7] - traffic_transmit_service_id
                            #flow[23] - direction
                            trafic_cost=self.get_actual_cost(tts_id, tgroup, octets_summ, stream_date, c_TRTRNodesCache)

                            #get a record from prepays cache
                            #keys: traffic_transmit_service_id, accounttarif.id, trafficclass
                            prepInf =  c_prepaysCache.get((tts_id, acct[12], tgroup))                            
                            
                            if prepInf:
                                #d = 5: checks whether in_direction is True; d = 6: whether out_direction
                                #if prepInf[d]:
                                #[0] - prepais.id, [1] - prepais.size
                                prepaid_id, prepaid = prepInf[0:2]
                                prepHnd = prepaid
                                if prepaid>0:                            
                                    if prepaid>=octets:
                                        prepaid=prepaid-octets
                                        octets=0
                                    elif octets>=prepaid:
                                        octets=octets-prepaid
                                        prepaid=abs(prepaid-octets)
                                        
                                    cur.execute("""UPDATE billservice_accountprepaystrafic SET size=size-%s WHERE id=%s""", (prepaid, prepaid_id,))
                                    connection.commit()
            
                            summ=(trafic_cost*octets)/(1048576)
        
                            if summ>0:
                                #account_id, tariff_id, summ
                                pickerLock.acquire()
                                gPicker.add_summ(flow[20], acct[4], summ)
                                pickerLock.release()
                    if store_classes:
                        cur.execute("""INSERT INTO billservice_netflowstream(
                                nas_id, account_id, tarif_id, direction,date_start, src_addr, traffic_class_id,
                                dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                                VALUES (%s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s);
                                """, (nas_id, account_id, tarif_id, flow_dir, stream_date,intToIp(flow[0],4), store_classes, intToIp(flow[1],4), flow[6],flow[9], flow[10], flow[13], True, False,))
                        connection.commit()
                 
                if writeProf:
                    icount += 1
                    timecount += time.clock() - a
                    if icount == 100:                        
                        logger.info("NFRoutine thread name: %s run time: %s", (self.getName(), timecount))
                        icount = 0; timecount = 0
                        
            except IndexError, ierr:
                if fqueue: time.sleep(3)                
                continue               
            except psycopg2.OperationalError, p2oerr:
                time.sleep(1)
                logger.error("%s : database connection is down: %s", (self.getName(), repr(p2oerr)))
                try: cur = connection.cursor()
                except: pass
            except psycopg2.ProgrammingError, p2perr:
                logger.error("%s : cursor programming error: %s", (self.getName(), repr(p2perr)))
            except psycopg2.InterfaceError, p2ierr:
                time.sleep(1)
                logger.error("%s : cursor interface error: %s", (self.getName(), repr(p2ierr)))
                try: cur = connection.cursor()
                except: pass
            except Exception, ex:
                time.sleep(1)
                logger.error("%s : exception: %s", (self.getName(), repr(ex)))
                    

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
    
    
'''
acct structure
[0]  - ba.id, 
[1]  - ba.ballance, 
[2]  - ba.credit, 
[3]  - act.datetime, 
[4]  - bt.id, 
[5]  - bt.access_parameters_id, 
[6]  - bt.time_access_service_id, 
[7]  - bt.traffic_transmit_service_id, 
[8]  - bt.cost,
[9]  - bt.reset_tarif_cost, 
[10] - bt.settlement_period_id, 
[11] - bt.active, 
[12] - act.id, 
[13] - ba.status 

'''
class AccountServiceThread(Thread):
    '''Handles simultaniously updated READ ONLY caches connected to account-tarif tables'''
    def __init__ (self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global caches, fMem, sendFlag, nfIncomingQueue, suicideCondition
        global curAT_acIdx
        global curAT_date, curAT_lock
        global curSPCache, curTTSCache
        global tpnInPeriod, prepaysCache, TRTRNodesCache, ClassesStore
        while True:
            a = time.clock()
            try:
                if suicideCondition[self.tname]: break
                cur = connection.cursor()
                ptime =  time.time()
                ptime = ptime - (ptime % 20)
                tmpDate = datetime.datetime.fromtimestamp(ptime)
                cur.execute("""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, ba.status   
                    FROM billservice_account as ba
                    LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                    LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id;""", (tmpDate,))
                #list cache
                
                accts = cur.fetchall()
                allowedUsersChecker(allowedUsers, lambda: len(accts))

                cur.execute("""SELECT id, reset_traffic, cash_method, period_check FROM billservice_traffictransmitservice;""")
                
                ttssTp = cur.fetchall()
                #connection.commit()
                cur.execute("""SELECT id, time_start, length, length_in, autostart FROM billservice_settlementperiod;""")
                
                spsTp = cur.fetchall()                

                cur.execute("""SELECT tpn.time_start, tpn.length, tpn.repeat_after, ttns.traffic_transmit_service_id
                            FROM billservice_timeperiodnode AS tpn
                            JOIN billservice_timeperiod_time_period_nodes AS timeperiod_timenodes ON timeperiod_timenodes.timeperiodnode_id=tpn.id
                            JOIN billservice_traffictransmitnodes_time_nodes AS ttntp ON ttntp.timeperiod_id=timeperiod_timenodes.timeperiod_id
                            JOIN billservice_traffictransmitnodes AS ttns ON ttns.id=ttntp.traffictransmitnodes_id;""")
                tpnsTp = cur.fetchall()
                '''
                cur.execute("""SELECT prepais.id, prepais.size, prepais.account_tarif_id, prept_tc.trafficclass_id, prepaidtraffic.traffic_transmit_service_id, prepaidtraffic.in_direction, prepaidtraffic.out_direction
                             FROM billservice_accountprepaystrafic as prepais
                             JOIN billservice_prepaidtraffic as prepaidtraffic ON prepaidtraffic.id=prepais.prepaid_traffic_id
                             JOIN billservice_prepaidtraffic_traffic_class AS prept_tc ON prept_tc.prepaidtraffic_id=prepaidtraffic.id
                             WHERE prepais.size>0 AND (ARRAY[prepais.account_tarif_id] && get_cur_acct(%s));""", (tmpDate,))
                             '''
                cur.execute("""SELECT prepais.id, prepais.size, prepais.account_tarif_id, prepaidtraffic.group_id, prepaidtraffic.traffic_transmit_service_id 
                             FROM billservice_accountprepaystrafic as prepais
                             JOIN billservice_prepaidtraffic as prepaidtraffic ON prepaidtraffic.id=prepais.prepaid_traffic_id
                             WHERE prepais.size>0 AND (ARRAY[prepais.account_tarif_id] && get_cur_acct(%s));""", (tmpDate,))
                prepTp = cur.fetchall()
                '''cur.execute("""SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start, tpn.length, tpn.repeat_after,
                               ARRAY(SELECT trafficclass_id FROM billservice_traffictransmitnodes_traffic_class WHERE traffictransmitnodes_id=ttsn.id) as classes, ttsn.traffic_transmit_service_id, ttsn.in_direction, ttsn.out_direction
                               FROM billservice_traffictransmitnodes as ttsn
                               JOIN billservice_timeperiodnode AS tpn on tpn.id IN 
                               (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id IN 
                               (SELECT timeperiod_id FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=ttsn.id));
                            """)'''
                cur.execute("""SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start, tpn.length, tpn.repeat_after,
                               ttsn.group_id, ttsn.traffic_transmit_service_id 
                               FROM billservice_traffictransmitnodes as ttsn
                               JOIN billservice_timeperiodnode AS tpn on tpn.id IN 
                               (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id IN 
                               (SELECT timeperiod_id FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=ttsn.id));
                            """)
                trtrnodsTp = cur.fetchall()
                cur.execute("""SELECT int_array_aggregate(id) FROM nas_trafficclass WHERE store=TRUE""")
                clsstoreTp = cur.fetchall()
                connection.commit()
                cur.close()
                
                tmpacIdx = {}

                for acct in accts:
                    tmpacIdx[acct[0]]  = acct
  
                tmpPerTP = defaultdict(lambda: False)
                #calculates whether traffic_transmit_service fits in any oh the periods
                for tpn in tpnsTp:
                    tmpPerTP[tpn[3]] = tmpPerTP[tpn[3]] or fMem.in_period_(tpn[0], tpn[1], tpn[2], tmpDate)[3]
                     
                prepaysTmp = {}
                if prepTp:                    
                    #keys: traffic_transmit_service_id, accounttarif.id, group_id
                    for prep in prepTp:
                        prepaysTmp[(prep[4],prep[2],prep[3])] = [prep[0], prep[1]]
                    prepaysCache = prepaysTmp
                    
                trafnodesTmp = defaultdict(list)
                """
                #keys: traffictransmitservice, trafficclass
                
                for trnode in trtrnodsTp:
                    for classnd in trnode[7]:
                        trafnodesTmp[(trnode[8],classnd)].append(trnode)
                """
                #keys: traffictransmitservice, group_id
                
                for trnode in trtrnodsTp:
                    if trnode[7]:
                        trafnodesTmp[(trnode[8],trnode[7])].append(trnode)
                #traffic_transmit_service cache, indexed by id
                tmpttsC = {}
                #settlement period cache, indexed by id
                tmpspC = {}
                
                
                for tts in ttssTp:
                    tmpttsC[tts[0]] = tts
                for sps in spsTp:
                    tmpspC[sps[0]] = sps
                
                    
                clsstore = set(clsstoreTp[0][0])
                
                #renew global cache links
                curAT_lock.acquire()
                curAT_acIdx   = tmpacIdx
                
                curSPCache = tmpspC
                curTTSCache = tmpttsC
                tpnInPeriod = tmpPerTP
                prepaysCache = prepaysTmp
                TRTRNodesCache = trafnodesTmp
                ClassesStore = clsstore
                curAT_date  = tmpDate
                curAT_lock.release()
                
                #clear memoize cache
                fMem.periodCache = {}
                
                #reread dynamic options
                '''
                    Переопределяет динамические опции.
                '''
                config.read("ebs_config_runtime.ini")
                logger.setNewLevel(int(config.get("nfroutine", "log_level")))
                global writeProf
                writeProf = logger.writeInfoP()
                    
                #check queue length            
                if len(nfIncomingQueue) > 1000:
                    if not sendFlag or sendFlag!='SLP!':
                        sendFlag = 'SLP!'
                        logger.lprint('Sleep flag set!')                        
                else:
                    if sendFlag and sendFlag=='SLP!':
                        sendFlag = ''
                        logger.lprint('Sleep flag unset!')
                        
                #write profinig infos
                if writeProf:        
                    logger.info("nfr ast time : %s", time.clock() - a)
                    logger.info("incoming queue len: %s", len(nfIncomingQueue))
                    logger.info("groupDictLen: %s", len(groupAggrDict))
                    logger.info("groupDequeLen: %s", len(groupDeque))
                    logger.info("statDictLen: %s", len(statAggrDict))
                    logger.info("statDequeLen: %s", len(statDeque))
                
                
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    logger.error("%s: database connection is down: %s", (self.getName(), repr(ex)))
                else:
                    logger.error("%s: exception: %s", (self.getName(), repr(ex)))
            
            gc.collect()
            time.sleep(180)
            

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
        #print 'New packet'
        pass    
    #TODO: send '0' when queue is too long
    def handle_read_event (self):
        try:
            data, addr = self.socket.recvfrom(32768)
            self.socket.sendto(sendFlag+str(len(data)), addr)
            nfIncomingQueue.append(data)
            #print data
            #print str(len(nfIncomingQueue)) + sendFlag
        except:            
            traceback.print_exc()
            return
        #self.handle_readfrom(data, addr)


    def handle_readfrom(self,data, address):
        pass
    def writable(self):
        return (0)

    def handle_error (self, *info):
        traceback.print_exc()
        logger.error('uncaptured python exception, closing channel %s', repr(self))
        self.close()
    
    def handle_close(self):
        self.close()     


        

def ddict_IO():
    return {'INPUT':0, 'OUTPUT':0}

def SIGTERM_handler(signum, frame):
    graceful_save()

def graceful_save():
    global nfIncomingQueue, depickerQueue, cacheThr, threads, suicideCondition, depickerQueue_
    asyncore.close_all()
    #cacheThr.exit()
    suicideCondition[cacheThr.tname] = True
    st_time = time.time()
    time.sleep(1)
    i = 0
    while True:
        if len(nfIncomingQueue) > 300:  break
        if len(nfIncomingQueue) == 0:   break
        if i == 4:                      break
        time.sleep(1)

    for thr in threads:
        if not isinstance(thr, DepickerThread):
            suicideCondition[thr.tname] = True
    time.sleep(1)
    depickerLock.acquire()
    depickerQueue_ = depickerQueue
    depickerQueue = deque()
    depickerLock.release()
    time.sleep(1.5)
    for thr in threads:
            suicideCondition[thr.tname] = True
           
    graceful_saver([['depickerQueue_'], ['nfIncomingQueue'], ['groupDeque', 'groupAggrDict'], ['statDeque', 'statAggrDict']],
                   globals(), 'nfroutine_', saveDir)
    
    pool.close()
    time.sleep(2)
    sys.exit()
        
def graceful_recover():
    graceful_loader(['depickerQueue','nfIncomingQueue','groupDeque', 'groupAggrDict','statDeque', 'statAggrDict'],
                    globals(), 'nfroutine_', saveDir)
    

def main():
    graceful_recover()
    global curAT_date, suicideCondition
    global threads, cacheThr, NfAsyncUDPServer
    #thread_list = [['routinethreads', NetFlowRoutine, 'NetFlowRoutine'],]
    threads=[]
    for i in xrange(int(config.get("nfroutine", "routinethreads"))):
        newNfr = NetFlowRoutine()
        newNfr.setName('NetFlowRoutine #%s ' % i)
        threads.append(newNfr)
    for i in xrange(int(config.get("nfroutine", "groupstatthreads"))):
        grdqTh = groupDequeThread()
        grdqTh.setName('groupDequeThread #%i' % i)
        threads.append(grdqTh)
    for i in xrange(int(config.get("nfroutine", "globalstatthreads"))):
        stdqTh = statDequeThread()
        stdqTh.setName('statDequeThread #%i' % i)
        threads.append(stdqTh)
    for i in xrange(int(config.get("nfroutine", "depickerthreads"))):
        depTh = DepickerThread()
        depTh.setName('depickerThread #%i' % i)
        threads.append(depTh)
    
    cacheThr = AccountServiceThread()
    cacheThr.setName('NFR AccountServiceThread')
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.start()
    while curAT_date == None:
        time.sleep(0.2)
        if not cacheThr.isAlive:
            sys.exit()
        
    #i= range(len(threads))
    for th in threads:
        suicideCondition[th.__class__.__name__] = False
        th.start()        
        logger.info("NFR %s start", th.getName())
        time.sleep(0.1)
        
    time.sleep(5)
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')
    #asyncore.
    NfAsyncUDPServer(coreAddr)
    
    print "ebs: nfroutine: started"
    while 1: 
        asyncore.poll(0.010)
#===============================================================================
import socket
if socket.gethostname() not in ['dmitry-desktop','dolphinik','sserv.net','sasha', 'xubuntu', 'iserver','kenny','billing', 'medusa', 'Billing.NemirovOnline']:
    import sys
    print "License key error. Exit from application."
    sys.exit(1)
    
if __name__ == "__main__":
    if "-D" in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
        
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")

        
    logger = isdlogger.isdlogger(config.get("nfroutine", "log_type"), loglevel=int(config.get("nfroutine", "log_level")), ident=config.get("nfroutine", "log_ident"), filename=config.get("nfroutine", "log_file")) 
    saver.log_adapt = logger.log_adapt
    logger.lprint('Nfroutine start')
    try:
        
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
        #temp save on restart or graceful stop
        saveDir = config.get("nfroutine", "save_dir")
        #store stat. for old tarifs and accounts?
        store_na_tarif   = False
        store_na_account = False
        if (config.get("nfroutine", "store_na_tarif")  =='True') or (config.get("nfroutine", "store_na_tarif")  =='1'):
            store_na_tarif   = True
        if (config.get("nfroutine", "store_na_account")=='True') or (config.get("nfroutine", "store_na_account")=='1'):
            store_na_account = True
        
        #write profiling info?
        writeProf = logger.writeInfoP()  
        
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
        #queue for Incoming packet lists
        nfIncomingQueue = deque()
        #lock for nfIncomingQueue operations
        nfQueueLock = Lock()
        
        #last cache renewal date
        curAT_date  = None
        #lock for cache operations
        curAT_lock  = Lock()
        
        #sendflag prefix
        sendFlag = ''
        
        
        #group statistinc an global statistics objects    
        #key = account, group id , time
        #[(1,2,3)][0][4]['INPUT']
        #[(1,2, )][1] = group info
        #lambda: [defaultdict(lambda: {'INPUT':0, 'OUTPUT':0}), None])
        groupAggrDict = {}   
        #key - account_id, time
        #[(1,2,3)][0][4]['INPUT']
        #[(1,2, )][1] = nas etc
        statAggrDict = {}   
        
        groupAggrTime = 300    
        statAggrTime  = 1800
        
        groupDeque = deque()
        statDeque  = deque()    
        groupLock = Lock()
        statLock  = Lock()    
        
        depickerQueue = deque()
        depickerLock  = Lock()
        
        gPicker = Picker()
        pickerLock = Lock()
        pickerTime = time.time() + 5
        
        #function that returns number of allowed users
        #create allowedUsers
        allowedUsers = setAllowedUsers(pool.connection(), "license.lic")        
        allowedUsers()
        
        fMem = pfMemoize()    
    
    
        #-------------------
        print "ebs: nfroutine: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nfroutine, exiting: ', repr(ex)
        logger.error('Exception in nfroutine, exiting: %s', repr(ex))