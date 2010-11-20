#-*-coding=utf-8-*-

import signal
import asyncore
import isdlogger
import threading
import ConfigParser

import psycopg2, psycopg2.extras
import time, datetime, os, sys, gc, traceback

from IPy import intToIp
from marshal import dumps, loads
from daemonize import daemonize
from threading import Thread, Lock
from copy import copy, deepcopy
from DBUtils.PooledDB import PooledDB
from DBUtils.PersistentDB import PersistentDB
from collections import deque, defaultdict


class groupDequeThread(Thread):

    def __init__ (self):
        Thread.__init__(self)

    def run(self):
        connection = persist.connection()
        connection._con.set_client_encoding('UTF8')
        cur = connection.cursor()
        global groupAggrDict, groupAggrTime
        global groupDeque, groupLock
        #direction type->operations
        gops = {1: lambda xdct: xdct['INPUT'], 2: lambda xdct: xdct['OUTPUT'] , 3: lambda xdct: xdct['INPUT'] + xdct['OUTPUT'], 4: lambda xdct: max(xdct['INPUT'], xdct['OUTPUT'])}
        global writeProf
        icount = 0
        timecount = 0
        while True:
                #gdata[1] - group_id, group_dir, group_type
                #gkey[0] - account_id, gkey[2] - date
                #ftm = open('routtmp', 'ab+')
            try:
                groupLock.acquire()
                #check whether double aggregation time passed - updates are rather costly
                if groupDeque[0][1] + 30 < time.time():
                    gkey = groupDeque.popleft()[0]
                    groupLock.release()
                else:
                    groupLock.release()
                    time.sleep(10)
                    continue
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
                        #classes.append(class_)
                        octs = gop(gdict)
                        octets += octs

                    cur.execute("""SELECT group_type1_fn(%s, %s, %s, %s, %s, %s, %s);""" , (groupInfo[0], account_id, octets, gdate, classes, octlist, max_class))
                    connection.commit()
                else:
                    continue

            except IndexError, ierr:
                groupLock.release()
                time.sleep(10)
                continue
            except Exception, ex:
                print "%s : exception: %s" % (self.getName(), repr(ex))          
                
                
class statDequeThread(Thread):
    '''Thread picks out and sends to the DB global statistics'''
    def __init__ (self):
        Thread.__init__(self)

    def run(self):
        connection = persist.connection()
        connection._con.set_client_encoding('UTF8')
        cur = connection.cursor()
        global statAggrDict, statAggrTime
        global statDeque, statLock
        global writeProf
        icount = 0
        timecount = 0
        while True:
            try:
                #check whether double aggregation time passed - updates are rather costly
                statLock.acquire()
                #if statDeque[0][1]:
                if statDeque[0][1] + 50 < time.time():
                    #get a key                
                    skey = statDeque.popleft()[0]
                    statLock.release()
                else:
                    statLock.release()
                    time.sleep(10)
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
                        
            except IndexError, ierr:
                statLock.release()
                time.sleep(10)
                continue
            except Exception, ex:
                print "%s : exception: %s" % (self.getName(), repr(ex))
                
class NetFlowRoutine(Thread):
    '''Thread that handles NetFlow statistic packets and bills according to them'''
    def __init__ (self):
        Thread.__init__(self)
     
    def isect_classes(self, groups_rec, class_list):
        '''Calculates intersection of group classes and flow classes.
           Returns a tuple.
        '''
        groups_rec[1].intersection_update(class_list)
        groups_rec[1] = tuple(groups_rec[1])
        return tuple(groups_rec)
   
    def run(self):
        connection = persist.connection()
        #connection._con._con.set_client_encoding('UTF8')
        connection._con.set_client_encoding('UTF8')
        #connection._con._con.set_isolation_level(0)
        global groupAggrDict, statAggrDict
        global groupAggrTime, statAggrTime
        global groupDeque, statDeque
        global groupLast, statLast
        
        global lastOneFname
        cur = connection.cursor()
        
        curDay = dateStart

        while curDay <= dateEnd:
            if curDay == dateEnd:
                fname = lastOneFname
            else:
                fname = tmpFolder + curDay.strftime('%Y%m%d')
                f = open(fname, 'w')
                try:
                    cur.copy_to(f, 'nfs' + curDay.strftime('%Y%m%d'), sep='|', columns=['account_id', 'date_start', 'traffic_class_id', 'octets', 'direction', 'nas_id', 'tarif_id'])
                except Exception, ex:
                    print repr(ex)
                    f.close()
                    continue
                f.close()
                connection.commit()
                
            print curDay.strftime('%Y%m%d')
            fr = open(fname, 'r')
            for dbline in fr:
                dblst = dbline.split('|')
                
                account_id = int(dblst[0])
                ftime = time.mktime(time.strptime(dblst[1], '%Y-%m-%d %H:%M:%S'))
                flow_classes = eval('['+dblst[2][1:-1]+']')
                octets = int(dblst[3])
                flow_dir = dblst[4]
                nas_id = int(dblst[5])
                tarif_id = int(dblst[6])
                
                if dblst[1] == '2009-01-13 07:52:20':
                    pass
                has_groups = False
                tarifGroups = tarif_groupsCache.get(tarif_id)
                if tarifGroups: 
                    has_groups = True

                if has_groups:
                    dr = 0
                    if flow_dir == 'INPUT':
                        dr = 2
                    elif flow_dir == 'OUTPUT':
                        dr = 1
                    groupLst = []
                    fcset = set(flow_classes)
                    for tgrp in tarifGroups:
                        if (tgrp[2] == dr) or (tgrp[0] == 0):
                            continue
                        group_cls = fcset.intersection(tgrp[1])
                        if group_cls:
                            group_add = tgrp[:]
                            group_add[1] = tuple(group_cls)
                            groupLst.append(tuple(group_add))
                        
                        
                    groups = groupLst
                    '''for tcl in flow_classes:
                        groupLst.update(tarifGroups.intersection(class_groupsCache.get((tcl, flow_dir), set())))                            
                    groups = tuple([self.isect_classes(groupsCache[group_][:], flow_classes) for group_ in groupLst])'''
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
                                grec = [defaultdict(lambda: {'INPUT':0, 'OUTPUT':0}), (group_id, group_dir, group_type)]
                                groupAggrDict[gkey] = grec
                            #aggregate bytes for every class/direction
                            for class_ in group_classes:
                                grec[0][class_][flow_dir] += octets                     
            
                        except Exception, ex:
                            print '%s groupstat exception: %s' % (self.getName(), repr(ex))
                            traceback.print_exc(file=sys.stderr)
                
                            
                #global statistics calculation
                stime = ftime - (ftime % statAggrTime)
                skey  = (account_id, stime)
                try:
                    srec = statAggrDict.get(skey)
                    if not srec:
                        statDeque.append((skey, time.time()))
                        srec = [defaultdict(lambda: {'INPUT':0, 'OUTPUT':0}), [nas_id, {'INPUT':0, 'OUTPUT':0}]]
                        statAggrDict[skey] = srec
                    #calculation for every class
                    for class_ in flow_classes:
                        srec[0][class_][flow_dir] += octets
                    #global data
                    srec[1][1][flow_dir] += octets                        
                except Exception, ex:
                    print '%s globalstat exception: %s' % (self.getName(), repr(ex))
                    traceback.print_exc(file=sys.stderr)
                    
            fr.close()
            os.unlink(fname)
            curDay += day_

    

class AccountServiceThread(Thread):
    '''Handles simultaniously updated READ ONLY caches connected to account-tarif tables'''
    def __init__ (self):
        Thread.__init__(self)
    def run(self):
        connection = persist.connection()
        connection._con.set_client_encoding('UTF8')
        global groupsCache, class_groupsCache, tarif_groupsCache
        cur = connection.cursor()
        cur.execute("SELECT id, ARRAY(SELECT trafficclass_id from billservice_group_trafficclass as bgtc WHERE bgtc.group_id = bsg.id) AS trafficclass, direction, type FROM billservice_group AS bsg;")
        groups = cur.fetchall()
        cur.execute("SELECT tarif_id, int_array_aggregate(group_id) AS group_ids FROM (SELECT tarif_id, group_id FROM billservice_trafficlimit UNION SELECT bt.id, btn.group_id FROM billservice_tariff AS bt JOIN billservice_traffictransmitnodes AS btn ON bt.traffic_transmit_service_id=btn.traffic_transmit_service_id WHERE btn.group_id IS NOT NULL) AS tarif_group GROUP BY tarif_id;")
        tarif_groups = cur.fetchall()
        connection.commit()
        
        
        #id, trafficclass, in_direction, out_direction, type
        gpcTmp = defaultdict(set)
        groups_ = {}
        for group in groups:
            if not group[1]: continue
            #direction = group[2]
            #g_id   = group[0]
            #g_type = group[3]
            #classes_ = group[1]
            lgroup = list(group)
            #lgroup[1] = set(lgroup[1])
            groups_[group[0]] = lgroup
            '''for tclass in group[1]:
                if direction   == 1:
                    gpcTmp[(tclass, 'INPUT')].add(g_id)
                elif direction == 2:
                    gpcTmp[(tclass, 'OUTPUT')].add(g_id)
                elif direction in (3,4):
                    gpcTmp[(tclass, 'INPUT')].add(g_id)
                    gpcTmp[(tclass, 'OUTPUT')].add(g_id)'''

        groupsCache = groups_
        class_groupsCache = gpcTmp
        del gpcTmp
        
        tg_ = defaultdict(list)
        for tarif_id, groups__ in tarif_groups:
            for grp in set(groups__):
                tg_[tarif_id].append(groupsCache.get(grp, [0,[]]))
            
        tarif_groupsCache = tg_
        global lastOneFname
        lastOneFname = tmpFolder + dateEnd.strftime('%Y%m%d')
        lastone = open(lastOneFname, 'w')
        cur.copy_to(lastone, 'nfs' + dateEnd.strftime('%Y%m%d'), sep='|', columns=['account_id', 'date_start', 'traffic_class_id', 'octets', 'direction', 'nas_id', 'tarif_id'])
        lastone.close()
        connection.commit()
        cur.close()
        global cachesRead
        cachesRead = True
                

            


def main():
    global cachesRead
    
    
    
    
    

    threads=[]
    for i in xrange(1):
        newNfr = NetFlowRoutine()
        newNfr.setName('grouper NetFlowRoutine #%s ' % i)
        threads.append(newNfr)
    for i in xrange(1):
        grdqTh = groupDequeThread()
        grdqTh.setName('grouper groupDequeThread #%i' % i)
        threads.append(grdqTh)
    for i in xrange(1):
        stdqTh = statDequeThread()
        stdqTh.setName('grouper statDequeThread #%i' % i)
        threads.append(stdqTh)

    cacheThr = AccountServiceThread()
    cacheThr.setName('NFR AccountServiceThread')
    cacheThr.start()
    
    while not cachesRead:
        time.sleep(0.2)
        if not cacheThr.isAlive:
            sys.exit()
        
    #i= range(len(threads))
    for th in threads:	
        th.start()
        print "%s start" % th.getName()
        time.sleep(0.1)

if __name__ == "__main__":
    
    dateStart = datetime.date(int(sys.argv[1][0:4]), int(sys.argv[1][4:6]), int(sys.argv[1][6:8]))
    if sys.argv[2] == 'now':
        dateEnd = datetime.date.today()
    else:
        dateEnd = datetime.date(int(sys.argv[2][0:4]), int(sys.argv[2][4:6]), int(sys.argv[2][6:8]))
    
    day_ = datetime.timedelta(days=1)
    
    tmpFolder = ''
    if len(sys.argv) > 3:
        tmpFolder = sys.argv[3] + '/'
        
        
    lastOneFname = ''
        
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")
    
    persist = PersistentDB(
        setsession=["SET synchronous_commit TO OFF;", 'SET DATESTYLE TO ISO;'],
        creator=psycopg2,
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"), 
                                                               config.get("db", "host"), config.get("db", "password")))

    #--------------------------------------------------------
    
    cachesRead = False
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
    groupLast = None
    statLast  = None
       
    
    
    main()