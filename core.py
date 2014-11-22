#-*-coding=utf-8-*-

from __future__ import with_statement
import sys

import site
site.addsitedir('/opt/ebs/venv/lib/python2.6/site-packages')
site.addsitedir('/opt/ebs/venv/lib/python2.7/site-packages')
import sys


sys.path.insert(0, "modules")
sys.path.append("cmodules")
"""DON'T REMOVE, NEEDED FOR PROPER FREEZING!!!"""
try:    import mx.DateTime
except: pass
from encodings import idna, ascii #DONT REMOVE, BLATS!

import IPy
import zlib
import signal
import random
import threading
import dictionary
import ConfigParser
import psycopg2, psycopg2.extras
import time, datetime, os, sys, gc, traceback
import socket
import isdlogger
import utilites

import itertools
import db

from decimal import Decimal
from copy import copy, deepcopy
from threading import Thread, Lock
from collections import defaultdict

from utilites import get_decimals_speeds
from utilites import settlement_period_info, in_period, in_period_info, create_speed

import ctypes
from ctypes.util import find_library
from ctypes import Structure

from hashlib import md5
import commands
from base64 import b64decode
from operator import itemgetter, attrgetter
#===============================================================================
# from importlib import import_module ##DONT REMOVE
# import contextlib
# import UserList
# import celery.utils.text
# 
# import celery.task
# 
# import kombu.entity
#===============================================================================
import celery.task


sys.path.append("/opt/ebs/data/workers/")
sys.path.append("workers/")
sys.path.append("celery/")

from tasks import PoD, change_speed, cred, update_vpn_speed_state, update_ipn_speed_state, update_pod_state
import tasks

from db import transaction, get_last_checkout, get_acctf_history, radiustraffictransaction
from db import get_last_addon_checkout, addon_history, check_in_suspended, TraftransTableException


from classes.cacheutils import CacheMaster
from classes.core_cache import *
from classes.flags import CoreFlags
from classes.vars import CoreVars
from utilites import renewCaches, savepid, get_connection, check_running, getpid, rempid

from psycopg2.extensions import  ISOLATION_LEVEL_SERIALIZABLE, ISOLATION_LEVEL_REPEATABLE_READ

from classes.core_class.RadiusSession import RadiusSession
from classes.core_class.BillSession import BillSession


psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

NAME = 'core'
DB_NAME = 'db'
SECONDS_PER_DAY = 86400
ZERO_SUM = 0
SECOND = datetime.timedelta(seconds=1)
PERIOD = 1
ADDON  = 2
MEGABYTE=Decimal(1048576)

def comparator(d, s):
    for key in s:
        if s[key]!='' and s[key]!='Null' and s[key]!='None':
            d[key]=s[key] 
    return d

class check_vpn_access(Thread):
    def __init__ (self):          
        Thread.__init__(self)


    def check_access(self):
        """
            Раз в 30 секунд происходит выборка всех пользователей
            OnLine, делается проверка,
            1. не вышли ли они за рамки временного диапазона
            2. Не ушли ли в нулевой балланс
            если срабатывает одно из двух условий-посылаем команду на отключение пользователя
            TO-DO: Переписать! Работает правильно.
            nas_id содержит в себе IP адрес. Сделано для уменьшения выборок в модуле core при старте сессии
            TO-DO: если NAS не поддерживает POD или в парметрах доступа ТП указан IPN - отсылать команды через SSH
        """
        global cacheMaster, suicideCondition, vars
        dateAT = datetime.datetime(2000, 1, 1)
        self.connection = get_connection(vars.db_dsn)
        caches = None
        while True:            
            try:
                if suicideCondition[self.__class__.__name__]:
                    try: self.connection.close()
                    except: pass
                    break
                a = time.time()

                if cacheMaster.date > dateAT:
                    cacheMaster.lock.acquire()
                    try:
                        caches = cacheMaster.cache
                        dateAT = deepcopy(cacheMaster.date)
                    except Exception, ex:
                        logger.error("%s: cache exception: %s", (self.getName, repr(ex)))
                    finally:
                        cacheMaster.lock.release()
                if not caches:
                    time.sleep(10)
                    continue
                if 0: assert isinstance(caches, CoreCaches)             
                   
                cur = self.connection.cursor()
                now = dateAT
                
                dublicated_ips = {}
                ips = []
                cur.connection.commit()
                cur.execute("""SELECT rs.id,rs.account_id, rs.subaccount_id, rs.sessionid,rs.framed_ip_address, rs.speed_string,
                                    lower(rs.framed_protocol) AS access_type,rs.nas_int_id, extract('epoch' from now()-rs.interrim_update) as last_update, rs.date_start,rs.ipinuse_id, rs.caller_id, ((SELECT pool_id FROM billservice_ipinuse WHERE id=rs.ipinuse_id)=(SELECT vpn_guest_ippool_id FROM billservice_tariff WHERE id=get_tarif(rs.account_id)))::boolean as guest_pool, rs.nas_port_id,
                                    rs.speed_change_queued, rs.pod_queued
                                    FROM radius_activesession AS rs WHERE rs.date_end IS NULL AND rs.date_start <= %s and session_status='ACTIVE';""", ( dateAT,))
                rows=cur.fetchall()
                cur.connection.commit()

                for row in rows:
                    try:
                        rs = RadiusSession(*row)
                        result=None
                        nas = caches.nas_cache.by_id.get(rs.nas_id)
                        acc = caches.account_cache.by_account.get(rs.account_id)
                        subacc = caches.subaccount_cache.by_id.get(rs.subaccount_id)
                        if not nas : continue
                        #Если не найден аккаунт или субаккаунт
                        if not (acc and subacc): continue
                        
                        if 0: assert isinstance(nas, NasData); assert isinstance(acc, AccountData)
                        
                        acstatus =  (subacc.allow_vpn_with_null and acc.ballance+acc.credit ==0) or (subacc.allow_vpn_with_minus and acc.ballance+acc.credit<0) or acc.ballance+acc.credit>0\
                                    or \
                                    (subacc.allow_vpn_with_block and (acc.balance_blocked or acc.disabled_by_limit))
                        acstatus_guest = rs.guest_pool
                        
                        if not (acc.account_status==1 and acc.tarif_active==True and caches.timeperiodaccess_cache.in_period.get(acc.tarif_id)):
                            ##dont check next if account disabled
                            acstatus=False
                        elif acstatus and acstatus_guest:
                            acstatus=False
                        elif not acstatus and acstatus_guest:
                            acstatus=True
                        #acstatus = acstatus and not (acstatus_guest and not acstatus) #and not  (((subacc.allow_vpn_with_null and acc.ballance+acc.credit ==0) or (subacc.allow_vpn_with_minus and acc.ballance+acc.credit<=0) or acc.ballance+acc.credit>0)\
                                    #and \
                                    #(subacc.allow_vpn_with_block or (not subacc.allow_vpn_with_block and not acc.balance_blocked and not acc.disabled_by_limit)))

                        if rs.framed_ip_address not in dublicated_ips:
                            dublicated_ips[rs.framed_ip_address]=[]
                        dublicated_ips[rs.framed_ip_address].append(rs)
                        
                        if acstatus and not rs.speed_change_queued: # caches.timeperiodaccess_cache.in_period.get(acc.tarif_id) - not need
                            #chech whether speed has changed
                            account_limit_speed = caches.speedlimit_cache.by_account_id.get(acc.account_id, [])
                            
                            accservices = []
                            addonservicespeed=[]  
                            br = False
                            if subacc:
                                accservices = caches.accountaddonservice_cache.by_subaccount.get(subacc.id, [])    
                                for accservice in accservices:                                 
                                    service = caches.addonservice_cache.by_id.get(accservice.service_id)           
                                    for pnode in caches.timeperiodnode_cache.by_id.get(service.timeperiod_id, []):                     
                                        if not accservice.deactivated  and service.change_speed and fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, now)[3]:                                                                        
                                            addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.min_tx, service.min_rx, service.priority, service.speed_units, service.change_speed_type)                                    
                                            br = True
                                            break   
                                    if br: break
                                    
                            br = False
                            if not addonservicespeed: 
                                accservices = caches.accountaddonservice_cache.by_account.get(acc.account_id, [])    
                                for accservice in accservices:                                 
                                    service = caches.addonservice_cache.by_id.get(accservice.service_id)          
                                    for pnode in caches.timeperiodnode_cache.by_id.get(service.timeperiod_id, []):
                                        if not accservice.deactivated  and service.change_speed and fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, now)[3]:                                                                        
                                            addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.min_tx, service.min_rx, service.priority, service.speed_units, service.change_speed_type)                                    
                                            br = True
                                            break    
                                        if br: break

                            defspeed = caches.defspeed_cache.by_id.get(acc.tarif_id)
                            speeds = caches.speed_cache.by_id.get(acc.tarif_id, [])
                            logger.debug("%s: account=%s sessionid=%s defspeed=%s speeds=%s speedlimit=%s addonservicespeed=%s vpn_speed=%s ", (self.getName(), acc.account_id, str(rs.sessionid), repr(defspeed), repr(speeds), repr(account_limit_speed), repr(addonservicespeed), subacc.vpn_speed))
                            speed = create_speed(defspeed, speeds,account_limit_speed, addonservicespeed, subacc.vpn_speed, dateAT, fMem)                            
                            
                            speed = get_decimals_speeds(speed)
                            logger.debug("%s: account=%s sessionid=%s total_speed=%s", (self.getName(), acc.account_id, str(rs.sessionid), repr(speed) ))
                            newspeed = ''.join([unicode(spi) for spi in speed])

                            if rs.speed_string != newspeed:                         
                                logger.debug("%s:send request for change speed for: account:  %s| nas: %s | sessionid: %s", (self.getName(), acc.account_id, nas.id, str(rs.sessionid)))
                                cur.execute("""UPDATE radius_activesession SET speed_string=%s, speed_change_queued=now() WHERE id=%s and nas_int_id=%s and nas_port_id=%s;
                                            """ , (newspeed, rs.id, rs.nas_id, rs.nas_port_id))   
                                change_speed.delay(account=acc._asdict(), subacc=subacc._asdict(), nas=nas._asdict(), 
                                                    access_type=str(rs.access_type),
                                                    format_string=str(nas.vpn_speed_action),session_id=str(rs.sessionid), vpn_ip_address=rs.framed_ip_address,
                                                    speed=speed, cb=tasks.update_vpn_speed_state.s(nas_id=rs.nas_id, nas_port_id=rs.nas_port_id, session_id=rs.id, newspeed=newspeed))

                                cur.connection.commit()
                                logger.debug("%s: speed change over: account:  %s| nas: %s | sessionid: %s", (self.getName(), acc.account_id, nas.id, str(rs.sessionid)))
                        elif not rs.pod_queued and not acstatus:
                            logger.debug("%s: Send POD: account:  %s| subacc: %s| nas: %s | sessionid: %s", (self.getName(), acc, subacc, nas.id, str(rs.sessionid)))
                            
                            
                            cur.execute("""UPDATE radius_activesession SET pod_queued=now() WHERE id=%s and nas_int_id=%s and nas_port_id=%s;
                                        """ , ( rs.id, rs.nas_id, rs.nas_port_id))
                            PoD.delay(acc._asdict(), subacc._asdict(), nas._asdict(), access_type=rs.access_type, session_id=str(rs.sessionid), vpn_ip_address=rs.framed_ip_address, nas_port_id=rs.nas_port_id, caller_id=str(rs.caller_id), format_string=str(nas.reset_action), cb=tasks.update_pod_state.s(nas_id=rs.nas_id, nas_port_id=rs.nas_port_id, session_id=rs.id))
                            cur.connection.commit()
                            logger.debug("%s: POD sended: account:  %s| nas: %s | sessionid: %s", (self.getName(), acc.account_id, nas.id, str(rs.sessionid)))
                            continue


                            
                        
                        from_start = (dateAT-rs.date_start).seconds+(dateAT-rs.date_start).days*86400
                            
                        if (rs.time_from_last_update and rs.time_from_last_update+15>=nas.acct_interim_interval*3+3) or (not rs.time_from_last_update and from_start>=nas.acct_interim_interval*3+3):
                            cur.execute("""UPDATE radius_activesession SET session_status='ACK' WHERE id=%s;
                                        """, (rs.id,))

                        cur.connection.commit()               
                    
                    except Exception, ex:
                        logger.error("%s: row exec exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                        if isinstance(ex, vars.db_errors): raise ex
                #cur.execute("UPDATE billservice_ipinuse SET disabled=now() WHERE dynamic=True and disabled is Null and ip::inet not in (SELECT DISTINCT framed_ip_address::inet FROM radius_activesession WHERE ipinuse_id is not NUll and (session_status='ACTIVE'));")    
                #cur.connection.commit()   
                
                #===============================================================
                # for key, value in dublicated_ips.iteritems():
                #    if len(value)<=1: continue
                #    logger.debug("%s: Dublicated IP detected %s %s", (self.getName(), key, value))
                #    value = sorted(value, key=attrgetter('date_start'))
                #    first = True
                #    for rs in value:
                #        if first == True:
                #            first = False
                #            continue
                #        logger.debug("%s: Send dublicates remove POD: account:  %s| nas: %s | sessionid: %s", (self.getName(), acc.account_id, nas.id, str(rs.sessionid)))
                #        PoD.delay(acc._asdict(), subacc._asdict(), nas._asdict(), access_type=rs.access_type, session_id=str(rs.sessionid), vpn_ip_address=rs.framed_ip_address, caller_id=str(rs.caller_id), format_string=str(nas.reset_action))
                #        logger.debug("%s: dublicates remove POD sended: account:  %s| nas: %s | sessionid: %s", (self.getName(), acc.account_id, nas.id, str(rs.sessionid)))
                #===============================================================

                cur.close()
                logger.info("VPNALIVE: VPN thread run time: %s", time.time() - a)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                self.connection.rollback()
                if ex.__class__ in vars.db_errors:
                    
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)
            time.sleep(vars.VPN_SLEEP + random.randint(0,5))

    def run(self):
        #self.remove_sessions()
        self.check_access()

class periodical_service_bill(Thread):
    """
    Процесс будет производить снятие денег у клиентов, у которых в ТП
    указан список периодических услуг.
    Нужно учесть что:
    1. Снятие может производиться в начале расчётного периода.
    Т.к. мы не можем производить проверку каждую секунду - нужно держать список снятий
    , чтобы проверять с какого времени мы уже не делали снятий и произвести их.
    2. Снятие может производиться в конце расчётного периода.
    ситуация аналогичная первой

    """
    def __init__ (self):
        Thread.__init__(self)
        self.PER_DAY = 1
        self.PER_DAY_DELTA = 1
        self.NOW = datetime.datetime(2000, 1, 1)

    #ps_type - 1 for periodocal service, 2 - for periodical addonservice 
            
    def iterate_ps(self, cur, acc, ps, dateAT, acctf_id, acctf_datetime, next_date, current, pss_type):
        account_ballance = (acc.ballance or 0) + (acc.credit or 0)
        susp_per_mlt = 1
        
        if pss_type == PERIOD:

            time_start_ps = acctf_datetime if ps.autostart else ps.time_start #Возможно баг. проверить на дату создания услуи и начало тарифного плана
            
            #Если в расчётном периоде указана длина в секундах-использовать её, иначе использовать предопределённые константы

            get_last_checkout_ = get_last_checkout
        elif pss_type == ADDON:
            if ps.temporary_blocked:
                susp_per_mlt = 0
            time_start_ps = ps.created
            get_last_checkout_ = get_last_addon_checkout
        else:
            return
        
        lc = get_last_checkout_(cur, ps.ps_id, acctf_id)  
        
        if lc is None and pss_type == PERIOD:
            last_checkout = ps.created if ps.created  and ps.created<acctf_datetime else acctf_datetime
            first_time = True
            logger.debug('%s: Periodical Service:  last checkout is None set last checkout=%s for account: %s service:%s type:%s', (self.getName(), last_checkout, acc.account_id, ps.ps_id, pss_type))
        elif lc is None and pss_type == ADDON:
            last_checkout = ps.created
            first_time = True
            logger.debug('%s: Addon Service:  last checkout is None set last checkout=%s for account: %s service:%s type:%s', (self.getName(), last_checkout, acc.account_id, ps.ps_id, pss_type))
        else:
            first_time = False
            last_checkout = lc
        
        #Расчитываем параметры расчётного периода на момент окончания тарифного плана или сейчас
        period_start, period_end, delta = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, dateAT)           
        # Проверка на расчётный период без повторения
        #if period_end < dateAT: return

            
        if ps.cash_method == "GRADUAL":

            logger.debug('%s: Periodical Service: GRADUAL last checkout %s for account: %s service:%s type:%s next date: %s', (self.getName(), last_checkout, acc.account_id, ps.ps_id, pss_type, next_date))                                  

            PER_DAY = SECONDS_PER_DAY / (ps.tpd if ps.tpd else vars.TRANSACTIONS_PER_DAY)
            PER_DAY_DELTA = datetime.timedelta(seconds=PER_DAY)
                
            if (dateAT - last_checkout).seconds + (dateAT - last_checkout).days*SECONDS_PER_DAY >= PER_DAY:
                #Проверяем наступил ли новый период
                
                # Смотрим сколько раз уже должны были снять деньги
                delta_from_last_checkout = dateAT - last_checkout
                last_checkout_seconds = delta_from_last_checkout.seconds + delta_from_last_checkout.days*SECONDS_PER_DAY
                nums,ost = divmod(last_checkout_seconds,PER_DAY)                                        
                chk_date = last_checkout + PER_DAY_DELTA

                #Добавить проверку на окончание периода
                #Смотрим на какую сумму должны были снять денег и снимаем её
                while chk_date <= dateAT:    
                    if chk_date >self.NOW:
                        logger.info('%s: Periodical Service: GRADUAL %s Can not bill future ps account: %s chk_date: %s', (self.getName(), ps.ps_id,  acc.account_id, chk_date))
                        return 
                    delta_coef = Decimal('1.00')
                    if pss_type == PERIOD and vars.USE_COEFF_FOR_PS==True and next_date and chk_date+PER_DAY_DELTA>next_date:# если следующая проверка будет в новом расчётном периоде - считаем дельту
                        
                        delta_coef=Decimal(str(float((next_date-chk_date).days*86400+(next_date-chk_date).seconds)/float(PER_DAY)))
                        logger.debug('%s: Periodical Service: %s Use coeff %s for ps account: %s', (self.getName(), ps.ps_id, delta_coef, acc.account_id))      
                        
                    logger.debug('%s: Periodical Service: GRADUAL  account: %s service:%s type:%s check date: %s next date: %s', (self.getName(), acc.account_id, ps.ps_id, pss_type, chk_date, next_date,))
                    period_start, period_end, delta = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)     
                    mult = 0 if check_in_suspended(cur, acc.account_id, chk_date)==True else 1 #Если на момент списания был в блоке - списать 0                                       
                    cash_summ = delta_coef*(mult*((PER_DAY * vars.TRANSACTIONS_PER_DAY * ps.cost) / (delta * vars.TRANSACTIONS_PER_DAY)))
                    if pss_type == PERIOD and (ps.deactivated is None or (ps.deactivated and ps.deactivated > chk_date)):
                        # Если это подключаемая услуга и дата отключения услуги ещё не наступила
                        #cur.execute("UPDATE billservice_account SET ballance=ballance-")

                        cur.execute("""SELECT 
                                        periodicaltr_fn(%s,%s,%s, %s::numeric, 
                                                        %s::character varying, 
                                                        %s::numeric, 
                                                        %s::timestamp without time zone, 
                                                        %s::timestamp without time zone,
                                                        %s::timestamp without time zone,  
                                                        %s, 
                                                        %s::numeric,
                                                        %s::boolean
                                                        ) as new_summ;""", (ps.ps_id, 
                                                                                           acctf_id, 
                                                                                           acc.account_id, 
                                                                                           acc.credit,  
                                                                                           'PS_GRADUAL', 
                                                                                           cash_summ, 
                                                                                           chk_date, 
                                                                                           chk_date, 
                                                                                           chk_date+PER_DAY_DELTA,
                                                                                           ps.condition, 
                                                                                           ps.condition_summ,
                                                                                           ps.delta_from_ballance
                                                                                           )
                                    )

                        cash_summ=cur.fetchone()[0]
                        cur.connection.commit()
                        #cur.execute("UPDATE billservice_account SET ballance=ballance-%s WHERE id=%s;", (new_summ, acc.account_id,))
                        
                        logger.debug('%s: Periodical Service: GRADUAL BATCH iter checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))                            
                    elif pss_type == ADDON:
                        cash_summ = Decimal(str(cash_summ)) * susp_per_mlt
                        addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_GRADUAL', cash_summ, chk_date)
                        cur.connection.commit()
                        logger.debug('%s: Addon Service Checkout thread: GRADUAL BATCH iter checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))
                        
                    else:
                        return
                    cur.connection.commit()
                    chk_date += PER_DAY_DELTA
                    if pss_type == PERIOD and ((next_date and chk_date>=next_date) or (ps.deactivated and ps.deactivated < chk_date)):
                        logger.debug('%s: Periodical Service: GRADUAL last billed is True for account: %s service:%s type:%s', (self.getName(), acc.account_id, ps.ps_id, pss_type))  
                        cur.execute("UPDATE billservice_periodicalservicelog SET last_billed=True WHERE service_id=%s and accounttarif_id=%s", (ps.ps_id, acctf_id))
                        cur.connection.commit()
                        return
                cur.connection.commit()
            
        if ps.cash_method == "AT_START":
            """
            Смотрим когда в последний раз платили по услуге. Если в текущем расчётном периоде
            не платили-производим снятие.
            """
            
            """
            Списывать в начале периода только, если последнее списание+период<следующего тарифного плана
            """

            
            summ = 0
            if first_time==True:
                period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, last_checkout)
                
            while first_time==True or last_checkout <= period_start:

                
                if first_time==False:
                    period_start_ast, last_checkout, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, last_checkout)
                
                
                chk_date = last_checkout
                if chk_date >self.NOW:
                    logger.debug('%s: Periodical Service: AT_START %s Can not bill future ps account: %s chk_date: %s', (self.getName(), ps.ps_id,  acc.account_id, chk_date))
                    return 
                if ps.created and ps.created >= chk_date and not last_checkout == ps.created:
                    # если указана дата начала перид. услуги и она в будующем - прпускаем её списание
                    return

                logger.debug('%s: Periodical Service: AT_START  account: %s service:%s type:%s check date: %s next date: %s', (self.getName(), acc.account_id, ps.ps_id, pss_type, chk_date, next_date,))
                
                                    

                #Если следующее списание произойдёт уже на новом тарифе - отмечаем, что тарификация произведена
                if  pss_type == PERIOD and ((next_date and chk_date>=next_date) or (ps.deactivated and ps.deactivated < chk_date)):
                    logger.debug('%s: Periodical Service: AT_START last billed is True for account: %s service:%s type:%s next date: %s', (self.getName(), acc.account_id, ps.ps_id, pss_type, next_date))  
                    cur.execute("UPDATE billservice_periodicalservicelog SET last_billed=True WHERE service_id=%s and accounttarif_id=%s", (ps.ps_id, acctf_id))
                    cur.connection.commit()
                    return

                mult = 0 if check_in_suspended(cur, acc.account_id, chk_date)==True else 1 #Если на момент списания был в блоке - списать 0
                cash_summ = mult*ps.cost # Установить сумму равной нулю, если пользователь в блокировке
                
                #if first_time == False:
                #    period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)
                #    chk_date =  chk_date+datetime.timedelta(seconds=delta_ast)

                delta_coef=1
                if pss_type == PERIOD and vars.USE_COEFF_FOR_PS==True and first_time and ((last_checkout-acctf_datetime).days*86400+(last_checkout-acctf_datetime).seconds)<delta_ast:
                    logger.warning('%s: Periodical Service: %s Use coeff for ps account: %s', (self.getName(), ps.ps_id, acc.account_id))
                    delta_coef=float((period_end_ast-acctf_datetime).days*86400+(period_end_ast-acctf_datetime).seconds)/float(delta_ast)        
                    cash_summ=Decimal(str(cash_summ))*Decimal(str(delta_coef))

                if pss_type == PERIOD and (ps.deactivated is None or (ps.deactivated and ps.deactivated > chk_date)):
                    _, ps_end_for_delta, _ = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)
                    #cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::numeric, %s::character varying, %s::numeric, %s::timestamp without time zone, %s, %s::numeric) as new_summ;", (ps.ps_id, acctf_id, acc.account_id, acc.credit,  'PS_AT_START', cash_summ, chk_date, ps.condition, ps.condition_summ))
                    cur.execute("""SELECT 
                                    periodicaltr_fn(%s,%s,%s, %s::numeric, 
                                                    %s::character varying, 
                                                    %s::numeric, 
                                                    %s::timestamp without time zone, 
                                                    %s::timestamp without time zone,
                                                    %s::timestamp without time zone,  
                                                    %s, 
                                                    %s::numeric,
                                                    %s::boolean
                                                    ) as new_summ;""", (ps.ps_id, 
                                                                                       acctf_id, 
                                                                                       acc.account_id, 
                                                                                       acc.credit,  
                                                                                       'PS_AT_START', 
                                                                                       cash_summ, 
                                                                                       chk_date, 
                                                                                       chk_date,
                                                                                       ps_end_for_delta,
                                                                                       ps.condition, 
                                                                                       ps.condition_summ,
                                                                                       ps.delta_from_ballance
                                                                                       )
                                )
                        
                    cash_summ=cur.fetchone()[0]
                    #cur.execute("UPDATE billservice_account SET ballance=ballance-%s WHERE id=%s;", (new_summ, acc.account_id,))
                    logger.debug('%s: Periodical Service: AT START iter checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))
                    pass
                elif pss_type == ADDON:
                    cash_summ = Decimal(str(cash_summ)) * susp_per_mlt
                    addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_AT_START', cash_summ, chk_date)
                    logger.debug('%s: Addon Service Checkout thread: AT START checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))                        
                cur.connection.commit()
                first_time=False
                    
            cur.connection.commit()
        if ps.cash_method=="AT_END":
            """
            Смотрим завершился ли хотя бы один расчётный период.
            Если завершился - считаем сколько уже их завершилось.    
            для остальных со статусом False
            """

            # Здесь нужно проверить сколько раз прошёл расчётный период    
            # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
            # Для последней проводки ставим статус Approved=True
            # для всех остальных False
            # Если дата начала периода больше последнего снятия или снятий не было и наступил новый период - делаем проводки
            
            #second_ = datetime.timedelta(seconds=1)
            cash_summ = 0
            if first_time or period_start > last_checkout:
                cash_summ = ps.cost
                chk_date = last_checkout
                
                while True:
                    period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)
                    
                    prev_period_start_ast, _, _ = fMem.settlement_period_(time_start_ps, 
                                                                          ps.length_in, 
                                                                          ps.length, 
                                                                          chk_date-datetime.timedelta(seconds=1)
                                                                          )
                    if first_time==False:
                        
                        chk_date = period_end_ast
                    logger.debug('%s: Periodical Service: AT_END  account: %s service:%s type:%s check date: %s next date: %s', (self.getName(), acc.account_id, ps.ps_id, pss_type, chk_date, next_date,))

                    mult = 0 if check_in_suspended(cur, acc.account_id, chk_date)==True else 1 #Если на момент списания был в блоке - списать 0
                    cash_summ = mult*ps.cost
                    
                    if chk_date >self.NOW:
                        logger.error('%s: Periodical Service: AT_END %s Can not bill future ps account: %s chk_date: %s new period start: %s', (self.getName(), ps.ps_id,  acc.account_id, chk_date, period_start_ast))
                        break

                    if period_start_ast>period_start: break
                    s_delta_ast = datetime.timedelta(seconds=delta_ast)
                    if pss_type == PERIOD and vars.USE_COEFF_FOR_PS==True and first_time and ((chk_date-acctf_datetime).days*86400+(chk_date-acctf_datetime).seconds)<delta_ast:
                        logger.debug('%s: Periodical Service: %s Use coeff for ps account: %s', (self.getName(), ps.ps_id, acc.account_id))
                        delta_coef=float((chk_date-acctf_datetime).days*86400+(chk_date-acctf_datetime).seconds)/float(delta_ast)        
                        cash_summ=Decimal(str(cash_summ))*Decimal(str(delta_coef))
                        
                    if first_time:
                        first_time = False
                        chk_date = last_checkout
                        tr_date = period_start_ast
                        if pss_type == PERIOD:
                            cash_summ = 0
                            #ps_history(cur, ps.ps_id, acc.acctf_id, acc.account_id, 'PS_AT_END', ZERO_SUM, tr_date)
                            cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::numeric, %s::character varying, %s::numeric, %s::timestamp without time zone, %s, %s::numeric) as new_summ;", (ps.ps_id, acctf_id, acc.account_id, acc.credit,  'PS_AT_END', cash_summ, tr_date, ps.condition, ps.condition_summ))
                            logger.debug('%s: Periodical Service: AT END First time checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))
#                            cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s);", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_GRADUAL', cash_summ, chk_date, ps.condition))
                        elif pss_type == ADDON:
                            addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_AT_END', ZERO_SUM, tr_date)
                            logger.debug('%s: Addon Service Checkout: AT END First time checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))
                        cur.connection.commit()
                        return
                    else:
                        if ps.created and ps.created >= chk_date and not last_checkout == ps.created:
                            # если указана дата начала перид. услуги и она в будующем - прпускаем её списание
                            return
                        
                            
                        if pss_type == PERIOD and (ps.deactivated is None or (ps.deactivated and ps.deactivated > chk_date)):
                            tr_date = chk_date
                            if (next_date and chk_date>=next_date) or (ps.deactivated and ps.deactivated < chk_date):
                                logger.debug('%s: Periodical Service: AT_END last billed is True for account: %s service:%s type:%s', (self.getName(), acc.account_id, ps.ps_id, pss_type))  
                                cur.execute("UPDATE billservice_periodicalservicelog SET last_billed=True WHERE service_id=%s and accounttarif_id=%s", (ps.ps_id, acctf_id))
                                cur.connection.commit()
                                return
                            #cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::numeric, %s::character varying, %s::numeric, %s::timestamp without time zone, %s, %s::numeric) as new_summ;", (ps.ps_id, acctf_id, acc.account_id, acc.credit,  'PS_AT_END', cash_summ, tr_date, ps.condition, ps.condition_summ))
                            
                            cur.execute("""SELECT 
                                            periodicaltr_fn(%s,%s,%s, %s::numeric, 
                                                            %s::character varying, 
                                                            %s::numeric, 
                                                            %s::timestamp without time zone, 
                                                            %s::timestamp without time zone,
                                                            %s::timestamp without time zone,  
                                                            %s, 
                                                            %s::numeric,
                                                            %s::boolean
                                                            ) as new_summ;""", (ps.ps_id, 
                                                                                               acctf_id, 
                                                                                               acc.account_id, 
                                                                                               acc.credit,  
                                                                                               'PS_AT_END', 
                                                                                               cash_summ, 
                                                                                               tr_date, 
                                                                                               prev_period_start_ast,
                                                                                               tr_date,
                                                                                               ps.condition, 
                                                                                               ps.condition_summ,
                                                                                               ps.delta_from_ballance
                                                                                               )
                                        )
                    
                            cash_summ=cur.fetchone()[0]
                            #cur.execute("UPDATE billservice_account SET ballance=ballance-%s WHERE id=%s;", (new_summ, acc.account_id,))
                            logger.debug('%s: Periodical Service: AT END iter checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))
                        elif pss_type == ADDON:
                            cash_summ = Decimal(str(cash_summ)) * susp_per_mlt
                            tr_date = chk_date
                            if ps.deactivated and ps.deactivated < chk_date:
                                #сделать расчёт остатка - сейчас эта штука компенсируется штрафами за досрочное отключение
                                cash_summ = 0
                                tr_date = ps.deactivated
                            addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_AT_END', cash_summ, tr_date)
                            logger.debug('%s: Addon Service Checkout thread: AT END checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))
                        else:
                            return
                    cur.connection.commit()
                    chk_date = period_end_ast
                    if chk_date-SECOND > period_start: break
            #cur.connection.commit()
            
        if pss_type == ADDON and ps.deactivated and dateAT >= ps.deactivated:
            cur.execute("UPDATE billservice_accountaddonservice SET last_checkout = deactivated WHERE id=%s", (ps.ps_id,))
            cur.connection.commit()
        #if pss_type == ZERO_SUM and ps.deactivated and dateAT >= ps.deactivated:
        #    cur.execute("UPDATE billservice_periodicalservice SET deleted = True WHERE id=%s;", (ps.ps_id,))

            #cur.connection.commit()
    

            
    def run(self):
        global cacheMaster, fMem, suicideCondition, transaction_number, vars
        self.connection = get_connection(vars.db_dsn)
        
        self.connection.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        while True:
            a_ = time.time()
            try:
                if suicideCondition[self.__class__.__name__]: break
                a = time.time()

                if cacheMaster.date <= dateAT:
                    time.sleep(10); continue
                else:
                    cacheMaster.lock.acquire()
                    try:
                        caches = cacheMaster.cache
                        dateAT = deepcopy(cacheMaster.date)
                    except Exception, ex:
                        logger.error("%s: cache exception: %s", (self.getName, repr(ex)))
                    finally:
                        cacheMaster.lock.release()                
                if 0: assert isinstance(caches, CoreCaches)

                cur = self.connection.cursor()
                #transactions per day              
                #n = SECONDS_PER_DAY / vars.TRANSACTIONS_PER_DAY
                #n_delta = datetime.timedelta(seconds=n)
                #now = dateAT
                

                self.NOW = dateAT
                #get a list of tarifs with periodical services & loop                

                for acc_id in caches.account_cache.by_account:
                    
                    acc =  caches.account_cache.by_account.get(acc_id)
                    if acc.account_status in [3, 4, 5,  '3', '4', '5']: continue
                    if acc_id == 6050:
                        pass
                    
                    if 0: assert isinstance(acc, AccountData)
                    acctf_raw_history = get_acctf_history(cur, acc.account_id)
                    by_id = {}
                    #Получаем историю смены субаккаунтов по которым не производились списания период. услуг
                    #Начальная индексация

                    for acctf_id, acctf_datetime, next_acctf_id, next_date, acc_tarif_id in acctf_raw_history:


                        for ps in caches.periodicalsettlement_cache.by_id.get(acc_tarif_id,[]):
                            
                            try:
                                current = True if next_acctf_id is None else False
                                
                                
                                dt = next_date if next_date else self.NOW
                                #logger.info("%s : preiter: acctf=%s now=%s dateat=%s current=%s next_date=%s", (self.getName(), acctf_id, self.NOW, dateAT, current, next_date))
                                self.iterate_ps(cur, acc, ps, dt, acctf_id, acctf_datetime, next_date, current, PERIOD)
                            
                            except Exception, ex:
                                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                                if ex.__class__ in vars.db_errors: raise ex
                    cur.connection.commit()
                cur.connection.commit()

                for addon_ps in caches.addonperiodical_cache.data:
                    if 0: assert isinstance(addon_ps, AddonPeriodicalData)
                    if not (addon_ps.account_id or addon_ps.subaccount_id): 
                        logger.error("Accountaddonservice %s has no account and subaccount", (addon_ps.ps_id))
                        continue
                    
                    subacc = caches.subaccount_cache.by_id.get(addon_ps.subaccount_id)
                    if subacc:
                        acc = caches.account_cache.by_account.get(subacc.account_id)
                    else:
                        acc = caches.account_cache.by_account.get(addon_ps.account_id)
                    if not acc:
                        logger.warning('%s: Addon Periodical Service: %s. Incostistent database ERROR. Account not found: %s', (self.getName(), addon_ps.ps_id, addon_ps.account_id))
                        continue
                    dt = dateAT if not addon_ps.deactivated else addon_ps.deactivated
                    try:
                        #self.iterate_ps(cur, caches, acc, addon_ps, mult, dateAT, ADDON)
                        #cur, acc, ps, dateAT, acctf_id, acctf_datetime, next_date, current, pss_type
                        self.iterate_ps(cur, acc, addon_ps, dt, None, addon_ps.created,  None, False, ADDON)
                    except Exception, ex:
                        logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                        if ex.__class__ in vars.db_errors: raise ex
                    cur.connection.commit()


                cur.close()
                logger.info("PSALIVE: Period. service thread run time: %s", time.time() - a)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                self.connection.rollback()
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(abs(vars.PERIODICAL_SLEEP-(time.time()-a_)) + random.randint(0,5))
            

class RadiusAccessBill(Thread):
    """
    Услуга применима только для VPN доступа, когда точно известна дата авторизации
    и дата отключения пользователя
    """
    def __init__(self):
        Thread.__init__(self)

    def get_actual_cost(self, date):
        pass

    def get_actual_prices(self, radtrafficnodes):
        
        for period in radtrafficnodes:
            if period.value!=0:
                return True
        return False
    
    def valued_prices(self, value, radtrafficnodes):
        d = {}

        for x in radtrafficnodes:
            d[value]=x

        keys = d.keys()
        keys.sort()
        keys.append(sys.maxint)
        #d=map(adict.get, keys)
        res=[]
        i=0
        l=len(keys)
        #перебираем все ноды по объёму. Оставляем только подходящие
        for x in keys:
            if value/(1024*1024)>=x and value/(1024*1024)<=keys[i+1]: 
                res.append(d[x]) 
            i+=1
            if l==i: break
        return res
        
    def run(self):
        """
        По каждой записи делаем транзакции для пользователя в соотв с его текущим тарифным планов
        """
        #connection = pool.connection()
        #connection._con._con.set_client_encoding('UTF8')
        global fMem, suicideCondition, cacheMaster, vars
        self.connection = get_connection(vars.db_dsn)
        self.connection.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        accounts_bytes_cache={} # account_id: date_start_date_end, bytes_in, bytes_out
        while True:
            try:
                if suicideCondition[self.__class__.__name__]:
                    try: self.connection.close()
                    except: pass
                    break
                a = time.time()
                if cacheMaster.date <= dateAT:
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

                if 0: assert isinstance(caches, CoreCaches)
                
                cur = self.connection.cursor()
                cur.execute("""SELECT rs.id, rs.account_id, rs.sessionid, rs.session_time, rs.bytes_in, rs.bytes_out, rs.interrim_update, rs.date_start, rs.date_end, acc_t.id, rs.lt_time, rs.lt_bytes_in, rs.lt_bytes_out,rs.nas_port_id,rs.nas_int_id  
                                 FROM radius_activesession AS rs
                                 LEFT JOIN billservice_accounttarif AS acc_t ON acc_t.id=(SELECT id FROM billservice_accounttarif WHERE account_id=rs.account_id and datetime<rs.date_start ORDER BY datetime DESC LIMIT 1) 
                                 WHERE (rs.need_traffic_co=True or rs.need_time_co=True) and ((rs.lt_time<rs.session_time) or (rs.lt_bytes_in<rs.bytes_in or rs.lt_bytes_out<rs.bytes_out))
                                  ORDER BY rs.interrim_update ASC LIMIT 20000;""")
                rows=cur.fetchall()
                cur.connection.commit()

                acctfs = []
                for r in rows:
                    if r[9]:
                        acctfs.append(str(r[9]))
                data=[]
                if acctfs:
                    cur.execute("""
                        select acct.id, t.radius_traffic_transmit_service_id, t.time_access_service_id FROM billservice_accounttarif as acct
                        JOIN billservice_tariff as t ON t.id=acct.tarif_id
                        WHERE t.radius_traffic_transmit_service_id is not NULL or t.time_access_service_id is not NULL and acct.id in (%s)
                        ;
                    """ % ','.join(acctfs) )
                    data = cur.fetchall()
                    cur.connection.commit()
                
                acctf_cache = {}
                for acct_id, radius_traffic_transmit_service_id, time_access_service_id in data:
                    acctf_cache[acct_id] = (radius_traffic_transmit_service_id, time_access_service_id)
                now = dateAT
                for row in rows:
                    rs = BillSession(*row)
                    radius_traffic_transmit_service_id, time_access_service_id = acctf_cache.get(rs.acctf_id, (None, None))
                    checkouted=False
                    #1. Ищем последнюю запись по которой была произведена оплата
                    #2. Получаем данные из услуги "Доступ по времени" из текущего ТП пользователя
                    #TODO:2. Проверяем сколько стоил трафик в начале сессии и не было ли смены периода.
                    #TODO:2.1 Если была смена периода -посчитать сколько времени прошло до смены и после смены,
                    # рассчитав соотв снятия.
                    #2.2 Если снятия не было-снять столько, на сколько насидел пользователь
                    #rs_id,  account_id, session_id, session_time, interrim_update, ps_id, tarif_id, accountt_tarif_id = row
                    logger.debug("RADCOTHREAD: Checking session: %s", repr(rs))
                    acc = caches.account_cache.by_account.get(rs.account_id)
                    #if acc.radius_traffic_transmit_service_id:continue
                    if acc and time_access_service_id:
                        logger.debug("RADCOTHREAD: Time tarification session: %s", rs.sessionid)
                        old_time = rs.lt_time or 0
                        logger.debug("RADCOTHREAD: Old session time: %s %s", (rs.sessionid, old_time))
    #                    old_time = old_time[0] if old_time else 0
                        
                        total_time = rs.session_time - old_time
                        logger.debug("RADCOTHREAD: Tarification time for session: %s %s", (rs.sessionid, total_time))
                        if rs.date_end:
                            taccs_service = caches.timeaccessservice_cache.by_id.get(time_access_service_id)
                            logger.debug("RADCOTHREAD: Tarification time of end session : %s", (rs.sessionid, ))
                            if taccs_service.rounding:
                                logger.debug("RADCOTHREAD: Rounding session time : %s", (rs.sessionid, ))
                                if taccs_service.tarification_step>0:
                                    total_time = divmod(total_time, taccs_service.tarification_step)[1]*taccs_service.tarification_step+taccs_service.tarification_step
                        logger.debug("RADCOTHREAD: Searching for prepaid time for session : %s", (rs.sessionid, ))
                        cur.execute("""SELECT id, size FROM billservice_accountprepaystime WHERE account_tarif_id=%s and prepaid_time_service_id=%s and current=True""", (rs.acctf_id,time_access_service_id,))
                        result = cur.fetchone()
                        cur.connection.commit()
                        prepaid_id, prepaid = result if result else (0, -1)
                        if prepaid > 0:
                            logger.debug("RADCOTHREAD: Prepaid time for session : %s %s", (rs.sessionid, prepaid))
                            if prepaid >= total_time:
                                total_time, prepaid = 0, prepaid - total_time
                            elif total_time >= prepaid:
                                total_time, prepaid = total_time - prepaid, 0
                            cur.execute("""UPDATE billservice_accountprepaystime SET size=%s WHERE id=%s""", (prepaid, prepaid_id,))
                            cur.connection.commit()
                        #get the list of time periods and their cost
                        logger.debug("RADCOTHREAD: Searching for time tarification node for session : %s", (rs.sessionid, ))
                        for period in caches.timeaccessnode_cache.by_id.get(time_access_service_id, []):
                            if 0: assert isinstance(period, TimeAccessNodeData)
                            #get period nodes and check them
                            for pnode in caches.timeperiodnode_cache.by_id.get(period.time_period_id, []):
                                if 0: assert isinstance(pnode, TimePeriodNodeData)
                                if fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, dateAT)[3]:
                                    logger.debug("RADCOTHREAD: Time tarification node for session %s was found", (rs.sessionid, ))
                                    summ = (total_time * period.cost) / Decimal("60")
                                    logger.debug("RADCOTHREAD: Summ for checkout for session %s %s", (rs.sessionid, summ))
                                    if summ > 0:
                                        #timetransaction(cur, rs.taccs_id, rs.acctf_id, rs.account_id, rs.id, summ, now)
                                        db.timetransaction_fn(cur, time_access_service_id, rs.acctf_id, rs.account_id, summ, now, unicode(rs.sessionid), rs.interrim_update)
                                        cur.connection.commit()
                                        logger.debug("RADCOTHREAD: Time for session %s was checkouted", (rs.sessionid, ))
                                    break

                        logger.debug("RADCOTHREAD: Session %s was checkouted (Time)", (rs.sessionid, ))

                    #
                    if acc and radius_traffic_transmit_service_id:  
                        logger.debug("RADCOTHREAD: Traffic tarification session: %s", rs.sessionid)
                        radius_traffic = caches.radius_traffic_transmit_service_cache.by_id.get(radius_traffic_transmit_service_id)
                        lt_bytes_in = rs.lt_bytes_in or 0
                        lt_bytes_out = rs.lt_bytes_out or 0
                        logger.debug("RADCOTHREAD: Last bytes in/out for session: %s (%s/%s)", (rs.sessionid, lt_bytes_in,lt_bytes_out))
    #                    old_time = old_time[0] if old_time else 0
                        bytes_in = 0
                        bytes_out = 0
                        total_bytes_value = 0
                        #проверяем есть ли ноды с указанным value
                        """
                        Если есть - получаем данные текущего расчётного периода абонента
                        Получаем значения байт из кэша accounts_bytes_cache для текущего расчётного периода
                        если данные найдены - обновляем значения в кэше приращёнными значениями.
                        Если не найдены - делаем запрос в базу данных и помещаем данные в кэш
                        """
                        if self.get_actual_prices(caches.radius_traffic_node_cache.by_id.get(radius_traffic_transmit_service_id, [])) and acc.settlement_period_id:
                            sp = caches.settlementperiod_cache.by_id.get(acc.settlement_period_id)
                            if 0: assert isinstance(sp, SettlementPeriodData)
                            
                            sp_defstart = acc.datetime if sp.autostart else sp.time_start
                            sp_start, sp_end, delta = fMem.settlement_period_(sp_defstart, sp.length_in, sp.length, dateAT)
                            date_start, date_end, bytes_in, bytes_out = accounts_bytes_cache.get(acc.acctf_id, (None, None, 0,0))
                            if date_start==sp_start and date_end==sp_end:
                                
                                # если в кэше есть данные о трафике для абонента за указанный расчётный период - обновляем кэш свежими значениями
                                bytes_in = bytes_in if bytes_in else 0
                                bytes_out = bytes_out if bytes_out else 0
                                bytes_in, bytes_out = bytes_in+rs.bytes_in-rs.lt_bytes_in, bytes_out+rs.bytes_out-rs.lt_bytes_out
                                logger.debug("RADCOTHREAD: Append traffic bytes to cached values for account %s for session %s (%s/%s)", (rs.account_id, rs.sessionid, bytes_in,bytes_out))
                                accounts_bytes_cache[acc.acctf_id] = (date_start, date_end, bytes_in, bytes_out)
                                #accounts_bytes_cache[acc.acctf_id]['bytes_in']+= rs.bytes_in-rs.lt_bytes_in
                                #accounts_bytes_cache[acc.acctf_id]['bytes_out']+= rs.bytes_out-rs.lt_bytes_out
                            else:    
                                cur.execute("""
                                    SELECT sum(bytes_in) as bytes_in, sum(bytes_out) as bytes_out FROM radius_activesession 
                                    WHERE account_id=%s and (date_start>=%s and interrim_update<=%s) or (date_start>=%s and date_end<=%s);                                
                                    """, (acc.account_id, sp_start, now, sp_start, now))
                                bytes_in, bytes_out = cur.fetchone()
                                bytes_in = bytes_in if bytes_in else 0
                                bytes_out = bytes_out if bytes_out else 0
                                logger.debug("RADCOTHREAD: Selecting bytes info from DB for account %s for session %s (%s/%s)", (rs.account_id, rs.sessionid, bytes_in,bytes_out))
                                accounts_bytes_cache[acc.acctf_id]=(sp_start, sp_end, bytes_in, bytes_out)
                                
                                             
                        #total_time = rs.session_time - old_time
                        [(0, u"Входящий"),(1, u"Исходящий"),(2, u"Вх.+Исх."),(3, u"Большее направление")]
                        if radius_traffic.direction==0:
                            total_bytes=rs.bytes_in-rs.lt_bytes_in
                            total_bytes_value = bytes_in
                        elif radius_traffic.direction==1:
                            total_bytes=rs.bytes_out-rs.lt_bytes_out
                            total_bytes_value = bytes_out
                        elif radius_traffic.direction==2:
                            total_bytes=(rs.bytes_out-rs.lt_bytes_out)+(rs.bytes_in-rs.lt_bytes_in)
                            total_bytes_value = bytes_in+bytes_out
                        elif radius_traffic.direction==3:
                            #Проверка на максимальное направление. Берётся расчётный период из тарифа
                            if acc.radius_traffic_transmit_service_id:
                                if bytes_in>=bytes_out:
                                    total_bytes = (rs.bytes_in-rs.lt_bytes_in)
                                else:
                                    total_bytes = (rs.bytes_out-rs.lt_bytes_out)
                            else:
                                #Если расчётный период не указан - считаем по отношению к началу сессии
                                total_bytes = max(((rs.bytes_in-rs.lt_bytes_in), (rs.bytes_out-rs.lt_bytes_out)))
                            total_bytes_value = max((bytes_in,bytes_out))
                        
                        logger.debug("RADCOTHREAD: Bytes for tarification for session %s %s", ( rs.sessionid, total_bytes))
                        #Если сессия окончена 
                        if rs.date_end:
                            #Если нужно делать округление
                            logger.debug("RADCOTHREAD: Tarification traffic of end session : %s", (rs.sessionid, ))
                            if radius_traffic.rounding==1:
                                logger.debug("RADCOTHREAD: Need traffic rounding of end session : %s", (rs.sessionid, ))
                                if radius_traffic.tarification_step>0:
                                    total_bytes = divmod(total_bytes, radius_traffic.tarification_step*1024)[0]*radius_traffic.tarification_step*1024+radius_traffic.tarification_step*1024
                                    logger.debug("RADCOTHREAD: Bytes for tarification for session %s after rounding %s", ( rs.sessionid, total_bytes))
                        logger.debug("RADCOTHREAD: Searching for prepaid traffic for session : %s", (rs.sessionid, ))
                        cur.execute("""SELECT id, size FROM billservice_accountprepaysradiustrafic WHERE account_tarif_id=%s and prepaid_traffic_id=%s and current=True""", (rs.acctf_id,acc.radius_traffic_transmit_service_id))
                        result = cur.fetchone()
                        cur.connection.commit()
                        prepaid_id, prepaid = result if result else (0, -1)
                        if prepaid > 0:
                            logger.debug("RADCOTHREAD: Prepaid traffic for session %s was found ", (rs.sessionid, prepaid))
                            if prepaid >= total_bytes:
                                total_bytes, prepaid = 0, prepaid - total_bytes
                            elif total_bytes >= prepaid:
                                total_bytes, prepaid = total_bytes - prepaid, 0
                            cur.execute("""UPDATE billservice_accountprepaysradiustrafic SET size=%s WHERE id=%s""", (prepaid, prepaid_id,))
                            cur.connection.commit()
                            logger.debug("RADCOTHREAD: Bytes for tarification for session %s %s ", (rs.sessionid, total_bytes))
                        #get the list of time periods and their cost
                        now = dateAT
                        for period in self.valued_prices(total_bytes_value,caches.radius_traffic_node_cache.by_id.get(radius_traffic_transmit_service_id, [])):
                            if 0: assert isinstance(period, RadiusTrafficNodeData)
                            #get period nodes and check them
                            for pnode in caches.timeperiodnode_cache.by_id.get(period.timeperiod_id, []):
                                if 0: assert isinstance(pnode, TimePeriodNodeData)
                                if fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, dateAT)[3]:
                                    logger.debug("RADCOTHREAD: Traffic tarification node for session %s was found. Cost=%s, total_bytes=%s", (rs.sessionid, period.cost, Decimal(total_bytes)))
                                    summ = (Decimal(total_bytes) * period.cost) / MEGABYTE
                                    logger.debug("RADCOTHREAD: Summ for checkout for session %s = %s", (rs.sessionid, summ))
                                    if summ > 0:
                                        #timetransaction(cur, rs.taccs_id, rs.acctf_id, rs.account_id, rs.id, summ, now)
                                        #db.timetransaction_fn(cur, rs.taccs_id, rs.acctf_id, rs.account_id, summ, now, unicode(rs.sessionid), rs.interrim_update)
                                        radiustraffictransaction(cur, radius_traffic_transmit_service_id, rs.acctf_id, rs.account_id, summ, created=now)
                                        cur.connection.commit()
                                    break

                            logger.debug("RADCOTHREAD: Session %s was checkouted (Traffic)", (rs.sessionid, ))

                    cur.execute("""UPDATE radius_activesession SET lt_bytes_in=%s, lt_bytes_out=%s, lt_time=%s
                                   WHERE date_start=%s and account_id=%s AND sessionid=%s and nas_port_id=%s and nas_int_id=%s
                                """, (rs.bytes_in, rs.bytes_out, rs.session_time, rs.date_start, rs.account_id, unicode(rs.sessionid), rs.nas_port_id, rs.nas_int_id))
                    logger.debug("RADCOTHREAD: Session %s was tarificated", (rs.sessionid, ))
                            
                    cur.connection.commit()
                cur.connection.commit()
                cur.close()
                logger.info("RADCOTHREAD: Time access thread run time: %s", time.time() - a)
            except TraftransTableException, ex:
                logger.info("%s : traftrans table not exists. Creating", (self.getName(),  )) 
                self.connection.rollback()
                try:
                    cur.execute("SELECT traftrans_crt_pdb(%s::date)", (now,))
                    cur.connection.commit()
                except Exception, ex:
                    logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc())) 
                    try: 
                        time.sleep(3)
                        if self.connection.closed():
                            try:
                                self.connection = get_connection(vars.db_dsn)
                                cur = self.connection.cursor()
                            except:
                                time.sleep(20)
                        else:
                            cur.connection.commit()
                            cur = self.connection.cursor()
                    except: 
                        time.sleep(10)
                        try:
                            self.connection.close()
                        except: pass
                        try:
                            self.connection = get_connection(vars.db_dsn)
                            cur = self.connection.cursor()
                        except:
                            time.sleep(20)
                            
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                self.connection.rollback()
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(vars.TIMEACCESS_SLEEP + random.randint(0,5))



class limit_checker(Thread):
    """
    Проверяет исчерпание лимитов. если лимит исчерпан-ставим соотв галочку в аккаунте
    """
    def __init__ (self):
        Thread.__init__(self)
 
    def run(self):
        #connection = pool.connection()
        #connection._con._con.set_client_encoding('UTF8')
        global suicideCondition, cacheMaster, fMem, vars
        self.connection = get_connection(vars.db_dsn)
        
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        while True:            
            try:
                if suicideCondition[self.__class__.__name__]:
                    try:    self.connection.close()
                    except: pass
                    break
                a = time.time()
                if cacheMaster.date <= dateAT:
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


                
                oldid = -1
                cur = self.connection.cursor()
                for acc in caches.account_cache.data:

                    if not acc.account_status == 1: continue
                    limits = caches.trafficlimit_cache.by_id.get(acc.tarif_id, [])
                    logger.debug("LIMIT_CHECKER: %s: acc_id: %s disabled_by_limit: %s limits: %s", (self.getName(), acc.account_id, acc.disabled_by_limit, limits))
                    if not limits:
                        if acc.disabled_by_limit:
                            cur.execute("""UPDATE billservice_account SET disabled_by_limit=False WHERE id=%s;""", (acc.account_id,))
                        cur.execute("""DELETE FROM billservice_accountspeedlimit WHERE account_id=%s;""", (acc.account_id,))
                        cur.connection.commit()
                        continue
                    block, speed_changed = (False, False)
                    for limit in limits:
                        if not limit.group_id: continue
                        
                        if oldid == acc.account_id and (block or speed_changed):
                            #Т.к. Лимиты отсортированы в порядке убывания размеров,то сначала проверяются все самые большие лимиты.
                            """
                            Если у аккаунта уже есть одно превышение лимита или изменена скорость
                            то больше для него лимиты не проверяем
                            """
                            continue
                        
                        sp = caches.settlementperiod_cache.by_id.get(limit.settlement_period_id)
                        if not sp: logger.info("NOT FOUND: SP: %s",limit.settlement_period_id); continue

                        
                        sp_defstart = acc.datetime if sp.autostart else sp.time_start
                        sp_start, sp_end, delta = fMem.settlement_period_(sp_defstart, sp.length_in, sp.length, dateAT)
                        if sp_start < acc.datetime: sp_start = acc.datetime
                        #если нужно считать количество трафика за последнеие N секунд, а не за рачётный период, то переопределяем значения
                        if limit.mode:
                            now = dateAT
                            sp_start = now - datetime.timedelta(seconds=delta)
                            sp_end   = now
                        
                        cur.connection.commit()        
                        cur.execute("""SELECT sum(bytes) AS size FROM billservice_groupstat
                                       WHERE group_id=%s AND account_id=%s AND datetime>%s AND datetime<%s
                                    """ , (limit.group_id, acc.account_id, sp_start, sp_end,)) 
                        sizes = cur.fetchone()
                        cur.connection.commit()
                        
                        tsize = sizes[0] if sizes[0] else 0
                        #limit_size = Decimal("%s" % limit.size)
                        #100% trace through!
                        if tsize > limit.size and limit.action==0:
                            block = True
                            cur.execute("""DELETE FROM billservice_accountspeedlimit WHERE account_id=%s;""", (acc.account_id,))                            
                        elif tsize > limit.size and limit.action == 1 and limit.speedlimit_id:
                            #Меняем скорость
                            cur.execute("SELECT speedlimit_ins_fn(%s, %s);", (limit.speedlimit_id, acc.account_id,))
                            speed_changed, block = (True, False)
                        elif tsize < limit.size:
                            cur.execute("""DELETE FROM billservice_accountspeedlimit WHERE account_id=%s;""", (acc.account_id,))
                        cur.connection.commit()
                        
                        oldid = acc.account_id
                        if acc.disabled_by_limit != block:
                            cur.execute("""UPDATE billservice_account SET disabled_by_limit=%s WHERE id=%s;
                                        """ , (block, acc.account_id,))
                            cur.connection.commit()
                            logger.info("set user %s new limit %s state %s", (acc.account_id, limit.trafficlimit_id, block))
    
                cur.connection.commit()
                cur.close()                
                logger.info("LMTALIVE: %s: run time: %s", (self.getName(), time.time() - a))
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                self.connection.rollback()
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(ex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(vars.LIMIT_SLEEP + random.randint(0,5))          


class addon_service(Thread):
    """
    Проверяет исчерпание лимитов. если лимит исчерпан-ставим соотв галочку в аккаунте
    """
    def __init__ (self):
        Thread.__init__(self)
 
    def run(self):
        #connection = pool.connection()
        #connection._con._con.set_client_encoding('UTF8')
        global suicideCondition, cacheMaster, fMem, vars
        self.connection = get_connection(vars.db_dsn)
        self.connection.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        while True:            
            try:
                if suicideCondition[self.__class__.__name__]:
                    try:    self.connection.close()
                    except: pass
                    break
                a = time.time()
                if cacheMaster.date <= dateAT:
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

                if 0: assert isinstance(caches, CoreCaches)
                
                oldid = -1
                cur = self.connection.cursor()

                for accountaddonservice in caches.accountaddonservice_cache.data:
                    #if 0: assert isinstance(acc, AccountData)
                    #if not acc.account_status == 1: continue

                    #accservices = caches.accountaddonservice_cache.by_account.get(acc.account_id, [])                          
                    #for accservice in accservices:                        
                    #if 0: assert isinstance(service, AccountAddonServiceData)                        

                    deactivated = None
                    service = caches.addonservice_cache.by_id.get(accountaddonservice.service_id)
                    
                    subacc = caches.subaccount_cache.by_id.get(accountaddonservice.subaccount_id)
                    if subacc:
                        acc = caches.account_cache.by_account.get(subacc.account_id)
                    else:
                        acc = caches.account_cache.by_account.get(accountaddonservice.account_id)
                    if not (subacc or acc): continue
                    #Проверка на требование отключения услуги
                    if service.service_type=='onetime':
                        
                        cur.execute("SELECT id FROM billservice_addonservicetransaction WHERE type_id ='ADDONSERVICE_ONETIME' and accountaddonservice_id=%s", (accountaddonservice.id,))
                        transactions = cur.fetchall()
                        if not transactions and accountaddonservice.activated<=dateAT and not accountaddonservice.temporary_blocked:

                            cur.execute("""
                            INSERT INTO billservice_addonservicetransaction(
                                        service_id, service_type, account_id, accountaddonservice_id, 
                                        accounttarif_id, type_id, summ, created)
                                VALUES (%s, 'onetime', %s, %s, 
                                        %s, %s, (-1)*%s,%s)
                            """,  (service.id, acc.account_id, accountaddonservice.id, acc.acctf_id, "ADDONSERVICE_ONETIME", accountaddonservice.cost, dateAT,))
                            cur.execute("UPDATE billservice_accountaddonservice SET last_checkout = %s WHERE id=%s", (dateAT, accountaddonservice.id))

                            
                        sp = caches.settlementperiod_cache.by_id.get(service.sp_period_id)
                        # Получаем delta
                        sp_start, sp_end, delta = fMem.settlement_period_(accountaddonservice.activated, sp.length_in, sp.length, dateAT)
                        tdelta = dateAT-accountaddonservice.activated
                        
                        if (tdelta.days*86400+tdelta.seconds)>=delta and not accountaddonservice.deactivated:
                            deactivated = dateAT
                            cur.execute("UPDATE billservice_accountaddonservice SET deactivated=%s WHERE id=%s", (dateAT,accountaddonservice.id,))
                            
                    if service.action:
                        if service.nas_id==0 and acc:
                            nas = caches.nas_cache.by_id.get(acc.nas_id)
                        elif service.nas_id==0 and subacc:
                            nas = caches.nas_cache.by_id.get(subacc.nas_id)
                        elif service.nas_id!=0:
                            nas = caches.nas_cache.by_id.get(service.nas_id)
                        
                        if not nas:
                            logger.info("Addon Service: %s: nas not set for account/subaccount/service %s/%s/%s", (self.getName(), repr(acc), repr(subacc), repr(service),))
                            continue
                        
                        allow = False
                        for pnode in caches.timeperiodnode_cache.by_id.get(service.timeperiod_id, []):                     
                            if fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, dateAT)[3]:   
                                allow = True
                                break
                        if allow and (not accountaddonservice.deactivated and not deactivated) and \
                        (service.action and not accountaddonservice.action_status) and \
                        not accountaddonservice.temporary_blocked and \
                         ((service.deactivate_service_for_blocked_account==False) or (service.deactivate_service_for_blocked_account==True and ((acc.ballance or 0+acc.credit or 0)>0 and acc.disabled_by_limit==False and acc.balance_blocked==False and acc.account_status==1 ))):
                            #выполняем service_activation_action
                            sended = cred.delay(acc._asdict(), subacc._asdict(), 'ipn', nas._asdict(), addonservice=service._asdict(), format_string=service.service_activation_action, cb=tasks.adds_enable_state.s(accountaddonservice.id))
                            #if sended is True: cur.execute()
                        
                        if allow==False or ((accountaddonservice.deactivated or accountaddonservice.temporary_blocked or deactivated or (service.deactivate_service_for_blocked_account==True and ((acc.ballance or 0 +acc.credit or 0)<=0 or acc.disabled_by_limit==True or acc.balance_blocked==True or acc.account_status!=1 ))) and accountaddonservice.action_status==True):
                            #выполняем service_deactivation_action
                            sended = cred.delay(acc._asdict(), subacc._asdict(), 'ipn', nas._asdict(), addonservice=service._asdict(), format_string=service.service_deactivation_action, cb=tasks.adds_disable_state.s(accountaddonservice.id))


                    cur.connection.commit()
                cur.connection.commit()
                cur.close()                
                logger.info("Addon Service: %s: run time: %s", (self.getName(), time.time() - a))
            except Exception, ex:
                cur.connection.rollback()
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                self.connection.rollback()
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(ex)))
                        time.sleep(10)
            gc.collect()
            #TODO: Вынести в конфиг
            time.sleep(120 + random.randint(0,5))     
            
class settlement_period_service_dog(Thread):
    """
    Для каждого пользователя по тарифному плану в конце расчётного периода производит
    1. Доснятие суммы
    2. Если денег мало для активации тарифного плана, ставим статус Disabled
    2. Сброс и начисление предоплаченного времени
    3. Сброс и начисление предоплаченного трафика
    алгоритм
    1. выбираем всех пользователей с текущими тарифными планами,
    у которых указан расчётный период и галочка "делать доснятие"
    2. Считаем сколько денег было взято по транзакциям.
    3. Если сумма меньше цены тарифного плана-делаем транзакцию, в которой снимаем деньги.
    """
    def __init__ (self):
        Thread.__init__(self)

    def run(self):
        """
        Сделать привязку к пользователю через billservice_accounttarif
        """         
        #connection = pool.connection()
        #connection._con._con.set_client_encoding('UTF8')
        global fMem, suicideCondition, cacheMaster, vars
        self.connection = get_connection(vars.db_dsn)
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        while True:
            try:
                if suicideCondition[self.__class__.__name__]:
                    try: self.connection.close()
                    except: pass
                    break
                a = time.time()
                if cacheMaster.date <= dateAT:
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

                if 0: assert isinstance(caches, CoreCaches)
                self.connection.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
                cur = self.connection.cursor()
                for acc in caches.account_cache.data:
                    try:
                        if 0: assert isinstance(acc, AccountData)
                        if not acc.account_status == 1: continue
                        
                        shedl = caches.shedulelog_cache.by_id.get(acc.account_id)
                        if not shedl: shedl = ShedulelogData(-1, *(None,)*10)
                        if 0: assert isinstance(shedl, ShedulelogData)

                        time_start, period_end = None, None
                        #now = datetime.datetime.now()
                        now=dateAT
                        if not acc.settlement_period_id:
                            #TODO:Проверить что находится в datetime. Теоретически все даты должны быть записаны датой начала расчётного периода
                            time_start, period_start, delta = (acc.datetime, acc.datetime, 86400*365*365)
                        else:
                            sp = caches.settlementperiod_cache.by_id.get(acc.settlement_period_id)

                            time_start = acc.datetime if sp.autostart else sp.time_start
                            period_start, period_end, delta = fMem.settlement_period_(time_start, sp.length_in, sp.length, dateAT)
                            #Если начало расчётного периода осталось в прошлом тарифном плане-за начало расчётного периода принимаем начало тарифного плана
                            if period_start < acc.datetime and not sp.autostart: period_start = acc.datetime                            
    
                        #нужно производить в конце расчётного периода
                        ballance_checkout = shedl.ballance_checkout if shedl.ballance_checkout else acc.datetime

                        if (ballance_checkout is None or ballance_checkout < period_start) and acc.reset_tarif_cost and period_end and acc.cost > 0:
                            #Снять сумму до стоимости тарифного плана                   
                            #Считаем сколько было списано по услугам                   
                            tnc, tkc, delta = settlement_period_info(time_start, sp.length_in, sp.length, dateAT, prev=True)
                            #Считаем сколько было списано по услугам
                            cur.execute("""SELECT transaction_sum(%s, %s, %s::timestamp without time zone, %s::timestamp without time zone);""",
                                        (acc.account_id, acc.acctf_id, tnc, tkc))
                            summ = cur.fetchone()[0] or 0    
                            if acc.cost > summ:
                                pay_summ = acc.cost - summ
                                transaction(cursor=cur,account=acc.account_id,approved=True,type='END_PS_MONEY_RESET',
                                            summ=pay_summ,created=now,tarif=acc.tarif_id,accounttarif=acc.acctf_id,
                                            description=u"Доснятие денег до стоимости тарифного плана у %s" % acc.account_id)
                            cur.execute("SELECT shedulelog_co_fn(%s, %s, %s::timestamp without time zone);", (acc.account_id, acc.acctf_id, now,))
                            cur.connection.commit()

                        account_balance = (acc.ballance or 0) + (acc.credit or 0)
                        blocked = False
                        #Если балланса не хватает - отключить пользователя
                        if (shedl.balance_blocked is None or (period_start and shedl.balance_blocked<period_start )) and acc.cost>account_balance \
                         and acc.cost != 0 and acc.require_tarif_cost and not acc.balance_blocked:
    
                            cur.execute("SELECT shedulelog_blocked_fn(%s, %s, %s::timestamp without time zone, %s);", 
                                        (acc.account_id, acc.acctf_id, now, acc.cost))
                            blocked = True
                            cur.connection.commit()
                        elif shedl.balance_blocked is None:
                            cur.execute('SELECT 1 FROM billservice_shedulelog WHERE account_id=%s', (acc.account_id, ))
                            if cur.fetchone():
                                cur.execute('UPDATE billservice_shedulelog SET balance_blocked=%s WHERE account_id=%s', (now, acc.account_id))
                            else:
                                cur.execute("INSERT INTO billservice_shedulelog(account_id, accounttarif_id, balance_blocked) VALUES(%s,%s, %s);", (acc.account_id, acc.acctf_id, now))
                            cur.connection.commit()
                            
                        if (acc.balance_blocked or blocked):
                            cur.execute("select COALESCE(max(balance), 0) FROM billservice_balancehistory where account_id=%s and datetime>%s;", (acc.account_id, period_start))
                            max_balance = cur.fetchone()
                            if not max_balance:
                                max_balance = account_balance
                            else:
                                max_balance = max_balance[0]
                            if  (max_balance >= acc.cost or not acc.require_tarif_cost):
                                cur.execute("""UPDATE billservice_account SET balance_blocked=False WHERE id=%s;""", (acc.account_id,))                            
                            cur.connection.commit()
                        
                        #print repr(acc)
                        reset_traffic = caches.traffictransmitservice_cache.by_id.get(acc.traffic_transmit_service_id, (None, None))[1]                        
                        radius_traffic = caches.radius_traffic_transmit_service_cache.by_id.get(acc.radius_traffic_transmit_service_id)
                        prepaid_traffic_reset = shedl.prepaid_traffic_reset if shedl.prepaid_traffic_reset else acc.datetime
                        prepaid_radius_traffic_reset = shedl.prepaid_radius_traffic_reset if shedl.prepaid_radius_traffic_reset else acc.datetime
                        #if (reset_traffic or acc.traffic_transmit_service_id is None) and (shedl.prepaid_traffic_reset is None or shedl.prepaid_traffic_reset<period_start or acc.acctf_id!= shedl.accounttarif_id):
                        need_traffic_reset=     shedl.prepaid_traffic_accrued and ( (acc.traffic_transmit_service_id is  None or acc.acctf_id != shedl.accounttarif_id)  or   (reset_traffic and prepaid_traffic_reset<period_start))
                        need_radius_traffic_reset= shedl.prepaid_radius_traffic_accrued and ((radius_traffic.reset_prepaid_traffic and  prepaid_radius_traffic_reset<period_start) or (acc.radius_traffic_transmit_service_id is None  or acc.acctf_id != shedl.accounttarif_id))

                        if need_traffic_reset:
                            #(Если нужно сбрасывать трафик или нет услуги доступа по трафику) И
                            #(Никогда не сбрасывали трафик или последний раз сбрасывали в прошлом расчётном периоде или пользователь сменил тариф)
                            """(Если наступил новый расчётный период и нужно сбрасывать трафик) или если нет услуги с доступом по трафику или если сменился тарифный план"""
                            cur.execute("SELECT shedulelog_tr_reset_fn(%s, %s, %s::timestamp without time zone);", \
                                        (acc.account_id, acc.acctf_id, now))  
                            cur.connection.commit()

                                    
                        if (shedl.prepaid_traffic_accrued is None or shedl.prepaid_traffic_accrued<period_start or acc.acctf_id != shedl.accounttarif_id) and acc.traffic_transmit_service_id:                          
                            #Начислить новый предоплаченный трафик
                            #TODO:если начисляем первый раз - начислять согласно коэффициенту оставшейся части расчётного периода
                            delta_coef=1
                            if period_end and ((period_end-acc.datetime).days*86400+(period_end-acc.datetime).seconds)<delta and vars.USE_COEFF_FOR_PREPAID==True:
                                delta_coef=float((period_end-acc.datetime).days*86400+(period_end-acc.datetime).seconds)/float(delta)
                                
                            cur.execute("SELECT shedulelog_tr_credit_fn(%s, %s, %s, %s, %s, %s::timestamp without time zone);", 
                                    (acc.account_id, acc.acctf_id, acc.traffic_transmit_service_id, need_traffic_reset, delta_coef, period_start))
                            cur.connection.commit()

                        if need_radius_traffic_reset:
                            #(Если нужно сбрасывать трафик или нет услуги доступа по трафику) И
                            #(Никогда не сбрасывали трафик или последний раз сбрасывали в прошлом расчётном периоде или пользователь сменил тариф)
                            """(Если наступил новый расчётный период и нужно сбрасывать трафик) или если нет услуги с доступом по трафику или если сменился тарифный план"""
                            cur.execute("SELECT shedulelog_radius_tr_reset_fn(%s, %s, %s::timestamp without time zone);", \
                                        (acc.account_id, acc.acctf_id, now))  
                            cur.connection.commit()

                        #Radius prepaid
                        if (shedl.prepaid_radius_traffic_accrued is None or shedl.prepaid_radius_traffic_accrued<period_start or acc.acctf_id != shedl.accounttarif_id) and acc.radius_traffic_transmit_service_id and radius_traffic:                          
                            #Начислить новый предоплаченный трафик
                            #TODO:если начисляем первый раз - начислять согласно коэффициенту оставшейся части расчётного периода
                            delta_coef=1
                            if vars.USE_COEFF_FOR_PREPAID==True and period_end and ((period_end-acc.datetime).days*86400+(period_end-acc.datetime).seconds)<delta:
                                delta_coef=float((period_end-acc.datetime).days*86400+(period_end-acc.datetime).seconds)/float(delta)
                                
                            cur.execute("SELECT shedulelog_radius_tr_credit_fn(%s, %s, %s, %s, %s, %s, %s, %s::timestamp without time zone);", 
                                        (acc.account_id, acc.acctf_id, acc.radius_traffic_transmit_service_id, need_radius_traffic_reset, radius_traffic.prepaid_value, radius_traffic.prepaid_direction, delta_coef, now))

                            cur.connection.commit()
                                                    
                        prepaid_time, reset_time = caches.timeaccessservice_cache.by_id.get(acc.time_access_service_id, (None, 0, None))[1:3]
                        need_time_reset = (reset_time and prepaid_time and shedl.prepaid_time_accrued and shedl.prepaid_time_reset<period_start) or (shedl.prepaid_time_accrued and (acc.time_access_service_id is None  or acc.acctf_id != shedl.accounttarif_id))   
                        
                        if need_time_reset:
                            #(Если нужно сбрасывать время или нет услуги доступа по времени) И                        
                            #(Никогда не сбрасывали время или последний раз сбрасывали в прошлом расчётном периоде или пользователь сменил тариф)                          
                            cur.execute("SELECT shedulelog_time_reset_fn(%s, %s, %s::timestamp without time zone);", 
                                        (acc.account_id, acc.acctf_id, now))                            
                            cur.connection.commit()        

                        if (shedl.prepaid_time_accrued is None or shedl.prepaid_time_accrued<period_start or acc.acctf_id != shedl.accounttarif_id) and acc.time_access_service_id:
                            delta_coef=1
                            if period_end and ((period_end-acc.datetime).days*86400+(period_end-acc.datetime).seconds)<delta  and vars.USE_COEFF_FOR_PREPAID==True:
                                delta_coef=float((period_end-acc.datetime).days*86400+(period_end-acc.datetime).seconds)/float(delta)     
                            cur.execute("SELECT shedulelog_time_credit_fn(%s, %s, %s, %s, %s, %s, %s::timestamp without time zone);", 
                                        (acc.account_id, acc.acctf_id, acc.time_access_service_id,need_time_reset, prepaid_time, delta_coef, now))   
                            cur.connection.commit()
                        
                        if account_balance > 0:
                            for ots in caches.onetimeservice_cache.by_id.get(acc.tarif_id, []):
                                if 0: assert isinstance(ots, OneTimeServiceData)
                                if not caches.onetimehistory_cache.by_acctf_ots_id.has_key((acc.acctf_id, ots.id)) \
                                   and not ots.created > acc.datetime:
                                    cur.execute("INSERT INTO billservice_onetimeservicehistory(accounttarif_id, onetimeservice_id, account_id, summ, created) VALUES(%s, %s, %s, (-1)*%s, %s);", (acc.acctf_id, ots.id, acc.account_id, ots.cost, now,))
                                    cur.connection.commit()
                                    caches.onetimehistory_cache.by_acctf_ots_id[(acc.acctf_id, ots.id)] = (1,)
                                    #Списывам с баланса просроченные обещанные платежи
                    except Exception, ex:
                        logger.error("%s : internal exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                        if ex.__class__ in vars.db_errors: raise ex
                cur.connection.commit()
                #Делаем проводки по разовым услугам тем, кому их ещё не делали
                cur.execute("""SELECT tr.id
                                    FROM billservice_transaction as tr
                                    WHERE 
                                    promise_expired = False and type_id='PROMISE_PAYMENT' and
                                    (end_promise<now() or (SELECT sum(summ) FROM billservice_transaction WHERE account_id=tr.account_id and type_id!='PROMISE_PAYMENT' and summ>0 and created>tr.created)>=tr.summ)""")
                promises = set(cur.fetchall())

                if promises:
                    cur.execute("""
                            INSERT INTO billservice_transaction(bill, account_id, type_id, approved, summ, description, created, promise_expired) 
                            SELECT id, account_id, 'PROMISE_DEBIT', approved, (-1)*summ, description, now(), True
                              FROM billservice_transaction as tr
                              WHERE tr.id in (%s) and tr.type_id='PROMISE_PAYMENT';
                    """ % ', '.join([str(x[0]) for x in promises]))
                    
                    cur.execute("""UPDATE billservice_transaction as tr SET promise_expired = True 
                                    WHERE id in (%s);""" % ', '.join([str(x[0]) for x in promises]))
                cur.connection.commit()
                for account in caches.account_cache.data:
                    if account.account_status==4:
                        sps=caches.suspended_cache.by_account_id.get(acc.account_id,[])
                        for sp in sps:
                            if sp.end_date and sp.start_date+datetime.timedelta(seconds = account.userblock_max_days)>=dateAT:
                                
                                """
                                Запрос должен быть именно такого вида, чтобы не допустить двойной установки статуса
                                UPDATE billservice_account SET status=1 WHERE id=%s and status=4;
                                """
                                cur.execute("UPDATE billservice_account SET status=1 WHERE id=%s and status=4;", (account.account_id,))
                                cur.connection.commit()
                        
                logger.info("SPALIVE: %s run time: %s", (self.getName(), time.time() - a))
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                self.connection.rollback()
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(vars.SETTLEMENT_PERIOD_SLEEP + random.randint(0,5))

class ipn_service(Thread):
    """
    Тред должен:
    1. Проверять не изменилась ли скорость для IPN клиентов и менять её на сервере доступа
    2. Если балланс клиента стал меньше 0 - отключать, если уже не отключен (параметр ipn_status в account) и включать, если отключен (ipn_status) и баланс стал больше 0
    3. Если клиент вышел за рамки разрешённого временного диапазона в тарифном плане-отключать
    """
    def __init__ (self):
        global vars
        Thread.__init__(self)
        self.connection = get_connection(vars.db_dsn)
        
    def run(self):
        global suicideCondition, cacheMaster, vars
        
        caches = None
        dateAT = datetime.datetime(2000, 1, 1)
        while True:     
    
            try:
                """
                Команды для админки
                Создание подаккаунтов IPN с шарингом скорости между аккаунтами
                /ip firewall address-list add list=internet_users address=$account_ipn_ip disabled=yes comment=$user_id;:if ([/queue simple find name=$user_id]="") do={/queue simple add name=$user_id disabled=yes};:local new "$ipn_ip_address"; :local res [/queue simple get $user_id target-addresses ]; :if ([:tostr [:find [:toarray $res] $new]] = "") do={:set res ($res + $new);  /queue simple set $user_id target-address=$res disabled=no; }}
                """
                if suicideCondition[self.__class__.__name__]:
                    try: self.connection.close()
                    except: pass
                    break
                a = time.time()

                if cacheMaster.date <= dateAT:
                    time.sleep(10); continue
                else:
                    cacheMaster.lock.acquire()
                    try:
                        caches = cacheMaster.cache
                        dateAT = deepcopy(cacheMaster.date)
                    except Exception, cex:
                        logger.error("%s: cache exception: %s", (self.getName, repr(cex)))
                    finally:
                        cacheMaster.lock.release()                
                if 0: assert isinstance(caches, CoreCaches)
                
                cur = self.connection.cursor()
                
                for acc in caches.account_cache.data:
                    try:
                        if 0: assert isinstance(acc, AccountData)

                        """Если у аккаунта не указан IPN IP, мы не можем производить над ним действия. Пропускаем."""       
                        subaccounts = caches.subaccount_cache.by_account_id.get(acc.account_id, [])
                        access_list = []
                            
                        for subacc in subaccounts:
                            if subacc.ipn_queued:
                                logger.info("IPNALIVE: %s: Queued IPN command for subaccount %s is not empty", (self.getName(), subacc.id))
                            if not subacc.nas_id : continue
                            access_list.append((subacc.id, subacc.ipn_ip_address,  subacc.ipn_mac_address, subacc.vpn_ip_address, subacc.nas_id, subacc))
                        #if not acc.tarif_active or acc.ipn_ip_address == '0.0.0.0' and '0.0.0.0' in [[x.ipn_ip_address, x.nas_id] if x is not '0.0.0.0' else 1 for x in subaccounts]: continue
                        accps = caches.accessparameters_cache.by_id.get(acc.access_parameters_id)
                        if (not accps) or (not accps.ipn_for_vpn): continue
                        if 0: assert isinstance(accps, AccessParametersData)
                        account_ballance = (acc.ballance or 0) + (acc.credit or 0)
                        period = caches.timeperiodaccess_cache.in_period[acc.tarif_id]# True/False
                        for id, ipn_ip_address, ipn_mac_address, vpn_ip_address, nas_id, subacc in access_list:
                            sended, recreate_speed = (None, False)
                            #logger.info("IPNALIVE: %s: check and set new status for subaccount/service %s/%s", (self.getName(), repr(acc), repr(subacc),))
                            nas = caches.nas_cache.by_id.get(nas_id)
                            
                            if not nas:
                                #logger.info("IPNALIVE: %s: nas not set for subaccount/service %s/%s", (self.getName(), repr(acc), repr(subacc),))
                                continue
                            if 0: assert isinstance(nas, NasData)
                            access_type = 'IPN'
                            #now = datetime.datetime.now()
                            now = dateAT
                            # Если на сервере доступа ещё нет этого пользователя-значит добавляем.
                            #Добавить обработку на предмет смены тарифного плана, сервера доступа, удаления аккаунта - подчищать за ним данные и сбрасывать флаги
                            ipn_add=False
                            ipn_disable = False
                            ipn_enable = False
                            if subacc and not subacc.ipn_added and acc.tarif_active:
                                ipn_add = True

                            if subacc and subacc.ipn_enabled==False and ( (account_ballance>0 or (account_ballance==0 and subacc.allow_ipn_with_null==True) or (account_ballance<0 and subacc.allow_ipn_with_minus==True) ) and period and acc.account_status == 1 and ((not acc.disabled_by_limit and not acc.balance_blocked) or acc.allow_ipn_with_block==True)) and acc.tarif_active:
                                ipn_enable = True

                            elif subacc.ipn_enabled is not False and subacc and (((acc.disabled_by_limit or acc.balance_blocked) and subacc.allow_ipn_with_block==False) or ((account_ballance<0 and subacc.allow_ipn_with_minus==False) or (account_ballance==0 and subacc.allow_ipn_with_null==False)) or period is False or acc.account_status != 1 or not acc.tarif_active):
                                ipn_disable = True    
              


                                    
                            cur.connection.commit()
        
                            #Приступаем к генерации настроек скорости
                            #Получаем настройки скорости по лимитам, если пользователь превысил какой-нибудь лимит.
                            account_limit_speed = caches.speedlimit_cache.by_account_id.get(acc.account_id, [])
                            
                            #TODO: caches.defspeed_cache.by_id - нужно же брать по tarif_id!! Это верно?? 
                            #Получаем подключаемые услуги абонента
                            accservices = []
                            addonservicespeed=[]
                            br = False  
                            if subacc:
                                accservices = caches.accountaddonservice_cache.by_subaccount.get(subacc.id, [])    
                                for accservice in accservices:                                 
                                    service = caches.addonservice_cache.by_id.get(accservice.service_id)           
                                    for pnode in caches.timeperiodnode_cache.by_id.get(service.timeperiod_id, []):                     
                                        if not accservice.deactivated  and service.change_speed and fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, dateAT)[3]:                                                                        
                                            addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.priority, service.min_tx, service.min_rx, service.speed_units, service.change_speed_type)
                                            br = True                                    
                                            break
                                    if br: break
                            br = False
                            if not addonservicespeed: 
                                accservices = caches.accountaddonservice_cache.by_account.get(acc.account_id, [])    
                                for accservice in accservices:                                 
                                    service = caches.addonservice_cache.by_id.get(accservice.service_id)           
                                    for pnode in caches.timeperiodnode_cache.by_id.get(service.timeperiod_id, []):                     
                                        if not accservice.deactivated  and service.change_speed and fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, dateAT)[3]:                                                                        
                                            addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.priority, service.min_tx, service.min_rx, service.speed_units, service.change_speed_type)                                    
                                            br = True
                                            break
                                    if br: break    
                            #Получаем параметры скорости                         
                            speed = create_speed(caches.defspeed_cache.by_id.get(acc.tarif_id), caches.speed_cache.by_id.get(acc.tarif_id, []),account_limit_speed, addonservicespeed, subacc.ipn_speed, dateAT, fMem)                            
                    
        
        
                            
                            newspeed = ''.join([unicode(spi) for spi in speed])
                            
                            ipnsp = caches.ipnspeed_cache.by_id.get(acc.account_id, IpnSpeedData(*(None,)*6))
                            if 0: assert isinstance(ipnsp, IpnSpeedData)
                            cs = None
                            cb = None
                            if newspeed!=subacc.speed or recreate_speed:
                                #отправляем на сервер доступа новые настройки скорости, помечаем state=True

                                ipn_speed_action = nas.subacc_ipn_speed_action
                                
                                if ipn_speed_action:
                                    cs = change_speed.s(account=acc._asdict(), subacc=subacc._asdict(), nas=nas._asdict(),
                                                                access_type=access_type,
                                                                format_string=ipn_speed_action,
                                                                speed=speed, cb = tasks.update_ipn_speed_state.s(subaccount_id=id, newspeed=newspeed))

                                
   
                                    subacc = subacc._replace(speed=newspeed)
                                                          

                                
                            logger.info("IPNALIVE: %s: new status for subaccount/service %s/%s ipn_add=%s ipn_enable=%s ipn_disable=%s change_speed=%s", (self.getName(), repr(acc), repr(subacc), ipn_add, ipn_enable, ipn_disable, newspeed))
                            if ipn_add:
                                #если нужно добавить субаккаунт - добавляем и, если нужно, активируем/деактивируем и, если нужно, устанавливаем скорость
                                cb = cred.s(acc._asdict(), subacc._asdict(), access_type, nas._asdict(), format_string=nas.subacc_enable_action, cb=tasks.ipn_enable_state.s(id, cb = cs) if ipn_enable else tasks.ipn_disable_state.s(id, cb=cs))
                                cred.delay(acc._asdict(), subacc._asdict(), access_type, nas._asdict(), format_string=nas.subacc_add_action, cb = tasks.ipn_add_state.s(id, cb = cb))
                            else:# Задания могут выполниться не по очереди
                                if ipn_enable:
                                    #Активируем и, если нужно, устанавливаем скорость
                                    cred.delay(acc._asdict(), subacc._asdict(), access_type, nas._asdict(), format_string=nas.subacc_enable_action, cb=tasks.ipn_enable_state.s(id, cb=cs))
                                elif ipn_disable:
                                    #Деактивируем и, если нужно, устанавливаем скорость
                                    cred.delay(acc._asdict(), subacc._asdict(), access_type, nas._asdict(), format_string=nas.subacc_disable_action, cb = tasks.ipn_disable_state.s(id, cb=cs))
                                elif cs:
                                    #Просто сменить скорость
                                    cs.apply_async()
                            if cb or cs:
                                cur.execute('UPDATE billservice_subaccount SET ipn_queued=now() WHERE id=%s', (subacc.id,))
                            cur.connection.commit()
                    except Exception, ex:
                        if ex.__class__ in vars.db_errors: raise ex
                        else:
                            logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
        
                cur.connection.commit()
                cur.close()
                logger.info("IPNALIVE: %s: run time: %s", (self.getName(), time.time() - a))
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                self.connection.rollback()
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(vars.IPN_SLEEP + random.randint(0,5))


#periodical function memoize class
class pfMemoize(object):
    __slots__ = ('periodCache', 'settlementCache', 'dicts')
    def __init__(self):
        self.periodCache = {}
        self.settlementCache = {}
        self.dicts = [self.periodCache, self.settlementCache]
        
    def in_period_(self, time_start, length, repeat_after, date_):
        res = self.periodCache.get((time_start, length, repeat_after, date_))
        if res is None:
            res = in_period_info(time_start, length, repeat_after, date_)
            self.periodCache[(time_start, length, repeat_after, date_)] = res
        return res
    
    def settlement_period_(self, time_start, length, repeat_after, stream_date):
        res = self.settlementCache.get((time_start, length, repeat_after, stream_date))
        if res is None:
            res = settlement_period_info(time_start, length, repeat_after, stream_date)
            self.settlementCache[(time_start, length, repeat_after, stream_date)] = res
        return res
    
    def clear(self):
        for dct in self.dicts: dct.clear()
  




class AccountServiceThread(Thread):
    '''Handles simultaniously updated READ ONLY caches connected to account-tarif tables'''
    def __init__ (self):
        Thread.__init__(self)
        #self.connection = pool.connection()
        #self.connection._con._con.set_client_encoding('UTF8')
        
    def run(self):        
        global suicideCondition, cacheMaster, flags, vars
        self.connection = get_connection(vars.db_dsn)
        counter = 0; now = datetime.datetime.now
        while True:
            if suicideCondition[self.__class__.__name__]:
                try:    self.connection.close()
                except: pass
                break
            try: 
                if flags.cacheFlag or (now() - cacheMaster.date).seconds > vars.CACHE_TIME:
                    run_time = time.time()                    
                    cur = self.connection.cursor()
                    #renewCaches(cur)
                    renewCaches(cur, cacheMaster, CoreCaches, 31, (fMem, vars.CRYPT_KEY), False)
                    cur.close()
                    if counter == 0:
                        aUC(AU, lambda: len(cacheMaster.cache.account_cache.data), ungraceful_save, flags)
                        if not flags.allowedUsersCheck: continue
                        counter = 0
                        #flags.allowedUsersCheck = True
                    counter += 1
                    if counter == 5:
                        #nullify 
                        counter, fMem.settlementCache, fMem.periodCache = 0, {}, {}
                    if flags.cacheFlag:
                        with flags.cacheLock: flags.cacheFlag = False
                    
                    logger.info("ast time : %s", time.time() - run_time)
            except Exception, ex:
                logger.error("%s : #30310004 : %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                self.connection.rollback()
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(20)
            
    
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
    
def SIGHUP_handler(signum, frame):
    global config
    logger.lprint("SIGHUP recieved")
    try:
        config.read("ebs_config.ini")
        logger.setNewLevel(int(config.get("core", "log_level")))
        flags.writeProf = logger.writeInfoP()
    except Exception, ex:
        logger.error("SIGHUP config reread error: %s", repr(ex))
    else:
        logger.lprint("SIGHUP config reread OK")
        
def SIGUSR1_handler(signum, frame):
    global flags
    logger.lprint("SIGUSR1 recieved\n")
    with flags.cacheLock: flags.cacheFlag = True
    
def graceful_save():
    global cacheThr, threads, suicideCondition, vars
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    logger.lprint("Core - about to exit gracefully.\n")
    time.sleep(20)
    rempid(vars.piddir, vars.name)
    logger.lprint("Core - exiting gracefully.\n")
    sys.exit()
    
def ungraceful_save():
    global cacheThr, threads, suicideCondition, vars
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    rempid(vars.piddir, vars.name)
    print "Core: exiting\n"
    logger.lprint("Core exiting.\n")
    sys.exit()
    
def mn():
    global caches, suicideCondition, threads, cacheThr, vars
    
    threads = []
    thrnames = [(check_vpn_access, 'Core VPN Thread'), (periodical_service_bill, 'Core Period. Bill Thread'), \
                (RadiusAccessBill, 'Core Radius Access Thread'), (limit_checker, 'Core Limit Thread'),\
                (settlement_period_service_dog, 'Core Settlement Per. Thread'), (ipn_service, 'Core IPN Thread'),(addon_service, 'Addon Service Thread'),]


    for thClass, thName in thrnames:
        threads.append(thClass())
        threads[-1].setName(thName)
    
    cacheThr = AccountServiceThread()
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.setName('Core AccountServiceThread')
    cacheThr.start()
    
    while cacheMaster.read is False or flags.allowedUsersCheck is False:        
        if not cacheThr.isAlive():
            print 'Core: exiting\n'
            sys.exit()
        time.sleep(10)
        if not cacheMaster.read: 
            print 'caches still not read, maybe you should check the log\n'
      
    #print 'caches ready\n'
    #print repr(cacheMaster.cache)
    for th in threads:	
        suicideCondition[th.__class__.__name__] = False
        th.start()
        time.sleep(0.2)
        
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')
    
    try:
        signal.signal(signal.SIGHUP, SIGHUP_handler)
    except: logger.lprint('NO SIGHUP!')
    
    try:
        signal.signal(signal.SIGUSR1, SIGUSR1_handler)
    except: logger.lprint('NO SIGUSR1!')
    
    #print "ebs: core: started\n"
    savepid(vars.piddir, vars.name)
    stderr_log = open(vars.log_file + '.err', 'ab')
    #redirect_stderr(stderr_log)
    sys.stderr = stderr_log
    #main thread should not exit!
    while True:
        time.sleep(20)
        if not cacheThr.isAlive():
            print 'Core: exiting\n'
            sys.exit()
        


#===============================================================================


if __name__ == "__main__":
       
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")
    Watcher()
    try:
        import psyco
        psyco.full(memory=100)
        psyco.profile(0.05, memory=100)
        psyco.profile(0.2)
    except:
        pass
    try:
        #psyco.log()

        vars = CoreVars()
        
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME)

        #create logger
        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file) 
        
        utilites.log_adapt = logger.log_adapt
        
        
        logger.lprint('core start\n')

        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)
        
        cacheMaster = CacheMaster()
        flags = CoreFlags()
        flags.writeProf = logger.writeInfoP()
        suicideCondition = {}

        a=open(b64decode('bGljZW5zZS5saWM=')).read().split(b64decode('QVM='))
        raw_uid, raw_crc = a
        l_uid = raw_uid[:32]
        srts=int(str(raw_uid[32:]).strip().lower(),16)
        if l_uid==md5(str('freedom')).hexdigest().upper():
            o = str('freedom')
        else:
            s,o=commands.getstatusoutput(b64decode('Y2F0IC9wcm9jL2NwdWluZm8gfCBncmVwICJtb2RlbCBuYW1lIg=='))
        uid = md5(o).hexdigest().upper()
        
        if l_uid!=uid:
            print b64decode('SW5jb3JyZWN0IGhhc2guIE5ldyBoYXJkd2FyZT8=')
            sys.exit()
            
        uid+=str(hex(srts))
        uid=uid.upper()
        crc=0
        i=0
        for x in uid:
            crc+=ord(x)**i-1
            i+=1
        
        cc=md5(str(crc)).hexdigest().upper()
        
        if raw_crc!=cc:
            print b64decode('SW5zdWNjZWZ1bGwgY3J5cHRvaGFzaA==')
            sys.exit()

        _1i = lambda: srts
        
        if not srts:
            _1i = lambda: ''
            
        def sAU(allowed, dbconnection = None):
            AU = lambda: int(allowed)
            if dbconnection:
                cur = dbconnection.cursor()
                cur.callproc('crt_allowed_checker', (AU(),))
                dbconnection.commit()
                cur.close()
                dbconnection.close()
            return AU
        
        def aUC(allowed, current, exit, flags):
            if current() > allowed():
                logger.error("SHUTTING DOWN: current amount of users[%s] exceeds allowed[%s] for the license file" , (str(current()), str(allowed())))
                print >> sys.stderr, "SHUTTING DOWN: current amount of users[%s] exceeds allowed[%s] for the license file" % (str(current()), str(allowed()))
                flags.allowedUsersCheck = False
                exit()
            else:
                flags.allowedUsersCheck = True
                
        tmpconnection = get_connection(vars.db_dsn)
        AU = sAU(_1i(), tmpconnection)        
        logger.info("Allowed users: %s", (AU(),))


        tasks.DSN = vars.db_dsn
        fMem = pfMemoize()    
        #--------------------------------------------------
        
        #print "ebs: core: configs read, about to start\n"
        #main()
        mn()
        
    except Exception, ex:
        print 'Exception in core, exiting: ', repr(ex)
        logger.error('Exception in core, exiting: %s \n %s', (repr(ex), traceback.format_exc()))

