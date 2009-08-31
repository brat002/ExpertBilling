#-*-coding: utf-8 -*-

from __future__ import with_statement

import gc
import os
import sys
import hmac
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

import auth
from auth import Auth, get_eap_handlers
from time import clock
from copy import copy, deepcopy
from daemonize import daemonize
from threading import Thread, Lock
from DBUtils.PooledDB import PooledDB
from collections import deque, defaultdict

from saver import allowedUsersChecker, setAllowedUsers
from utilites import in_period,in_period_info, create_speed_string, get_corrected_speed
from db import get_account_data_by_username_dhcp,get_default_speed_parameters, get_speed_parameters, get_nas_by_ip, get_account_data_by_username, time_periods_by_tarif_id
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

from classes.rad_cache import *
from classes.cacheutils import CacheMaster
from classes.flags import RadFlags
from classes.vars import RadVars, RadQueues
from classes.rad_class.CardActivateData import CardActivateData
from utilites import renewCaches, savepid, rempid, get_connection, getpid, check_running
from pkgutil import simplegeneric

from utilities import Session, data_utilities, utilities_sql

try:    import mx.DateTime
except: print 'cannot import mx'

w32Import = False
try:    import win32api,win32process,win32con
except: pass
else:   w32Import = True

#gigaword = 4294967296
#account_timeaccess_cache={}
#account_timeaccess_cache_count=0

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

@simplegeneric
def sendto (self, data, addr):
    self.outbuf.append((data, addr))
    initiate_send(self)

@simplegeneric
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
            if why[0] == 'EWOULDBLOCK':
                return
            else:
                raise socket.error, why


class RadServer(object):


    def __init__(self, addresses = [], authports = [1812], acctports = [1813], hosts = {}, dict = None, auth_queue_maxlen = 2000, acct_queue_maxlen = 10000, poll_timeout = 500):

        self.dict = dict
        self.authports = authports
        self.acctports = acctports
        self.hosts = hosts
        self.fdmap = {}
        self.authfds = []
        self.acctfds = []
        self.pollobj = None
        self.POLL_TIMEOUT = poll_timeout
        self.AUTH_QUEUE_MAXLEN = auth_queue_maxlen
        self.ACCT_QUEUE_MAXLEN = acct_queue_maxlen

        self.acct_deque = deque()
        self.acct_lock  = Lock()
        self.auth_deque = deque()
        self.auth_lock  = Lock()
        for addr in addresses:
            self.BindToAddress(addr)



    def BindToAddress(self, addr):
        for authport in self.authports:
            authfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            authfd.bind((addr, authport))
            self.authfds.append(authfd)

        for acctport in self.acctports:
            acctfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            acctfd.bind((addr, acctport))	    
            self.acctfds.append(acctfd)



    def RegisterSockets(self):
        """Prepare all sockets to receive packets."""
        events = select.POLLIN | select.POLLPRI | select.POLLERR

        # register auth sockets
        for sock in self.authfds:
            self.fdmap[sock.fileno()] = (sock, SOCKTYPE_AUTH)
            self.pollobj.register(sock, events)

        # register accounting sockets
        for sock in self.acctfds:
            self.fdmap[sock.fileno()] = (sock, SOCKTYPE_ACCT)
            self.pollobj.register(sock, events)



    def Run(self):
        self.fdmap = {}

        # register sockets for event polling
        self.pollobj = select.poll()
        self.RegisterSockets()

class ListenThread(Thread):

    def __init__(self, server, suicide_condition):
        Thread.__init__(self)
        assert isinstance(server, RadServer)
        self.server = server
        self.suicide_condition = suicide_condition



    def run(self):
        while True:
            if self.suicide_condition[self.__class__.__name__]: break
            try:
                for (socknum, event) in self.server.pollobj.poll(self.server.POLL_TIMEOUT):
                    if event != select.POLLIN:
                        logger.error("%s: unexpected event %s!", (self.getName(), event))
                        continue
    
                    # receive packet
                    (sock, socktype) = self.server.fdmap[socknum]
                    (data, addr) = sock.recvfrom(MAX_PACKET_SIZE)


                    try:
                        self.ProcessPacket(data, addr, sock, socktype)
                    except Exception, ex:
                        logger.error("%s: process packet error %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            except Exception, ex:
                logger.error("%s: thread error %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))



    def ProcessPacket(self, data, addr, sock, socktype):
        if socktype == SOCKTYPE_AUTH:
            # create auth packet
            pkt = packet.Packet(dict = self.server.dict, packet = data)
            pkt.timestamp = time.time()
            pkt.source = addr
            pkt.fd = sock

            if pkt.code != packet.AccessRequest:
                logger.warning("%s :dropped auth packet: received non-AccessRequest packet %s | %s", (self.getName() ,pkt.code, repr(addr)))
                return
            with self.server.auth_lock:
                self.server.auth_deque.append(pkt)
            return

        if socktype == SOCKTYPE_ACCT:
            # create acct packet
            pkt = packet.AcctPacket(dict = self.server.dict, packet = data)
            pkt.timestamp = time.time()
            pkt.source = addr
            pkt.fd = sock			

            if not pkt.code in [packet.AccountingRequest, packet.AccountingResponse]:
                logger.warning("%s :dropped acct packet: received non-Acc Request/Response packet %s | %s", (self.getName() ,pkt.code, repr(addr)))
                return

            #dump packet if the queue is too long
            with self.server.acct_lock:
                self.server.acct_deque.append(pkt)
            return


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
            data, addr = self.socket.recvfrom(vars.MAX_DATAGRAM_LEN)
        except Exception, ex:            
            logger.error('Socket read error: %s \n %s', (repr(ex),traceback.format_exc()))
            return
        self.handle_readfrom(data, addr)

    def handle_readfrom(self,data, address):
        pass

    def writable (self):
        return len(self.outbuf)

    def handle_error (self, *info):        
        logger.error('uncaptured python exception, closing channel %s \n %s', (repr(self), traceback.format_exc()))
        self.close()

    def handle_close(self):
        try:    self.dbconn.close()
        except: pass
        self.close()

def authNA(packet):
    return packet.ReplyPacket()

def get_accesstype(packetobject):
    """
    Returns access type name by which a user connects to the NAS
    """

    try:
        nas_port_type = packetobject.get('NAS-Port-Type', (None,))[0]
        if nas_port_type == 'Virtual' and packetobject.get('Service-Type', [''])[0]=='Framed-User':
            return 'PPTP'
        elif nas_port_type == 'Ethernet' and packetobject.get('Service-Type', [''])[0]=='Framed-User': 
            return 'PPPOE'
        elif nas_port_type == 'Wireless-802.11':
            return 'W802.1x'
        elif packetobject.has_key('Mikrotik-Host-IP'):
            return 'HotSpot'
        elif nas_port_type == 'Ethernet' and not packetobject.has_key('Service-Type'):
            return 'DHCP'
        else:
            logger.warning('Nas access type warning: unknown type: %s', nas_port_type)
    except Exception, ex:
        logger.error('Packet access type error: %s \n %s', (repr(ex), repr(packetobject)))
    return

class AsyncAuthServ(AsyncUDPServer):
    def __init__(self, host, port):
        global vars
        self.outbuf = []
        AsyncUDPServer.__init__(self, host, port)
        self.dbconn = get_connection(vars.db_dsn)
        self.dbconn.set_isolation_level(0)
        self.dateCache = datetime.datetime(2000, 1, 1)
        self.caches = None

    def handle_readfrom(self, data, addrport):
        global cacheMaster, queues, vars, flags, fMem
        
        try:     
            #if caches were renewed, renew local copies
            if cacheMaster.date > self.dateCache:
                cacheMaster.lock.acquire()
                try:
                    self.caches = cacheMaster.cache
                    dateAT = deepcopy(cacheMaster.date)
                except Exception, ex:
                    logger.error("%s: cache exception: %s", (self.getName(), repr(ex)))
                finally:
                    cacheMaster.lock.release()
                    
            if not self.caches:
                raise Exception("Caches were not ready!")
            
            if 0: assert isinstance(self.caches, RadCaches)
                        
            t = clock()
            returndata = ''
            #data=self.request[0] # or recv(bufsize, flags)
            assert len(data)<=4096
            packetobject=packet.Packet(dict=vars.DICT,packet=data)
            nas_ip = str(packetobject['NAS-IP-Address'][0])
            access_type = get_accesstype(packetobject)
            logger.debug("Received data packet from: %s", str(addrport))
            logger.debug("Access type: %s, packet: %s", (access_type, packetobject))
            if access_type in ['PPTP', 'PPPOE', 'W802.1x']:
                logger.info("Auth Type %s, raw packet: %s", (access_type, data))
                coreconnect = HandleSAuth(packetobject=packetobject, access_type=access_type)
                coreconnect.nasip = nas_ip
                coreconnect.fMem = fMem; coreconnect.caches = self.caches
                authobject, packetfromcore=coreconnect.handle()
                
                if packetfromcore is None: logger.info("Unknown NAS %s", str(nas_ip)); return
    
                logger.info("Password check: %s", authobject.code)
                returndata, replypacket = authobject.ReturnPacket(packetfromcore) 
                logger.debug("REPLY packet: %s", repr(replypacket))
    
            elif access_type in ['HotSpot']:
                logger.info("Auth Type %s", access_type)
                coreconnect = HandleHotSpotAuth(packetobject=packetobject, access_type=access_type, dbCur=self.dbconn.cursor())
                coreconnect.nasip = nas_ip
                coreconnect.fMem = fMem; coreconnect.caches = self.caches
                authobject, packetfromcore=coreconnect.handle()
                
                if packetfromcore is None: logger.info("Unknown NAS %s", str(nas_ip)); return
    
                logger.info("Password check: %s", authobject.code)
                returndata=authobject.ReturnPacket(packetfromcore) 
                
            elif access_type in ['DHCP'] :
                coreconnect = HandleSDHCP(packetobject=packetobject)
                coreconnect.nasip = nas_ip; coreconnect.caches = self.caches
                authobject, packetfromcore = coreconnect.handle()
                if packetfromcore is None: logger.info("Unknown NAS %s", str(nas_ip)); return
                returndata=authobject.ReturnPacket(packetfromcore)
            else:
                #-----
                coreconnect = HandleSNA(packetobject)
                coreconnect.nasip = nas_ip; coreconnect.caches = self.caches
                right, packetfromcore = coreconnect.handle()
                if packetfromcore is None: return
                returndata=authNA(packetfromcore)
                 
            logger.info("AUTH time: %s", (clock()-t))
            if returndata:
                self.sendto(returndata,addrport)
                del returndata
                     
            del packetfromcore
            del coreconnect
            logger.info("ACC: %s", (clock()-t))
                
        except Exception, ex:
            logger.error("Auth Server readfrom exception: %s \n %s", (repr(ex), traceback.format_exc()))
            if ex.__class__ in vars.db_errors:
                time.sleep(5)
                try:
                    self.dbconn = get_connection(vars.db_dsn)
                except Exception, eex:
                    logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                    time.sleep(10)
                        
class AsyncAcctServ(AsyncUDPServer):
    def __init__(self, host, port):
        self.outbuf = []
        AsyncUDPServer.__init__(self, host, port)
        self.dbconn = get_connection(vars.db_dsn)
        self.dbconn.set_isolation_level(0)
        self.dateCache = datetime.datetime(2000, 1, 1)
        self.caches = None


    def handle_readfrom(self, data, addrport):
        global cacheMaster, vars, fMem
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
                    
            if not self.caches:
                raise Exception("Caches were not ready!")
            
            if 0: assert isinstance(self.caches, RadCaches)

                        
            t = clock()
            assert len(data) <= vars.MAX_DATAGRAM_LEN
            packetobject=packet.AcctPacket(dict=vars.DICT,packet=data)
            dbCur=self.dbconn.cursor()
            coreconnect = HandleSAcct(packetobject=packetobject, dbCur=dbCur)
            coreconnect.caches = self.caches               
            
            packetfromcore = coreconnect.handle()
            
            if packetfromcore is not None: 
                returndat=packetfromcore.ReplyPacket()
                self.socket.sendto(returndat,addrport)
                del returndat
                
            del packetfromcore
            del coreconnect    
            logger.info("ACC: %s", (clock()-t))
            dbCur.connection.commit()
            dbCur.close()
        except Exception, ex:
            logger.error("Acc Server readfrom exception: %s \n %s", (repr(ex), traceback.format_exc()))



class AuthHandler(Thread):
    def __init__(self, server):
        Thread.__init__(self)
        global vars
        self.outbuf = deque()
        #AsyncUDPServer.__init__(self, host, port)
        self.dbconn = get_connection(vars.db_dsn)
        #self.dbconn.set_isolation_level(0)
        self.dateCache = datetime.datetime(2000, 1, 1)
        self.caches = None
        self.server = server
        assert isinstance(self.server, RadServer)



    def run(self):
        global cacheMaster, queues, vars, flags, fMem
        while True:
            if suicideCondition[self.__class__.__name__]: break
            try:     
                #if caches were renewed, renew local copies
                if cacheMaster.date > self.dateCache:
                    cacheMaster.lock.acquire()
                    try:
                        self.caches = cacheMaster.cache
                        dateAT = deepcopy(cacheMaster.date)
                    except Exception, ex:
                        logger.error("%s: cache exception: %s", (self.getName(), repr(ex)))
                    finally:
                        cacheMaster.lock.release()
                        if 0: assert isinstance(self.caches, RadCaches)

                if not self.caches:
                    raise Exception("Caches were not ready!")

                packetobject = None
                with self.server.auth_lock:
                    if len(self.server.auth_deque) > 0:
                        packetobject = self.server.auth_deque.popleft()
                if not packetobject:
                    time.sleep(0.5)
                    continue
                if False: assert isinstance(packetobject, packet.Packet)
                auth_time = clock()
                returndata = ''
                nas_ip = str(packetobject['NAS-IP-Address'][0])
                access_type = get_accesstype(packetobject)
                logger.debug("%s: Access type: %s, packet: %s", (self.getName(), access_type, packetobject.code))
                user_name = ''
                try:
                    user_name = str(packetobject['User-Name'][0])
                except:
                    pass
                if access_type in ['PPTP', 'PPPOE', 'W802.1x']:
                    coreconnect = HandleSAuth(packetobject=packetobject, access_type=access_type)
                    coreconnect.nasip = nas_ip
                    coreconnect.fMem = fMem; coreconnect.caches = self.caches
                    authobject, packetfromcore=coreconnect.handle()

                    if packetfromcore is None: logger.info("Unknown NAS %s", str(nas_ip)); return

                    logger.info("Password check: %s", authobject.code)
                    #logger.debug("AUTH packet: %s", show_packet(packetfromcore))
                    returndata, replypacket = authobject.ReturnPacket(packetfromcore) 
                    logger.debug("REPLY packet: %s", repr(replypacket)) 

                elif access_type in ['HotSpot']:
                    coreconnect = HandleHotSpotAuth(packetobject=packetobject, access_type=access_type, dbCur=self.dbconn.cursor())
                    coreconnect.nasip = nas_ip
                    coreconnect.fMem = fMem; coreconnect.caches = self.caches
                    authobject, packetfromcore=coreconnect.handle()

                    if packetfromcore is None: logger.info("Unknown NAS %s", str(nas_ip)); return

                    logger.info("%s: Password check: %s", (self.getName(), authobject.code))
                    returndata=authobject.ReturnPacket(packetfromcore) 

                elif access_type in ['DHCP'] :
                    coreconnect = HandleSDHCP(packetobject=packetobject)
                    coreconnect.nasip = nas_ip; coreconnect.caches = self.caches
                    authobject, packetfromcore = coreconnect.handle()
                    if packetfromcore is None: logger.info("Unknown NAS %s", str(nas_ip)); return
                    returndata=authobject.ReturnPacket(packetfromcore)
                else:
                    #-----
                    coreconnect = HandleSNA(packetobject)
                    coreconnect.nasip = nas_ip; coreconnect.caches = self.caches
                    right, packetfromcore = coreconnect.handle()
                    if packetfromcore is None: return
                    returndata=authNA(packetfromcore)                  

                if returndata:
                    packetobject.fd.sendto(returndata, packetobject.source)
                    del returndata

                del packetfromcore
                del coreconnect
                logger.info("%s: AUTH time: %s USER: %s NAS: %s TYPE: %s", (self.getName(), clock()-auth_time, user_name, nas_ip, access_type))

            except Exception, ex:
                logger.error("%s Packet handler exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.dbconn = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)

class AcctHandler(Thread):
    def __init__(self, server):
        Thread.__init__(self)
        self.outbuf = deque()
        self.dbconn = get_connection(vars.db_dsn)
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.settimeout(vars.ACCT_SOCK_TIMEOUT)
        self.dateCache = datetime.datetime(2000, 1, 1)
        self.caches = None
        self.server = server
        assert isinstance(self.server, RadServer)

    def run(self):
        global cacheMaster, vars, fMem
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
                        if 0: assert isinstance(self.caches, RadCaches)

                if not self.caches:
                    raise Exception("Caches were not ready!")
                
                packetobject = None
                with self.server.acct_lock:
                    if len(self.server.acct_deque) > 0:
                        packetobject = self.server.acct_deque.popleft()
                if not packetobject:
                    time.sleep(0.5)
                    continue
                if False: assert isinstance(packetobject, packet.AcctPacket)

                acct_time = clock()
                dbCur = self.dbconn.cursor()
                coreconnect = HandleSAcct(packetobject=packetobject, dbCur=dbCur)
                coreconnect.caches = self.caches          

                packetfromcore = coreconnect.handle()

                if packetfromcore is not None: 
                    returndata = packetfromcore.ReplyPacket()
                    packetobject.fd.sendto(returndata, packetobject.source)
                    #self.socket.sendto(returndat,addrport)
                    del returndata
                    del packetfromcore             
                 
                logger.info("ACCT: %s, USER: %s, NAS: %s, ACCESS TYPE: %s", (clock()-acct_time, coreconnect.userName, coreconnect.nasip, coreconnect.access_type))
                dbCur.connection.commit()
                dbCur.close()
                del coreconnect 
            except Exception, ex:
                logger.error("%s readfrom exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.dbconn = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)

class HandleSBase(object):
    __slots__ = ('packetobject', 'cacheDate', 'nasip', 'caches', 'replypacket', 'userName')

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

    def add_values(self, tarif_id):
        attrs = self.caches.radattrs_cache.by_id.get(tarif_id, [])
        for attr in attrs:
            if 0: assert isinstance(attr, RadiusAttrsData)
            if attr.vendor:
                self.replypacket.AddAttribute((attr.vendor,attr.attrid), str(attr.value))
            else:
                self.replypacket.AddAttribute(attr.attrid, str(attr.value))

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
            #print self.caches.speedlimit_cache
            result = get_corrected_speed(result, correction)
            #print "corrected", result
            if result==[]: 
                result = defaults if defaults else ["0/0","0/0","0/0","0/0","8","0/0"]                

            result_params=create_speed_string(result)
            self.speed=result_params
        if self.nas_type[:8]==u'mikrotik' and result_params!='':
            self.replypacket.AddAttribute((14988,8),result_params)


    def handle(self):
        nas = self.caches.nas_cache.by_ip.get(self.nasip) 
        if not nas: return '',None
        if 0: assert isinstance(nas, NasData)
        self.nas_type = nas.type
        self.replypacket = packet.Packet(secret=str(nas.secret),dict=vars.DICT)

        station_id = self.packetobject.get('Calling-Station-Id', [''])[0]
        user_name = str(self.packetobject['User-Name'][0])

        #row = get_account_data_by_username(self.cur, self.packetobject['User-Name'][0], self.access_type, station_id=station_id, multilink = self.multilink, common_vpn = common_vpn)
        acc = self.caches.account_cache.by_username.get(user_name)
        authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nas.secret), access_type=self.access_type, challenges = queues.challenges)

        if acc is None:
            logger.warning("Unknown User %s", user_name)
            return self.auth_NA(authobject)  

        if 0: assert isinstance(acc, AccountData)
        authobject.plainusername = str(acc.username)
        authobject.plainpassword = str(acc.password)

        logger.debug("Account data : %s", repr(acc))

        process, ok, left = authobject._HandlePacket()
        if not process:
            logger.warning(left, ())
            logger.debug("Auth object : %s" , authobject)
            #self.cur.close()
            if ok:
                return authobject, self.replypacket
            else:
                return self.auth_NA(authobject)


        process, ok, left = authobject._ProcessPacket()
        if not process:
            logger.warning(left, ())
            logger.debug("Auth object : %s" , authobject)
            if ok:
                return authobject, self.replypacket
            else:
                return self.auth_NA(authobject)

        check_auth, left = authobject.check_auth()
        logger.debug("Auth object : %s" , authobject)
        if not check_auth:
            logger.warning(left, ())
            return self.auth_NA(authobject) 

        #print common_vpn,access_type,self.access_type
        if (not vars.COMMON_VPN) and ((acc.access_type is None) or (acc.access_type != self.access_type)):
            logger.warning("Unallowed Access Type for user %s: access_type error. access type - %s; packet access type - %s", (user_name, acc.access_type, self.access_type))
            return self.auth_NA(authobject)

        acstatus = (((not acc.allow_vpn_null and acc.ballance >0) or acc.allow_vpn_null) \
                    and \
                    (acc.allow_vpn_block or (not acc.allow_vpn_block and not acc.balance_blocked and not acc.disabled_by_limit and acc.account_status == 1)))
        #acstatus = True
        if not acstatus:
            logger.warning("Unallowed account status for user %s: account_status is false", user_name)
            return self.auth_NA(authobject)      

        if self.access_type == 'PPTP' and acc.associate_pptp_ipn_ip and not (acc.ipn_ip_address == station_id):
            logger.warning("Unallowed NAS PPTP for user %s: station_id status is false, station_id - %s , ipn_ip - %s; ipn_mac - %s access_type: %s", (user_name, station_id, acc.ipn_ip_address, acc.ipn_mac_address, self.access_type))
            return self.auth_NA(authobject) 
        
        if self.access_type == 'PPPOE' and acc.associate_pppoe_mac and not (acc.ipn_mac_address == station_id):
            logger.warning("Unallowed NAS PPPOE for user %s: station_id status is false, station_id - %s , ipn_ip - %s; ipn_mac - %s access_type: %s", (user_name, station_id, acc.ipn_ip_address, acc.ipn_mac_address, self.access_type))
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
        if vars.IGNORE_NAS_FOR_VPN is False and int(acc.nas_id)!=int(nas.id):
            logger.warning("Unallowed NAS for user %s", user_name)
            return self.auth_NA(authobject) 

        allow_dial = self.caches.period_cache.in_period.get(acc.tarif_id, False)

        logger.info("Authorization user:%s allowed_time:%s User Status:%s Balance:%s Disabled by limit:%s Balance blocked:%s Tarif Active:%s", ( self.packetobject['User-Name'][0], allow_dial, acc.account_status, acc.ballance, acc.disabled_by_limit, acc.balance_blocked, acc.tarif_active))
        if self.packetobject['User-Name'][0]==user_name and allow_dial and acc.tarif_active:
            authobject.set_code(2)
            self.replypacket.username = str(user_name) #Нельзя юникод
            self.replypacket.password = str(acc.password) #Нельзя юникод
            self.replypacket.AddAttribute('Service-Type', 2)
            self.replypacket.AddAttribute('Framed-Protocol', 1)
            self.replypacket.AddAttribute('Framed-IP-Address', acc.vpn_ip_address)
            #account_speed_limit_cache
            self.create_speed(acc.tarif_id, acc.account_id, speed=acc.vpn_speed)
            self.add_values(acc.tarif_id)
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

    def add_values(self, tarif_id):
        attrs = self.caches.radattrs_cache.by_id.get(tarif_id, [])
        for attr in attrs:
            if 0: assert isinstance(attr, RadiusAttrsData)
            if attr.vendor:
                self.replypacket.AddAttribute((attr.vendor,attr.attrid), str(attr.value))
            else:
                self.replypacket.AddAttribute(attr.attrid, str(attr.value))

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
            #print "speed", result_params
        if self.nas_type[:8]==u'mikrotik' and result_params!='':
            self.replypacket.AddAttribute((14988,8),result_params)


    def handle(self):
        nas = self.caches.nas_cache.by_ip.get(self.nasip) 
        if not nas: return '',None
        if 0: assert isinstance(nas, NasData)

        #self.nas_id=str(row[0])
        self.nas_type = nas.type
        #self.secret = str(row[1])
        self.replypacket=packet.Packet(secret=str(nas.secret),dict=vars.DICT)

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

        check_auth, left = authobject.check_auth()
        if not check_auth:
            logger.warning(left, ())
            self.cur.close()
            return self.auth_NA(authobject)   

        #print user_name, pin, nas.id, str(self.packetobject['Mikrotik-Host-IP'][0])

        self.cur.execute("""SELECT * FROM card_activate_fn(%s, %s, %s, %s::inet) AS 
                         A(account_id int, "password" character varying, nas_id int, tarif_id int, account_status boolean, 
                         balance_blocked boolean, ballance numeric, disabled_by_limit boolean, tariff_active boolean)
                        """, (user_name, pin, nas.id, str(self.packetobject['Mikrotik-Host-IP'][0])))

        acct_card = self.cur.fetchone()
        self.cur.connection.commit()
        self.cur.close()


        if acct_card is None:
            logger.warning("Unknown User %s", user_name)
            return self.auth_NA(authobject)

        acct_card = CardActivateData(*acct_card)

        acstatus = acct_card.ballance >0 and not acct_card.balance_blocked and not acct_card.disabled_by_limit and acct_card.account_status

        if not acstatus:
            logger.warning("Unallowed account status for user %s: account_status is false", user_name)
            return self.auth_NA(authobject)       

        if int(acct_card.nas_id)!=int(nas.id):
            logger.warning("Unallowed NAS for user %s", user_name)
            return self.auth_NA(authobject)


        allow_dial = self.caches.period_cache.in_period.get(acct_card.tarif_id, False)

        logger.info("Authorization user:%s allowed_time:%s User Status:%s Balance:%s Disabled by limit:%s Balance blocked:%s Tarif Active:%s", ( self.packetobject['User-Name'][0], allow_dial, acct_card.account_status, acct_card.ballance, acct_card.disabled_by_limit, acct_card.balance_blocked,acct_card.tariff_active))
        if self.packetobject['User-Name'][0]==user_name and allow_dial and acct_card.tariff_active:
            authobject.set_code(packet.AccessAccept)
            #self.replypacket.AddAttribute('Framed-IP-Address', '192.168.22.32')
            self.create_speed(acct_card.tarif_id, acct_card.account_id, speed='')
            self.add_values(acct_card.tarif_id)
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
        """Deny access"""

        authobject.set_code(3)
        return authobject, self.packetobject


    def handle(self):
        nas = self.caches.nas_cache.by_ip.get(self.nasip)
        if not nas: return '',None
        if 0: assert isinstance(nas, NasData)

        self.replypacket=packet.Packet(secret=nas.secret,dict=vars.DICT)

        acc = self.caches.account_cache.by_ipn_mac.get(self.packetobject['User-Name'][0])
        authobject=Auth(packetobject=self.packetobject, username='', password = '',  secret=str(nas.secret), access_type='DHCP')
        if acc is None:
            return self.auth_NA(authobject)
        if 0: assert isinstance(acc, AccountData)

        if vars.IGNORE_NAS_FOR_VPN is False and int(acc.nas_id)!=int(nas.id):
            return self.auth_NA(authobject)
        #print dir(acc)
        acstatus = (acc.assign_dhcp_null or acc.ballance>0) and \
                 (acc.assign_dhcp_block or (not acc.balance_blocked and not acc.disabled_by_limit and acc.account_status))

        if not acstatus:
            logger.warning("Unallowed account status for user %s: account_status is false", acc.username)
            return self.auth_NA(authobject)

        if acc.tarif_active:
            authobject.set_code(2)
            self.replypacket.AddAttribute('Framed-IP-Address', acc.ipn_ip_address)
            self.replypacket.AddAttribute('Framed-IP-Netmask', acc.netmask)
            self.replypacket.AddAttribute('Session-Timeout',   vars.SESSION_TIMEOUT)
            return authobject, self.replypacket
        else:
            return self.auth_NA(authobject)

#acct class
class HandleSAcct(HandleSBase):
    """process account information after connection"""
    """ Если это аккаунтинг хотспот-сервиса, при поступлении Accounting-Start пишем в профиль пользователя IP адрес, который ему выдал микротик"""
    __slots__ = () + ('cur', 'access_type')

    def __init__(self, packetobject, dbCur):
        super(HandleSAcct, self).__init__()
        self.packetobject=packetobject
        self.nasip=packetobject['NAS-IP-Address'][0]
        self.replypacket=packetobject.CreateReply()
        self.access_type=get_accesstype(packetobject)
        #print self.access_type
        self.cur = dbCur
        self.userName = ''

    def get_bytes(self):
        bytes_in  = self.packetobject['Acct-Input-Octets'][0]  + self.packetobject.get('Acct-Input-Gigawords', (0,))[0]  * vars.GIGAWORD
        bytes_out = self.packetobject['Acct-Output-Octets'][0] + self.packetobject.get('Acct-Output-Gigawords', (0,))[0] * vars.GIGAWORD
        return (bytes_in, bytes_out)

    def acct_NA(self):
        """Deny access"""
        # Access denided
        self.replypacket.code = packet.AccessReject
        return self.replypacket

    def handle(self):
        nas_by_int_id = False
        nas_name = ''
        if self.packetobject.has_key('NAS-Identifier'):
            nas_name = self.packetobject['NAS-Identifier'][0]
            nas = self.caches.nas_cache.by_ip_n_identify.get((self.nasip,nas_name))
            nas_by_int_id = True
        else:
            nas = self.caches.nas_cache.by_ip.get(self.nasip)
        if not nas:
            logger.info('ACCT: unknown NAS: %s', (self.nasip,))
            return None
        if 0: assert isinstance(nas, NasData)

        self.replypacket.secret=str(nas.secret)        
        #if self.packetobject['User-Name'][0] not in account_timeaccess_cache or account_timeaccess_cache[self.packetobject['User-Name'][0]][2]%10==0:
        self.userName = str(self.packetobject['User-Name'][0])

        acc = self.caches.account_cache.by_username.get(self.userName)
        if acc is None:
            self.cur.connection.commit()
            self.cur.close()
            logger.warning("Unknown User or user tarif %s", self.userName)
            return self.acct_NA()
        if 0: assert isinstance(acc, AccountData)

        self.replypacket.code = packet.AccountingResponse
        now = datetime.datetime.now()
        
        #packet_session = self.packetobject['Acct-Session-Id'][0]
        if self.packetobject['Acct-Status-Type']==['Start']:
            if nas_by_int_id:
                self.cur.execute("""SELECT id FROM radius_activesession
                                WHERE account_id=%s AND sessionid=%s AND
                                caller_id=%s AND called_id=%s AND 
                                nas_int_id=%s AND framed_protocol=%s;
                             """, (acc.account_id, self.packetobject['Acct-Session-Id'][0],\
                                    self.packetobject['Calling-Station-Id'][0],
                                    self.packetobject['Called-Station-Id'][0], \
                                    nas.id, self.access_type,))
            else:                
                self.cur.execute("""SELECT id FROM radius_activesession
                                    WHERE account_id=%s AND sessionid=%s AND
                                    caller_id=%s AND called_id=%s AND 
                                    nas_id=%s AND framed_protocol=%s;
                                 """, (acc.account_id, self.packetobject['Acct-Session-Id'][0],\
                                        self.packetobject['Calling-Station-Id'][0],
                                        self.packetobject['Called-Station-Id'][0], \
                                        self.packetobject['NAS-IP-Address'][0], self.access_type,))

            allow_write = self.cur.fetchone() is None

            if allow_write:
                self.cur.execute("""INSERT INTO radius_activesession(account_id, sessionid, date_start,
                                 caller_id, called_id, framed_ip_address, nas_id, 
                                 framed_protocol, session_status, nas_int_id)
                                 VALUES (%s, %s,%s,%s, %s, %s, %s, %s, 'ACTIVE', %s);
                                 """, (acc.account_id, self.packetobject['Acct-Session-Id'][0], now,
                                        self.packetobject['Calling-Station-Id'][0], 
                                        self.packetobject['Called-Station-Id'][0], 
                                        self.packetobject['Framed-IP-Address'][0],
                                        self.packetobject['NAS-IP-Address'][0], self.access_type, nas.id))
                if nas_by_int_id:
                    with queues.sessions_lock:
                        queues.sessions[str(self.packetobject['Acct-Session-Id'][0])] = (nas.id, now)

            if acc.time_access_service_id:
                self.cur.execute("""INSERT INTO radius_session(account_id, sessionid, date_start,
                                 caller_id, called_id, framed_ip_address, nas_id, 
                                 framed_protocol, checkouted_by_time, checkouted_by_trafic) 
                                 VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s)
                                 """, (acc.account_id, 
                                        self.packetobject['Acct-Session-Id'][0], now,
                                        self.packetobject['Calling-Station-Id'][0], 
                                        self.packetobject['Called-Station-Id'][0], 
                                        self.packetobject['Framed-IP-Address'][0],
                                        self.packetobject['NAS-IP-Address'][0], 
                                        self.access_type, False, False,))


        elif self.packetobject['Acct-Status-Type']==['Alive']:
            bytes_in, bytes_out = self.get_bytes()
            if acc.time_access_service_id:
                self.cur.execute("""INSERT INTO radius_session(account_id, sessionid, interrim_update,
                                 caller_id, called_id, framed_ip_address, nas_id, session_time,
                                 bytes_out, bytes_in, framed_protocol, checkouted_by_time, checkouted_by_trafic)
                                 VALUES ( %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s);
                                 """, (acc.account_id, self.packetobject['Acct-Session-Id'][0],
                                        now, self.packetobject['Calling-Station-Id'][0],
                                        self.packetobject['Called-Station-Id'][0], 
                                        self.packetobject['Framed-IP-Address'][0],
                                        self.packetobject['NAS-IP-Address'][0],
                                        self.packetobject['Acct-Session-Time'][0],
                                        bytes_in, bytes_out, self.access_type, False, False,))

            if nas_by_int_id:
                nas_int_id, sess_time = queues.sessions.get(self.packetobject['Acct-Session-Id'][0], (None, None))
                if nas_int_id:
                    self.cur.execute("""UPDATE radius_activesession
                                 SET interrim_update=%s,bytes_out=%s, bytes_in=%s, session_time=%s, session_status='ACTIVE'
                                 WHERE sessionid=%s and nas_int_id=%s and account_id=%s and framed_protocol=%s;
                                 """, (now, bytes_in, bytes_out, self.packetobject['Acct-Session-Time'][0], self.packetobject['Acct-Session-Id'][0], nas_int_id, acc.account_id, self.access_type,))
            else:
                self.cur.execute("""UPDATE radius_activesession
                             SET interrim_update=%s,bytes_out=%s, bytes_in=%s, session_time=%s, session_status='ACTIVE'
                             WHERE sessionid=%s and nas_id=%s and account_id=%s and framed_protocol=%s;
                             """, (now, bytes_in, bytes_out, self.packetobject['Acct-Session-Time'][0], self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0], acc.account_id, self.access_type,))


        elif self.packetobject['Acct-Status-Type']==['Stop']:
            bytes_in, bytes_out=self.get_bytes()
            if acc.time_access_service_id:
                self.cur.execute("""INSERT INTO radius_session(account_id, sessionid, interrim_update, date_end,
                                 caller_id, called_id, framed_ip_address, nas_id, session_time,
                                    bytes_in, bytes_out, framed_protocol, checkouted_by_time, checkouted_by_trafic)
                                    VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s);
                                    """, (acc.account_id, self.packetobject['Acct-Session-Id'][0],
                                          now, now, self.packetobject['Calling-Station-Id'][0],
                                          self.packetobject['Called-Station-Id'][0], 
                                          self.packetobject['Framed-IP-Address'][0], 
                                          self.packetobject['NAS-IP-Address'][0],
                                          self.packetobject['Acct-Session-Time'][0],
                                          bytes_in, bytes_out, self.access_type, False, False,))

            if nas_by_int_id:
                nas_int_id, sess_time = queues.sessions.get(self.packetobject['Acct-Session-Id'][0], (None, None))
                if nas_int_id is not None:
                    self.cur.execute("""UPDATE radius_activesession SET date_end=%s, session_status='ACK'
                                 WHERE sessionid=%s and nas_int_id=%s and account_id=%s and framed_protocol=%s;
                                 """, (now,self.packetobject['Acct-Session-Id'][0], nas_int_id, acc.account_id, self.access_type,))
            else:
                self.cur.execute("""UPDATE radius_activesession SET date_end=%s, session_status='ACK'
                             WHERE sessionid=%s and nas_id=%s and account_id=%s and framed_protocol=%s;
                             """, (now,self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0], acc.account_id, self.access_type,))

               
        return self.replypacket




class CacheRoutine(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        #connection = pool.connection()
        #connection._con._con.set_client_encoding('UTF8')
        global suicideCondition, cacheMaster, flags, vars
        self.connection = get_connection(vars.db_dsn)
        counter = 0; now = datetime.datetime.now
        first_time = True
        while True:
            if suicideCondition[self.__class__.__name__]: break            
            try: 
                if flags.cacheFlag or (now() - cacheMaster.date).seconds > vars.CACHE_TIME:
                    run_time = time.clock()                    
                    cur = self.connection.cursor()
                    #renewCaches(cur)
                    renewCaches(cur, cacheMaster, RadCaches, 41, (fMem,))
                    if first_time:
                        queues.sessions.get_data((cur, utilities_sql.utilites_sql['get_sessions'], (cacheMaster.date,)), (([0], [1,2])))
                        first_time = False
                    cur.connection.commit()
                    cur.close()
                    if counter == 0:
                        allowedUsersChecker(allowedUsers, lambda: len(cacheMaster.cache.account_cache.data), ungraceful_save, flags)
                        if not flags.allowedUsersCheck: continue                    
                        counter += 1
                    if counter == 12:
                        #nullify 
                        counter, fMem.periodCache = 0, {}
                    if flags.cacheFlag:
                        with flags.cacheLock: flags.cacheFlag = False

                    logger.info("ast time : %s", time.clock() - run_time)
                    if not w32Import:
                        logger.info("AUTH queue len: %s", len(queues.rad_server.auth_deque))
                        logger.info("ACCT queue len: %s", len(queues.rad_server.acct_deque))
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
            time.sleep(20)


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
    global  cacheThr, suicideCondition, vars
    asyncore.close_all()
    suicideCondition[cacheThr.__class__.__name__] = True
    logger.lprint("About to stop gracefully.")
    time.sleep(5)
    #pool.close()
    rempid(vars.piddir, vars.name)
    print "RAD: exiting"
    logger.lprint("Stopping gracefully.")
    sys.exit()

def ungraceful_save():
    global suicideCondition
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    rempid(vars.piddir, vars.name)
    asyncore.close_all()
    print "RAD: exiting"
    logger.lprint("RAD exiting.")
    sys.exit()

def main():
    global threads, curCachesDate, cacheThr, suicideCondition, server_auth, server_acct
    threads = []
    if not w32Import:
        queues.rad_server = RadServer(addresses=['0.0.0.0'], dict=vars.DICT, poll_timeout=vars.POLL_TIMEOUT)
        for i in xrange(vars.LISTEN_THREAD_NUM):
            newLthr = ListenThread(queues.rad_server, suicideCondition)
            newLthr.setName('LTHR:#%i: ListenThread' % i)
            threads.append(newLthr)
        for i in xrange(vars.AUTH_THREAD_NUM):
            newAuth = AuthHandler(queues.rad_server)
            newAuth.setName('AUTH:#%i: AuthHandler' % i)
            threads.append(newAuth)
        for i in xrange(vars.ACCT_THREAD_NUM):
            newAcct = AcctHandler(queues.rad_server)
            newAcct.setName('ACCT:#%i: AcctHandler' % i)
            threads.append(newAcct)
    cacheThr = CacheRoutine()
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.setName("CacheRoutine")
    cacheThr.start()    

    time.sleep(2)
    while cacheMaster.read is False or flags.allowedUsersCheck is False:        
        if not cacheThr.isAlive:
            print 'Exception in cache thread: exiting'
            sys.exit()
        time.sleep(10)
        if not cacheMaster.read: 
            print 'caches still not read, maybe you should check the log'

    print 'caches ready'
    if not w32Import:
        logger.warning("Using normal poll multithreaded server!", ())
        queues.rad_server.Run()
        listen_sleep = float(vars.POLL_TIMEOUT) / (1000 * vars.LISTEN_THREAD_NUM)
        for th in threads:
            suicideCondition[th.__class__.__name__] = False
            th.start()        
            logger.info("NFR %s start", th.getName())
            if isinstance(th, ListenThread):
                time.sleep(listen_sleep)
            else:
                time.sleep(0.1)
    else:
        logger.warning("Using windows server!", ())
        server_auth = AsyncAuthServ("0.0.0.0", vars.AUTH_PORT)
        server_acct = AsyncAcctServ("0.0.0.0", vars.ACCT_PORT)
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
    savepid(vars.piddir, vars.name)
    if not w32Import:
        while 1: 
            time.sleep(300)
    else:
        poll_time = float(vars.POLL_TIMEOUT) / 1000
        while 1:
            asyncore.poll(poll_time)

if __name__ == "__main__":
    if "-D" in sys.argv:
        pass
        #daemonize("/dev/null", "log.txt", "log.txt")

    config = ConfigParser.ConfigParser()

    config.read("ebs_config.ini")


    server_auth = None
    server_acct = None
    try:
        flags = RadFlags()
        vars  = RadVars()
        queues= RadQueues()
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME)

        cacheMaster = CacheMaster()

        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file)
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
        if not globals().has_key('_1i'):
            _1i = lambda: ''
        allowedUsers = setAllowedUsers(_1i())        
        allowedUsers()
        queues.sessions = Session.DictSession(data_utilities.get_db_data, data_utilities.simple_list_index)
        #-------------------
        print "ebs: rad: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in rad, exiting: ', repr(ex)
        logger.error('Exception in rpc, exiting: %s \n %s', (repr(ex), traceback.format_exc()))        
