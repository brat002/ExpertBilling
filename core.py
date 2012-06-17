#-*-coding=utf-8-*-

from __future__ import with_statement

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
import utilites, saver

import itertools
import db

from decimal import Decimal
from copy import copy, deepcopy
from db import Object as Object
from daemonize import daemonize
from threading import Thread, Lock
from collections import defaultdict


from constants import rules
from saver import allowedUsersChecker, setAllowedUsers
from utilites import parse_custom_speed, parse_custom_speed_lst, cred, get_decimals_speeds
from utilites import rosClient, settlement_period_info, in_period, in_period_info

from utilites import create_speed_string, change_speed, PoD, get_active_sessions, get_corrected_speed
from db import  dbRoutine
from db import transaction, ps_history, get_last_checkout
from db import timetransaction, get_last_addon_checkout, addon_history


from classes.cacheutils import CacheMaster
from classes.core_cache import *
from classes.flags import CoreFlags
from classes.vars import CoreVars
from utilites import renewCaches, savepid, get_connection, check_running, getpid, rempid

#from utilities.misc_utilities import redirect_stderr, redirect_stdout

from classes.core_class.RadiusSession import RadiusSession
from classes.core_class.BillSession import BillSession

import ssh_paramiko

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

    def create_speed(self, default, speeds,  correction, addonservicespeed, speed, date_):          
        if speed=='':            
            defaults = default            
            defaults = defaults[:6] if defaults else ["0/0","0/0","0/0","0/0","8","0/0"]            
            result=[]            
            min_delta, minimal_period = -1, []            
            now=date_            
            for speed in speeds:                
                #Определяем составляющую с самым котортким периодом из всех, которые папали в текущий временной промежуток
                tnc,tkc,delta,res = fMem.in_period_(speed[6],speed[7],speed[8], now)                
                #print "res=",res                
                if res==True and (delta<min_delta or min_delta==-1):                    
                    minimal_period=speed                    
                min_delta=delta            
            
            minimal_period = minimal_period[:6] if minimal_period else ["0/0","0/0","0/0","0/0","","0/0"]            
            for k in xrange(0, 6):                
                s=minimal_period[k]                
                if s=='0/0' or s=='/' or s=='':                    
                    res=defaults[k]                
                else:                    
                    res=s                
                result.append(res)   #Проводим корректировку скорости в соответствии с лимитом            
            #print self.caches.speedlimit_cache      
   
            result = get_corrected_speed(result, correction)            
            if addonservicespeed:                
                result = get_corrected_speed(result, addonservicespeed)                        
            if result==[]:                 
                result = defaults if defaults else ["0/0","0/0","0/0","0/0","8","0/0"]                            
            
            return result
        else:
            try:
                return parse_custom_speed_lst(speed)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s Can not parse account speed %s", (self.getName(), repr(ex), traceback.format_exc()), acc.ipn_speed)
                return ["0/0","0/0","0/0","0/0","8","0/0"] 
            


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
                a = time.clock()

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

                cur.connection.commit()
                cur.execute("""SELECT rs.id,rs.account_id, rs.subaccount_id, rs.sessionid,rs.framed_ip_address, rs.speed_string,
                                    lower(rs.framed_protocol) AS access_type,rs.nas_id, extract('epoch' from %s-rs.interrim_update) as last_update, rs.date_start,rs.ipinuse_id, rs.caller_id, ((SELECT pool_id FROM billservice_ipinuse WHERE id=rs.ipinuse_id)=(SELECT vpn_guest_ippool_id FROM billservice_tariff WHERE id=get_tarif(rs.account_id)))::boolean as guest_pool
                                    FROM radius_activesession AS rs WHERE rs.date_end IS NULL AND rs.date_start <= %s and session_status='ACTIVE';""", (dateAT, dateAT,))
                rows=cur.fetchall()
                cur.connection.commit()
                #try:
                #    sessions = convert(rosClient('10.10.1.100', 'admin', 'Wind0za', r"/queue/simple/getall"))
                for row in rows:
                    try:
                        rs = RadiusSession(*row)
                        result=None
                        nas = caches.nas_cache.by_ip.get(str(rs.nas_id))
                        acc = caches.account_cache.by_account.get(rs.account_id)
                        subacc = caches.subaccount_cache.by_id.get(rs.subaccount_id)
                        if not nas : continue
                        #Если не найден аккаунт или субаккаунт
                        if not (acc and subacc): continue
                        
                        if 0: assert isinstance(nas, NasData); assert isinstance(acc, AccountData)
                        

                        acstatus = acc.account_status==1 and acc.tarif_active==True and (((subacc.allow_vpn_with_null and acc.ballance+acc.credit >=0) or (subacc.allow_vpn_with_minus and acc.ballance+acc.credit<=0) or acc.ballance+acc.credit>0)\
                                    and \
                                    (subacc.allow_vpn_with_block or (not subacc.allow_vpn_with_block and not acc.balance_blocked and not acc.disabled_by_limit)))
                        acstatus_guest = rs.guest_pool and acc.account_status==1 and acc.tarif_active==True and (((subacc.allow_vpn_with_null and acc.ballance+acc.credit >=0) or (subacc.allow_vpn_with_minus and acc.ballance+acc.credit<=0) or acc.ballance+acc.credit>0)\
                                    and \
                                    (subacc.allow_vpn_with_block or (not subacc.allow_vpn_with_block and not acc.balance_blocked and not acc.disabled_by_limit)))
                        acstatus = acstatus and not acstatus_guest
                        if (acstatus or (rs.guest_pool and acstatus_guest==False)) and caches.timeperiodaccess_cache.in_period.get(acc.tarif_id):
                            #chech whether speed has changed
                            account_limit_speed = caches.speedlimit_cache.by_account_id.get(acc.account_id, [])
                            
                            accservices = []
                            addonservicespeed=[]  
                            if subacc:
                                accservices = caches.accountaddonservice_cache.by_subaccount.get(subacc.id, [])    
                                for accservice in accservices:                                 
                                    service = caches.addonservice_cache.by_id.get(accservice.service_id)                                
                                    if not accservice.deactivated  and service.change_speed:                                                                        
                                        addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.priority, service.min_tx, service.min_rx, service.speed_units, service.change_speed_type)                                    
                                        break   
                            if not addonservicespeed: 
                                accservices = caches.accountaddonservice_cache.by_account.get(acc.account_id, [])    
                                for accservice in accservices:                                 
                                    service = caches.addonservice_cache.by_id.get(accservice.service_id)                                
                                    if not accservice.deactivated  and service.change_speed:                                                                        
                                        addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.priority, service.min_tx, service.min_rx, service.speed_units, service.change_speed_type)                                    
                                        break    

                            speed = self.create_speed(caches.defspeed_cache.by_id.get(acc.tarif_id), caches.speed_cache.by_id.get(acc.tarif_id, []),account_limit_speed, addonservicespeed, acc.vpn_speed, dateAT)                            

                            speed = get_decimals_speeds(speed)
                            newspeed = ''.join([unicode(spi) for spi in speed])

                            if rs.speed_string != newspeed:                         
                                logger.debug("%s: about to change speed for: account:  %s| nas: %s | sessionid: %s", (self.getName(), acc.account_id, nas.id, str(rs.sessionid)))   
                                coa_result = change_speed(vars.DICT, acc, subacc, nas, 
                                                    access_type=str(rs.access_type),
                                                    format_string=str(nas.vpn_speed_action),session_id=str(rs.sessionid), vpn_ip_address=rs.framed_ip_address,
                                                    speed=speed)

                                if coa_result==True:
                                    cur.execute("""UPDATE radius_activesession SET speed_string=%s WHERE id=%s;
                                                """ , (newspeed, rs.id,))
                                    cur.connection.commit()
                                logger.debug("%s: speed change over: account:  %s| nas: %s | sessionid: %s", (self.getName(), acc.account_id, nas.id, str(rs.sessionid)))
                        else:
                            logger.debug("%s: about to send POD: account:  %s| nas: %s | sessionid: %s", (self.getName(), acc.account_id, nas.id, str(rs.sessionid)))
                            result = PoD(vars.DICT, acc, subacc, nas, access_type=rs.access_type, session_id=str(rs.sessionid), vpn_ip_address=rs.framed_ip_address, caller_id=str(rs.caller_id), format_string=str(nas.reset_action))
                            logger.debug("%s: POD over: account:  %s| nas: %s | sessionid: %s", (self.getName(), acc.account_id, nas.id, str(rs.sessionid)))

                        if result is True:
                            disconnect_result='ACK'
                        elif result is False:
                            disconnect_result='NACK'
                            
                        if result is not None:
                            cur.execute("""UPDATE radius_activesession SET session_status=%s, acct_terminate_cause='BILLING_POD_REQUEST' WHERE sessionid=%s;
                                        """, (disconnect_result, rs.sessionid,))
                            if rs.ipinuse_id and disconnect_result=='ACK':
                                cur.execute("""UPDATE billservice_ipinuse SET disabled=now() WHERE id=%s;
                                        """, ( rs.ipinuse_id,))                                
                            cur.connection.commit()  
                        
                        from_start = (dateAT-rs.date_start).seconds+(dateAT-rs.date_start).days*86400
                            
                        if (rs.time_from_last_update and rs.time_from_last_update+15>=nas.acct_interim_interval) or (not rs.time_from_last_update and from_start>=nas.acct_interim_interval+60):
                            cur.execute("""UPDATE radius_activesession SET session_status='NACK' WHERE sessionid=%s;
                                        """, (rs.sessionid,))
                            cur.connection.commit()               
                    
                    except Exception, ex:
                        logger.error("%s: row exec exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                        if isinstance(ex, vars.db_errors): raise ex
                cur.execute("UPDATE billservice_ipinuse SET disabled=now() WHERE dynamic=True and disabled is Null and ip::inet not in (SELECT DISTINCT framed_ip_address::inet FROM radius_activesession WHERE ipinuse_id is not NUll and (session_status='ACTIVE'));")    
                cur.connection.commit()   
                cur.close()
                logger.info("VPNALIVE: VPN thread run time: %s", time.clock() - a)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
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
    def iterate_ps(self, cur, caches, acc, ps, mult, dateAT, pss_type):
        account_ballance = (acc.ballance or 0) + (acc.credit or 0)
        susp_per_mlt = 1
        if pss_type == PERIOD:
            susp_per_mlt = 0 if not acc.current_acctf or caches.suspended_cache.by_account_id.has_key(acc.account_id) else 1
            
            time_start_ps = acc.datetime if ps.autostart else ps.time_start
            
            self.NOW = dateAT if acc.current_acctf else acc.end_date
            #Если в расчётном периоде указана длина в секундах-использовать её, иначе использовать предопределённые константы
            period_start, period_end, delta = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, self.NOW)                                
            # Проверка на расчётный период без повторения
            if period_end < self.NOW: return
            get_last_checkout_ = get_last_checkout
        elif pss_type == ADDON:
            if ps.temporary_blocked:
                susp_per_mlt = 0
            time_start_ps = ps.created
            self.NOW = dateAT if not ps.deactivated else ps.deactivated
            period_start, period_end, delta = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, self.NOW) 
            get_last_checkout_ = get_last_addon_checkout
        else:
            return
        s_delta = datetime.timedelta(seconds=delta)
        
        if ps.cash_method == "GRADUAL":
            last_checkout = get_last_checkout_(cur, ps.ps_id, acc.acctf_id, acc.end_date)  
            logger.debug('%s: Periodical Service: GRADUAL last checkout %s for account: %s service:%s type:%s', (self.getName(), last_checkout, acc.account_id, ps.ps_id, pss_type))                                  
            if last_checkout is None:
                if pss_type == PERIOD:
                    #Если списаний по этой услуге не было - за дату начала списания берём дату подключения пользователя на тариф.
                    last_checkout = acc.datetime if ps.created is None or ps.created < period_start else ps.created
                    
                elif pss_type == ADDON:
                    last_checkout = ps.created
                logger.debug('%s: Periodical Service: GRADUAL last checkout is None set last checkout=%s for account: %s service:%s type:%s', (self.getName(), last_checkout, acc.account_id, ps.ps_id, pss_type))
            
            if (self.NOW - last_checkout).seconds + (self.NOW - last_checkout).days*SECONDS_PER_DAY >= self.PER_DAY:
                #Проверяем наступил ли новый период
                if self.NOW - self.PER_DAY_DELTA <= period_start:
                    # Если начался новый период
                    # Находим когда начался прошльый период
                    # Смотрим сколько денег должны были снять за прошлый период и производим корректировку
                    #period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=length_in_sp, now=now-datetime.timedelta(seconds=n))
                    pass
                
                # Смотрим сколько раз уже должны были снять деньги
                lc = self.NOW - last_checkout
                last_checkout_seconds = lc.seconds + lc.days*SECONDS_PER_DAY
                nums,ost = divmod(last_checkout_seconds,self.PER_DAY)                                        
                chk_date = last_checkout + self.PER_DAY_DELTA
                if nums>1 or not acc.current_acctf:
                    #Смотрим на какую сумму должны были снять денег и снимаем её
                    while chk_date <= self.NOW:    
                        period_start, period_end, delta = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)                                            
                        cash_summ = mult*((self.PER_DAY * vars.TRANSACTIONS_PER_DAY * ps.cost) / (delta * vars.TRANSACTIONS_PER_DAY))
                        if pss_type == PERIOD:
                            #cur.execute("UPDATE billservice_account SET ballance=ballance-")
                            cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s) as new_summ;", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_GRADUAL', cash_summ, chk_date, ps.condition))
                            new_summ=cur.fetchone()[0]
                            #cur.execute("UPDATE billservice_account SET ballance=ballance-%s WHERE id=%s;", (new_summ, acc.account_id,))
                            
                            logger.debug('%s: Periodical Service: GRADUAL BATCH iter checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, new_summ))                            
                        elif pss_type == ADDON:
                            cash_summ = cash_summ * susp_per_mlt
                            addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_GRADUAL', cash_summ, chk_date)
                            logger.debug('%s: Addon Service Checkout thread: GRADUAL BATCH iter checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))
                        cur.connection.commit()
                        chk_date += self.PER_DAY_DELTA
                else:
                    #make an approved transaction
                    cash_summ = mult*(susp_per_mlt * (self.PER_DAY * vars.TRANSACTIONS_PER_DAY * ps.cost) / (delta * vars.TRANSACTIONS_PER_DAY))
                    if pss_type == PERIOD:
                        #if (ps.condition==1 and account_ballance<=0) or (ps.condition==2 and account_ballance>0) or (ps.condition==3 and account_ballance<=0):
                            #ps_condition_type 0 - Всегда. 1- Только при положительном балансе. 2 - только при орицательном балансе
                        #    cash_summ = 0
                        #ps_history(cur, ps.ps_id, acc.acctf_id, acc.account_id, 'PS_GRADUAL', cash_summ, chk_date)
                        cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s) as new_summ;", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_GRADUAL', cash_summ, chk_date, ps.condition))
                        new_summ=cur.fetchone()[0]
                        #cur.execute("UPDATE billservice_account SET ballance=ballance-%s WHERE id=%s;", (new_summ, acc.account_id,))
                        logger.debug('%s: Periodical Service: Gradual checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, new_summ))                            
                    elif pss_type == ADDON:
                        cash_summ = cash_summ * susp_per_mlt
                        addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_GRADUAL', cash_summ, chk_date)
                        logger.debug('%s: Addon Service Checkout thread: AT START checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))
            cur.connection.commit()
            
        if ps.cash_method == "AT_START":
            """
            Смотрим когда в последний раз платили по услуге. Если в текущем расчётном периоде
            не платили-производим снятие.
            """
            
            """
            Списывать в начале периода только, если последнее списание+период<следующего тарифного плана
            """
            last_checkout = get_last_checkout_(cur, ps.ps_id, acc.acctf_id, acc.end_date)
            # Здесь нужно проверить сколько раз прошёл расчётный период
            # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
            # Для последней проводки ставим статус Approved=True
            # для всех сотальных False
            # Если последняя проводка меньше или равно дате начала периода-делаем снятие
            
            summ = 0
            if pss_type == PERIOD:
                #если не (указано начало периода или начало услуги меньше начала текущего периода) или (указано начало услуги и дата подключения на тариф больше или равна началу действия услуги 
                if (last_checkout is None and ps.created is not None and period_start<ps.created):
                    return
                first_time = False
                if last_checkout is None:
                    last_checkout = acc.datetime if ps.created is None or ps.created < period_start else ps.created
                    first_time = True
            elif pss_type == ADDON:
                #print "addon AT_START"
                first_time = False
                if last_checkout is None:
                    last_checkout = ps.created
                    first_time = True
                
            #if (first_time or (ps.created or last_checkout) <= period_start) or (not first_time and last_checkout < period_start):
            if first_time or last_checkout < period_start:
                cash_summ = ps.cost

                chk_date = last_checkout
                period_end_ast= None
                #Смотрим на какую сумму должны были снять денег и снимаем её 
                if not first_time:
                    period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)
                    s_delta_ast = datetime.timedelta(seconds=delta_ast)
                    time_start_ps = period_start_ast + s_delta_ast
                    chk_date = period_start_ast + s_delta_ast
                    
                while True:
                    #Если тариф закрыт, а доснятие за прошлый расчётный период произошло-прерываем цикл
                    if acc.end_date and acc.end_date == period_end_ast:
                        break
                    cash_summ = mult*ps.cost
                    period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)
                    s_delta_ast = datetime.timedelta(seconds=delta_ast)
                    chk_date = period_start_ast
                    delta_coef=1
                    if vars.USE_COEFF_FOR_PS==True and first_time and ((period_end_ast-acc.datetime).days*86400+(period_end_ast-acc.datetime).seconds)<delta_ast:
                        logger.warning('%s: Periodical Service: %s Use coeff for ps account: %s', (self.getName(), ps.ps_id, acc.account_id))
                        delta_coef=float((period_end_ast-acc.datetime).days*86400+(period_end_ast-acc.datetime).seconds)/float(delta_ast)        
                        cash_summ=cash_summ*Decimal(str(delta_coef))
                                
                    if ps.created and ps.created >= chk_date and not last_checkout == ps.created:
                        cash_summ = 0
                    if pss_type == PERIOD:
                        cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s) as new_summ;", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_AT_START', cash_summ, chk_date, ps.condition))
                        new_summ=cur.fetchone()[0]
                        #cur.execute("UPDATE billservice_account SET ballance=ballance-%s WHERE id=%s;", (new_summ, acc.account_id,))
                        logger.debug('%s: Periodical Service: AT START iter checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, new_summ))
                    elif pss_type == ADDON:
                        cash_summ = cash_summ * susp_per_mlt
                        addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_AT_START', cash_summ, chk_date)
                        logger.debug('%s: Addon Service Checkout thread: GRADUAL checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))                        
                    cur.connection.commit()
                    chk_date += s_delta_ast
                    first_time=False
                    if chk_date > period_start: break
            cur.connection.commit()
        if ps.cash_method=="AT_END":
            """
            Смотрим завершился ли хотя бы один расчётный период.
            Если завершился - считаем сколько уже их завершилось.    
            для остальных со статусом False
            """
            last_checkout = get_last_checkout_(cur, ps.ps_id, acc.acctf_id, acc.end_date)
            cur.connection.commit()
            #first_time, last_checkout = (True, now) if last_checkout is None else (False, last_checkout)
            if pss_type == PERIOD:
                if (last_checkout is None and ps.created is not None and period_end<ps.created):
                    return
                first_time = False
                if last_checkout is None:
                    last_checkout = period_start if ps.created is None or ps.created < period_start else ps.created
                    first_time = True
            elif pss_type == ADDON:
                first_time = False
                if last_checkout is None:
                    last_checkout = ps.created
                    first_time = True
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
                if not first_time:
                    period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, last_checkout)
                    s_delta_ast = datetime.timedelta(seconds=delta_ast)
                    chk_date = period_end_ast
                    time_start_ps = period_start_ast
                while True:
                    cash_summ = mult*ps.cost
                    period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)
                    if period_start_ast>period_start: break
                    s_delta_ast = datetime.timedelta(seconds=delta_ast)
                    if vars.USE_COEFF_FOR_PS==True and ((period_end_ast-acc.datetime).days*86400+(period_end_ast-acc.datetime).seconds)<delta_ast:
                        logger.debug('%s: Periodical Service: %s Use coeff for ps account: %s', (self.getName(), ps.ps_id, acc.account_id))
                        delta_coef=float((period_end_ast-acc.datetime).days*86400+(period_end_ast-acc.datetime).seconds)/float(delta_ast)        
                        cash_summ=cash_summ*Decimal(str(delta_coef))
                        
                    if first_time:
                        first_time = False
                        chk_date = last_checkout
                        tr_date = period_start_ast
                        if pss_type == PERIOD:
                            ps_history(cur, ps.ps_id, acc.acctf_id, acc.account_id, 'PS_AT_END', ZERO_SUM, tr_date)
                            logger.debug('%s: Periodical Service: AT END First time checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, new_summ))
#                            cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s);", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_GRADUAL', cash_summ, chk_date, ps.condition))
                        elif pss_type == ADDON:
                            addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_AT_END', ZERO_SUM, tr_date)
                            logger.debug('%s: Addon Service Checkout: AT END First time checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, new_summ))
                    else:
                        if ps.created and ps.created >= chk_date and not last_checkout == ps.created:
                            cash_summ = ZERO_SUM
                        if pss_type == PERIOD:
                            tr_date = chk_date
                            if acc.end_date and acc.end_date < chk_date:
                                cash_summ = 0
                                tr_date = acc.end_date
                            cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s) as new_summ;", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_AT_END', cash_summ, tr_date, ps.condition))
                            new_summ=cur.fetchone()[0]
                            #cur.execute("UPDATE billservice_account SET ballance=ballance-%s WHERE id=%s;", (new_summ, acc.account_id,))
                            logger.debug('%s: Periodical Service: AT END iter checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, new_summ))
                        elif pss_type == ADDON:
                            cash_summ = cash_summ * susp_per_mlt
                            tr_date = chk_date
                            if ps.deactivated and ps.deactivated < chk_date:
                                #сделать расчёт остатка
                                cash_summ = 0
                                tr_date = ps.deactivated
                            addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_AT_END', cash_summ, tr_date)
                            logger.debug('%s: Addon Service Checkout thread: AT END checkout for account: %s service:%s summ %s', (self.getName(), acc.account_id, ps.ps_id, cash_summ))
                    cur.connection.commit()
                    chk_date = period_end_ast
                    if chk_date-SECOND > period_start: break
            #cur.connection.commit()
            
        if pss_type == ADDON and ps.deactivated and dateAT >= ps.deactivated:
            cur.execute("UPDATE billservice_accountaddonservice SET last_checkout = deactivated WHERE id=%s", (ps.ps_id,))
        #if pss_type == ZERO_SUM and ps.deactivated and dateAT >= ps.deactivated:
        #    cur.execute("UPDATE billservice_periodicalservice SET deleted = True WHERE id=%s;", (ps.ps_id,))

            #cur.connection.commit()
    
    def run(self):
        global cacheMaster, fMem, suicideCondition, transaction_number, vars
        self.connection = get_connection(vars.db_dsn)
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        while True:
            a_ = time.clock()
            try:
                if suicideCondition[self.__class__.__name__]: break
                a = time.clock()

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
                
                self.PER_DAY = SECONDS_PER_DAY / vars.TRANSACTIONS_PER_DAY
                self.PER_DAY_DELTA = datetime.timedelta(seconds=self.PER_DAY)
                self.NOW = dateAT
                #get a list of tarifs with periodical services & loop                
                for row in caches.periodicaltarif_cache.data:
                    tariff_id, settlement_period_id = row
                    #debit every account for tarif on every periodical service
                    for ps in caches.periodicalsettlement_cache.by_id.get(tariff_id,[]):
                        if 0: assert isinstance(ps, PeriodicalServiceSettlementData)
                        for acc in itertools.chain(caches.account_cache.by_tarif.get(tariff_id,[]), \
                                                   caches.underbilled_accounts_cache.by_tarif.get(tariff_id, [])):
                            if 0: assert isinstance(acc, AccountData)
                            try:
                                if acc.acctf_id is None: continue
                                mult=1
                                if acc.account_status in [2,4]:
                                    mult=0
                                self.iterate_ps(cur, caches, acc, ps, mult, dateAT, PERIOD)
                                
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
                        logger.warning('%s: Addon Periodical Service: %s Account not found: %s', (self.getName(), addon_ps.ps_id, addon_ps.account_id))
                    mult=1
                    if acc.account_status in [2,4]:
                        mult=0                   
                    try:
                        self.iterate_ps(cur, caches, acc, addon_ps, mult, dateAT, ADDON)
                    except Exception, ex:
                        logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                        if ex.__class__ in vars.db_errors: raise ex
                    cur.connection.commit()
                        
                
                if caches.underbilled_accounts_cache.underbilled_acctfs:
                    cur.execute("""UPDATE billservice_accounttarif SET periodical_billed=TRUE WHERE id IN (%s);""" % \
                                ' ,'.join((str(i) for i in caches.underbilled_accounts_cache.underbilled_acctfs)))
                    cur.connection.commit()
                cur.close()
                logger.info("PSALIVE: Period. service thread run time: %s", time.clock() - a)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(abs(vars.PERIODICAL_SLEEP-(time.clock()-a_)) + random.randint(0,5))
            
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
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        accounts_bytes_cache={} # account_id: date_start_date_end, bytes_in, bytes_out
        while True:
            try:
                if suicideCondition[self.__class__.__name__]:
                    try: self.connection.close()
                    except: pass
                    break
                a = time.clock()
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
                cur.execute("""SELECT rs.id, rs.account_id, rs.sessionid, rs.session_time, rs.bytes_in, rs.bytes_out, rs.interrim_update, rs.date_start, rs.date_end, tarif.time_access_service_id, tarif.radius_traffic_transmit_service_id, tarif.id, acc_t.id, rs.lt_time, rs.lt_bytes_in, rs.lt_bytes_out,rs.nas_port_id,rs.nas_int_id  
                                 FROM radius_activesession AS rs
                                 JOIN billservice_accounttarif AS acc_t ON acc_t.id=(SELECT id FROM billservice_accounttarif WHERE account_id=rs.account_id and datetime<rs.date_start ORDER BY datetime DESC LIMIT 1) 
                                 JOIN billservice_tariff AS tarif ON tarif.id=acc_t.tarif_id
                                 WHERE ((rs.lt_time<rs.session_time and tarif.time_access_service_id is not null) or (rs.lt_bytes_in<rs.bytes_in and rs.lt_bytes_out<rs.bytes_out and tarif.radius_traffic_transmit_service_id is not null))
                                  ORDER BY rs.interrim_update ASC LIMIT 20000;""")
                rows=cur.fetchall()
                cur.connection.commit()
                now = dateAT
                for row in rows:
                    rs = BillSession(*row)
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
                    if acc.time_access_service_id:
                        logger.debug("RADCOTHREAD: Time tarification session: %s", rs.sessionid)
                        old_time = rs.lt_time or 0
                        logger.debug("RADCOTHREAD: Old session time: %s %s", (rs.sessionid, old_time))
    #                    old_time = old_time[0] if old_time else 0
                        
                        total_time = rs.session_time - old_time
                        logger.debug("RADCOTHREAD: Tarification time for session: %s %s", (rs.sessionid, total_time))
                        if rs.date_end:
                            taccs_service = caches.timeaccessservice_cache.by_id.get(rs.taccs_id)
                            logger.debug("RADCOTHREAD: Tarification time of end session : %s", (rs.sessionid, ))
                            if taccs_service.rounding:
                                logger.debug("RADCOTHREAD: Rounding session time : %s", (rs.sessionid, ))
                                if taccs_service.tarification_step>0:
                                    total_time = divmod(total_time, taccs_service.tarification_step)[1]*taccs_service.tarification_step+taccs_service.tarification_step
                        logger.debug("RADCOTHREAD: Searching for prepaid time for session : %s", (rs.sessionid, ))
                        cur.execute("""SELECT id, size FROM billservice_accountprepaystime WHERE account_tarif_id=%s and prepaid_time_service_id=%s and current=True""", (rs.acctf_id,rs.taccs_id,))
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
                        for period in caches.timeaccessnode_cache.by_id.get(rs.taccs_id, []):
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
                                        db.timetransaction_fn(cur, rs.taccs_id, rs.acctf_id, rs.account_id, summ, now, unicode(rs.sessionid), rs.interrim_update)
                                        cur.connection.commit()
                                        logger.debug("RADCOTHREAD: Time for session %s was checkouted", (rs.sessionid, ))
                                    break
                        cur.execute("""UPDATE radius_activesession SET lt_time=%s
                                       WHERE date_start=%s AND account_id=%s AND sessionid=%s and nas_port_id=%s and and nas_int_id=%s
                                    """, (rs.session_time, rs.date_start, rs.account_id, unicode(rs.sessionid),rs.nas_port_id, rs.nas_int_id))
                        checkouted=True
                        logger.debug("RADCOTHREAD: Session %s was checkouted (Time)", (rs.sessionid, ))
                        cur.connection.commit()  
                    #
                    if acc.radius_traffic_transmit_service_id:  
                        logger.debug("RADCOTHREAD: Traffic tarification session: %s", rs.sessionid)
                        radius_traffic = caches.radius_traffic_transmit_service_cache.by_id.get(acc.radius_traffic_transmit_service_id)
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
                        if self.get_actual_prices(caches.radius_traffic_node_cache.by_id.get(rs.traccs_id, [])) and acc.settlement_period_id:
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
                        for period in self.valued_prices(total_bytes_value,caches.radius_traffic_node_cache.by_id.get(rs.traccs_id, [])):
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
                                        cur.execute("""INSERT INTO billservice_traffictransaction(
                                                        account_id, accounttarif_id, summ, 
                                                        created, radiustraffictransmitservice_id)
                                                        VALUES ( %s, %s, %s, %s, 
                                                        %s);
                                                """, (rs.account_id, rs.acctf_id, summ, now, rs.traccs_id))
                                        cur.connection.commit()
                                    break
                            cur.execute("""UPDATE radius_activesession SET lt_bytes_in=%s, lt_bytes_out=%s
                                           WHERE date_start=%s and account_id=%s AND sessionid=%s and nas_port_id=%s and nas_int_id=%s
                                        """, (rs.bytes_in, rs.bytes_out, rs.date_start, rs.account_id, unicode(rs.sessionid), rs.nas_port_id, rs.nas_int_id))
                            cur.connection.commit()  
                            checkouted=True
                            logger.debug("RADCOTHREAD: Session %s was checkouted (Traffic)", (rs.sessionid, ))
                    if checkouted==False:
                        logger.debug("RADCOTHREAD: Session %s was not tarificated", (rs.sessionid, ))
                                
                cur.connection.commit()
                cur.close()
                logger.info("TIMEALIVE: Time access thread run time: %s", time.clock() - a)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
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
                a = time.clock()
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
                for acc in caches.account_cache.data:
                    if 0: assert isinstance(acc, AccountData)
                    if not acc.account_status == 1: continue
                    limits = caches.trafficlimit_cache.by_id.get(acc.tarif_id, [])
                    if not limits:
                        if acc.disabled_by_limit:
                            cur.execute("""UPDATE billservice_account SET disabled_by_limit=False WHERE id=%s;""", (acc.account_id,))
                        cur.execute("""DELETE FROM billservice_accountspeedlimit WHERE account_id=%s;""", (acc.account_id,))
                        cur.connection.commit()
                        continue
                    block, speed_changed = (False, False)
                    for limit in limits:
                        if 0: assert isinstance(limit, TrafficLimitData)
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
                        if 0: assert isinstance(sp, SettlementPeriodData)
                        
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
                logger.info("LMTALIVE: %s: run time: %s", (self.getName(), time.clock() - a))
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
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
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        while True:            
            try:
                if suicideCondition[self.__class__.__name__]:
                    try:    self.connection.close()
                    except: pass
                    break
                a = time.clock()
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
                            sql = """
                            INSERT INTO billservice_addonservicetransaction(
                                        service_id, service_type, account_id, accountaddonservice_id, 
                                        accounttarif_id, type_id, summ, created)
                                VALUES (%s, 'onetime', %s, %s, 
                                        %s, '%s', %s, '%s')

                            """ % (service.id, acc.account_id, accountaddonservice.id, acc.acctf_id, "ADDONSERVICE_ONETIME", service.cost, dateAT,)
                            cur.execute(sql)
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
                        if (not accountaddonservice.deactivated and not deactivated) and \
                        (service.action and not accountaddonservice.action_status) and \
                        not accountaddonservice.temporary_blocked and \
                         ((service.deactivate_service_for_blocked_account==False) or (service.deactivate_service_for_blocked_account==True and ((acc.ballance+acc.credit)>0 and acc.disabled_by_limit==False and acc.balance_blocked==False and acc.account_status==1 ))):
                            #выполняем service_activation_action
                            cur.connection.commit()
                            sended = cred(acc, subacc, 'ipn', nas, format_string=service.service_activation_action)
                            if sended is True: cur.execute("UPDATE billservice_accountaddonservice SET action_status=%s WHERE id=%s" % (True, accountaddonservice.id))
                        
                        if (accountaddonservice.deactivated or accountaddonservice.temporary_blocked or deactivated or (service.deactivate_service_for_blocked_account==True and ((acc.ballance+acc.credit)<=0 or acc.disabled_by_limit==True or acc.balance_blocked==True or acc.account_status!=1 ))) and accountaddonservice.action_status==True:
                            #выполняем service_deactivation_action
                            cur.connection.commit()
                            sended = cred(acc, subacc, 'ipn', nas, format_string=service.service_deactivation_action)
                            if sended is True: cur.execute("UPDATE billservice_accountaddonservice SET action_status=%s WHERE id=%s" % (False, accountaddonservice.id))

                    cur.connection.commit()
                cur.connection.commit()
                cur.close()                
                logger.info("Addon Service: %s: run time: %s", (self.getName(), time.clock() - a))
            except Exception, ex:
                cur.connection.rollback()
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
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
                a = time.clock()
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
                            if 0: assert isinstance(sp, SettlementPeriodData)
                            time_start = acc.datetime if sp.autostart else sp.time_start
                            period_start, period_end, delta = fMem.settlement_period_(time_start, sp.length_in, sp.length, dateAT)
                            #Если начало расчётного периода осталось в прошлом тарифном плане-за начало расчётного периода принимаем начало тарифного плана
                            if period_start < acc.datetime: period_start = acc.datetime                            
    
                        #нужно производить в конце расчётного периода
                        ballance_checkout = shedl.ballance_checkout if shedl.ballance_checkout else acc.datetime
                        if acc.username=='23521':
                            pass
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
                        #Если балланса не хватает - отключить пользователя
                        if (shedl.balance_blocked is None or shedl.balance_blocked<=period_start) and acc.cost>=account_balance \
                         and acc.cost != 0 and acc.require_tarif_cost and not acc.balance_blocked:
                            '''cur.execute("""SELECT transaction_block_sum(%s, %s::timestamp without time zone, %s::timestamp without time zone);""",
                                          (acc.account_id, period_start, now))'''
                            #cur.execute("""SELECT transaction_sum(%s, %s, %s::timestamp without time zone, %s::timestamp without time zone);""",
                            #              (acc.account_id, acc.acctf_id, period_start, now))
                            #cur.execute("SELECT balance FROM billservice_balancehistory WHERE datetime<%s  and account_id=%s ORDER BY datetime DESC limit 1", (now,acc.account_id,))
                            #pstart_balance = (cur.fetchone()[0] or 0) + account_balance
                            #pstart_balance = (cur.fetchone()[0] or 0)
                            #if acc.cost > pstart_balance:
                            if acc.cost > (acc.ballance + acc.credit):
                                cur.execute("SELECT shedulelog_blocked_fn(%s, %s, %s::timestamp without time zone, %s);", 
                                            (acc.account_id, acc.acctf_id, now, acc.cost))
                            cur.connection.commit()
                            
                        if acc.balance_blocked and (account_balance >= acc.cost or not acc.require_tarif_cost):
                            """Если пользователь отключён, но баланс уже больше разрешённой суммы-включить пользователя"""
                            '''cur.execute("""SELECT transaction_block_sum(%s, %s::timestamp without time zone, %s::timestamp without time zone);""",
                                          (acc.account_id, period_start, now))'''
                            #cur.execute("""SELECT transaction_sum(%s, %s, %s::timestamp without time zone, %s::timestamp without time zone);""",
                            #              (acc.account_id, acc.acctf_id, period_start, now))
                            #pstart_balance = (cur.fetchone()[0] or 0) + account_balance
                            #pstart_balance = (cur.fetchone()[0] or 0)
                            #if acc.cost <= pstart_balance:
                            #if acc.cost <= (pstart_balance + acc.ballance + acc.credit):
                            cur.execute("""UPDATE billservice_account SET balance_blocked=False WHERE id=%s;""", (acc.account_id,))                            
                            cur.connection.commit()
                        
                        #print repr(acc)
                        reset_traffic = caches.traffictransmitservice_cache.by_id.get(acc.traffic_transmit_service_id, (None, None))[1]                        
                        radius_traffic = caches.radius_traffic_transmit_service_cache.by_id.get(acc.radius_traffic_transmit_service_id)
                        prepaid_traffic_reset = shedl.prepaid_traffic_reset if shedl.prepaid_traffic_reset else acc.datetime
                        prepaid_radius_traffic_reset = shedl.prepaid_radius_traffic_reset if shedl.prepaid_radius_traffic_reset else acc.datetime
                        #if (reset_traffic or acc.traffic_transmit_service_id is None) and (shedl.prepaid_traffic_reset is None or shedl.prepaid_traffic_reset<period_start or acc.acctf_id!= shedl.accounttarif_id):
                        need_traffic_reset=(reset_traffic and prepaid_traffic_reset<period_start) or not acc.traffic_transmit_service_id or acc.acctf_id != shedl.accounttarif_id
                        need_radius_traffic_reset=(radius_traffic and prepaid_radius_traffic_reset<period_start) or not acc.radius_traffic_transmit_service_id or acc.acctf_id != shedl.accounttarif_id

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
                                    (acc.account_id, acc.acctf_id, acc.traffic_transmit_service_id, need_traffic_reset, delta_coef, now))
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
                        need_time_reset = (reset_time or acc.time_access_service_id is None) and (shedl.prepaid_time_reset is None or (shedl.prepaid_time_reset if shedl.prepaid_time_reset else period_start<period_start) or acc.acctf_id!=shedl.accounttarif_id)   
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
                                    cur.execute("INSERT INTO billservice_onetimeservicehistory(accounttarif_id, onetimeservice_id, account_id, summ, created) VALUES(%s, %s, %s, %s, %s);", (acc.acctf_id, ots.id, acc.account_id, ots.cost, now,))
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
                                    (end_promise<now() or (SELECT sum(summ*(-1)) FROM billservice_transaction WHERE account_id=account_id and type_id!='PROMISE_PAYMENT' and summ<0 and created>created)>=summ)""")
                promises = cur.fetchall()

                if promises:
                    cur.execute("""
                            INSERT INTO billservice_transaction(bill, account_id, type_id, approved, summ, description, created, promise_expired) 
                            SELECT id,account_id, 'PROMISE_DEBIT', approved, (-1)*summ, description, now(), True
                              FROM billservice_transaction as tr
                              WHERE tr.id in (%s);
                    """ % ', '.join([str(x[0]) for x in promises]))
                    
                cur.execute("""UPDATE billservice_transaction as tr SET promise_expired = True 
                                WHERE id in (%s);""" % ', '.join([str(x[0]) for x in promises]))
                cur.connection.commit()
                for account in caches.account_cache.data:
                    if account.account_status==4:
                        sps=caches.suspended_cache.by_account_id.get(acc.account_id,[])
                        for sp in sps:
                            if sp.end_date and sp.start_date+account.userblock_max_days>=dateAT:
                                
                                """
                                Запрос должен быть именно такого вида, чтобы не допустить двойной установки статуса
                                UPDATE billservice_account SET status=1 WHERE id=%s and status=4;
                                """
                                cur.execute("UPDATE billservice_account SET status=1 WHERE id=%s and status=4;", (account.account_id,))
                                cur.connection.commit()
                        
                logger.info("SPALIVE: %s run time: %s", (self.getName(), time.clock() - a))
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
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
        
    def create_speed(self, default, speeds,  correction, addonservicespeed, speed, date_):        
        """
        Функция форматирования строки для изменения скорости
        """
        result_params=speeds        
        if speed=='':   
            """
            Если в профиле пользователя не указаны конкретные настройки скорости, получаем их
            """         
            defaults = default            
            speeds   =  result_params            
            defaults = defaults[:6] if defaults else ["0/0","0/0","0/0","0/0","8","0/0"]            
            result=[]            
            min_delta, minimal_period = -1, []            
            now=date_            
            for speed in speeds:                
                #Определяем составляющую с самым котортким периодом из всех, которые папали в текущий временной промежуток
                tnc,tkc,delta,res = fMem.in_period_(speed[6],speed[7],speed[8], now)                
                if res==True and (delta<min_delta or min_delta==-1):                    
                    minimal_period=speed                    
                min_delta=delta            
            
            minimal_period = minimal_period[:6] if minimal_period else ["0/0","0/0","0/0","0/0","","0/0"]            
            for k in xrange(0, 6):                
                s=minimal_period[k]                
                if s=='0/0' or s=='/' or s=='':                    
                    res=defaults[k]                
                else:                    
                    res=s                
                result.append(res)   #Проводим корректировку скорости в соответствии с лимитом            
            result = get_corrected_speed(result, correction)            
            if addonservicespeed:                
                result = get_corrected_speed(result, addonservicespeed)                        
            if result==[]:                 
                result = defaults if defaults else ["0/0","0/0","0/0","0/0","8","0/0"]                            
            
            return result
        else:
            try:
                return parse_custom_speed_lst(acc.ipn_speed)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s Can not parse account speed %s", (self.getName(), repr(ex), traceback.format_exc()), acc.ipn_speed)
                return ["0/0","0/0","0/0","0/0","8","0/0"]           
           
    
      
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
                a = time.clock()

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
                        #if acc.ipn_ip_address != '0.0.0.0':
                        if acc.nas_id:
                            access_list.append(('', '', '', '', acc.nas_id, True, None))
                            
                        for subacc in subaccounts:
                            if not subacc.nas_id or (subacc.ipn_ip_address=='0.0.0.0' and subacc.ipn_mac_address==''): continue
                            access_list.append((subacc.id, subacc.ipn_ip_address,  subacc.ipn_mac_address, subacc.vpn_ip_address, subacc.nas_id, False,  subacc))
                        #if not acc.tarif_active or acc.ipn_ip_address == '0.0.0.0' and '0.0.0.0' in [[x.ipn_ip_address, x.nas_id] if x is not '0.0.0.0' else 1 for x in subaccounts]: continue
                        accps = caches.accessparameters_cache.by_id.get(acc.access_parameters_id)
                        if (not accps) or (not accps.ipn_for_vpn): continue
                        if 0: assert isinstance(accps, AccessParametersData)
                        account_ballance = (acc.ballance or 0) + (acc.credit or 0)
                        period = caches.timeperiodaccess_cache.in_period[acc.tarif_id]# True/False
                        for id, ipn_ip_address, ipn_mac_address, vpn_ip_address, nas_id, legacy, subacc in access_list:
                            sended, recreate_speed = (None, False)
                            
                            nas = caches.nas_cache.by_id.get(nas_id)
                            
                            if not nas:
                                logger.info("IPNALIVE: %s: nas not set for account/subaccount/service %s/%s", (self.getName(), repr(acc), repr(subacc),))
                                continue
                            if 0: assert isinstance(nas, NasData)
                            access_type = 'IPN'
                            #now = datetime.datetime.now()
                            now = dateAT
                            # Если на сервере доступа ещё нет этого пользователя-значит добавляем.
                            if not acc.ipn_added and acc.tarif_active and legacy:
                                #sended = cred(acc, subacc, access_type, nas, format_string=nas.user_add_action)
                                sended = cred(acc, {}, '', nas, format_string=nas.user_add_action)
                                if sended is True and legacy: cur.execute("UPDATE billservice_account SET ipn_added=%s WHERE id=%s" % (True, acc.account_id))
                                acc = acc._replace(ipn_added=sended)
                            if subacc and not subacc.ipn_added and acc.tarif_active and not legacy:
                                sended = cred(acc, subacc, access_type, nas, format_string=nas.subacc_add_action)
                                
                                if sended is True: cur.execute("UPDATE billservice_subaccount SET ipn_added=%s WHERE id=%s" % (True, id))
                                subacc = subacc._replace(ipn_added=sended)    
                            if legacy and (not acc.ipn_status) and ( (account_ballance>0 or (account_ballance==0 and acc.allow_ipn_with_null==True) or (account_ballance<0 and acc.allow_ipn_with_minus==True) ) and period and acc.account_status == 1 and ((not acc.disabled_by_limit and not acc.balance_blocked) or acc.allow_ipn_with_block==True)) and acc.tarif_active:
                                """
                                acc.ipn_status - отображает активна или неактивна ACL запись на сервере доступа для абонента
                                """
                                #шлём команду, на включение пользователя, account_ipn_status=True
                                #ipn_added = acc.ipn_added
                                """Делаем пользователя enabled"""
        
                                #sended = cred(acc, subacc, access_type, nas, format_string=nas.user_enable_action)
                                sended = cred(acc, {}, '', nas, format_string=nas.user_enable_action)
                                recreate_speed = True                        
                                if sended is True and legacy: cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s" % (True, acc.account_id))
                                acc = acc._replace(ipn_status=True)
                            elif subacc and subacc.ipn_enabled==False and ( (account_ballance>0 or (account_ballance==0 and subacc.allow_ipn_with_null==True) or (account_ballance<0 and subacc.allow_ipn_with_minus==True) ) and period and acc.account_status == 1 and ((not acc.disabled_by_limit and not acc.balance_blocked) or acc.allow_ipn_with_block==True)) and acc.tarif_active and not legacy:
                                sended = cred(acc, subacc, access_type, nas, format_string=nas.subacc_enable_action)
                                if sended is True and not legacy: cur.execute("UPDATE billservice_subaccount SET ipn_enabled=%s WHERE id=%s" % (True, id))
                                subacc = subacc._replace(ipn_enabled=True)
                            elif legacy and acc.ipn_status and (((acc.disabled_by_limit or acc.balance_blocked) and acc.allow_ipn_with_block==False) or ((account_ballance<0 and acc.allow_ipn_with_minus==False) or (account_ballance==0 and acc.allow_ipn_with_null==False)) or period is False or acc.account_status != 1 or not acc.tarif_active):
                                #шлём команду на отключение пользователя,account_ipn_status=False
                                #sended = cred(acc, subacc, access_type, nas, format_string=nas.user_disable_action)
                                sended = cred(acc, {}, '', nas, format_string=nas.user_disable_action)    
                                if sended is True and legacy: cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s", (False, acc.account_id,))
                                acc = acc._replace(ipn_status=False)
                            elif not legacy and subacc.ipn_enabled is not False and subacc and (((acc.disabled_by_limit or acc.balance_blocked) and subacc.allow_ipn_with_block==False) or ((account_ballance<0 and subacc.allow_ipn_with_minus==False) or (account_ballance==0 and subacc.allow_ipn_with_null==False)) or period is False or acc.account_status != 1 or not acc.tarif_active):
                                #шлём команду на отключение пользователя,account_ipn_status=False
                                sended = cred(acc, subacc, access_type, nas, format_string=nas.subacc_disable_action)    
                                if sended is True: cur.execute("UPDATE billservice_subaccount SET ipn_enabled=%s WHERE id=%s", (False, id,))                            
                                subacc = subacc._replace(ipn_enabled=False)
                            cur.connection.commit()
        
                            #Приступаем к генерации настроек скорости
                            #Получаем настройки скорости по лимитам, если пользователь превысил какой-нибудь лимит.
                            account_limit_speed = caches.speedlimit_cache.by_account_id.get(acc.account_id, [])
                            
                            #TODO: caches.defspeed_cache.by_id - нужно же брать по tarif_id!! Это верно?? 
                            #Получаем подключаемые услуги абонента
                            accservices = []
                            addonservicespeed=[]  
                            if subacc:
                                accservices = caches.accountaddonservice_cache.by_subaccount.get(subacc.id, [])    
                                for accservice in accservices:                                 
                                    service = caches.addonservice_cache.by_id.get(accservice.service_id)                                
                                    if not accservice.deactivated  and service.change_speed:                                                                        
                                        addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.priority, service.min_tx, service.min_rx, service.speed_units, service.change_speed_type)                                    
                                        break   
                            if not addonservicespeed: 
                                accservices = caches.accountaddonservice_cache.by_account.get(acc.account_id, [])    
                                for accservice in accservices:                                 
                                    service = caches.addonservice_cache.by_id.get(accservice.service_id)                                
                                    if not accservice.deactivated  and service.change_speed:                                                                        
                                        addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.priority, service.min_tx, service.min_rx, service.speed_units, service.change_speed_type)                                    
                                        break    
                            #Получаем параметры скорости                         
                            speed = self.create_speed(caches.defspeed_cache.by_id.get(acc.tarif_id), caches.speed_cache.by_id.get(acc.tarif_id, []),account_limit_speed, addonservicespeed, acc.ipn_speed, dateAT)                            
                    
        
        
                            
                            newspeed = ''.join([unicode(spi) for spi in speed[:6]])
                            
                            ipnsp = caches.ipnspeed_cache.by_id.get(acc.account_id, IpnSpeedData(*(None,)*6))
                            if 0: assert isinstance(ipnsp, IpnSpeedData)
                            if ((newspeed != ipnsp.speed and legacy) or (not legacy and (newspeed!=subacc.speed or recreate_speed))) or recreate_speed:
                                #отправляем на сервер доступа новые настройки скорости, помечаем state=True
                                if legacy: 
                                    ipn_speed_action=nas.ipn_speed_action 
                                else: 
                                    ipn_speed_action = nas.subacc_ipn_speed_action
                                
                                if ipn_speed_action:
                                    sended_speed = change_speed(vars.DICT, acc, subacc, nas,
                                                                access_type=access_type,
                                                                format_string=ipn_speed_action,
                                                                speed=speed[:6])
                                else:
                                    sended_speed = True
                                
                                if legacy: 
                                    cur.execute("SELECT accountipnspeed_ins_fn( %s, %s::character varying, %s, %s::timestamp without time zone);", (acc.account_id, newspeed, sended_speed, now,))
                                else:
                                    cur.execute("UPDATE billservice_subaccount SET speed=%s WHERE id=%s;", (newspeed, id))      
                                    subacc = subacc._replace(speed=newspeed)
                                                          
                                cur.connection.commit()
                    except Exception, ex:
                        if ex.__class__ in vars.db_errors: raise ex
                        else:
                            logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
        
                cur.connection.commit()
                cur.close()
                logger.info("IPNALIVE: %s: run time: %s", (self.getName(), time.clock() - a))
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
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
                    run_time = time.clock()                    
                    cur = self.connection.cursor()
                    #renewCaches(cur)
                    renewCaches(cur, cacheMaster, CoreCaches, 31, (fMem,), False)
                    cur.close()
                    if counter == 0:
                        allowedUsersChecker(allowedUsers, lambda: len(cacheMaster.cache.account_cache.data), ungraceful_save, flags)
                        if not flags.allowedUsersCheck: continue
                        counter = 0
                        #flags.allowedUsersCheck = True
                    counter += 1
                    if counter == 5:
                        #nullify 
                        counter, fMem.settlementCache, fMem.periodCache = 0, {}, {}
                    if flags.cacheFlag:
                        with flags.cacheLock: flags.cacheFlag = False
                    
                    logger.info("ast time : %s", time.clock() - run_time)
            except Exception, ex:
                logger.error("%s : #30310004 : %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                if ex.__class__ in vars.db_errors:
                    time.sleep(5)
                    try:
                        self.connection = get_connection(vars.db_dsn)
                    except Exception, eex:
                        logger.info("%s : database reconnection error: %s" , (self.getName(), repr(eex)))
                        time.sleep(10)
            gc.collect()
            time.sleep(20)
            
    

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
    
def main():
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
        time.sleep(30)
        if not cacheThr.isAlive():
            print 'Core: exiting\n'
            sys.exit()
        


#===============================================================================


if __name__ == "__main__":
    if "-D" in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
       
    
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")
    
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
        saver.log_adapt    = logger.log_adapt
        
        logger.lprint('core start\n')
        ssh_paramiko.SSH_BACKEND=vars.SSH_BACKEND
        ssh_paramiko.install_logger(logger)
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)
        
        cacheMaster = CacheMaster()
        flags = CoreFlags()
        flags.writeProf = logger.writeInfoP()
        suicideCondition = {}
        #function that returns number of allowed users
        #create allowedUsers
        if not globals().has_key('_1i'):
            _1i = lambda: ''
        tmpconnection = get_connection(vars.db_dsn)
        allowedUsers = setAllowedUsers(_1i(), tmpconnection)        
        logger.info("Allowed users: %s", (allowedUsers(),))


        
        fMem = pfMemoize()    
        #--------------------------------------------------
        
        #print "ebs: core: configs read, about to start\n"
        main()
        
    except Exception, ex:
        print 'Exception in core, exiting: ', repr(ex)
        logger.error('Exception in core, exiting: %s \n %s', (repr(ex), traceback.format_exc()))

