#-*-coding: utf-8 -*-

import gc
import os
import sys
import time
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
import saver_ as saver, utilites

from auth import Auth
from time import clock
from copy import copy, deepcopy
from daemonize import daemonize
from threading import Thread, Lock
from DBUtils.PooledDB import PooledDB
from collections import deque, defaultdict

from saver_ import allowedUsersChecker, setAllowedUsers
from utilites import in_period,in_period_info, create_speed_string, get_corrected_speed
from db import get_account_data_by_username_dhcp,get_default_speed_parameters, get_speed_parameters, get_nas_by_ip, get_account_data_by_username, time_periods_by_tarif_id
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

from classes.rad_cache import *
from classes.cacheutils import CacheMaster
from classes.flags import RadFlags
from classes.vars import RadVars, RadQueues
from classes.rad_class.CardActivateData import CardActivateData

try:    import mx.DateTime
except: print 'cannot import mx'

w32Import = False
try:    import win32api,win32process,win32con
except: pass
else:   w32Import = True

#gigaword = 4294967296
#account_timeaccess_cache={}
#account_timeaccess_cache_count=0

        
def show_packet(packetobject):
    b = ''
    #b = ''.join((str(packetobject._DecodeKey(key))+str(packetobject[packetobject._DecodeKey(key)][0])+"\n" for key,item in packetobject.items()))
    for key,value in packetobject.items():
        b+=str(packetobject._DecodeKey(key))+str(packetobject[packetobject._DecodeKey(key)][0])+"\n"
    return b
        
class AsyncUDPServer(asyncore.dispatcher):
    ac_out_buffer_size = 8096*10
    ac_in_buffer_size = 8096*10
    
    def __init__(self, host, port):
        self.outbuf = deque()

        asyncore.dispatcher.__init__(self)

        self.host = host
        self.port = port
        self.dbconn = None
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.socket.settimeout(5)
        #self.socket.setblocking(True)
        self.bind( (host, port) )
        self.set_reuse_addr()

        
    def handle_read_event (self):
        try:
            data, addr = self.socket.recvfrom(4096)
        except Exception, ex:            
            logger.error('Socket read error: %s \n %s', (repr(ex),traceback.format_exc()))
            return
        self.handle_readfrom(data, addr)

    def handle_readfrom(self,data, address):
        pass
    
    def writable (self):
        return len(self.outbuf)

    def sendto (self, data, addr):
        self.outbuf.append((data, addr))
        self.initiate_send()
    
    
    def initiate_send(self):
        b = self.outbuf
        #self.send()

        while len(b):
            data, addr = b.popleft()
            try:
                result = self.socket.sendto (data, addr)
                if result != len(data):
                    logger.warning('Sent packet truncated to %s bytes', result)
            except socket.error, why:
                if why[0] == EWOULDBLOCK:
                    return
                else:
                    raise socket.error, why

                
    def handle_error (self, *info):        
        logger.error('uncaptured python exception, closing channel %s \n %s', (repr(self), traceback.format_exc()))
        self.close()
    
    def handle_close(self):
        self.close()
        
def authNA(packet):
    return packet.ReplyPacket()

def get_accesstype(packetobject):
    """
    Returns access type name by which a user connects to the NAS
    """

    try:
        nas_port_type = packetobject['NAS-Port-Type'][0]
        if nas_port_type == 'Virtual' and packetobject.get('Service-Type', [''])[0]=='Framed-User':
            return 'PPTP'
        elif nas_port_type == 'Ethernet' and packetobject.get('Service-Type', [''])[0]=='Framed-User': 
            return 'PPPOE'
        elif packetobject.has_key('Mikrotik-Host-IP'):
            return 'HotSpot'
        elif nas_port_type == 'Ethernet' and not packetobject.has_key('Service-Type'):
            return 'DHCP'
        else:
            logger.warning('Nas access type warning: unknown type: %s', nas_port_type)
    except Exception, ex:
        logger.error('Packet access type error: %s \n %s', (repr(ex), show_packet(packetobject)))
    return
    
class AsyncAuthServ(AsyncUDPServer):
    def __init__(self, host, port, dbpool):
        self.outbuf = []
        AsyncUDPServer.__init__(self, host, port)
        self.dbconn = dbpool
        self.dbconn._con._con.set_isolation_level(0)
        self.dbconn._con._con.set_client_encoding('UTF8')
        self.dateCache = datetime.datetime(2000, 1, 1)       

    def handle_readfrom(self, data, addrport):
        global cacheMaster, queues, vars, flags, fMem
        
        
        
        try:     
            #if caches were renewed, renew local copies
            if cacheMaster.date <= self.dateCache:
                time.sleep(10); continue
            else:
                cacheMaster.lock.acquire()
                try:
                    caches = cacheMaster.cache
                    dateAT = deepcopy(cacheMaster.date)
                except Exception, ex:
                    logger.error("%s: cache exception: %s", (self.getName(), repr(ex)))
                finally:
                    cacheMaster.lock.release()
    
            if 0: assert isinstance(caches, RadCaches)
                        
            t = clock()
            returndata = ''
            #data=self.request[0] # or recv(bufsize, flags)
            assert len(data)<=4096
            packetobject=packet.Packet(dict=vars.dict,packet=data)
            nas_ip = str(packetobject['NAS-IP-Address'][0])
            access_type = get_accesstype(packetobject)
            
            if access_type in ['PPTP', 'PPPOE']:
                logger.info("Auth Type %s", access_type)
    
                coreconnect = HandleSAuth(packetobject=packetobject, access_type=access_type)
                coreconnect.nasip = nas_ip
                coreconnect.fMem = fMem; coreconnect.caches = caches
                authobject, packetfromcore=coreconnect.handle()
                
                if packetfromcore is None: logger.info("Unknown NAS %s", str(nas_ip)); return
    
                logger.info("Password check: %s", authobject.code)
                returndata=authobject.ReturnPacket(packetfromcore) 
    
            elif access_type in ['HotSpot']:
                logger.info("Auth Type %s", access_type)
                coreconnect = HandleHotSpotAuth(packetobject=packetobject, access_type=access_type, dbCur=self.dbconn.cursor())
                coreconnect.nasip = nas_ip
                coreconnect.fMem = fMem; coreconnect.caches = caches
                authobject, packetfromcore=coreconnect.handle()
                
                if packetfromcore is None: logger.info("Unknown NAS %s", str(nas_ip)); return
    
                logger.info("Password check: %s", authobject.code)
                returndata=authobject.ReturnPacket(packetfromcore) 
                
            elif access_type in ['DHCP'] :
                coreconnect = HandleSDHCP(packetobject=packetobject)
                coreconnect.nasip = nas_ip; coreconnect.caches = caches
                authobject, packetfromcore = coreconnect.handle()
                if packetfromcore is None: logger.info("Unknown NAS %s", str(nas_ip)); return
                returndata=authobject.ReturnPacket(packetfromcore)
            else:
                #-----
                coreconnect = HandleSNA(packetobject)
                coreconnect.nasip = nas_ip; coreconnect.nasCache = self.cacheNas
                returnpacket = coreconnect.handle()
                if returnpacket is None: return
                returndata=authNA(returnpacket)
                 
            logger.info("AUTH time: %s", (clock()-t))
            if returndata:
                self.sendto(returndata,addrport)
                del returndata
                
            del packetfromcore
            del coreconnect
            logger.info("ACC: %s", (clock()-t))
                
        except Exception, ex:
            logger.error("Auth Server readfrom exception: %s \n %s", (repr(ex), traceback.format_exc()))

class AsyncAcctServ(AsyncUDPServer):
    def __init__(self, host, port, dbconn):
        self.outbuf = []
        AsyncUDPServer.__init__(self, host, port)
        self.dbconn = dbconn
        self.dbconn._con._con.set_isolation_level(0)
        self.dbconn._con._con.set_client_encoding('UTF8')
        self.dateCache = datetime.datetime(2000, 1, 1)


    def handle_readfrom(self, data, addrport):
        global cacheMaster, vars, fMem
        
        try:  
            if cacheMaster.date <= self.dateCache:
                time.sleep(10); continue
            else:
                cacheMaster.lock.acquire()
                try:
                    caches = cacheMaster.cache
                    dateAT = deepcopy(cacheMaster.date)
                except Exception, ex:
                    logger.error("%s: cache exception: %s", (self.getName(), repr(ex)))
                finally:
                    cacheMaster.lock.release()
    
            if 0: assert isinstance(caches, RadCaches)

                        
            t = clock()
            assert len(data)<=4096
            packetobject=packet.AcctPacket(dict=vars.dict,packet=data)
    
            coreconnect = HandleSAcct(packetobject=packetobject, nasip=addrport[0], dbCur=self.dbconn.cursor())
            coreconnect.caches = caches               
            
            packetfromcore = coreconnect.handle()
            
            if packetfromcore is not None: 
                returndat=packetfromcore.ReplyPacket()
                self.socket.sendto(returndat,addrport)
                del returndat
                
            del packetfromcore
            del coreconnect    
            logger.info("ACC: %s", (clock()-t))            
        except Exception, ex:
            logger.error("Acc Server readfrom exception: %s \n %s", (repr(ex), traceback.format_exc()))


class HandleSBase(object):
    __slots__ = ('packetobject', 'cacheDate', 'nasip', 'caches', 'replypacket')

    def auth_NA(self):
        """
        Denides access
        """        
        self.packetobject.username=None
        self.packetobject.password=None
        # Access denided
        self.packetobject.code=3
        return self.packetobject

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
        nas = self.caches.nas_cache.by_ip.get(self.nasip)       
        
        if nas is not None:
            self.packetobject.secret = str(nas.secret)
            return "", self.auth_NA()

        
#auth_class
class HandleSAuth(HandleSBase):
    __slots__ = () + ('access_type', 'secret', 'speed','nas_id', 'nas_type', 'multilink', 'fMem')
    def __init__(self,  packetobject, access_type):
        self.packetobject = packetobject
        self.access_type=access_type
        self.secret = ''        
        logger.debugfun('%s', show_packet, (packetobject,))


    def auth_NA(self, authobject):
        """
        Deny access
        """
        authobject.set_code(3)
        return authobject, self.packetobject
    
    def create_speed(self, tarif_id, account_id, speed=''):
        result_params=speed
        if speed=='':
            defaults = self.caches.defspeed_cache.by_id.get(tarif_id)
            speeds   = self.caches.speed_cache.by_id.get(tarif_id, [])
            defaults = defaults[:6] if defaults else ["0/0","0/0","0/0","0/0","8","0/0"]
            result=[]
            min_delta, minimal_period = -1, []
            now=datetime.datetime.now()
            for speed in speeds:
                #Определяем составляющую с самым котортким периодом из всех, которые папали в текущий временной промежуток

                tnc,tkc,delta,res = fMem.in_period_(speed[6],speed[7],speed[8], now)
                #print "res=",res
                if res==True and (delta<min_delta or min_delta==-1):
                    minimal_period=speed
                    min_delta=delta
            minimal_period = minimal_period[:6] if minimal_period else ["0/0","0/0","0/0","0/0","8","0/0"]

            for k in xrange(0, 6):
                s=minimal_period[k]
                if s=='0/0' or s=='/' or s=='':
                    res=defaults[k]
                else:
                    res=s
                result.append(res)
            

            correction = self.caches.speedlimit_cache.by_id.get(account_id)
            #Проводим корректировку скорости в соответствии с лимитом

            result = get_corrected_speed(result, correction)
            #print "corrected", result
            if result==[]: 
                result = defaults if defaults else ["0/0","0/0","0/0","0/0","8","0/0"]                
            
            result_params=create_speed_string(result)
            self.speed=result_params
        if self.nas_type[:8]==u'mikrotik' and result_params!='':
            self.replypacket.AddAttribute((14988,8),result_params)

    def get_nas_info(self):
        row = get_nas_by_ip(self.cur, self.nasip)
        return row

    def handle(self):
        nas = self.nasCache.get(self.nasip)
        if not nas: return '',None
        if 0: assert isinstance(nas, NasData)
        #self.nas_id=str(row[0])
        self.nas_type = nas.type
        #self.multilink = row[3]
        #self.secret = str(row[1])
        self.replypacket = packet.Packet(secret=str(nas.secret),dict=vars.dict)

        station_id = self.packetobject.get('Calling-Station-Id', [''])[0]
        user_name = str(self.packetobject['User-Name'][0])

        #row = get_account_data_by_username(self.cur, self.packetobject['User-Name'][0], self.access_type, station_id=station_id, multilink = self.multilink, common_vpn = common_vpn)
        acc = self.caches.account_cache.by_username.get(user_name)
        authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nas.secret), access_type=self.access_type)
        
        if acc is None:
            logger.warning("Unknown User %s", user_name)
            return self.auth_NA(authobject)  
        
        if 0: assert isinstance(acc, AccountData)
        authobject.plainusername = str(acc.username)
        authobject.plainpassword = str(acc.password)
        if authobject.check_auth() is  False:
            logger.warning("Bad User/Password %s", user_name)
            return self.auth_NA(authobject)         

        #print common_vpn,access_type,self.access_type
        if (not common_vpn) and ((acc.access_type is None) or (acc.access_type != self.access_type)):
            logger.warning("Unallowed Access Type for user %s: access_type error. access type - %s; packet access type - %s", (user_name, acc.access_type, self.access_type))
            return self.auth_NA(authobject)
        
        acstatus = ((not acc.allow_vpn_null and acc.ballance >0) or acc.allow_vpn_null) \
                    and \
                    (acc.allow_vpn_null or (not acc.allow_vpn_block and not acc.balance_blocked and not acc.disabled_by_limit and acc.account_status))
        
        if not acstatus:
            logger.warning("Unallowed account status for user %s: account_status is false", user_name)
            return self.auth_NA(authobject)      
        
        if nas.multilink is False:
            station_id_status = False
            if len(station_id) == 17:
                """MAC - PPPOE"""
                station_id_status = ((str(acc.ipn_mac_address) == station_id) or (acc.ipn_mac_address == ''))
            else:
                """IP - PPTP"""
                station_id_status = ((str(acc.ipn_ip_address)  == station_id) or (acc.ipn_ip_address  == '0.0.0.0'))
            
            if not station_id_status:
                logger.warning("Unallowed NAS for user %s: station_id status is false, station_id - %s , ipn_ip - %s; ipn_mac - %s ", (user_name, station_id, acc.ipn_ip_address, acc.ipn_mac_address))
                return self.auth_NA(authobject) 
            
        #username, password, nas_id, ipaddress, tarif_id, access_type, status, balance_blocked, ballance, disabled_by_limit, speed, tarif_status = row
        if flags.ignore_nas_for_vpn is False and int(acc.nas_id)!=int(nas.nas_id):
            logger.warning("Unallowed NAS for user %s", user_name)
            return self.auth_NA(authobject) 
        
        allow_dial = self.caches.period_cache.in_period.get(acc.tarif_id, False)

        logger.info("Authorization user:%s allowed_time:%s User Status:%s Balance:%s Disabled by limit:%s Balance blocked:%s Tarif Active:%s", ( self.packetobject['User-Name'][0], allow_dial, acc.account_status, acc.ballance, acc.disabled_by_limit, acc.balance_blocked, acc.tarif_active))
        if self.packetobject['User-Name'][0]==user_name and allow_dial and acc.tarif_active:
            authobject.set_code(2)
            self.replypacket.username = str(user_name) #Нельзя юникод
            self.replypacket.password = str(password) #Нельзя юникод
            self.replypacket.AddAttribute('Service-Type', 2)
            self.replypacket.AddAttribute('Framed-Protocol', 1)
            self.replypacket.AddAttribute('Framed-IP-Address', acc.vpn_ip_address)
            #account_speed_limit_cache
            self.create_speed(acc.tarif_id, acc.account_id, speed=acc.vpn_speed)
            #print "Setting Speed For User" , self.speed
            return authobject, self.replypacket
        else:
            return self.auth_NA(authobject)
        

#HotSpot_class
#auth_class
class HandleHotSpotAuth(HandleSBase):
    __slots__ = () + ('access_type', 'secret', 'speed','nas_id', 'nas_type', 'fMem', 'cur')
    def __init__(self,  packetobject, access_type, dbCur):
        #self.nasip = str(packetobject['NAS-IP-Address'][0])
        self.packetobject = packetobject
        self.access_type=access_type
        self.secret = ''
        self.cur = dbCur
        
        logger.debugfun('%s', show_packet, (packetobject,))
        
    def auth_NA(self, authobject):
        """
        Deny access
        """
        authobject.set_code(3)
        return authobject, self.packetobject
    
    def create_speed(self, tarif_id, account_id, speed=''):
        result_params=speed
        if speed=='':
            defaults = self.caches.defspeed_cache.by_id.get(tarif_id)
            speeds   = self.caches.speed_cache.by_id.get(tarif_id, [])
            defaults = defaults[:6] if defaults else ["0/0","0/0","0/0","0/0","8","0/0"]
            result=[]
            min_delta, minimal_period = -1, []
            now=datetime.datetime.now()
            for speed in speeds:
                #Определяем составляющую с самым котортким периодом из всех, которые папали в текущий временной промежуток
                tnc,tkc,delta,res = fMem.in_period_(speed[6],speed[7],speed[8], now)
                if res==True and (delta<min_delta or min_delta==-1):
                    minimal_period=speed
                    min_delta=delta

            minimal_period = minimal_period[:6] if minimal_period else ["0/0","0/0","0/0","0/0","8","0/0"]
            for k in xrange(0, 6):
                s=minimal_period[k]
                if s=='0/0' or s=='/' or s=='':
                    res=defaults[k]
                else:
                    res=s
                result.append(res)           

            correction = self.caches.speedlimit_cache.by_id.get(account_id)
            #Проводим корректировку скорости в соответствии с лимитом

            result = get_corrected_speed(result, correction)
            #print "corrected", result
            if result==[]: 
                result = defaults if defaults else ["0/0","0/0","0/0","0/0","8","0/0"] 
            result_params=create_speed_string(result)
            self.speed=result_params
        if self.nas_type[:8]==u'mikrotik' and result_params!='':
            self.replypacket.AddAttribute((14988,8),result_params)


    def handle(self):
        nas = self.nasCache.get(self.nasip)
        if not nas: return '',None
        if 0: assert isinstance(nas, NasData)
        
        #self.nas_id=str(row[0])
        self.nas_type = nas.type
        #self.secret = str(row[1])
        self.replypacket=packet.Packet(secret=str(nas.secret),dict=vars.dict)

        user_name = str(self.packetobject['User-Name'][0])

        authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nas.secret), access_type=self.access_type)
        self.cur.execute("SELECT pin FROM billservice_card WHERE sold IS NOT NULL AND login = %s AND now() BETWEEN start_date AND end_date;", (user_name,))
        pin = self.cur.fetchone()
        
        if pin == None:
            self.cur.close()
            return self.auth_NA(authobject)
        else:
            pin = pin[0]

        authobject.plainusername = str(user_name)
        authobject.plainpassword = str(pin)

        if authobject.check_auth()==False:
            logger.warning("Bad User/Password %s", user_name)
            self.cur.close()
            return self.auth_NA(authobject)   
        

        self.cur.execute("""SELECT * FROM card_activate_fn(%s, %s, %s, %s::inet) AS 
                            A(account_id int, "password" character varying, nas_id int, tarif_id int, account_status boolean, 
                            balance_blocked boolean, ballance double precision, disabled_by_limit boolean, tariff_active boolean)
                         """, (user_name, pin, nas.id, str(self.packetobject['Mikrotik-Host-IP'][0])))

        acct_card = self.cur.fetchone()
        self.cur.connection.commit()
        self.cur.close()

        
        if acct_row is None:
            logger.warning("Unknown User %s", user_name)
            return self.auth_NA(authobject)
        
        acct_card = CardActivateData(*acct_card)

        acstatus = acct_card.ballance >0 and not acct_card.balance_blocked and not acct_card.disabled_by_limit and acct_card.account_status
        
        if not acstatus:
            logger.warning("Unallowed account status for user %s: account_status is false", user_name)
            return self.auth_NA(authobject)       
       
        if int(acct_card.nas_id)!=int(nas.nas_id):
            logger.warning("Unallowed NAS for user %s", user_name)
            return self.auth_NA(authobject)


        allow_dial = self.caches.period_cache.in_period.get(acct_card.tarif_id, False)

        logger.info("Authorization user:%s allowed_time:%s User Status:%s Balance:%s Disabled by limit:%s Balance blocked:%s Tarif Active:%s", ( self.packetobject['User-Name'][0], allow_dial, acc_status, ballance, disabled_by_limit, balance_blocked, tarif_status))
        if self.packetobject['User-Name'][0]==user_name and allow_dial and acct_card.tariff_active:
            authobject.set_code(2)
            self.replypacket.AddAttribute('Framed-IP-Address', '192.168.22.32')
            self.create_speed(acct_card.tarif_id, acct_card.account_id, speed='')
            return authobject, self.replypacket
        else:
            return self.auth_NA(authobject)


#auth_class
class HandleSDHCP(HandleSBase):
    __slots__ = () + ('secret', 'nas_id', 'nas_type',)
    def __init__(self,  packetobject):
        super(HandleSDHCP, self).__init__()
        
        self.packetobject = packetobject
        self.secret = ""
        logger.debugfun('%s', show_packet, (packetobject,))

    def auth_NA(self, authobject):
        """
        Deny access
        """
        authobject.set_code(3)
        return authobject, self.packetobject
    
            
    def handle(self):
        row = self.nasCache.get(self.nasip)
        
        if row==None:
            return '', None

        self.nas_id=str(row[0])
        self.nas_type=row[2]
        self.secret=str(row[1])
        
        self.replypacket=packet.Packet(secret=self.secret,dict=dict)
        
        acct_row = self.atCache_mac.get(self.packetobject['User-Name'][0])
        authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(self.secret), access_type='DHCP')
        if acct_row==None:
            return self.auth_NA(authobject)

        user_name = acct_row[1]
        mac_address = acct_row[2]
        nas_id = acct_row[5]
        ipaddress, netmask, speed, allow_dhcp_null, allow_dhcp_block = acct_row[18:23]
        balance_blocked = acct_row[10]
        disabled_by_limit = acct_row[12]
        ballance = acct_row[11]
        tarif_status = acct_row[14]
        acc_status = acct_row[17]
        if ignore_nas_for_vpn==False and int(nas_id)!=int(self.nas_id):
            return self.auth_NA(authobject)

        acstatus = (allow_dhcp_null==True or ballance>0) and (allow_dhcp_block==True or (balance_blocked==False and disabled_by_limit==False and acc_status==True))
        
        
        if not acstatus:
            logger.warning("Unallowed account status for user %s: account_status is false", user_name)
            return self.auth_NA(authobject)
        
        if tarif_status==True:
            authobject.set_code(2)
            self.replypacket.AddAttribute('Framed-IP-Address', ipaddress)
            self.replypacket.AddAttribute('Framed-IP-Netmask',netmask)
            self.replypacket.AddAttribute('Session-Timeout', session_timeout)
            #self.create_speed(tarif_id, speed=speed)
            return authobject, self.replypacket
        else:
            return self.auth_NA(authobject)

#acct class
class HandleSAcct(HandleSBase):
    """process account information after connection"""
    """ Если это аккаунтинг хотспот-сервиса, при поступлении Accounting-Start пишем в профиль пользователя IP адрес, который ему выдал микротик"""
    __slots__ = () + ('cur', 'access_type', 'acctCache_unIdx', 'access_type')
    
    def __init__(self, packetobject, nasip, dbCur):
        super(HandleSAcct, self).__init__()
        self.packetobject=packetobject
        self.nasip=packetobject['NAS-IP-Address'][0]
        self.replypacket=packetobject.CreateReply()
        self.access_type=get_accesstype(packetobject)
        #print self.access_type
        self.cur = dbCur

    def get_bytes(self):
        if self.packetobject.get('Acct-Input-Gigawords'):
            bytes_in=self.packetobject['Acct-Input-Octets'][0]+(self.packetobject['Acct-Input-Gigawords'][0]*vars.gigaword)
        else:
            bytes_in=self.packetobject['Acct-Input-Octets'][0]

        if self.packetobject.get('Acct-Output-Gigawords'):
            bytes_out=self.packetobject['Acct-Output-Octets'][0]+(self.packetobject['Acct-Output-Gigawords'][0]*vars.gigaword)
        else:
            bytes_out=self.packetobject['Acct-Output-Octets'][0]
        return (bytes_in, bytes_out)

    def acct_NA(self):
        """Deny access"""
        # Access denided
        self.replypacket.code=3
        return self.replypacket
    
    def handle(self):
        #self.cur.execute("""SELECT secret from nas_nas WHERE ipaddress=%s;""", (self.nasip,))
        row = self.nasCache.get(self.nasip)
        if row==None: return None
        
        n_secret = row[1]        
        self.replypacket.secret=str(n_secret)        
        #if self.packetobject['User-Name'][0] not in account_timeaccess_cache or account_timeaccess_cache[self.packetobject['User-Name'][0]][2]%10==0:
        userName = self.packetobject['User-Name'][0]

        acct_row = self.acctCache_unIdx.get(userName)

        if acct_row==None:
            self.cur.close()
            logger.warning("Unkown User or user tarif %s", userName)
            return self.acct_NA()
        
        account_id  = acct_row[0]
        time_access = acct_row[3]

        self.replypacket.code=5
        now = datetime.datetime.now()

        #print 'access_type', self.access_type
        #print get_accesstype(self.packetobject)
        #print self.packetobject.keys()
        #print 123
        if self.packetobject['Acct-Status-Type']==['Start']:

            self.cur.execute("""SELECT id FROM radius_activesession
                                WHERE account_id=%s AND sessionid=%s AND
                                caller_id=%s AND called_id=%s AND 
                                nas_id=%s AND framed_protocol=%s;
                             """, (account_id, self.packetobject['Acct-Session-Id'][0],\
                                 self.packetobject['Calling-Station-Id'][0],
                                 self.packetobject['Called-Station-Id'][0], \
                                 self.packetobject['NAS-IP-Address'][0],self.access_type,))

            allow_write = self.cur.fetchone()==None

            if time_access and allow_write:
                self.cur.execute("""INSERT INTO radius_session(account_id, sessionid, date_start,
                                           caller_id, called_id, framed_ip_address, nas_id, 
                                           framed_protocol, checkouted_by_time, checkouted_by_trafic) 
                                           VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s)
                                 """, (account_id, 
                                       self.packetobject['Acct-Session-Id'][0], now,
                                       self.packetobject['Calling-Station-Id'][0], 
                                       self.packetobject['Called-Station-Id'][0], 
                                       self.packetobject['Framed-IP-Address'][0],
                                       self.packetobject['NAS-IP-Address'][0], 
                                       self.access_type, False, False,))
            if allow_write:
                self.cur.execute("""INSERT INTO radius_activesession(account_id, sessionid, date_start,
                                           caller_id, called_id, framed_ip_address, nas_id, 
                                           framed_protocol, session_status)
                                           VALUES (%s, %s,%s,%s, %s, %s, %s, %s, 'ACTIVE');
                                 """, (account_id, self.packetobject['Acct-Session-Id'][0], now,
                                       self.packetobject['Calling-Station-Id'][0], 
                                       self.packetobject['Called-Station-Id'][0], 
                                       self.packetobject['Framed-IP-Address'][0],
                                       self.packetobject['NAS-IP-Address'][0], self.access_type,))

        if self.packetobject['Acct-Status-Type']==['Alive']:
            bytes_in, bytes_out=self.get_bytes()
            if time_access:
                self.cur.execute("""INSERT INTO radius_session(account_id, sessionid, interrim_update,
                                           caller_id, called_id, framed_ip_address, nas_id, session_time,
                                           bytes_out, bytes_in, framed_protocol, checkouted_by_time, checkouted_by_trafic)
                                           VALUES ( %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s);
                                 """, (account_id, self.packetobject['Acct-Session-Id'][0],
                                 now, self.packetobject['Calling-Station-Id'][0],
                                 self.packetobject['Called-Station-Id'][0], 
                                 self.packetobject['Framed-IP-Address'][0],
                                 self.packetobject['NAS-IP-Address'][0],
                                 self.packetobject['Acct-Session-Time'][0],
                                 bytes_in, bytes_out, self.access_type, False, False,))
                
            self.cur.execute("""UPDATE radius_activesession
                                SET interrim_update=%s,bytes_out=%s, bytes_in=%s, session_time=%s, session_status='ACTIVE'
                                WHERE sessionid=%s and nas_id=%s and account_id=%s and framed_protocol=%s;
                             """, (now, bytes_in, bytes_out, self.packetobject['Acct-Session-Time'][0], self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0],account_id, self.access_type,))


        if self.packetobject['Acct-Status-Type']==['Stop']:
            bytes_in, bytes_out=self.get_bytes()
            if time_access:
                self.cur.execute("""INSERT INTO radius_session(account_id, sessionid, interrim_update, date_end,
                                           caller_id, called_id, framed_ip_address, nas_id, session_time,
                                           bytes_in, bytes_out, framed_protocol, checkouted_by_time, checkouted_by_trafic)
                                           VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s);
                                 """, (account_id, self.packetobject['Acct-Session-Id'][0],
                                 now, now, self.packetobject['Calling-Station-Id'][0],
                                 self.packetobject['Called-Station-Id'][0], 
                                 self.packetobject['Framed-IP-Address'][0], 
                                 self.packetobject['NAS-IP-Address'][0],
                                 self.packetobject['Acct-Session-Time'][0],
                                 bytes_in, bytes_out, self.access_type, False, False,))

            self.cur.execute("""UPDATE radius_activesession SET date_end=%s, session_status='ACK'
                                WHERE sessionid=%s and nas_id=%s and account_id=%s and framed_protocol=%s;
                             """, (now,self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0],account_id, self.access_type,))

        self.cur.connection.commit()
        self.cur.close()        
        return self.replypacket




class CacheRoutine(Thread):
    '''
    [0]  - ba.id, 
    [1]  - ba.username, 
    [2]  - ba.ipn_mac_address, 
    [3]  - bt.time_access_service_id, 
    [4]  - ba.password, 
    [5]  - ba.nas_id, 
    [6]  - ba.vpn_ip_address, 
    [7]  - bt.id, 
    [8]  - accps.access_type, 
    [9]  - ba.status, 
    [10] - ba.balance_blocked, 
    [11] - (ba.ballance+ba.credit) as ballance, 
    [12] - ba.disabled_by_limit, 
    [13] - ba.vpn_speed, 
    [14] - bt.active,
    [15] - ba.allow_vpn_null, 
    [16] - ba.allow_vpn_block, 
    [17] - ba.status
    [18] - ba.ipn_ip_address, 
    [19] - ba.netmask, 
    [20] - ba.ipn_speed 
    [21] - ba.allow_dhcp_null
    [22] - ba.allow_dhcp_block
    '''
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global suicideCondition, cacheMaster, flags
        counter = 0; now = datetime.datetime.now
        while True:
            if suicideCondition[self.__class__.__name__]: break            
            try: 
                if flags.cacheFlag or (now() - cacheMaster.date).seconds > 60:
                    run_time = time.clock()                    
                    cur = connection.cursor()
                    #renewCaches(cur)
                    renewCaches(cur, cacheMaster, RadCaches, 41)
                    cur.close()
                    if counter == 0:
                        allowedUsersChecker(allowedUsers, lambda: len(cacheMaster.cache.account_cache.data))
                    counter += 1
                    if counter == 12:
                        #nullify 
                        counter, fMem.periodCache = 0, {}
                    if flags.cacheFlag:
                        with flags.cacheLock: flags.cacheFlag = False
                    
                    logger.info("ast time : %s", time.clock() - run_time)
            except Exception, ex:
                logger.error("%s : #30410004 : %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                
            gc.collect()
            time.sleep(20)
            
    def run2(self):

        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        
        global curCachesDate, curCachesLock, allowedUsers
        global curNasCache, curATCache_userIdx, curATCache_macIdx        
        global tp_asInPeriod, curDefSpCache, curNewSpCache, account_speed_limit_cache
        
        i_fMem = 0
        while True:
            if suicideCondition[self.__class__.__name__]: break
            a = time.clock()
            try:
                cur = connection.cursor()
                ptime =  time.time()
                ptime = ptime - (ptime % 20)
                tmpDate = datetime.datetime.fromtimestamp(ptime)
                
                cur.execute("""SELECT ba.id, ba.username, ba.ipn_mac_address, bt.time_access_service_id, 
                    ba.password, ba.nas_id, ba.vpn_ip_address, bt.id, accps.access_type, 
                    ba.status, ba.balance_blocked, (ba.ballance+ba.credit) as ballance, 
                    ba.disabled_by_limit, ba.vpn_speed, bt.active, 
                    ba.allow_vpn_null, ba.allow_vpn_block, ba.status, ba.ipn_ip_address, ba.netmask, ba.ipn_speed, ba.assign_dhcp_null, ba.assign_dhcp_block
                    FROM billservice_account as ba
                    JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                    JOIN billservice_tariff AS bt ON bt.id=act.tarif_id
                    LEFT JOIN billservice_accessparameters as accps on accps.id = bt.access_parameters_id ;""", (tmpDate,))
                connection.commit()                
                accts = cur.fetchall()
                allowedUsersChecker(allowedUsers, lambda: len(accts))
                
                cur.execute("""SELECT id, secret, type, multilink, ipaddress FROM nas_nas;""")
                connection.commit()
                nasTp = cur.fetchall()
                
                cur.execute("""SELECT tpn.time_start::timestamp without time zone as time_start, tpn.length as length, tpn.repeat_after as repeat_after, bst.id
                    FROM billservice_timeperiodnode as tpn
                    JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
                    JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
                    JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id""")
                connection.commit()
                tpnapsTp = cur.fetchall()
                
                cur.execute("""
                   SELECT 
                    accessparameters.max_limit,accessparameters.burst_limit,
                    accessparameters.burst_treshold, accessparameters.burst_time,
                    accessparameters.priority, accessparameters.min_limit,
                    tariff.id
                    FROM billservice_accessparameters as accessparameters
                    JOIN billservice_tariff as tariff ON tariff.access_parameters_id=accessparameters.id;
                    """)
                connection.commit()
                defspTmp = cur.fetchall()
                
                cur.execute("""
                   SELECT 
                    timespeed.max_limit,timespeed.burst_limit,
                    timespeed.burst_treshold,timespeed.burst_time,
                    timespeed.priority, timespeed.min_limit,
                    timenode.time_start, timenode.length, timenode.repeat_after,
                    tariff.id 
                    FROM billservice_timespeed as timespeed
                    JOIN billservice_tariff as tariff ON tariff.access_parameters_id=timespeed.access_parameters_id
                    JOIN billservice_timeperiod_time_period_nodes as tp ON tp.timeperiod_id=timespeed.time_id
                    JOIN billservice_timeperiodnode as timenode ON tp.timeperiodnode_id=timenode.id;""")
                connection.commit()
                nspTmp = cur.fetchall()
                
                cur.execute("""SELECT speedlimit.max_tx, speedlimit.max_rx, 
                                  speedlimit.burst_tx, speedlimit.burst_rx, 
                                  speedlimit.burst_treshold_tx, speedlimit.burst_treshold_rx, 
                                  speedlimit.burst_time_tx, speedlimit.burst_time_rx, 
                                  speedlimit.priority,
                                  speedlimit.min_tx, speedlimit.min_rx, accountspeedlimit.account_id
                                  FROM billservice_speedlimit as speedlimit, billservice_accountspeedlimit as accountspeedlimit
                                  WHERE accountspeedlimit.speedlimit_id=speedlimit.id;""")
                acctlimitTmp = cur.fetchall()
                connection.commit()
                
                #index on username
                tmpunIdx = {}
                #index on ipn mac address
                tmpmcIdx = {}
                
                #index on account_id in accountlimit
                acctlimit = {}
                
                for tmplimit in acctlimitTmp:
                    acctlimit[tmplimit[11]] = tmplimit
                    
                for acct in accts:
                    tmpunIdx[str(acct[1])] = acct
                    tmpmcIdx[str(acct[2])] = acct
                
                tmpnasC = {}
                
                for nas in nasTp:
                    tmpnasC[str(nas[4])] = nas
                        
                tmpPerAPTP = defaultdict(lambda: False)
                for tpnap in tpnapsTp:
                    tmpPerAPTP[tpnap[3]] = tmpPerAPTP[tpnap[3]] or fMem.in_period_(tpnap[0], tpnap[1], tpnap[2], tmpDate)[3]
                 
                # default speed cache
                tmpdsC = {}
                #nondef speed cache
                tmpnsC = defaultdict(list)
                
                for ds in defspTmp:
                    tmpdsC[ds[6]] = ds
                for ns in nspTmp:
                    tmpnsC[ns[9]].append(ns)
                  
                curCachesLock.acquire()
                account_speed_limit_cache = acctlimit 
                curNasCache = tmpnasC
                curATCache_userIdx = tmpunIdx
                curATCache_macIdx  = tmpmcIdx
                tp_asInPeriod = tmpPerAPTP
                curDefSpCache = tmpdsC
                curNewSpCache = tmpnsC
                curCachesDate = tmpDate
                curCachesLock.release()
                i_fMem += 1
                if i_fMem == 9:
                    i_fMem = 0
                    fMem.periodCache = {}
                    #reread dynamic options
                    config.read("ebs_config_runtime.ini")
                    logger.setNewLevel(int(config.get("radius", "log_level")))
                    global writeProf
                    writeProf = logger.writeInfoP()
                
                if writeProf:
                    pass

            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    logger.error("%s: database connection is down: %s", (self.getName(), repr(ex)))
                else:
                    logger.error("%s: exception: %s", (self.getName(), repr(ex)))
            
            gc.collect()
            time.sleep(60)
    
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



def setpriority(pid=None,priority=1):
    """ Set The Priority of a Windows Process.  Priority is a value between 0-5 where
        2 is normal priority.  Default sets the priority of the current
        python process but can take any valid process ID. """    

    priorityclasses = [win32process.IDLE_PRIORITY_CLASS,
                       win32process.BELOW_NORMAL_PRIORITY_CLASS,
                       win32process.NORMAL_PRIORITY_CLASS,
                       win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                       win32process.HIGH_PRIORITY_CLASS,
                       win32process.REALTIME_PRIORITY_CLASS]
    if pid == None:
        pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, priorityclasses[priority])



def SIGTERM_handler(signum, frame):
    graceful_save()

def SIGHUP_handler(signum, frame):
    global config
    logger.lprint("SIGHUP recieved")
    try:
        config.read("ebs_config.ini")
    except Exception, ex:
        logger.error("SIGHUP config reread error: %s", repr(ex))
    else:
        logger.lprint("SIGHUP config reread OK")
        
def SIGUSR1_handler(signum, frame):
    global flags
    logger.lprint("SIGUSR1 recieved")
    with flags.cacheLock: flags.cacheFlag = True
    
def graceful_save():
    global  cacheThr, suicideCondition
    asyncore.close_all()
    suicideCondition[cacheThr.__class__.__name__] = True
    time.sleep(5)
    pool.close()
    sys.exit()

        

def main():
    global curCachesDate, cacheThr, suicideCondition
    cacheThr = CacheRoutine()
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.setName("CacheRoutine")
    cacheThr.start()    
    
    while curCachesDate == None:
        time.sleep(0.2)
        if not cacheThr.isAlive:
            sys.exit()
    
    server_auth = AsyncAuthServ("0.0.0.0", 1812, pool.connection())
    server_acct = AsyncAcctServ("0.0.0.0", 1813, pool.connection())
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')
    
    try:
        signal.signal(signal.SIGHUP, SIGHUP_handler)
    except: logger.lprint('NO SIGHUP!')
    
    try:
        signal.signal(signal.SIGUSR1, SIGUSR1_handler)
    except: logger.lprint('NO SIGUSR1!')
    
    print "ebs: rad: started"
    while 1: 
        asyncore.poll(0.01)
        
if __name__ == "__main__":
    if "-D" in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
        
    flags = RadFlags()
    vars  = RadVars()
    queues= RadQueues()
    cacheMaster = CacheMaster()
    cacheMaster.date = None
    
    config = ConfigParser.ConfigParser()
    if os.name=='nt' and w32Import:
        setpriority(priority=4)
    config.read("ebs_config.ini") 
    
    vars.dict=dictionary.Dictionary("dicts/dictionary","dicts/dictionary.microsoft", 'dicts/dictionary.mikrotik')
    
    
    logger = isdlogger.isdlogger(config.get("radius", "log_type"), loglevel=int(config.get("radius", "log_level")), ident=config.get("radius", "log_ident"), filename=config.get("radius", "log_file")) 
    utilites.log_adapt = logger.log_adapt
    saver.log_adapt    = logger.log_adapt
    logger.lprint('Radius start')
    
    try:
        #write profiling info?
        writeProf = logger.writeInfoP()         
        
        pool = PooledDB(
            mincached=3, maxcached=10,
            blocking=True, creator=psycopg2,
            dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"),
                                                                   config.get("db", "host"), config.get("db", "password")))
        
        
        suicideCondition = {}
        fMem = pfMemoize()
    
        flags.common_vpn = True if config.get("radius", "common_vpn") == "True" else False    
        vars.session_timeout = int(config.get("dhcp", "session_timeout"))        
        flags.ignore_nas_for_vpn = True if config.get("radius", "ignore_nas_for_vpn") == "True" else False
                
        allowedUsers = setAllowedUsers(pool.connection(), "license.lic")        
        allowedUsers()
        #-------------------
        print "ebs: rad: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in rpc, exiting: ', repr(ex)
        logger.error('Exception in rpc, exiting: %s \n %s', (repr(ex), traceback.format_exc()))
        
