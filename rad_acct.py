#-*-coding: utf-8 -*-

from __future__ import with_statement
import site
site.addsitedir('/opt/ebs/venv/lib/python2.6/site-packages')
site.addsitedir('/opt/ebs/venv/lib/python2.7/site-packages')
import gc
import os
import sys
sys.path.insert(0, "modules")
sys.path.append("cmodules")
import time
import select
import signal
import socket
import packet
import asyncore
import datetime
import traceback
import dictionary
import ConfigParser
import psycopg2, psycopg2.extras

import isdlogger
import saver, utilites

from time import clock
from copy import deepcopy
from threading import Thread, Lock

from collections import defaultdict, deque


psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

from classes.rad_acct_cache import *
from classes.cacheutils import CacheMaster
from classes.flags import RadFlags
from classes.vars import RadVars, RadQueues
from utilites import renewCaches, savepid, rempid, get_connection, getpid, check_running
import Queue



w32Import = False


from twisted.internet.protocol import DatagramProtocol

try:
    from twisted.internet import epollreactor
    epollreactor.install()
except:
    print 'No poll(). Using select() instead.'

from twisted.internet import reactor


NAME = 'radius'
DB_NAME = 'db'


SOCKTYPE_AUTH = 12
SOCKTYPE_ACCT = 13
MAX_PACKET_SIZE = 8192

        
def show_packet(packetobject):
    b = ''
    #b = ''.join((str(packetobject._DecodeKey(key))+str(packetobject[packetobject._DecodeKey(key)][0])+"\n" for key,item in packetobject.items()))
    for key,value in packetobject.items():
        b+=str(packetobject._DecodeKey(key))+str(packetobject[packetobject._DecodeKey(key)][0])+"\n"
    return b


def get_accesstype(packetobject):
    """
    Returns access type name by which a user connects to the NAS
    """
    #print show_packet(packetobject)
    try:
        nas_port_type = packetobject.get('NAS-Port-Type', (None,))[0]
        calling_station = packetobject.get('Calling-Station-Id', [''])[0]
        if nas_port_type == 'Virtual' and packetobject.get('Service-Type', [''])[0]=='Framed-User':
            return 'PPTP'
        elif (nas_port_type == 'Ethernet' or (not nas_port_type and len(calling_station)==17 and calling_station.rfind(':')!=-1)) and packetobject.get('Service-Type', [''])[0]=='Framed-User': 
            return 'PPPOE'
        elif nas_port_type == (None,) and packetobject.get('Service-Type', [''])[0]=='Framed-User': 
            return 'Wireless'        
        elif nas_port_type == 'Wireless-802.11':
            return 'W802.1x'
        elif packetobject.has_key('Mikrotik-Host-IP'):
            return 'HotSpot'
        elif nas_port_type == 'Ethernet' and not packetobject.has_key('Service-Type'):
            return 'DHCP'
        elif nas_port_type == 'Virtual' and packetobject.get('Service-Type', [''])[0]=='lISG':
            #print 'lISG'
            return 'lISG'
        elif packetobject.get('Acct-Status-Type', [''])[0]=='Accounting-On': 
            return 'Accounting-On'
        else:
            logger.warning('Nas access type warning: unknown type: %s', nas_port_type)
            logger.warning('Packet: %s', (repr(packetobject)))
    except Exception, ex:
        logger.error('Packet access type error: %s \n %s', (repr(ex), repr(packetobject)))
    return

     
class Reception_UDP(DatagramProtocol):
    '''
    Twisted Asynchronous server that recieves datagrams with RAD ACCT packets
    and appends them to 'radAcctQueue' queue.
    '''

        
    def datagramReceived(self, data, addrport):
        if len(data) <= vars.MAX_DATAGRAM_LEN:
            acct_queue.put((data, addrport, self.transport))
        else:
            logger.error("RAD ACCT server exception: packet %s <= %s", (len(data), vars.MAX_DATAGRAM_LEN))
                               

class AcctHandler(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.dbconn = get_connection(vars.db_dsn)
        self.dateCache = datetime.datetime(2000, 1, 1)
        self.caches = None

    def run(self):
        global cacheMaster, vars, suicideCondition
        while True:
            if suicideCondition[self.__class__.__name__]: break
            try:  
                if cacheMaster.date > self.dateCache:
                    cacheMaster.lock.acquire()
                    try:
                        self.caches = cacheMaster.cache
                        dateAT = deepcopy(cacheMaster.date)
                    except Exception, ex:
                        logger.error("%s: cache exception: %s", (self.getName(), repr(ex)))
                    finally:
                        cacheMaster.lock.release()
                        if 0: assert isinstance(self.caches, RadAcctCaches)

                if not self.caches:
                    raise Exception("Caches were not ready!")
                
                packetobject = None
                d = acct_queue.get(timeout=0.1)
                if not d:
                    time.sleep(0.1)
                    continue
                data,addrport, transport = d
                if data:
                    packetobject = packet.Packet(dict = vars.DICT, packet = data)
                else:
                    continue
                            
                if not packetobject:
                    time.sleep(0.15)
                    continue
                
                if False: assert isinstance(packetobject, packet.AcctPacket)

                acct_time = time.time()
                dbCur = self.dbconn.cursor()
                coreconnect = HandleSAcct(packetobject=packetobject, dbCur=dbCur, transport = transport, addrport = addrport)
                coreconnect.caches = self.caches          

                coreconnect.handle()
       
                 
                logger.info("ACCT: %s, USER: %s, NAS: %s, ACCESS TYPE: %s", (time.time()-acct_time, coreconnect.userName, coreconnect.nasip, coreconnect.access_type))
                #dbCur.connection.commit()
                dbCur.close()
                del coreconnect
            except Queue.Empty, ex: 
                continue
            except Exception, ex:
                
                logger.error("%s readfrom exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.dbconn = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)

class PacketSender(Thread):

    def run(self):
        global vars, suicideCondition
        while True:
            if suicideCondition[self.__class__.__name__]: 
                break
            try:
                d = acct_output_queue.get(timeout=0.1)
                if not d:
                    time.sleep(0.5)
                    continue
                data,addrport, transport = d
                transport.write(data, addrport)
            except Queue.Empty, ex:
                continue
            except Exception, ex:
                logger.error("%s readfrom exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))


                        
class HandleSBase(object):
    __slots__ = ('packetobject', 'cacheDate', 'nasip', 'caches', 'replypacket', 'userName', 'transport', 'addrport')

    def auth_NA(self):
        """
        Denides access
        """        
        self.packetobject.username=None
        self.packetobject.password=None
        # Access denided
        self.packetobject.code = packet.AccessReject
        return self.packetobject

    # Main
    def handle(self):
        pass



#acct class
class HandleSAcct(HandleSBase):
    """process account information after connection"""
    """ Если это аккаунтинг хотспот-сервиса, при поступлении Accounting-Start пишем в профиль пользователя IP адрес, который ему выдал микротик"""
    __slots__ = () + ('cur', 'access_type')

    def __init__(self, packetobject, dbCur, transport, addrport):
        super(HandleSAcct, self).__init__()
        self.packetobject=packetobject
        nas_ip = str(packetobject.get('NAS-IP-Address', [''])[0])
        if not nas_ip:
            nas_ip = addrport[0]
        self.nasip=nas_ip
        self.replypacket=packetobject.CreateReply()
        self.access_type=get_accesstype(packetobject)
        #print self.access_type
        self.cur = dbCur
        self.userName = ''
        self.transport = transport
        self.addrport = addrport

    def get_bytes(self):
        bytes_in  = self.packetobject['Acct-Input-Octets'][0]  + self.packetobject.get('Acct-Input-Gigawords', (0,))[0]  * vars.GIGAWORD
        bytes_out = self.packetobject['Acct-Output-Octets'][0] + self.packetobject.get('Acct-Output-Gigawords', (0,))[0] * vars.GIGAWORD
        return (bytes_in, bytes_out)

    def acct_NA(self):
        """Deny access"""
        # Access denided
        self.replypacket.code = packet.AccessReject
        acct_output_queue.put((self.replypacket.ReplyPacket(), self.addrport, self.transport))
    
    def reply(self):
        #self.transport.write(self.replypacket.ReplyPacket(), self.addrport)
        
        acct_output_queue.put((self.replypacket.ReplyPacket(), self.addrport, self.transport))
        
    def handle(self):
        # TODO: Прикрутить корректное определение НАС-а
        nas_by_int_id = False
        nas_int_id = None
        nas_name = ''
        acc = None
        nas=None
        if self.packetobject.has_key('NAS-Identifier'):
            nas_name = self.packetobject['NAS-Identifier'][0]
            nasses = self.caches.nas_cache.by_ip_n_identify.get((self.nasip,nas_name))
            nas_by_int_id = True
        else:
            nasses = self.caches.nas_cache.by_ip.get(self.nasip)
        if not nasses:
            logger.info('ACCT: unknown NAS: %s', (self.nasip,))
            return None
        ipinuse_id = None
        class_info=self.packetobject.get('Class', ",")[0].split(",")
        session_speed = ''
        if len(class_info)==4:
            subacc_id, ipinuse_id, nas_int_id, session_speed = class_info
        elif len(class_info)==3:
            subacc_id, ipinuse_id, session_speed = class_info
        elif len(class_info)==2:
            subacc_id, session_speed = class_info
            
        if nas_int_id=='None':
            nas_int_id=None
        else:
            try:
                nas_int_id=int(nas_int_id)
            except:
                logger.warning("Nas, presented in Class attribute %s can`t be converted to int", (nas_int_id, ))
                nas_int_id=None
        #if 0: assert isinstance(nas, NasData)
        logger.info('ACCT: Extracting subacc_id, speed from cookie: subacc=%s ipinuse=%s nas_int_id=%s speed=%s', (subacc_id, ipinuse_id, nas_int_id, session_speed,))
        self.replypacket.secret=str(nasses[0].secret)  
        if self.packetobject.get('Acct-Status-Type', [''])[0]=='Accounting-On':
            self.replypacket.code = packet.AccountingResponse
            logger.info('ACCT: Processing Accounting On from nas: %s', (self.nasip,))
            return self.reply()
             
        #if self.packetobject['User-Name'][0] not in account_timeaccess_cache or account_timeaccess_cache[self.packetobject['User-Name'][0]][2]%10==0:
        self.userName = str(self.packetobject['User-Name'][0])
        #subacc = SubAccount()
        if self.access_type=='lISG':
            subacc = self.caches.subaccount_cache.by_ipn_ip.get(self.userName)
        if self.access_type=='Wireless':
            logger.info('ACCT: Searching subaccount by mac %s', (self.userName,))
            subacc = self.caches.subaccount_cache.by_mac.get(self.userName)
        elif not subacc_id:
            logger.info('ACCT: Searching subaccount by username %s', (self.userName,))
            subacc = self.caches.subaccount_cache.by_username.get(self.userName)
        elif subacc_id:
            logger.info('ACCT: Searching subaccount by id %s', (subacc_id,))
            subacc = self.caches.subaccount_cache.by_id.get(int(subacc_id))

        if subacc:
            acc = self.caches.account_cache.by_id.get(subacc.account_id)
        elif self.access_type=='HotSpot':
            acc = self.caches.account_cache.by_username.get(self.userName)
        
        if not acc:        
            logger.info('ACCT: Account for subaccount %s not found. HotSpot user not found', (subacc_id,))
            return self.acct_NA()
        
        if acc is None:
            self.cur.connection.commit()
            #self.cur.close()
            logger.warning("Unknown User %s", self.userName)
            return self.acct_NA()
        if 0: assert isinstance(acc, AccountData)
        if nas_int_id:
            nas = self.caches.nas_cache.by_id.get(nas_int_id)
            if not nas:
                logger.warning("Nas, presented in Class attribute %s not found in system. Settings nas_int_id to Null and search real nas", (nas_int_id, ))
                nas_int_id=None
        if not nas:
            nas = self.caches.nas_cache.by_id.get(subacc.nas_id)
        if (nas and nas not in nasses) and (vars.IGNORE_NAS_FOR_VPN is False):
            """
            Если NAS пользователя найден  и нас не в списке доступных и запрещено игнорировать сервера доступа 
            """
            logger.warning("Account nas(%s) is not in sended nasses and IGNORE_NAS_FOR_VPN is False %s", (repr(nas), nasses,))
            return self.acct_NA()
        elif not nas:
            """
            Иначе, если указан любой NAS - берём первый из списка совпавших по IP
            """
            nas = nasses[0]
        self.replypacket.secret=str(nas.secret)

        if not vars.IGNORE_NAS_FOR_VPN:
            nas_by_int_id = False
            
        self.replypacket.code = packet.AccountingResponse
        
        self.reply()
        now = datetime.datetime.now()
        #print self.packetobject
        #packet_session = self.packetobject['Acct-Session-Id'][0]
        logger.warning("Session %s", (repr(self.packetobject),))
        if self.packetobject['Acct-Status-Type']==['Start']:
            logger.warning("Starting session %s", (repr(self.packetobject),))
            if nas_int_id:
                self.cur.execute("""SELECT id FROM radius_activesession
                               WHERE account_id=%s AND sessionid=%s AND
                               caller_id=%s AND called_id=%s AND 
                               nas_int_id=%s AND framed_protocol=%s and session_status='ACTIVE' and interrim_update is Null;
                            """, (acc.account_id, self.packetobject['Acct-Session-Id'][0],\
                                   self.packetobject.get('Calling-Station-Id', [''])[0],
                                   self.packetobject.get('Called-Station-Id',[''])[0], \
                                   nas_int_id, self.access_type,))
            else:                
                self.cur.execute("""SELECT id FROM radius_activesession
                                   WHERE account_id=%s AND sessionid=%s AND
                                   caller_id=%s AND called_id=%s AND 
                                   nas_id=%s AND framed_protocol=%s and session_status='ACTIVE' and interrim_update is Null;
                                """, (acc.account_id, self.packetobject['Acct-Session-Id'][0],\
                                       self.packetobject.get('Calling-Station-Id', [''])[0],
                                       self.packetobject.get('Called-Station-Id',[''])[0], \
                                       self.nasip, self.access_type,))

            allow_write = self.cur.fetchone() is None


            if allow_write:
                self.cur.execute("""INSERT INTO radius_activesession(account_id, subaccount_id, sessionid, date_start,
                                 caller_id, called_id, framed_ip_address, nas_id, 
                                 framed_protocol, session_status, nas_int_id, speed_string,nas_port_id,ipinuse_id)
                                 VALUES (%s, %s, %s,%s,%s, %s, %s, %s, %s, 'ACTIVE', %s, %s, %s, %s);
                                 """, (acc.account_id, subacc.id, self.packetobject['Acct-Session-Id'][0], now,
                                        self.packetobject.get('Calling-Station-Id', [''])[0], 
                                        self.packetobject.get('Called-Station-Id',[''])[0], 
                                        self.packetobject.get('Framed-IP-Address',[''])[0],
                                        self.nasip, self.access_type, nas_int_id, session_speed, self.packetobject['NAS-Port'][0] if self.packetobject.get('NAS-Port') else None ,ipinuse_id if ipinuse_id else None ))
                if ipinuse_id:
                    self.cur.execute("UPDATE billservice_ipinuse SET ack=True where id=%s", (ipinuse_id,))
        elif self.packetobject['Acct-Status-Type']==['Alive']:
            bytes_in, bytes_out = self.get_bytes()


            if nas_int_id:
                self.cur.execute("""UPDATE radius_activesession
                             SET interrim_update=%s,bytes_out=%s, bytes_in=%s, session_time=%s, framed_ip_address=%s, session_status='ACTIVE'
                             WHERE sessionid=%s and nas_int_id=%s and account_id=%s  and framed_protocol=%s and nas_port_id=%s and date_end is Null;
                             """, (now, bytes_in, bytes_out, self.packetobject['Acct-Session-Time'][0], self.packetobject.get('Framed-IP-Address',[''])[0], self.packetobject['Acct-Session-Id'][0], nas_int_id, acc.account_id, self.access_type,self.packetobject['NAS-Port'][0] if self.packetobject.get('NAS-Port') else None))
            else:
                self.cur.execute("""UPDATE radius_activesession
                             SET interrim_update=%s,bytes_out=%s, bytes_in=%s, session_time=%s, framed_ip_address=%s, session_status='ACTIVE'
                             WHERE sessionid=%s and nas_id=%s and account_id=%s and framed_protocol=%s and nas_port_id=%s and date_end is Null;
                             """, (now, bytes_in, bytes_out, self.packetobject['Acct-Session-Time'][0], self.packetobject.get('Framed-IP-Address',[''])[0], self.packetobject['Acct-Session-Id'][0], self.nasip, acc.account_id, self.access_type,self.packetobject['NAS-Port'][0] if self.packetobject.get('NAS-Port') else None))


        elif self.packetobject['Acct-Status-Type']==['Stop']:
            bytes_in, bytes_out=self.get_bytes()


            if nas_int_id:
                self.cur.execute("""UPDATE radius_activesession SET date_end=%s, session_status='ACK', acct_terminate_cause=%s
                             WHERE sessionid=%s and nas_int_id=%s and account_id=%s and framed_protocol=%s and nas_port_id=%s and date_end is Null;;
                             """, (now, self.packetobject.get('Acct-Terminate-Cause', [''])[0], self.packetobject['Acct-Session-Id'][0], nas_int_id, acc.account_id, self.access_type,self.packetobject['NAS-Port'][0] if self.packetobject.get('NAS-Port') else None,))
            else:
                self.cur.execute("""UPDATE radius_activesession SET date_end=%s, session_status='ACK', acct_terminate_cause=%s
                             WHERE sessionid=%s and nas_id=%s and account_id=%s and framed_protocol=%s and nas_port_id=%s and date_end is Null;;
                             """, (now, self.packetobject.get('Acct-Terminate-Cause', [''])[0], self.packetobject['Acct-Session-Id'][0], self.nasip, acc.account_id, self.access_type,self.packetobject['NAS-Port'][0] if self.packetobject.get('NAS-Port') else None,))
            if ipinuse_id:
                self.cur.execute("UPDATE billservice_ipinuse SET disabled=now() WHERE id=%s", (ipinuse_id,))
        self.cur.connection.commit()
        #self.cur.close()       
        




class CacheRoutine(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        #connection = pool.connection()
        #connection._con._con.set_client_encoding('UTF8')
        global suicideCondition, cacheMaster, flags, vars
        self.connection = get_connection(vars.db_dsn)
        counter = 0; now = datetime.datetime.now
        while True:
            if suicideCondition[self.__class__.__name__]:
                 
                break            
            try: 
                if flags.cacheFlag or (now() - cacheMaster.date).seconds > vars.CACHE_TIME:
                    run_time = time.time()                    
                    cur = self.connection.cursor()
                    #renewCaches(cur)
                    renewCaches(cur, cacheMaster, RadAcctCaches, 41, (vars.CRYPT_KEY, ))
                    #cur.connection.commit()
                    cur.close()            
                    counter += 1
                    if flags.cacheFlag:
                        with flags.cacheLock: flags.cacheFlag = False
                    logger.info("ast time : %s", time.time() - run_time)

            except Exception, ex:
                logger.error("%s : #30410004 : %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(5)


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
        logger.setNewLevel(int(config.get("radius", "log_level")))
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
    global  cacheThr, packetSenderThr, suicideCondition, vars
    #asyncore.close_all()
    suicideCondition[cacheThr.__class__.__name__] = True
    suicideCondition[packetSenderThr.__class__.__name__] = True

    logger.lprint("About to stop gracefully.")
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    #print suicideCondition
    #time.sleep(1)
    #pool.close()
    rempid(vars.piddir, vars.name)
    print "RAD ACCT: exiting"
    logger.lprint("Stopping gracefully.")
    #
    reactor.callFromThread(reactor.disconnectAll)
    reactor.callFromThread(reactor.stop)
    #reactor.stop()
    

def ungraceful_save():
    global suicideCondition, cacheThr, packetSenderThr
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    rempid(vars.piddir, vars.name)
    asyncore.close_all()
    print "RAD ACCT: exiting"
    logger.lprint("RAD ACCT exiting.")
    for th in threads:
        th.join()
    cacheThr.join()    
    packetSenderThr.join()
    sys.exit()

def main():
    global threads, curCachesDate, cacheThr, suicideCondition, server_acct, sqlloggerthread, packetSenderThr
    threads = []

    for i in xrange(vars.ACCT_THREAD_NUM):
        newAcct = AcctHandler()
        newAcct.setName('ACCT:#%i: AcctHandler' % i)
        threads.append(newAcct)
            
    cacheThr = CacheRoutine()
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.setName("CacheRoutine")
    cacheThr.start()    

    packetSenderThr = PacketSender()
    suicideCondition[packetSenderThr.__class__.__name__] = False
    packetSenderThr.setName("PacketSender")
    packetSenderThr.start()    
    
    time.sleep(2)
    while cacheMaster.read is False:        
        if not cacheThr.isAlive:
            print 'Exception in cache thread: exiting'
            sys.exit()
        time.sleep(10)
        if not cacheMaster.read: 
            print 'rad_acct caches still not read, maybe you should check the log'
    
    #print dir(cacheMaster.cache)
    print 'caches ready'

    for th in threads:
        suicideCondition[th.__class__.__name__] = False
        th.start()        
        logger.info("Thread %s started", th.getName())
        time.sleep(0.1)

    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')

    try:
        signal.signal(signal.SIGINT, SIGINT_handler)
    except: logger.lprint('NO SIGINT!')
    
    try:
        signal.signal(signal.SIGHUP, SIGHUP_handler)
    except: logger.lprint('NO SIGHUP!')

    try:
        signal.signal(signal.SIGUSR1, SIGUSR1_handler)
    except: logger.lprint('NO SIGUSR1!')

    print "ebs: rad_acct: started"
    savepid(vars.piddir, vars.name)
    reactor.listenUDP(1813, Reception_UDP())
    reactor.run(installSignalHandlers=False)

if __name__ == "__main__":
    if "-D" in sys.argv:
        pass
        #daemonize("/dev/null", "log.txt", "log.txt")

    config = ConfigParser.ConfigParser()

    config.read("ebs_config.ini")
    if '--help' in sys.argv:
        print "-p <port> for custom port assignement"
        sys.exit(0)
    


        

    server_acct = None
    try:
        import psyco
        #psyco.log()
        psyco.full(memory=100)
        psyco.profile(0.05, memory=100)
        psyco.profile(0.2)
    except:
        print "Can`t run optimizer"
        
    try:
        flags = RadFlags()
        vars  = RadVars()
        queues= RadQueues()
        acct_queue = Queue.Queue()
        acct_output_queue = Queue.Queue()
        sessions_speed={}#account:(speed,datetime)
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME)

        if '-p' in sys.argv and len(sys.argv)==3:
            port = sys.argv[2]
        elif '-p' in sys.argv:
            print "unknown port"
            sys.exit()
        else:
            port = vars.ACCT_PORT
        
        cacheMaster = CacheMaster()

        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file)
        utilites.log_adapt = logger.log_adapt
        saver.log_adapt    = logger.log_adapt
        logger.lprint('Radius start')
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)

        #write profiling info?
        flags.writeProf = logger.writeInfoP()         

        suicideCondition = {}
        

        #-------------------
        
        print "ebs: rad_acct: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in rad, exiting: ', repr(ex)
        logger.error('Exception in rpc, exiting: %s \n %s', (repr(ex), traceback.format_exc()))        
