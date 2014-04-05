#-*-coding: utf-8 -*-

from __future__ import with_statement
import site
site.addsitedir('/opt/ebs/venv/lib/python2.6/site-packages')
site.addsitedir('/opt/ebs/venv/lib/python2.7/site-packages')
import gc
import sys
sys.path.insert(0, "modules")
sys.path.append("cmodules")
import time
import signal
import packet
import asyncore
import datetime
import traceback
import ConfigParser

import isdlogger
import saver, utilites

from time import clock
from copy import deepcopy
from threading import Thread, Lock

from collections import deque

import commands
from hashlib import md5
from base64 import b64decode

from classes.rad_auth_cache import *
from classes.rad_class.CardActivateData import CardActivateData

from classes.flags import RadFlags
from classes.vars import RadVars, RadQueues
from utilites import savepid, rempid, get_connection, getpid, check_running, command_string_parser, speed_list_to_dict, create_speed
import Queue
from option_parser import parse

from utilites import in_period_info
import auth
from auth import Auth, get_eap_handlers
from cacherouter import Cache
import cacherouter
globals()['mikrobill.cacherouter'] = cacherouter

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

def authNA(packet):
    return packet.ReplyPacket()

def get_accesstype(packetobject):
    """
    Returns access type name by which a user connects to the NAS
    """
    #print show_packet(packetobject)
    try:
        nas_port_type = packetobject.get('NAS-Port-Type', (None,))[0]
        calling_station = packetobject.get('Calling-Station-Id', [''])[0]
        logger.info('Nas port type: %s Service Type %s Calling-Station-Id %s', (nas_port_type, packetobject.get('Service-Type', [''])[0], calling_station ))
        if nas_port_type == 'Virtual' and packetobject.get('Service-Type', [''])[0]=='Framed-User':
            return 'PPTP'
        elif (nas_port_type in ['Ethernet', 'Async'] or (len(calling_station)==17 and calling_station.rfind(':')!=-1)) and packetobject.get('Service-Type', [''])[0]=='Framed-User':
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
    Twisted Asynchronous server that recieves datagrams with RAD AUTH packets
    and appends them to 'radAuthQueue' queue.
    '''

        
    def datagramReceived(self, data, addrport):
        if len(data) <= vars.MAX_DATAGRAM_LEN:
            auth_queue.put((data, addrport, self.transport))
        else:
            logger.error("RAD AUTH server exception: packet %s <= %s", (len(data), vars.MAX_DATAGRAM_LEN))
                               

class AuthHandler(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.dbconn = get_connection(vars.db_dsn)
        self.dbconn.set_isolation_level(0)
        self.dbconn.set_session(autocommit=True)
        self.dateCache = datetime.datetime(2000, 1, 1)
        self.caches = None
        self.cache = Cache(self.dbconn, vars.memcached_host, vars.CRYPT_KEY, logger = logger)

    def run(self):
        global vars, suicideCondition
        while True:
            if suicideCondition[self.__class__.__name__]: break
            try:  

                
                packetobject = None
                d = auth_queue.get(block=True, timeout=0.03)
                if not d:
                    time.sleep(0.01)
                    continue
                data,addrport, transport = d
                if data:
                    packetobject = packet.Packet(dict = vars.DICT, packet = data)
                else:
                    continue


                auth_time = time.time()
                returndata = ''
                nas_ip = str(packetobject.get('NAS-IP-Address', [''])[0])
                if not nas_ip:
                    nas_ip = addrport[0]
                access_type = get_accesstype(packetobject)
                logger.debug("%s: Access type: %s, packet: %s", (self.getName(), access_type, packetobject.code))
                user_name = ''
                try:
                    user_name = str(packetobject['User-Name'][0])
                except:
                    pass
                if access_type in ['HotSpot']:
                    coreconnect = HandleHotSpotAuth(packetobject=packetobject, access_type=access_type, dbCur=self.dbconn.cursor(), transport = transport, addrport = addrport)
                    coreconnect.nasip = nas_ip
                    coreconnect.fMem = fMem; coreconnect.caches = self.caches
                    coreconnect.cache = self.cache
                    coreconnect.handle()


                elif access_type in ['DHCP', 'Wireless'] :
                    coreconnect = HandleSDHCP(packetobject=packetobject, transport = transport, addrport = addrport)
                    coreconnect.nasip = nas_ip; coreconnect.caches = self.caches
                    coreconnect.cache = self.cache
                    coreconnect.handle()

                    
                elif access_type in ['lISG'] :
                    coreconnect = HandlelISGAuth(packetobject=packetobject, access_type=access_type, transport = transport, addrport = addrport)
                    coreconnect.nasip = nas_ip; coreconnect.caches = self.caches
                    coreconnect.cache = self.cache
                    authobject, packetfromcore = coreconnect.handle()
                    if packetfromcore is None: 
                        logger.info("Unknown NAS or Account %s", str(nas_ip))
                        self.dbconn.commit()
                        continue

                    authobject.ReturnPacket(packetfromcore)                    
                    
                else:
                    a = time.time()
                    coreconnect = HandleSAuth(packetobject=packetobject, access_type=access_type, dbconn=self.dbconn, transport = transport, addrport = addrport)
                    coreconnect.nasip = nas_ip
                    coreconnect.fMem = fMem; coreconnect.caches = self.caches
                    coreconnect.cache = self.cache
                    coreconnect.handle()
                    
                    #logger.debug("AUTH packet: %s", show_packet(packetfromcore))

                self.dbconn.commit()
                logger.info("AUTH: %s, USER: %s, NAS: %s, ACCESS TYPE: %s", (time.time()-auth_time, user_name, nas_ip, access_type))
                #dbCur.connection.commit()

                del coreconnect
            except Queue.Empty, ex:
                continue 
            except Exception, ex:
                logger.error("%s readfrom exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                
                
                if ex.__class__ in vars.db_errors:
                    
                    try:
                        try:
                            self.dbconn.rollback()
                        except:
                            logger.info("%s : transaction tollback error" , (self.getName(), ))
                        self.dbconn = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(1)


class SQLLoggerThread(Thread):

    def __init__(self, suicide_condition):
        Thread.__init__(self)
        self.suicide_condition = suicide_condition
        self.dbconn = get_connection(vars.db_dsn)
        self.dbconn.set_isolation_level(0)
        self.cursor = self.dbconn.cursor()
        self.sqllog_deque = deque()
        self.sqllog_lock  = Lock()

        # 'loggerthread initialized'
    
    def add_message(self, account=None, subaccount=None, nas=None, type='', service='', cause='', datetime=None):
        self.sqllog_deque.append((account, subaccount, nas, type, service, cause, datetime))
        #print 'message added'

    def run(self):
        a=0
        while True:
            
            #print 'log check'
            #print "vars.SQLLOG_FLUSH_TIMEOUT", vars.SQLLOG_FLUSH_TIMEOUT
            
            if self.suicide_condition[self.__class__.__name__]: 
                break
            if time.time()-a<vars.SQLLOG_FLUSH_TIMEOUT: 
                time.sleep(2)
                
                continue
            with self.sqllog_lock:
                d = []
                while len(self.sqllog_deque) > 0:
                    d.append(self.sqllog_deque.pop())
                self.cursor.executemany("""INSERT INTO radius_authlog(account_id, subaccount_id, nas_id, type, service, cause, datetime)
                                    VALUES(%s,%s,%s,%s,%s,%s,%s)""", d)
                    #print account, subaccount, nas, type, service, cause, datetime
            #self.dbconn.commit()
            a=time.time()

            
class HandleSBase(object):
    __slots__ = ('packetobject', 'cacheDate', 'nasip', 'caches', 'replypacket', 'userName', 'transport', 'addrport', 'cache', 'authobject')

    def auth_NA(self):
        """
        Denides access
        """        
        self.packetobject.username=None
        self.packetobject.password=None
        self.replypacket = None
        self.addrport = None
        self.transport = None
        # Access denided
        self.packetobject.code = packet.AccessReject
        self.cache = None
        return self.packetobject

    def reply(self):
        #self.transport.write(self.replypacket.ReplyPacket(), self.addrport)
        returndata, replypacket = self.authobject.ReturnPacket(self.replypacket, mppe_support=vars.MPPE_SUPPORT) 
        logger.debug("REPLY packet: %s", repr(replypacket))               

        self.transport.write(returndata, self.addrport)
        
    # Main
    def handle(self):
        pass

class HandleSNA(HandleSBase):
    __slots__ = () 
    def __init__(self,  packetobject):
        """TO-DO: Сделать проверку в методе get_nas_info на тип доступа"""
        #self.nasip = str(packetobject['NAS-IP-Address'][0])
        self.packetobject = packetobject.CreateReply()
        #self.cur = dbCur

    def handle(self):
        nas = self.cache.get_nas_by_ip(self.nasip)       

        if nas is not None:
            self.packetobject.secret = str(nas.secret)
            return "", self.auth_NA()
        

class HandleSAuth(HandleSBase):
    __slots__ = () + ('access_type', 'secret', 'speed','session_speed','nas_id', 'nas_type', 'multilink', 'fMem', 'datetime','dbconn','cursor', 'transport', 'addrport')
    def __init__(self,  packetobject, access_type, dbconn, transport, addrport):
        self.packetobject = packetobject
        self.access_type=access_type or 'UNKNOWN'
        self.secret = ''     
        self.session_speed = ''   
        self.dbconn=dbconn
        self.cursor=None
        self.transport = transport
        self.addrport = addrport



    def auth_NA(self, authobject):
        """
        Deny access
        """
        self.authobject.set_code(3)

        returndata, replypacket = self.authobject.ReturnPacket(self.packetobject.CreateReply()) 
        logger.debug("REPLY packet: %s", repr(replypacket))               

        self.transport.write(returndata, self.addrport)

        
    def add_values(self, tarif_id, nas_id, account_status):
        # CREATE ONE SECTION
        attrs = self.cache.get_radiusattr_by_tarif_id(tarif_id) or []
        account_status =  1 if account_status else 2
        for attr in attrs:
            if attr.account_status != 0 and attr.account_status!=account_status: continue

            if attr.vendor:
                self.replypacket.AddAttribute((attr.vendor,attr.attrid), str(attr.value))
            else:
                self.replypacket.AddAttribute(attr.attrid, str(attr.value))
    
        attrs = self.cache.get_radiusattr_by_nas_id(nas_id) or []
        for attr in attrs:
            if attr.account_status != 0 and attr.account_status!=account_status: continue

            if attr.vendor:
                self.replypacket.AddAttribute((attr.vendor,attr.attrid), str(attr.value))
            else:
                self.replypacket.AddAttribute(attr.attrid, str(attr.value))
                
    def find_free_ip(self,id, acct_interval):
        def next(id):
            pool= self.cache.get_ippool_by_id(id)
            if not pool: return None
            return pool.next_pool_id
        
        processed_pools=[]
        first = True
        while True:
            if first==False:
                id=next(id)
                if not id: return None,None   
                if id in processed_pools: logger.error("Recursion in ippools was found");  return id,None
            else:
                first=False
            
            processed_pools.append(id)

            self.cursor.execute('SELECT get_free_ip_from_pool(%s, %s);', (id, acct_interval))
            framed_ip_address = self.cursor.fetchone()[0]
            if framed_ip_address: return id, framed_ip_address

    def create_speed(self, nas, subacc_id, tarif_id, account_id, speed=''):
        if not (nas.speed_value1 or nas.speed_value2): return
        defaults = self.cache.get_defspeed_by_tarif_id(tarif_id)
        speeds   = self.cache.get_speed_by_tarif_id(tarif_id) or []
        correction = self.cache.get_speedlimit_by_account_id(account_id)
        
        logger.info("Account speed status account_id=%s subaccount_id=%s tarif_id=%s speed=%s", (account_id, subacc_id, tarif_id, speed))

        
        now=datetime.datetime.now()
        addonservicespeed=[]  
        br = False
        if subacc_id:
            accservices = self.cache.get_accountaddonservice_by_subaccount_id(subacc_id) or []
            for accservice in accservices:                                 
                service = self.cache.get_addonservice_by_id(accservice.service_id)     
                for pnode in self.cache.get_timeperiodnode_by_timeperiod_id(service.timeperiod_id) or []:                                       
                    if not accservice.deactivated  and service.change_speed and fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, now)[3]:                                                                        
                        addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.min_tx, service.min_rx, service.priority,  service.speed_units, service.change_speed_type)                                    
                        br = True
                        break   
                if br: break
        br = False
        if not addonservicespeed: 
            accservices = self.cache.get_accountaddonservice_by_account_id(account_id) or []
            for accservice in accservices:                                 
                service = self.cache.get_addonservice_by_id(accservice.service_id)           
                for pnode in self.cache.get_timeperiodnode_by_timeperiod_id(service.timeperiod_id) or []:                     
                    if not accservice.deactivated  and service.change_speed and fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, now)[3]:                                                                        
                        addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.min_tx, service.min_rx, service.priority, service.speed_units, service.change_speed_type)                                    
                        br = True
                        break    
                if br: break
                
        logger.info("Account speed data account_id=%s defaults=%s speeds=%s correction=%s addonservicespeed=%s", (account_id, repr(defaults), repr(speeds), repr(correction), repr(addonservicespeed)))
        
        speed = create_speed(defaults, speeds,  correction, addonservicespeed, speed, now, fMem)
        
        logger.info("Account speed account_id=%s result speed %s", (account_id, repr(speed)))
        
        
        self.session_speed = newspeed = ''.join([unicode(spi) for spi in speed]) 
        #print speed_sess
        command_dict=speed_list_to_dict(speed)
        
        if nas.speed_value1:
            result_params = command_string_parser(command_string=nas.speed_value1, command_dict=command_dict)
            if result_params and nas.speed_vendor_1:
                self.replypacket.AddAttribute((nas.speed_vendor_1,nas.speed_attr_id1),result_params)
            elif result_params and not nas.speed_vendor_1:
                self.replypacket.AddAttribute(nas.speed_attr_id1,result_params)


        if nas.speed_value2:
            result_params = command_string_parser(command_string=nas.speed_value2, command_dict=command_dict)
            if result_params and nas.speed_vendor_2:
                self.replypacket.AddAttribute((nas.speed_vendor_2,str(nas.speed_attr_id2)), result_params)
            elif result_params and not nas.speed_vendor_2:
                self.replypacket.AddAttribute(nas.speed_attr_id2,result_params)
                

    def create_cursor(self):
        if not self.cursor:
            self.cursor=self.dbconn.cursor()

    
    def handle(self):
        global sqlloggerthread
        self.datetime = datetime.datetime.now()
        #nasses = self.cache.get_nas_by_ip(self.nasip)
        a = time.time()
        nasses = self.cache.get_nas_by_ip(self.nasip)

        if not nasses:
            logger.warning("Requested NAS IP (%s) not found in nasses %s", (self.nasip, str(nasses),))
            sqlloggerthread.add_message(type="AUTH_NAS_NOT_FOUND", service=self.access_type, cause=u'Сервер доступа с IP %s не найден ' % self.nasip, datetime=self.datetime) 
            return '',None
        self.replypacket = packet.Packet(secret=str(nasses[0].secret),dict=vars.DICT)      
        logger.info("NAS or NASSES Found %s", (str(nasses),))
        #if 0: assert isinstance(nas, NasData)

        
        station_id = self.packetobject.get('Calling-Station-Id', [''])[0]
        if self.access_type == 'PPPOE'  and nasses[0].type=='cisco':
            station_id = station_id.replace("-",':')
        user_name = str(self.packetobject['User-Name'][0])


        logger.warning("Searching account username=%s in subaccounts with pptp-ipn_ip or pppoe-ipn_mac link %s", (user_name, station_id))
        self.authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nasses[0].secret), access_type=self.access_type, challenges = queues.challenges)
        
        subacc = self.cache.get_subaccount_by_username_w_ipn_vpn_link(user_name, station_id)
        if not subacc:
            logger.warning("Searching account username=%s in subaccounts witouth pptp-ipn_ip or pppoe-ipn_mac link", (user_name, ))
            subacc = self.cache.get_subaccount_by_username(user_name)
        if not subacc:
            logger.warning("Subaccount with username  %s not found", (user_name,))   
            sqlloggerthread.add_message(nas=nasses[0].id,type="AUTH_SUBACC_NOT_FOUND", service=self.access_type, cause=u'Субаккаунт с логином %s и ip/mac %s в системе не найден.' % (user_name, station_id), datetime=self.datetime) 
            return self.auth_NA(self.authobject)     

        acc = self.cache.get_account_by_id(subacc.account_id)
        
        if not acc:
            logger.warning("Account with username  %s not found", (user_name,))
            sqlloggerthread.add_message(nas=nasses[0].id, type="AUTH_ACC_NOT_FOUND", service=self.access_type, cause=u'Аккаунт для субаккаунта с логином %s в системе не найден.' % (user_name, ), datetime=self.datetime)
            return self.auth_NA(self.authobject)
            
        username = subacc.username 
        password = subacc.password
        vpn_ip_address = subacc.vpn_ip_address
        # Сервер доступа может быть не указан 
        nas_id = subacc.nas_id

        if self.access_type=='W802.1x':
            #nas = self.cache.get_nas_by_id(subacc.switch_id, None) # Пока не реализована нужна логика на стороне интерфейса
            nas = self.cache.get_nas_by_id(nas_id)
        else:
            nas = self.cache.get_nas_by_id(nas_id)
        logger.info("Nas id for user %s: %s ", (user_name, nas_id))
        if self.access_type in ['PPTP','L2TP'] and subacc.associate_pptp_ipn_ip and not (subacc.ipn_ip_address == station_id):
            logger.warning("Unallowed dialed ipn_ip_address for user %s vpn: station_id - %s , ipn_ip - %s; vpn_ip - %s access_type: %s", (user_name, station_id, subacc.ipn_ip_address, subacc.vpn_ip_address, self.access_type))
            sqlloggerthread.add_message(nas=nas_id, type="AUTH_ASSOC_PPTP_IPN_IP", service=self.access_type, cause=u'Попытка авторизации %s с неразрешённого IPN IP адреса %s.' % (user_name, station_id,), datetime=self.datetime)
            return self.auth_NA(self.authobject) 
        
        if self.access_type == 'PPPOE' and subacc.associate_pppoe_ipn_mac and not (subacc.ipn_mac_address == station_id):
            logger.warning("Unallowed dialed mac for user %s: station_id - %s , ipn_ip - %s; ipn_mac - %s access_type: %s", (user_name, station_id, subacc.ipn_ip_address, subacc.ipn_mac_address, self.access_type))
            sqlloggerthread.add_message(nas=nas_id, type="AUTH_ASSOC_PPTP_IPN_MAC", service=self.access_type, cause=u'Попытка авторизации %s с неразрешённого IPN MAC адреса %s.' % (user_name, station_id), datetime=self.datetime)
            return self.auth_NA(self.authobject) 
          

        if (nas and nas not in nasses) and vars.IGNORE_NAS_FOR_VPN is False and self.access_type in ['PPTP', 'PPPOE']:
            """
            Если NAS пользователя найден  и нас не в списке доступных и запрещено игнорировать сервера доступа 
            """
            logger.warning("Account nas(%s) is not in sended nasses and IGNORE_NAS_FOR_VPN is False %s", (repr(nas), nasses,))
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_BAD_NAS", service=self.access_type, cause=u'Субаккаунт %s привязан к конкретному серверу доступа, но запрос на авторизацию поступил с IP %s.' % (user_name, self.nasip), datetime=self.datetime)
            return self.auth_NA(self.authobject)
        elif not nas_id and self.access_type!='W802.1x':
            """
            Иначе, если указан любой NAS - берём первый из списка совпавших по IP
            """
            nas = nasses[0]
        elif (nas and nas not in nasses)  and self.access_type=='W802.1x':
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_8021x_NAS", service=self.access_type, cause=u'Для 802.1x авторизации должен быть указан коммутатор. Запрос на авторизацию поступил с IP %s.' % (self.nasip), datetime=self.datetime)
            logger.warning("Requested 802.1x authorization nas(%s) not assigned to user %s", (repr(nas), repr(subacc),))
            return self.auth_NA(self.authobject)            
            

        self.nas_type = nas.type
        self.replypacket = packet.Packet(secret=str(nas.secret),dict=vars.DICT)         
        self.authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nas.secret), access_type=self.access_type, challenges = queues.challenges, logger = logger)


 
        self.authobject.plainusername = str(username)
        self.authobject.plainpassword = str(password)

        
        logger.debug("Account data : %s", repr(acc))
        logger.debug("SubAccount data : %s", repr(subacc))

        process, ok, left = self.authobject._HandlePacket()
        if not process:
            logger.warning(left, ())
            logger.debug("Auth object : %s" , self.authobject)
            #self.cur.close()
            if ok:
                self.reply()
            else:
                return self.auth_NA(self.authobject)


        process, ok, left = self.authobject._ProcessPacket()
        if not process:
            logger.warning(left, ())
            logger.debug("Auth object : %s" , self.authobject)
            if ok:
                return self.reply()
            else:
                return self.auth_NA(self.authobject)

        check_auth, left = self.authobject.check_auth()
        logger.debug("Auth object : %s" , self.authobject)
        if not check_auth:
            logger.warning(left, ())
            sqlloggerthread.add_message(account=acc.id, subaccount=subacc.id, type="AUTH_BAD_PASSWORD", service=self.access_type, cause=u'Ошибка авторизации. Необходимо проверить указанный пароль.', datetime=self.datetime)
            return self.auth_NA(self.authobject) 

        #print common_vpn,access_type,self.access_type
        if acc.access_type not in ['PPTP', 'L2TP', 'PPPOE'] and (not vars.COMMON_VPN) and (acc.access_type != self.access_type) :
            logger.warning("Unallowed Tarif Access Type for user %s. Account access type - %s; packet access type - %s", (username, acc.access_type, self.access_type))
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_WRONG_ACCESS_TYPE", service=self.access_type, cause=u'Способ доступа %s не совпадает с разрешённым в параметрах тарифного плана %s.' % (self.access_type, acc.access_type), datetime=self.datetime)
            return self.auth_NA(self.authobject)

        if acc.status != 1:
            sqlloggerthread.add_message(account=acc.id, subaccount=subacc.id, type="AUTH_ACCOUNT_DISABLED", service=self.access_type, cause=u'Аккаунт отключен', datetime=self.datetime)
            return self.auth_NA(self.authobject)  
        
        acstatus = (((subacc.allow_vpn_with_null and acc.ballance >=0) or (subacc.allow_vpn_with_minus and acc.ballance<=0) or acc.ballance>0)\
                    and \
                    (subacc.allow_vpn_with_block or (not subacc.allow_vpn_with_block and not acc.balance_blocked and not acc.disabled_by_limit)))
        #acstatus = True

        
        if not acstatus and not acc.vpn_guest_ippool_id:
            logger.warning("Unallowed account status for user %s: account_status is false(allow_vpn_null=%s, ballance=%s, allow_vpn_with_minus=%s, allow_vpn_block=%s, ballance_blocked=%s, disabled_by_limit=%s, account_status=%s)", (username,subacc.allow_vpn_with_null,acc.ballance, subacc.allow_vpn_with_minus, subacc.allow_vpn_with_block, acc.balance_blocked, acc.disabled_by_limit, acc.status))
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_VPN_BALLANCE_ERROR", service=self.access_type, cause=u'Баланс %s, блокировка по лимитам %s, блокировка по недостатку баланса в начале р.п. %s' % (acc.ballance, acc.disabled_by_limit, acc.balance_blocked), datetime=self.datetime)
            return self.auth_NA(self.authobject)

        allow_dial = True #self.caches.period_cache.in_period.get(acc.tarif_id, False)

        logger.info("Authorization user:%s allowed_time:%s User Status:%s Balance:%s Disabled by limit:%s Balance blocked:%s Tarif Active:%s", ( self.packetobject['User-Name'][0], allow_dial, acc.status, acc.ballance, acc.disabled_by_limit, acc.balance_blocked, acc.tariff_active))
        if allow_dial and acc.tariff_active:
            
            if not acc.sessionscount==subacc.sessionscount==0:
                sc = subacc.sessionscount if subacc.sessionscount else acc.sessionscount #Переопределение на дефолтное значение

                self.create_cursor()
                try:
                    self.cursor.execute("""SELECT count(*) from radius_activesession WHERE account_id=%s and (date_end is null and (interrim_update is not Null or extract('epoch' from now()-date_start)<=%s)) and session_status='ACTIVE';""", (acc.id, nas.acct_interim_interval))
                    self.cursor.connection.commit()
                    cnt = self.cursor.fetchone()
                    if cnt and sc:
                        if cnt[0]>=sc:
                            logger.warning("Max sessions count %s reached for username %s. If this error persist - check your nas settings and perform maintance radius_activesession table", (sc, username,))
                            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_SESSIONS_COUNT_REACHED", service=self.access_type, cause=u'Превышено количество одновременных сессий для аккаунта', datetime=self.datetime)
                            return self.auth_NA(self.authobject)                      
                except Exception, ex:
                    logger.error("Couldn't check session dublicates for user %s account=%s because %s", (str(user_name), acc.id, repr(ex)))
                    return self.auth_NA(self.authobject) 

            ipinuse_id=''
            address_requested = False
            if (subacc.vpn_ip_address in ('0.0.0.0','', None) and (subacc.ipv4_vpn_pool_id or acc.vpn_ippool_id)) or (acstatus==False and acc.vpn_guest_ippool_id) :
               
                with vars.cursor_lock:
                    try:
                        self.create_cursor()
                        pool_id=subacc.ipv4_vpn_pool_id if subacc.ipv4_vpn_pool_id else acc.vpn_ippool_id
                        logger.debug("Searching free ip for subaccount %s in vpn  pool with id %s ", (str(user_name), pool_id))
                        if acstatus==False:
                            pool_id=acc.vpn_guest_ippool_id
                            logger.debug("Searching free ip for subaccount %s in vpn guest pool with id %s ", (str(user_name), acc.vpn_guest_ippool_id))
                            self.cursor.execute('SELECT get_free_ip_from_pool(%s, %s);', (pool_id, nas.acct_interim_interval))
                            
                            
                            vpn_ip_address = self.cursor.fetchone()[0]
                        else:
                            pool_id, vpn_ip_address = self.find_free_ip(pool_id, nas.acct_interim_interval)
                        address_requested = True
                        #self.cursor.connection.commit()
                        if vpn_ip_address in ['0.0.0.0', '', None]:
                            logger.error("Couldn't find free ipv4 address for user %s id %s in pool: %s", (str(user_name), subacc.id, pool_id))
                            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_EMPTY_FREE_IPS", service=self.access_type, cause=u'В указанном пуле нет свободных IP адресов', datetime=self.datetime)
                            #vars.cursor_lock.release()
                            return self.auth_NA(self.authobject)
                        if address_requested:
                            self.cursor.execute("INSERT INTO billservice_ipinuse(pool_id, ip, datetime, dynamic, ack) VALUES(%s,%s,now(),True, False) RETURNING id;",(pool_id, vpn_ip_address))
                            ipinuse_id=self.cursor.fetchone()[0]
                            self.cursor.connection.commit()
                        #self.cursor.connection.commit()
                    except Exception, ex:
                        logger.error("Couldn't get an address for user %s | id %s from pool: %s :: %s", (str(user_name), subacc.id, subacc.ipv4_vpn_pool_id, repr(ex)))
                        sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_IP_POOL_ERROR", service=self.access_type, cause=u'Ошибка выдачи свободного IP адреса', datetime=self.datetime)
                        return self.auth_NA(self.authobject) 
            else:
                vpn_ip_address = subacc.vpn_ip_address


             
            self.authobject.set_code(2)
            self.replypacket.username = str(username) #Нельзя юникод
            self.replypacket.password = str(password) #Нельзя юникод
            self.replypacket.AddAttribute('Service-Type', 2)
            self.replypacket.AddAttribute('Framed-Protocol', 1)
            if vpn_ip_address not in ['0.0.0.0', '', None] and vpn_ip_address.rfind(':')==-1:
                self.replypacket.AddAttribute('Framed-IP-Address', vpn_ip_address)
            self.replypacket.AddAttribute('Acct-Interim-Interval', nas.acct_interim_interval)
            #self.replypacket.AddAttribute('Framed-Compression', 0)
            if (subacc.vpn_ipv6_ip_address and subacc.vpn_ipv6_ip_address!='::') or vpn_ip_address.rfind(':')!=-1:
                #self.replypacket.AddAttribute('Framed-Interface-Id', str(subacc.vpn_ipv6_ip_address))
                self.replypacket.AddAttribute('Framed-IPv6-Prefix', str(subacc.vpn_ipv6_ip_address))
            #account_speed_limit_cache
            

                
            self.create_speed(nas, subacc.id, acc.tarif_id, acc.id, speed=subacc.vpn_speed)
            #if self.session_speed:
            self.replypacket.AddAttribute('Class', str("%s,%s,%s,%s" % (subacc.id,ipinuse_id,nas.id,str(self.session_speed))))
            self.add_values(acc.tarif_id, nas.id, acstatus)

            #print "Setting Speed For User" , self.speed
            if vars.SQLLOG_SUCCESS:
                sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_OK", service=self.access_type, cause=u'Авторизация прошла успешно.', datetime=self.datetime)
            #return self.authobject, self.replypacket
            self.reply()
            if self.access_type=='PPPOE' and vars.GET_MAC_FROM_PPPOE==True:
                logger.debug("Trying to update subaccount %s with id %s ipn mac address to: %s ", (str(user_name), subacc.id, station_id))
                with vars.cursor_lock:
                    try:
                        self.create_cursor()
                        self.cursor.execute("UPDATE billservice_subaccount SET ipn_mac_address=%s WHERE id=%s", (station_id, subacc.id,))
                        self.cursor.connection.commit()
                        logger.debug("Update subaccount %s with id %s ipn mac address to: %s was succefull", (str(user_name), subacc.id, station_id))
                    except Exception, ex:
                        logger.error("Error update subaccount %s with id %s ipn mac address to: %s %s", (str(user_name), subacc.id, station_id, repr(ex)))
                        

        else:
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_BAD_TIME", service=self.access_type, cause=u'Тариф неактивен(%s) или запрещённое время %s' % (acc.tariff_active==False, allow_dial==False), datetime=self.datetime)
            return self.auth_NA(self.authobject)


class HandlelISGAuth(HandleSAuth):
    
    def handle(self):
        global sqlloggerthread
        self.datetime = datetime.datetime.now()
        nasses = self.cache.get_nas_by_ip(self.nasip)
        if not nasses:
            logger.warning("Requested NAS IP (%s) not found in nasses %s", (self.nasip, str(nasses),))
            sqlloggerthread.add_message(type="AUTH_NAS_NOT_FOUND", service=self.access_type, cause=u'Сервер доступа с IP %s не найден ' % self.nasip, datetime=self.datetime) 
            return '',None
        
        #if 0: assert isinstance(nas, NasData)


        #station_id = self.packetobject.get('Calling-Station-Id', [''])[0]
        station_id = str(self.packetobject['User-Name'][0])
        user_name = station_id
        #print station_id
        #row = get_account_data_by_username(self.cur, self.packetobject['User-Name'][0], self.access_type, station_id=station_id, multilink = self.multilink, common_vpn = common_vpn)
        #print self.caches.account_cache.by_ipn_ip_nas
        logger.warning("Searching lISG account for ip address %s", station_id)
        #acc = self.caches.account_cache.by_ipn_ip_nas.get((station_id, nas.id))
        #subacc = SubAccount()
        subacc = self.cache.get_subaccount_by_ipn_ip(station_id)
        self.authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nasses[0].secret), access_type=self.access_type, challenges = queues.challenges)
        if not subacc:
            logger.warning("Subcccount for lISG not found for ip address %s", (station_id,))
            sqlloggerthread.add_message(type="AUTH_SUBACC_NOT_FOUND", service=self.access_type, cause=u'Субаккаунт с логином  ipn ip %s в системе не найден.' % (station_id,), datetime=self.datetime)
            #Не учитывается сервер доступа
            return self.auth_NA(self.authobject)
        acc = self.cache.get_account_by_id(subacc.account_id)
        
        if not acc:
            logger.warning("Account with username  %s not found", (user_name,))
            sqlloggerthread.add_message(type="AUTH_ACC_NOT_FOUND", service=self.access_type, cause=u'Аккаунт для субаккаунта с логином %s в системе не найден.' % (subacc.username, ), datetime=self.datetime)
            return self.auth_NA(self.authobject)
            
        nas_id = subacc.nas_id

        nas = self.cache.get_nas_by_id(nas_id)
        

        
        if vars.IGNORE_NAS_FOR_VPN is False and (nas and nas not in nasses):
            """
            Если NAS пользователя найден  и нас не в списке доступных и запрещено игнорировать сервера доступа 
            """
            logger.warning("Account nas(%s) is not in sended nasses and IGNORE_NAS_FOR_VPN is False %s", (repr(nas), nasses,))
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_BAD_NAS", service=self.access_type, cause=u'Субаккаунт привязан к конкретному серверу доступа, но запрос на авторизацию поступил с IP %s.' % (self.nasip), datetime=self.datetime)
            return self.auth_NA(self.authobject)
        elif not nas_id:
            """
            Иначе, если указан любой NAS - берём первый из списка совпавших по IP
            """
            nas = nasses[0]

        nas_id = nas.id    
        self.authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nas.secret), access_type=self.access_type, challenges = queues.challenges)

        self.nas_type = nas.type
        self.replypacket = packet.Packet(secret=str(nas.secret),dict=vars.DICT)
        
        logger.debug("Account data : %s", repr(acc))

        process, ok, left = self.authobject._HandlePacket()
        if not process:
            logger.warning(left, ())
            logger.debug("Auth object : %s" , self.authobject)
            #self.cur.close()
            if ok:
                return self.authobject, self.replypacket
            else:
                return self.auth_NA(self.authobject)
 
 
        process, ok, left = self.authobject._ProcessPacket()
        if not process:
            logger.warning(left, ())
            logger.debug("Auth object : %s" , self.authobject)
            if ok:
                return self.authobject, self.replypacket
            else:
                return self.auth_NA(self.authobject)
 
        check_auth, left = self.authobject.check_auth()
        logger.debug("Auth object : %s" , self.authobject)
        if not check_auth:
            logger.warning(left, ())
            return self.auth_NA(self.authobject) 

        if acc.status != 1:
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_ACCOUNT_DISABLED", service=self.access_type, cause=u'Аккаунт отключен', datetime=self.datetime)
            return self.auth_NA(self.authobject)  
        
        #print common_vpn,access_type,self.access_type
        if (acc.access_type is None) or (acc.access_type != self.access_type):
            logger.warning("Unallowed Access Type for user %s. Access type - %s; packet access type - %s", (user_name, acc.access_type, self.access_type))
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_WRONG_ACCESS_TYPE", service=self.access_type, cause=u'Способ доступа %s не совпадает с разрешённым в параметрах тарифного плана %s.' % (self.access_type, acc.access_type), datetime=self.datetime)
            return self.auth_NA(self.authobject)

        acstatus = (((subacc.allow_vpn_with_null and acc.ballance >=0) or (subacc.allow_vpn_with_minus and acc.ballance<=0) or acc.ballance>0)\
                    and \
                    (subacc.allow_vpn_with_block or (not subacc.allow_vpn_with_block and not acc.balance_blocked==True and not acc.disabled_by_limit==True)))
        #acstatus = True
        if not acstatus:
            logger.warning("Unallowed account status for user %s: account_status is false(allow_vpn_null=%s, ballance=%s, allow_vpn_with_minus=%s, allow_vpn_block=%s, ballance_blocked=%s, disabled_by_limit=%s, account_status=%s)", (subacc.username, subacc.allow_vpn_with_null,acc.ballance, subacc.allow_vpn_with_minus, subacc.allow_vpn_with_block, acc.balance_blocked, acc.disabled_by_limit, acc.status))
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_VPN_BALLANCE_ERROR", service=self.access_type, cause=u'Баланс %s, блокировка по лимитам %s, блокировка по недостатку баланса в начале р.п. %s' % (acc.ballance, acc.disabled_by_limit, acc.balance_blocked), datetime=self.datetime)
            return self.auth_NA(self.authobject)     

     

        #username, password, nas_id, ipaddress, tarif_id, access_type, status, balance_blocked, ballance, disabled_by_limit, speed, tarif_status = row

        allow_dial = True #self.caches.period_cache.in_period.get(acc.tarif_id, False)

        logger.info("Authorization user:%s allowed_time:%s User Status:%s Balance:%s Disabled by limit:%s Balance blocked:%s Tarif Active:%s", ( self.packetobject['User-Name'][0], allow_dial, acc.status, acc.ballance, acc.disabled_by_limit, acc.balance_blocked, acc.tariff_active))
        if allow_dial and acc.tariff_active:
            self.authobject.set_code(2)
            self.replypacket.username = '' #Нельзя юникод
            self.replypacket.password = '' #Нельзя юникод
            if subacc.vpn_ip_address not in ['', '0.0.0.0', '0.0.0.0/0']:
                self.replypacket.AddAttribute('Framed-IP-Address', subacc.vpn_ip_address)
            else:
                self.replypacket.AddAttribute('Framed-IP-Address', subacc.ipn_ip_address)
            self.replypacket.AddAttribute('Acct-Interim-Interval', nas.acct_interim_interval)
            #self.create_speed(nas, subacc.id, acc.tarif_id, acc.account_id, speed=subacc.vpn_speed)
            #self.replypacket.AddAttribute('Class', str("%s,0,%s,%s" % (subacc.id,nas_id,str(self.session_speed))))
            
            self.create_speed(nas, subacc.id, acc.tarif_id, acc.id, speed=subacc.vpn_speed)
            #if self.session_speed:
            self.replypacket.AddAttribute('Class', str("%s,0,%s,%s" % (subacc.id,nas_id,str(self.session_speed))))


            self.add_values(acc.tarif_id, nas.id, acstatus)
            if vars.SQLLOG_SUCCESS:
                sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_OK", service=self.access_type, cause=u'Авторизация прошла успешно.', datetime=self.datetime)
            self.reply()
        else:
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_BAD_TIME", service=self.access_type, cause=u'Тариф неактивен(%s) или запрещённое время %s' % (acc.tariff_active==False, allow_dial==False), datetime=self.datetime)
            return self.auth_NA(self.authobject)
             
#HotSpot_class
#auth_class
class HandleHotSpotAuth(HandleSAuth):
    __slots__ = () + ('access_type', 'secret', 'speed','nas_id', 'nas_type', 'fMem', 'cursor', 'transport', 'addrport')
    def __init__(self,  packetobject, access_type, dbCur, transport, addrport):
        #self.nasip = str(packetobject['NAS-IP-Address'][0])
        self.packetobject = packetobject
        self.access_type=access_type
        self.secret = ''
        self.cursor = dbCur
        self.transport = transport
        self.addrport = addrport

        #logger.debugfun('%s', show_packet, (packetobject,))



        
    def handle(self):
        global sqlloggerthread
        self.datetime = datetime.datetime.now()
        nasses = self.cache.get_nas_by_ip(self.nasip) 
        if not nasses:
            logger.warning("Requested NAS IP (%s) not found in nasses %s", (self.nasip, str(nasses),))
            sqlloggerthread.add_message(type="AUTH_NAS_NOT_FOUND", service=self.access_type, cause=u'Сервер доступа с IP %s не найден ' % self.nasip, datetime=self.datetime) 
            return '',None
        #if 0: assert isinstance(nas, NasData)
        nas = nasses[0]
        #self.nas_id=str(row[0])
        self.nas_type = nas.type
        #self.secret = str(row[1])
        self.replypacket=packet.Packet(secret=str(nas.secret),dict=vars.DICT)

        user_name = str(self.packetobject['User-Name'][0])
        mac=str(self.packetobject['User-Name'][0]).lower() if str(self.packetobject['User-Name'][0]).lower().count(':')==5 else str(self.packetobject['Calling-Station-Id'][0]).lower() 
        ip=str(self.packetobject['Mikrotik-Host-IP'][0])
        self.cursor.execute("SELECT pin FROM billservice_card WHERE activated is NULL and salecard_id IS NOT NULL AND login = %s AND now() BETWEEN start_date AND end_date;", (user_name,))
        pin = self.cursor.fetchone()
        acc=None
        if pin:
            logger.info("Activating account username %s pin %s ip %s mac %s", (user_name, pin[0], ip,mac))
            self.cursor.execute("""SELECT * FROM card_activate_fn(%s, %s, %s::inet, %s::text) AS 
                             A(account_id int, subaccount_id int, "password" text, nas_id int, tarif_id int, status int, 
                             balance_blocked boolean, ballance numeric, disabled_by_limit boolean, tariff_active boolean,ipv4_vpn_pool_id int, tarif_vpn_ippool_id int,vpn_ip_address inet,ipn_ip_address inet,ipn_mac_address text,access_type text)
                            """, (user_name, pin[0], ip,mac))
    
            acct_card = self.cursor.fetchone()
            self.cursor.connection.commit()
            #self.cursor.close()
    
            acc = acct_card
            
            if acct_card is None:
                logger.warning("Card with login %s was not found", user_name)
                #sqlloggerthread.add_message(nas=nas.id, type="AUTH_BAD_USER", service=self.access_type, cause=u'Пользователь HotSpot с логином %s не найден или не может быть активирован.' % (user_name,), datetime=self.datetime)
                #return self.auth_NA(authobject)
            
            acct_card = CardActivateData(*acct_card)
            acc = acct_card            
        
        ["HotSpot", 'HotSpotIp+Mac', 'HotSpotIp+Password','HotSpotMac','HotSpotMac+Password']
        """
        HotSpot - оставляем логику по умолчанию
        HotSpotIp+Mac - в субаккаунт добавляем только IPN IP и ipn_mac
        HotSpotIp+Password - в субаккаунт добавляем IPN IP и password
        HotSpotMac - в субаккаунт
        """
        self.authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nas.secret), access_type=self.access_type)
        subacc = self.cache.get_subaccount_by_username(user_name)
        logger.info("Subacc %s for username %s acc %s", (subacc, user_name, acc))
        if not acc and subacc:
            acc=self.cache.get_account_by_id(subacc.account_id)
            logger.info("Subacc %s access type=%s for username %s", (subacc, acc.access_type, user_name, ))
            if not acc.access_type=='HotSpot':
                acc=None
        if not acc and mac:
            subacc = self.cache.get_subaccount_by_mac(mac)
            if subacc:
                acc=self.cache.get_account_by_id(subacc.account_id)
                if acc.access_type not in ['HotSpotMac','HotSpotIp+Mac']:
                    acc=None
                    
                if acc.access_type=='HotSpotIp+Mac' and subacc.ipn_ip_address!=ip:
                    acc=None
                logger.info("Subacc %s access type=%s for username %s", (subacc, acc.access_type if acc else 'acc not found', user_name, ))

        if not acc and ip:
            subacc = self.cache.get_subaccount_by_ipn_ip(ip)
            if subacc:
                acc=self.cache.get_account_by_id(subacc.account_id)
                if acc.access_type!='HotSpotIp+Password':
                    acc=None
                    subacc=None
                logger.info("Subacc %s access type=%s for username %s", (subacc, acc.access_type, user_name, ))
                    
        if not acc:
            """
            Если не нашли совпадений ранее - пытаемся найти карту, чтобы активировать нового абонента
            """
           
            sqlloggerthread.add_message(nas=nas.id, type="CARD_USER_NOT_FOUND", service=self.access_type, cause=u'Карта/пользователь с логином %s ip %s и mac %s не найдены ' % (user_name, ip, mac), datetime=self.datetime)
            self.cursor.close()
            return self.auth_NA(self.authobject)

        else:
            if subacc:
                pin = subacc.password
            else:
                pin = acc.password

        
        if str(acc.access_type) in ['HotSpot','HotSpotIp+Password', 'HotSpotMac+Password']:
            self.authobject.plainusername = str(user_name)
            if subacc:
                self.authobject.plainpassword = str(subacc.password)
            else:
                self.authobject.plainpassword = str(pin)
    
            check_auth, left = self.authobject.check_auth()
            if not check_auth:
                logger.warning(left, ())
                sqlloggerthread.add_message(nas=nas.id, type="AUTH_BAD_PASSWORD", service=self.access_type, cause=u'Ошибка авторизации. Необходимо проверить указанный пароль.', datetime=self.datetime)
                self.cursor.close()
                return self.auth_NA(self.authobject)   
            

        if subacc:
            acstatus = acc.status==1 and (((subacc.allow_vpn_with_null and acc.ballance >=0) or (subacc.allow_vpn_with_minus and acc.ballance<=0) or acc.ballance>0)\
                        and \
                        (subacc.allow_vpn_with_block or (not subacc.allow_vpn_with_block and not acc.balance_blocked and not acc.disabled_by_limit)))
        else:
            acstatus = acc.ballance >0 and not acc.balance_blocked and not acc.disabled_by_limit and acc.status==1

        if subacc:
            subacc_id=subacc.id
        else:
            subacc_id = acc.subaccount_id
            subacc=acc
            
        if not acstatus:
            if subacc:
                logger.warning("Unallowed account status for user %s: account_status is false(allow_vpn_null=%s, ballance=%s, allow_vpn_with_minus=%s, allow_vpn_block=%s, ballance_blocked=%s, disabled_by_limit=%s, account_status=%s)", (user_name,subacc.allow_vpn_with_null,acc.ballance, subacc.allow_vpn_with_minus, subacc.allow_vpn_with_block, acc.balance_blocked, acc.disabled_by_limit, acc.status))
            else:
                logger.warning("Unallowed account status for user %s: account_status is false(allow_vpn_null=%s, ballance=%s, ballance_blocked=%s, disabled_by_limit=%s, account_status=%s)", (user_name,subacc.allow_vpn_with_null,acc.ballance, acc.balance_blocked, acc.disabled_by_limit, acc.status))
            sqlloggerthread.add_message(nas=acc.nas_id, subaccount=subacc_id, account=acc.id, type="AUTH_HOTSPOT_BALLANCE_ERROR", service=self.access_type, cause=u'Баланс %s, блокировка по лимитам %s, блокировка по недостатку баланса в начале р.п. %s' % (acc.ballance, acc.disabled_by_limit, acc.balance_blocked), datetime=self.datetime)
            return self.auth_NA(self.authobject)     
        
        allow_dial = True #self.caches.period_cache.in_period.get(acc.tarif_id, False)

        logger.info("Authorization user:%s allowed_time:%s User Status:%s Balance:%s Disabled by limit:%s Balance blocked:%s Tarif Active:%s", ( self.packetobject['User-Name'][0], allow_dial, acc.status, acc.ballance, acc.disabled_by_limit, acc.balance_blocked,acc.tariff_active))
        vpn_ip_address = None
        ipinuse_id=''
        pool_id=None
        if ((subacc and subacc.ipv4_vpn_pool_id) or acc.vpn_ippool_id) and acc.vpn_ip_address in ('0.0.0.0','0.0.0.0/32',''):
            with vars.cursor_lock:
                try:
                    #self.create_cursor()
                    pool_id=acc.ipv4_vpn_pool_id if acc.ipv4_vpn_pool_id else acc.vpn_ippool_id
                    self.cursor.execute('SELECT get_free_ip_from_pool(%s, %s);', (pool_id, nas.acct_interim_interval))
                    vpn_ip_address = self.cursor.fetchone()[0]
                    if not vpn_ip_address:
                        pool_id, vpn_ip_address = self.find_free_ip(pool_id, nas.acct_interim_interval)

                    #self.cursor.connection.commit()
                    if not vpn_ip_address:
                        logger.error("Couldn't find free ipv4 address for user %s id %s in pool: %s", (str(user_name), subacc_id, pool_id))
                        sqlloggerthread.add_message(account=acc.id, subaccount=subacc_id, type="AUTH_EMPTY_FREE_IPS", service=self.access_type, cause=u'В указанном пуле нет свободных IP адресов', datetime=self.datetime)
                        #vars.cursor_lock.release()
                        return self.auth_NA(self.authobject)
                   

                    #vars.cursor.connection.commit()   
                    #vars.cursor_lock.release()
                    #self.cursor.connection.commit()
                            
                except Exception, ex:
                    #vars.cursor_lock.release()
                    logger.error("Couldn't get an address for user %s | id %s from pool: %s :: %s", (str(user_name), subacc_id, pool_id, repr(ex)))
                    sqlloggerthread.add_message(account=acc.id, subaccount=subacc.id, type="AUTH_IP_POOL_ERROR", service=self.access_type, cause=u'Ошибка выдачи свободного IP адреса', datetime=self.datetime)
                    return self.auth_NA(self.authobject) 

        else:
            if subacc:
                vpn_ip_address = subacc.vpn_ip_address
            else:
                vpn_ip_address=acc.vpn_ip_address
                
        if allow_dial and acc.tariff_active:
            self.authobject.set_code(packet.AccessAccept)
            #self.replypacket.AddAttribute('Framed-IP-Address', '192.168.22.32')


            if vpn_ip_address not in [None, '', '0.0.0.0', '0.0.0.0/0']:
                self.replypacket.AddAttribute('Framed-IP-Address', vpn_ip_address)
            elif subacc and subacc.vpn_ip_address not in [None, '', '0.0.0.0', '0.0.0.0/0']:
                self.replypacket.AddAttribute('Framed-IP-Address', subacc.vpn_ip_address)  
                              
            self.replypacket.AddAttribute('Acct-Interim-Interval', nas.acct_interim_interval)
            self.create_speed(nas, None, acc.tarif_id, acc.id, speed='')
            self.replypacket.AddAttribute('Class', str("%s,%s,%s,%s" % (subacc_id,ipinuse_id,nas.id, str(self.session_speed))))
            self.add_values(acc.tarif_id, nas.id, acstatus)
            if vars.SQLLOG_SUCCESS:
                sqlloggerthread.add_message(nas=nas.id, subaccount=subacc_id, account=acc.id,  type="AUTH_OK", service=self.access_type, cause=u'Авторизация прошла успешно.', datetime=self.datetime)            
            self.reply()
            if ipinuse_id:
                self.cursor.execute("INSERT INTO billservice_ipinuse(pool_id,ip,datetime, dynamic) VALUES(%s,%s,now(),True) RETURNING id;",(pool_id, vpn_ip_address))
                ipinuse_id=self.cursor.fetchone()[0]
                
        else:
            sqlloggerthread.add_message(nas=nas.id, subaccount=subacc_id, account=acc.id, type="AUTH_BAD_TIME", service=self.access_type, cause=u'Тариф неактивен(%s) или запрещённое время %s' % (acc.tariff_active==False, allow_dial==False), datetime=self.datetime)
            return self.auth_NA(self.authobject)


#auth_class
class HandleSDHCP(HandleSAuth):
    __slots__ = () + ('secret', 'nas_id', 'nas_type', 'transport', 'addrport')
    def __init__(self,  packetobject, transport, addrport):
        super(HandleSAuth, self).__init__()

        self.packetobject = packetobject
        self.secret = ""
        self.access_type=get_accesstype(packetobject)
        self.replypacket = packetobject
        self.transport = transport
        self.addrport = addrport
        #logger.debugfun('%s', show_packet, (packetobject,))


    def auth_NA(self, authobject):
        """
        Deny access
        """
        if vars.DHCP_FRAMED_GUEST_POOL:
            self.replypacket.AddAttribute('Framed-Pool', vars.DHCP_FRAMED_GUEST_POOL)
            self.replypacket.AddAttribute('Session-Timeout',   vars.DHCP_GUEST_SESSION_TIMEOUT)
            self.authobject.code = packet.AccessAccept
        else:
            self.replypacket.username=None
            self.replypacket.password=None
            # Access denided
            self.authobject.code = packet.AccessReject


        returndata, replypacket = self.authobject.ReturnPacket(self.replypacket) 
        logger.debug("REPLY packet: %s", repr(replypacket))               

        self.transport.write(returndata, self.addrport)

    def handle(self):
        global sqlloggerthread
        self.datetime = datetime.datetime.now()
        nasses = self.cache.get_nas_by_ip(self.nasip)
        if not nasses: 
            sqlloggerthread.add_message(type="AUTH_NAS_NOT_FOUND", service=self.access_type, cause=u'Сервер доступа c IP %s в системе не найден.' % (self.nasip,), datetime=self.datetime)
            return '',None
        #if 0: assert isinstance(nas, NasData)
        mac = self.packetobject['User-Name'][0].lower()
        #acc = self.caches.account_cache.by_ipn_mac.get(mac)
 
        self.authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nasses[0].secret), access_type='DHCP')
        subacc = self.cache.get_subaccount_by_mac(mac)
        subaccount_switch=None
        nas=nasses[0]
        self.replypacket=packet.Packet(secret=nas.secret,dict=vars.DICT)
        nas_id=nas.id
        acc=None
        if subacc:
            subaccount_switch = self.cache.get_switch_by_id(subacc.switch_id)

        if self.packetobject.get("Agent-Remote-ID") and self.packetobject.get("Agent-Circuit-ID"):
            if subaccount_switch:
                identify, vlan, module, port=parse(subaccount_switch.option82_template, self.packetobject.get("Agent-Remote-ID",[''])[0],self.packetobject.get("Agent-Circuit-ID",[''])[0])
                
            else:
                identify, vlan, module, port=parse('dlink-32xx', self.packetobject.get("Agent-Remote-ID",[''])[0],self.packetobject.get("Agent-Circuit-ID",[''])[0])
            switch = self.cache.get_switch_by_identify(identify)# реальный свитч, с которого пришёл запрос
            logger.warning("DHCP option82 remote_id, port %s %s", (identify, port,))
            if not switch:
                sqlloggerthread.add_message(nas=nas_id, type="DHCP_CANT_FIND_SWITH_BY_REMOTE_ID", service=self.access_type, cause=u'Невозможно найти коммутатор с remote-id %s ' % (identify, ), datetime=self.datetime)
                return self.auth_NA(self.authobject)  


            if not subacc:
                """
                если субаккаунт не найден по маку первоначально, ищем субаккаунт по id свитча и порту
                """
                subacc=self.cache.get_by_switch_port(switch.id, port)    
                if subacc:
                    subaccount_switch= self.cache.get_switch_by_id(subacc.switch_id)
                else:
                    sqlloggerthread.add_message(nas=nas_id,  type="DHCP_PORT_SWITCH_WRONG", service=self.access_type, cause=u'Субаккаунт с remote-id %s и портом %s не найден' % (identify, port), datetime=self.datetime)
                    return self.auth_NA(self.authobject)  
            acc = self.cache.get_account_by_id(subacc.account_id)
            if not acc:
                logger.warning("Account not found for DHCP request with mac address %s", (mac, ))
                #Не учитывается сервер доступа
                sqlloggerthread.add_message(type="AUTH_ACC_NOT_FOUND", service=self.access_type, cause=u'Аккаунт для субаккаунта с mac %s в системе не найден.' % (mac, ), datetime=self.datetime)
                return self.auth_NA(self.authobject)
            if subaccount_switch.option82_auth_type==0 and (subaccount_switch.remote_id!=switch.remote_id or subacc.switch_port!=port):
                sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="DHCP_PORT_WRONG", service=self.access_type, cause=u'Remote-id или порт не совпадают %s %s' % (identify, port), datetime=self.datetime)
                return self.auth_NA(self.authobject)  
            elif subaccount_switch.option82_auth_type==1 and (subaccount_switch.remote_id!=switch.remote_id or subacc.switch_port!=port):
                sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="DHCP_PORT_WRONG", service=self.access_type, cause=u'Remote-id или порт не совпадают %s %s' % (identify, port), datetime=self.datetime)
                return self.auth_NA(self.authobject)  
            elif subaccount_switch.option82_auth_type==2 and subaccount_switch.id!=switch.id:
                sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="DHCP_SWITCH_WRONG", service=self.access_type, cause=u'Свитч c remote-id=%s не совпадает с указанным в настройках субаккаунта' % (identify, port), datetime=self.datetime)
                return self.auth_NA(self.authobject)  
                    
          
        if not subacc:
            logger.warning("Subaccount not found for DHCP request with mac address %s", (mac, ))
            #Не учитывается сервер доступа
            sqlloggerthread.add_message(type="AUTH_SUBACC_NOT_FOUND", service=self.access_type, cause=u'Субаккаунт с ipn_mac %s в системе не найден.' % (mac, ), datetime=self.datetime)
            return self.auth_NA(self.authobject)
        
        if not subacc.allow_dhcp and self.access_type=='DHCP':
            logger.warning("Subaccount with mac %s have no rights for DHCP ", (mac, ))
            sqlloggerthread.add_message(type="AUTH_DHCP_DONT_ALLOW", service=self.access_type, cause=u'Субаккаунту с mac %s запрещена выдача IP по DHCP.' % (mac,), datetime=self.datetime)
            return self.auth_NA(self.authobject)            
        if not acc:
            acc = self.cache.get_account_by_id(subacc.account_id)
            
        if not acc:
            logger.warning("Account not found for %s request with mac address %s", (self.access_type, mac, ))
            #Не учитывается сервер доступа
            sqlloggerthread.add_message(type="AUTH_ACC_NOT_FOUND", service=self.access_type, cause=u'Аккаунт для субаккаунта с mac %s в системе не найден.' % (mac, ), datetime=self.datetime)
            return self.auth_NA(self.authobject)
        
        nas_id = subacc.nas_id

        
        nas = self.cache.get_nas_by_id(nas_id) 
        if (nas and nas not in nasses) and vars.IGNORE_NAS_FOR_DHCP is False:
            """
            Если NAS пользователя найден  и нас не в списке доступных и запрещено игнорировать сервера доступа 
            """
            logger.warning("Account nas(%s) is not in sended nasses and IGNORE_NAS_FOR_%s is False %s", (repr(nas), nasses,self.access_type))
            sqlloggerthread.add_message(account=acc.id, subaccount=subacc.id, type="AUTH_BAD_NAS", service=self.access_type, cause=u'Субаккаунт привязан к конкретному серверу доступа, но запрос на авторизацию поступил с IP %s.' % (self.nasip), datetime=self.datetime)
            return self.auth_NA(self.authobject)
        elif not nas_id:
            """
            Иначе, если указан любой NAS - берём первый из списка совпавших по IP
            """
            nas = nasses[0]
        nas_id = nas.id
        self.replypacket=packet.Packet(secret=nas.secret,dict=vars.DICT)
 
        self.authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nas.secret), access_type='DHCP')


        #print dir(acc)
        acstatus = (((subacc.allow_dhcp_with_null and acc.ballance >=0) or (subacc.allow_dhcp_with_minus and acc.ballance<=0) or acc.ballance>0)  and \
                    (subacc.allow_dhcp_with_block or (not subacc.allow_dhcp_with_block and not acc.balance_blocked==True and not acc.disabled_by_limit==True)))
        #acstatus = True
        
        if acc.status != 1:
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_ACCOUNT_DISABLED", service=self.access_type, cause=u'Аккаунт отключен', datetime=self.datetime)
            return self.auth_NA(self.authobject)   
        
        if not acstatus:
            logger.warning("Unallowed account status for user %s: account_status is false(allow_vpn_null=%s, ballance=%s, allow_vpn_with_minus=%s, allow_vpn_block=%s, ballance_blocked=%s, disabled_by_limit=%s, account_status=%s)", (mac,subacc.allow_vpn_with_null,acc.ballance, subacc.allow_vpn_with_minus, subacc.allow_vpn_with_block, acc.balance_blocked, acc.disabled_by_limit, acc.status))
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="AUTH_%s_BALLANCE_ERROR" % self.access_type, service=self.access_type, cause=u'Баланс %s, блокировка по лимитам %s, блокировка по недостатку баланса в начале р.п. %s' % (acc.ballance, acc.disabled_by_limit, acc.balance_blocked), datetime=self.datetime)
            return self.auth_NA(self.authobject)      

        allow_dial = True
        if acc.access_type in ['DHCP', 'Wireless']:
            allow_dial = True #self.caches.period_cache.in_period.get(acc.tarif_id, False)
        if acstatus and allow_dial and acc.tariff_active:
            self.authobject.set_code(2)
            self.replypacket.AddAttribute('Framed-IP-Address', subacc.ipn_ip_address)
            #self.replypacket.AddAttribute('Framed-IP-Netmask', "255.255.255.0")
            self.replypacket.AddAttribute('Session-Timeout',   vars.SESSION_TIMEOUT)
            if acc.access_type in ['DHCP', 'Wireless']:
                self.add_values(acc.tarif_id, nas.id, acstatus)
                self.create_speed(nas, subacc.id, acc.tarif_id, acc.id, speed=subacc.ipn_speed)
            if vars.SQLLOG_SUCCESS:
                sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="%s_AUTH_OK" % self.access_type, service=self.access_type, cause=u'Авторизация прошла успешно.', datetime=self.datetime)
            self.reply()
        else:
            sqlloggerthread.add_message(nas=nas_id, account=acc.id, subaccount=subacc.id, type="%s_AUTH_BAD_TIME" % self.access_type, service=self.access_type, cause=u'Тариф пользователя неактивен(%s) или время доступа выходит за рамки разрешённого %s' % (acc.tariff_active==False, allow_dial==False), datetime=self.datetime)
            return self.auth_NA(self.authobject)




def SIGTERM_handler(signum, frame):
    logger.lprint("SIGTERM recieved")
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
    global  suicideCondition, vars
    #asyncore.close_all()
    print "\nPlease, wait...."


    suicideCondition[SQLLoggerThread.__class__.__name__] = True
    
    logger.lprint("About to stop gracefully.")
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    time.sleep(5)
    #pool.close()
    rempid(vars.piddir, vars.name)
    print "RAD AUTH: exiting"
    logger.lprint("Stopping gracefully.")
    
    reactor.callFromThread(reactor.disconnectAll)
    reactor.callFromThread(reactor.stop)
    #reactor.stop()

def ungraceful_save():
    global suicideCondition
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    rempid(vars.piddir, vars.name)
    asyncore.close_all()
    print "RAD AUTH: exiting"
    logger.lprint("RAD AUTH exiting.")
    for th in threads:
        th.join()


    sys.exit()

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
    
def main():
    global threads, curCachesDate, suicideCondition, server_acct, sqlloggerthread, SQLLoggerThread
    threads = []

    for i in xrange(vars.AUTH_THREAD_NUM):
        newAcct = AuthHandler()
        newAcct.setName('AUTH:#%i: AuthHandler' % i)
        threads.append(newAcct)
            
   

    sqlloggerthread = SQLLoggerThread(suicideCondition)
    if vars.ENABLE_SQLLOG:
        
        sqlloggerthread.setName('SQLLOG:THR:#%i: SqlLogThread' % 1)
        threads.append(sqlloggerthread)

    


    for th in threads:
        suicideCondition[th.__class__.__name__] = False
        th.start()        
        logger.info("Thread %s started", th.getName())
        time.sleep(0.1)

    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')

    try:
        signal.signal(signal.SIGINT, SIGTERM_handler)
    except: logger.lprint('NO SIGINT!')
    
    try:
        signal.signal(signal.SIGHUP, SIGHUP_handler)
    except: logger.lprint('NO SIGHUP!')

    try:
        signal.signal(signal.SIGUSR1, SIGUSR1_handler)
    except: logger.lprint('NO SIGUSR1!')

    print "ebs: rad_auth: started"
    savepid(vars.piddir, vars.name)
    reactor.listenUDP(1812, Reception_UDP())
    reactor.run(installSignalHandlers=True)

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()

    config.read("ebs_config.ini")



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
        auth_queue = Queue.Queue()
        auth_output_queue = Queue.Queue()
        sessions_speed={}#account:(speed,datetime)
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME)

        if '-p' in sys.argv and len(sys.argv)==3:
            port = sys.argv[2]
        elif '-p' in sys.argv:
            print "unknown port"
            sys.exit()
        else:
            port = vars.AUTH_PORT
            
        

        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename='log/rad_auth_log')
        utilites.log_adapt = logger.log_adapt
        saver.log_adapt    = logger.log_adapt
        logger.lprint('Radius start')
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)
        for eap_handler in get_eap_handlers():
            handler_dict = {}
            handler_lock = Lock()
            queues.eap_auth_chs[eap_handler]   = handler_dict
            queues.eap_auth_locks[eap_handler] = handler_lock
            queues.challenges[eap_handler] = {'get': handler_dict.pop, 'set': handler_dict.__setitem__, 'lock': handler_lock}
            
        auth.set_identity_check(vars.EAP_ID_TYPE)
        auth.set_eap_access_types(vars.EAP_ACCESS_TYPES)
        #write profiling info?
        flags.writeProf = logger.writeInfoP()         

        suicideCondition = {}
        fMem = pfMemoize()
    

        #-------------------
        print "ebs: rad_auth: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in rad, exiting: ', repr(ex)
        logger.error('Exception in rad_auth, exiting: %s \n %s', (repr(ex), traceback.format_exc()))        
