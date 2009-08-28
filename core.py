#-*-coding=utf-8-*-

from __future__ import with_statement

import IPy
import hmac
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
import db, utilites

from decimal import Decimal
from copy import copy, deepcopy
from db import Object as Object
from daemonize import daemonize
from encodings import idna, ascii
from threading import Thread, Lock
from DBUtils.PooledDB import PooledDB
from collections import defaultdict


from constants import rules
from saver import allowedUsersChecker, setAllowedUsers
from utilites import parse_custom_speed, parse_custom_speed_lst, cred
from utilites import rosClient, settlement_period_info, in_period, in_period_info

from utilites import create_speed_string, change_speed, PoD, get_active_sessions, get_corrected_speed
from db import delete_transaction, get_default_speed_parameters, get_speed_parameters, dbRoutine
from db import transaction, transaction_noret, ps_history, get_last_checkout, time_periods_by_tarif_id 
from db import timetransaction, transaction, set_account_deleted, get_limit_speed, get_last_addon_checkout, addon_history

try:    import mx.DateTime
except: print 'cannot import mx'

from classes.cacheutils import CacheMaster
from classes.core_cache import *
from classes.flags import CoreFlags
from classes.vars import CoreVars
from utilites import renewCaches, savepid, get_connection, check_running, getpid, rempid

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
            
            minimal_period = minimal_period[:6] if minimal_period else ["0/0","0/0","0/0","0/0","8","0/0"]            
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
                #print "corrected", result            
            if result==[]:                 
                result = defaults if defaults else ["0/0","0/0","0/0","0/0","8","0/0"]                            
            
            return result
        else:
            try:
                return parse_custom_speed_lst(acc.ipn_speed)
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
                #close frozen sessions
                #now = datetime.datetime.now()
                now = dateAT
                cur.execute("""UPDATE radius_activesession 
                               SET session_time=extract(epoch FROM date_end-date_start), date_end=interrim_update, session_status='NACK' 
                               WHERE ((now()-interrim_update>=interval '00:06:00') or (now()-date_start>=interval '00:03:00' and interrim_update IS Null)) AND date_end IS Null;
                               UPDATE radius_activesession SET session_status='ACK' WHERE (date_end IS NOT NULL) AND (session_status='ACTIVE');""")
#===============================================================================
#                cur.execute("""UPDATE radius_activesession 
#                               SET session_time=extract(epoch FROM date_end-date_start), date_end=now(), session_status='NACK' 
#                               WHERE now()-date_start>=interval '00:15:00' and interrim_update IS Null and session_status='ACTIVE' AND date_end IS Null;
#                               UPDATE radius_activesession SET session_status='ACK' WHERE date_end IS Null AND session_status='ACTIVE');""")
#===============================================================================
                cur.connection.commit()
                #cur.execute("""DELETE FROM radius_activesession WHERE session_time = 0;""")
                #cur.connection.commit()
                cur.execute("""SELECT rs.id,rs.account_id,rs.sessionid,rs.speed_string,
                                    lower(rs.framed_protocol) AS access_type,rs.nas_id
                                    FROM radius_activesession AS rs WHERE rs.date_end IS NULL AND rs.date_start <= %s and session_status='ACTIVE';""", (dateAT,))
                rows=cur.fetchall()
                cur.connection.commit()
                for row in rows:
                    #print row
                    try:
                        rs = RadiusSession(*row)
                        #print rs
                        result=None
                        nas = caches.nas_cache.by_ip.get(str(rs.nas_id))
                        acc = caches.account_cache.by_account.get(rs.account_id)
                        #print not nas or not acc or not acc.account_status
                        #print nas, acc, acc.account_status
                        if not nas or not acc or not acc.account_status == 1: continue
                        
                        if 0: assert isinstance(nas, NasData); assert isinstance(acc, AccountData)
                        
                        acstatus = (((not acc.allow_vpn_null and acc.ballance + acc.credit>0) or acc.allow_vpn_null) \
                                    and \
                                    (acc.allow_vpn_null or (not acc.allow_vpn_block and not acc.balance_blocked and not acc.disabled_by_limit))) and acc.account_status == 1
                        
                        #print "hotspot acstatus", acstatus
                        #print dir(caches.timeperiodaccess_cache)
                        if acstatus and caches.timeperiodaccess_cache.in_period[acc.tarif_id]:
                            #chech whether speed has changed
                            account_limit_speed = caches.speedlimit_cache.by_account_id.get(acc.account_id, [])
                            #TODO: caches.defspeed_cache.by_id - нужно же брать по tarif_id!! Это верно??                            
                            accservices = caches.accountaddonservice_cache.by_account.get(acc.account_id, [])                                                 
                            addonservicespeed=[]                            
                            for accservice in accservices:                                 
                                service = caches.addonservice_cache.by_id.get(accservice.service_id)                                
                                if not accservice.deactivated  and service.change_speed:                                                                        
                                    addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.priority, service.min_tx, service.min_rx, 0, service.speed_units, service.change_speed_type)                                    
                                    break                            
                            speed = self.create_speed(caches.defspeed_cache.by_id.get(acc.tarif_id), caches.speed_cache.by_id.get(acc.tarif_id, []),account_limit_speed, addonservicespeed, acc.ipn_speed, dateAT)                            


                            newspeed = ''.join([unicode(spi) for spi in speed[:6]])
                            #print newspeed
                            if rs.speed_string != newspeed:
                                #print "set speed", newspeed
                                coa_result=change_speed(vars.DICT, rs.account_id, str(acc.username), str(acc.vpn_ip_address), str(acc.ipn_ip_address), 
                                                        str(acc.ipn_mac_address), str(nas.ipaddress),nas.type, str(nas.name),
                                                        str(nas.login), str(nas.password), nas_secret=str(nas.secret),
                                                        session_id=str(rs.sessionid), access_type=str(rs.access_type),format_string=str(nas.vpn_speed_action),
                                                        speed=speed[:6])                           
        
                                if coa_result==True:
                                    cur.execute("""UPDATE radius_activesession SET speed_string=%s WHERE id=%s;
                                                """ , (newspeed, rs.id,))
                                    cur.connection.commit()
                        else:
                            #print "send POD"
                            result = PoD(vars.DICT, rs.account_id, str(acc.username),str(acc.vpn_ip_address), str(acc.ipn_ip_address), 
                                         str(acc.ipn_mac_address),str(rs.access_type),str(nas.ipaddress), nas_type=nas.type, 
                                         nas_name=str(nas.name),nas_secret=str(nas.secret),nas_login=str(nas.login), 
                                         nas_password=str(nas.password),session_id=str(rs.sessionid), format_string=str(nas.reset_action))
        
                        if   result is True:
                            disconnect_result='ACK'
                        elif result is False:
                            disconnect_result='NACK'
                            
                        if result is not None:
                            cur.execute("""UPDATE radius_activesession SET session_status=%s WHERE sessionid=%s;
                                        """, (disconnect_result, rs.sessionid,))
                            cur.connection.commit()                            
                    
                    except Exception, ex:
                        logger.error("%s: row exec exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                        if isinstance(ex, vars.db_dsn): raise ex
                    
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
    def iterate_ps(self, cur, caches, acc, ps, dateAT, pss_type):
        account_ballance = (acc.ballance or 0) + (acc.credit or 0)
        susp_per_mlt = 1
        if pss_type == PERIOD:
            susp_per_mlt = 0 if not acc.current_acctf or caches.suspended_cache.by_id.has_key(acc.account_id) else 1
            
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
            """
            # Смотрим сколько расчётных периодов закончилось со времени последнего снятия
            # Если закончился один-снимаем всю сумму, указанную в периодической услуге
            # Если закончилось более двух-значит в системе был сбой. Делаем последнюю транзакцию
            # а остальные помечаем неактивными и уведомляем администратора
            """
            last_checkout = get_last_checkout_(cur, ps.ps_id, acc.acctf_id, acc.end_date)                                    
            if last_checkout is None:
                if pss_type == PERIOD:
                    last_checkout = period_start if ps.created is None or ps.created < period_start else ps.created
                elif pss_type == ADDON:
                    last_checkout = ps.created

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
                        cash_summ = (self.PER_DAY * vars.TRANSACTIONS_PER_DAY * ps.cost) / (delta * vars.TRANSACTIONS_PER_DAY)
                        if pss_type == PERIOD:
                            cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s);", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_GRADUAL', cash_summ, chk_date, ps.condition))
                        elif pss_type == ADDON:
                            cash_summ = cash_summ * susp_per_mlt
                            addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_GRADUAL', cash_summ, chk_date)
                        cur.connection.commit()
                        chk_date += self.PER_DAY_DELTA
                else:
                    #make an approved transaction
                    cash_summ = susp_per_mlt * (self.PER_DAY * vars.TRANSACTIONS_PER_DAY * ps.cost) / (delta * vars.TRANSACTIONS_PER_DAY)
                    if pss_type == PERIOD:
                        if (ps.condition==1 and account_ballance<=0) or (ps.condition==2 and account_ballance>0):
                            #ps_condition_type 0 - Всегда. 1- Только при положительном балансе. 2 - только при орицательном балансе
                            cash_summ = 0
                        ps_history(cur, ps.ps_id, acc.acctf_id, acc.account_id, 'PS_GRADUAL', cash_summ, chk_date)
                    elif pss_type == ADDON:
                        cash_summ = cash_summ * susp_per_mlt
                        addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_GRADUAL', cash_summ, chk_date)
            
            cur.connection.commit()
            
        if ps.cash_method == "AT_START":
            """
            Смотрим когда в последний раз платили по услуге. Если в текущем расчётном периоде
            не платили-производим снятие.
            """
            last_checkout = get_last_checkout_(cur, ps.ps_id, acc.acctf_id, acc.end_date)
            # Здесь нужно проверить сколько раз прошёл расчётный период
            # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
            # Для последней проводки ставим статус Approved=True
            # для всех сотальных False
            # Если последняя проводка меньше или равно дате начала периода-делаем снятие
            
            summ = 0
            if pss_type == PERIOD:
                if not (ps.created is None or ps.created <= period_start) or (ps.created is not None and acc.datetime >= ps.created):
                    return
                first_time = False
                if last_checkout is None:
                    last_checkout = acc.datetime if ps.created is None or ps.created < acc.datetime else ps.created
                    first_time = True
            elif pss_type == ADDON:
                first_time = False
                if last_checkout is None:
                    last_checkout = ps.created
                    first_time = True
                
            #if (first_time or (ps.created or last_checkout) <= period_start) or (not first_time and last_checkout < period_start):
            if first_time or last_checkout < period_start:
                cash_summ = ps.cost
                """
                Если не стоит галочка "Снимать деньги при нулевом балансе", значит не списываем деньги на тот период, 
                пока денег на счету не было
                """
                chk_date = last_checkout
                #Смотрим на какую сумму должны были снять денег и снимаем её                                            
                while True:
                    period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)
                    s_delta_ast = datetime.timedelta(seconds=delta_ast)
                    chk_date = period_start_ast
                    if ps.created and ps.created >= chk_date:
                        cash_summ = 0
                    if pss_type == PERIOD:
                        cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s);", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_AT_START', cash_summ, chk_date, ps.condition))                                                
                    elif pss_type == ADDON:
                        cash_summ = cash_summ * susp_per_mlt
                        addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_AT_START', cash_summ, chk_date)
                    cur.connection.commit()
                    chk_date += s_delta_ast
                    if not chk_date <= period_start: break
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
                if not (ps.created is None or ps.created <= period_end) or (ps.created is not None and acc.datetime >= ps.created):
                    return
                first_time = False
                if last_checkout is None:
                    last_checkout = acc.datetime if ps.created is None or ps.created < acc.datetime else ps.created
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
                while True:
                    period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)
                    s_delta_ast = datetime.timedelta(seconds=delta_ast)
                    chk_date = period_end_ast - SECOND
                    if first_time:
                        first_time = False
                        chk_date = last_checkout
                        if pss_type == PERIOD:
                            ps_history(cur, ps.ps_id, acc.acctf_id, acc.account_id, 'PS_AT_END', ZERO_SUM, chk_date)
                        elif pss_type == ADDON:
                            cash_summ = cash_summ * susp_per_mlt
                            addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_AT_END', cash_summ, chk_date)
                    else:
                        if ps.created and ps.created >= chk_date:
                            cash_summ = ZERO_SUM
                        if pss_type == PERIOD:
                            cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s);", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_AT_END', cash_summ, chk_date, ps.condition))
                        elif pss_type == ADDON:
                            cash_summ = cash_summ * susp_per_mlt
                            addon_history(cur, ps.addon_id, 'periodical', ps.ps_id, acc.acctf_id, acc.account_id, 'ADDONSERVICE_PERIODICAL_AT_END', cash_summ, chk_date)
                    cur.connection.commit()
                    chk_date = period_end_ast + SECOND
                    if not chk_date < period_start: break
            #cur.connection.commit()
            
        if pss_type == ADDON and ps.deactivated and dateAT >= ps.deactivated:
            cur.execute("UPDATE billservice_accountaddonservice SET last_checkout = deactivated WHERE id=%s", (ps.ps_id,))
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
                                if acc.acctf_id is None or acc.account_status == 2: continue
                                self.iterate_ps(cur, caches, acc, ps, dateAT, PERIOD)
                                '''
                                susp_per_mlt = 0 if not acc.current_acctf or caches.suspended_cache.by_id.has_key(acc.account_id) else 1
                                account_ballance = (acc.ballance or 0) + (acc.credit or 0)
                                time_start_ps = acc.datetime if ps.autostart else ps.time_start
                                
                                now = dateAT if acc.current_acctf else acc.end_date
                                #Если в расчётном периоде указана длина в секундах-использовать её, иначе использовать предопределённые константы
                                period_start, period_end, delta = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, now)                                
                                # Проверка на расчётный период без повторения
                                if period_end < now: continue
                                
                                s_delta = datetime.timedelta(seconds=delta)
                                if ps.cash_method == "GRADUAL":
                                    """
                                    # Смотрим сколько расчётных периодов закончилось со времени последнего снятия
                                    # Если закончился один-снимаем всю сумму, указанную в периодической услуге
                                    # Если закончилось более двух-значит в системе был сбой. Делаем последнюю транзакцию
                                    # а остальные помечаем неактивными и уведомляем администратора
                                    """
                                    last_checkout = get_last_checkout(cur, ps.ps_id, acc.acctf_id, acc.end_date)                                    
                                    if last_checkout is None:
                                        last_checkout = period_start if ps.created is None or ps.created < period_start else ps.created

                                    if (now - last_checkout).seconds + (now - last_checkout).days*SECONDS_PER_DAY >= n:
                                        #Проверяем наступил ли новый период
                                        if now - datetime.timedelta(seconds=n) <= period_start:
                                            # Если начался новый период
                                            # Находим когда начался прошльый период
                                            # Смотрим сколько денег должны были снять за прошлый период и производим корректировку
                                            #period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=length_in_sp, now=now-datetime.timedelta(seconds=n))
                                            pass
                                        
                                        # Смотрим сколько раз уже должны были снять деньги
                                        lc = now - last_checkout
                                        last_checkout_seconds = lc.seconds + lc.days*SECONDS_PER_DAY
                                        nums,ost = divmod(last_checkout_seconds,n)                                        
                                        chk_date = last_checkout + n_delta
                                        if nums>1 or not acc.current_acctf:
                                            #Смотрим на какую сумму должны были снять денег и снимаем её
                                            while chk_date <= now:    
                                                period_start, period_end, delta = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)                                            
                                                cash_summ = (n * vars.TRANSACTIONS_PER_DAY * ps.cost) / (delta * vars.TRANSACTIONS_PER_DAY)
                                                cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s);", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_GRADUAL', cash_summ, chk_date, ps.condition))
                                                cur.connection.commit()
                                                chk_date += n_delta
                                        else:
                                            #make an approved transaction
                                            cash_summ = susp_per_mlt * (n * vars.TRANSACTIONS_PER_DAY * ps.cost) / (delta * vars.TRANSACTIONS_PER_DAY)
                                            if (ps.condition==1 and account_ballance<=0) or (ps.condition==2 and account_ballance>0):
                                                #ps_condition_type 0 - Всегда. 1- Только при положительном балансе. 2 - только при орицательном балансе
                                                cash_summ = 0
                                            ps_history(cur, ps.ps_id, acc.acctf_id, acc.account_id, 'PS_GRADUAL', cash_summ, chk_date)
                                    cur.connection.commit()
                                    
                                if ps.cash_method == "AT_START":
                                    """
                                    Смотрим когда в последний раз платили по услуге. Если в текущем расчётном периоде
                                    не платили-производим снятие.
                                    """
                                    last_checkout = get_last_checkout(cur, ps.ps_id, acc.acctf_id, acc.end_date)
                                    # Здесь нужно проверить сколько раз прошёл расчётный период
                                    # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                                    # Для последней проводки ставим статус Approved=True
                                    # для всех сотальных False
                                    # Если последняя проводка меньше или равно дате начала периода-делаем снятие
                                    
                                    summ = 0
                                    
                                    if not (ps.created is None or ps.created <= period_start) or (ps.created is not None and acc.datetime >= ps.created):
                                        continue
                                    first_time = False
                                    if last_checkout is None:
                                        last_checkout = acc.datetime if ps.created is None or ps.created < acc.datetime else ps.created
                                        first_time = True
                                        
                                    #if (first_time or (ps.created or last_checkout) <= period_start) or (not first_time and last_checkout < period_start):
                                    if first_time or last_checkout < period_start:
                                        cash_summ = ps.cost
                                        """
                                        Если не стоит галочка "Снимать деньги при нулевом балансе", значит не списываем деньги на тот период, 
                                        пока денег на счету не было
                                        """
                                        chk_date = last_checkout
                                        #Смотрим на какую сумму должны были снять денег и снимаем её                                            
                                        while True:
                                            period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)
                                            s_delta_ast = datetime.timedelta(seconds=delta_ast)
                                            chk_date = period_start_ast
                                            if ps.created and ps.created >= chk_date:
                                                cash_summ = 0
                                            cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s);", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_AT_START', cash_summ, chk_date, ps.condition))                                                
                                            cur.connection.commit()
                                            chk_date += s_delta_ast
                                            if not chk_date <= period_start: break
                                    cur.connection.commit()
                                if ps.cash_method=="AT_END":
                                    """
                                    Смотрим завершился ли хотя бы один расчётный период.
                                    Если завершился - считаем сколько уже их завершилось.    
                                    для остальных со статусом False
                                    """
                                    last_checkout = get_last_checkout(cur, ps.ps_id, acc.acctf_id, acc.end_date)
                                    cur.connection.commit()
                                    #first_time, last_checkout = (True, now) if last_checkout is None else (False, last_checkout)
                                    if not (ps.created is None or ps.created <= period_end) or (ps.created is not None and acc.datetime >= ps.created):
                                        continue
                                    first_time = False
                                    if last_checkout is None:
                                        last_checkout = acc.datetime if ps.created is None or ps.created < acc.datetime else ps.created
                                        first_time = True
                                    # Здесь нужно проверить сколько раз прошёл расчётный период    
                                    # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                                    # Для последней проводки ставим статус Approved=True
                                    # для всех остальных False
                                    # Если дата начала периода больше последнего снятия или снятий не было и наступил новый период - делаем проводки
                                    
                                    second_ = datetime.timedelta(seconds=1)
                                    cash_summ = 0
                                    if first_time or period_start > last_checkout:
                                        cash_summ = ps.cost
                                        chk_date = last_checkout
                                        while True:
                                            period_start_ast, period_end_ast, delta_ast = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)
                                            s_delta_ast = datetime.timedelta(seconds=delta_ast)
                                            chk_date = period_end_ast - second_
                                            if first_time:
                                                first_time = False
                                                chk_date = last_checkout
                                                ps_history(cur, ps.ps_id, acc.acctf_id, acc.account_id, 'PS_AT_END', ZERO_SUM, chk_date)
                                            else:
                                                if ps.created and ps.created >= chk_date:
                                                    cash_summ = ZERO_SUM
                                                cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::decimal, %s::timestamp without time zone, %s);", (ps.ps_id, acc.acctf_id, acc.account_id, 'PS_AT_END', cash_summ, chk_date, ps.condition))
                                            cur.connection.commit()
                                            chk_date = period_end_ast + second_
                                            if not chk_date < period_start: break
                                            
                                    cur.connection.commit()'''
                            except Exception, ex:
                                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                                if ex.__class__ in vars.db_errors: raise ex
                            cur.connection.commit()
                cur.connection.commit()
                for addon_ps in caches.addonperiodical_cache.data:
                    if 0: assert isinstance(addon_ps, AddonPeriodicalData)
                    acc = caches.account_cache.by_account.get(addon_ps.account_id)
                    if not acc:
                        logger.warning('%s: Addon Periodical Service: %s Account not found: %s', (self.getName(), addon_ps.ps_id, addon_ps.account_id))
                    try:
                        self.iterate_ps(cur, caches, acc, addon_ps, dateAT, ADDON)
                    except Exception, ex:
                                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                                if ex.__class__ in vars.db_errors: raise ex
                    cur.connection.commit()
                        
                
                if caches.underbilled_accounts_cache.underbilled_acctfs:
                    print caches.underbilled_accounts_cache.underbilled_acctfs
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
            
class TimeAccessBill(Thread):
    """
    Услуга применима только для VPN доступа, когда точно известна дата авторизации
    и дата отключения пользователя
    """
    def __init__(self):
        Thread.__init__(self)

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
                cur.execute("""SELECT rs.id, rs.account_id, rs.sessionid, rs.session_time, rs.interrim_update,tarif.time_access_service_id, tarif.id, acc_t.id 
                                 FROM radius_session AS rs
                                 JOIN billservice_accounttarif AS acc_t ON acc_t.account_id=rs.account_id AND (SELECT True FROM billservice_account where id=rs.account_id and status=1) 
                                 JOIN billservice_tariff AS tarif ON tarif.id=acc_t.tarif_id
                                 WHERE (NOT rs.checkouted_by_time) and (rs.date_start IS NULL) AND (tarif.active) AND (acc_t.datetime < rs.interrim_update) AND (tarif.time_access_service_id is NOT NULL)
                                  AND rs.interrim_update < %s ORDER BY rs.interrim_update ASC;""", (dateAT,))
                rows=cur.fetchall()
                cur.connection.commit()
                for row in rows:
                    rs = BillSession(*row)
                    #1. Ищем последнюю запись по которой была произведена оплата
                    #2. Получаем данные из услуги "Доступ по времени" из текущего ТП пользователя
                    #TODO:2. Проверяем сколько стоил трафик в начале сессии и не было ли смены периода.
                    #TODO:2.1 Если была смена периода -посчитать сколько времени прошло до смены и после смены,
                    # рассчитав соотв снятия.
                    #2.2 Если снятия не было-снять столько, на сколько насидел пользователь
                    #rs_id,  account_id, session_id, session_time, interrim_update, ps_id, tarif_id, accountt_tarif_id = row
                    cur.execute("""SELECT session_time FROM radius_session WHERE sessionid=%s AND checkouted_by_time IS TRUE \
                                   AND interrim_update < %s 
                                   ORDER BY interrim_update DESC LIMIT 1""", (rs.sessionid, dateAT))
                    old_time = cur.fetchone()
                    old_time = old_time[0] if old_time else 0
                    
                    total_time = rs.session_time - old_time
    
                    cur.execute("""SELECT id, size FROM billservice_accountprepaystime WHERE account_tarif_id=%s""", (rs.acctf_id,))
                    result = cur.fetchone()
                    cur.connection.commit()
                    prepaid_id, prepaid = result if result else (0, -1)
                    if prepaid > 0:
                        if prepaid >= total_time:
                            total_time, prepaid = 0, prepaid - total_time
                        elif total_time >= prepaid:
                            total_time, prepaid = total_time - prepaid, 0
                        cur.execute("""UPDATE billservice_accountprepaystime SET size=%s WHERE id=%s""", (prepaid, prepaid_id,))
                        cur.connection.commit()
                    #get the list of time periods and their cost
                    now = datetime.datetime.now()
                    for period in caches.timeaccessnode_cache.by_id.get(rs.taccs_id, []):
                        if 0: assert isinstance(period, TimeAccessNodeData)
                        #get period nodes and check them
                        for pnode in caches.timeperiodnode_cache.by_id.get(period.time_period_id, []):
                            if 0: assert isinstance(pnode, TimePeriodNodeData)
                            if fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, dateAT)[3]:
                                summ = (total_time * period.cost) / 60
                                if summ > 0:
                                    #timetransaction(cur, rs.taccs_id, rs.acctf_id, rs.account_id, rs.id, summ, now)
                                    db.timetransaction_fn(cur, rs.taccs_id, rs.acctf_id, rs.account_id, summ, now, unicode(rs.sessionid), rs.interrim_update)
                                    cur.connection.commit()
                    cur.execute("""UPDATE radius_session SET checkouted_by_time=True
                                   WHERE account_id=%s AND sessionid=%s AND interrim_update=%s
                                """, (rs.account_id, unicode(rs.sessionid),rs.interrim_update,))
                    cur.connection.commit()                    
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

                for acc in caches.account_cache.data:
                    if 0: assert isinstance(acc, AccountData)
                    if not acc.account_status == 1: continue

                    #limits = caches.trafficlimit_cache.by_id.get(acc.tarif_id, [])                    #print acc                    
                    accservices = caches.accountaddonservice_cache.by_account.get(acc.account_id, [])                    #print services                    #time.sleep(1)                    #continue                                     
                    for accservice in accservices:                        
                        if 0: assert isinstance(service, AccountAddonServiceData)                        

                        
                        service = caches.addonservice_cache.by_id.get(accservice.service_id)
                        #Проверка на требование отключения услуги
                        if service.service_type=='onetime':
                            
                            cur.execute("SELECT id FROM billservice_addonservicetransaction WHERE type_id ='ADDONSERVICE_ONETIME' and accountaddonservice_id=%s", (accservice.id,))
                            transactions = cur.fetchall()
                            if not transactions and accservice.activated<=dateAT and not accservice.temporary_blocked:
                                sql = """
                                INSERT INTO billservice_addonservicetransaction(
                                            service_id, service_type, account_id, accountaddonservice_id, 
                                            accounttarif_id, type_id, summ, created)
                                    VALUES (%s, 'onetime', %s, %s, 
                                            %s, '%s', %s, '%s')

                                """ % (service.id, acc.account_id, accservice.id, acc.acctf_id, "ADDONSERVICE_ONETIME", service.cost, dateAT,)
                                #print sql
                                cur.execute(sql)
                                cur.execute("UPDATE billservice_accountaddonservice SET last_checkout = %s WHERE id=%s", (dateAT, accservice.id))

                                
                            sp = caches.settlementperiod_cache.by_id.get(service.sp_period_id)
                            # Получаем delta
                            sp_start, sp_end, delta = fMem.settlement_period_(accservice.activated, sp.length_in, sp.length, dateAT)
                            tdelta = dateAT-accservice.activated
                            
                            if (tdelta.days*86400+tdelta.seconds)>=delta:
                                service.deactivated = dateAT
                        if service.action:
                            if service.nas_id==0:
                                nas = caches.nas_cache.by_id.get(acc.nas_id)
                            else:
                                nas = caches.nas_cache.by_id.get(service.nas_id)
                                
                        if accservice.deactivated is None and (service.action and not accservice.action_status) and not accservice.temporary_blocked:
                            #выполняем service_activation_action
                            sended = cred(acc.account_id, acc.username,acc.password, 'ipn',
                                          acc.vpn_ip_address, acc.ipn_ip_address, 
                                          acc.ipn_mac_address, nas.ipaddress, nas.login, 
                                          nas.password, format_string=service.service_activation_action)
                            if sended is True: cur.execute("UPDATE billservice_accountaddonservice SET action_status=%s WHERE id=%s" % (True, acc.account_id))
                        
                        if (accservice.deactivated or accservice.temporary_blocked) and accservice.action_status==True:
                            #выполняем service_deactivation_action
                            sended = cred(acc.account_id, acc.username,acc.password, 'ipn',
                                          acc.vpn_ip_address, acc.ipn_ip_address, 
                                          acc.ipn_mac_address, nas.ipaddress, nas.login, 
                                          nas.password, format_string=service.service_deactivation_action)
                            if sended is True: cur.execute("UPDATE billservice_accountaddonservice SET action_status=%s WHERE id=%s" % (False, acc.account_id))


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
            time.sleep(vars.LIMIT_SLEEP + random.randint(0,5))     
            
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
                        if not shedl: shedl = ShedulelogData(-1, *(None,)*8)
                        if 0: assert isinstance(shedl, ShedulelogData)
                        
                        time_start, period_end = None, None
                        now = datetime.datetime.now()
                        if not acc.settlement_period_id:
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
                        if ballance_checkout < period_start and acc.reset_tarif_cost and period_end and acc.cost > 0:
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
                            cur.execute("""SELECT transaction_block_sum(%s, %s::timestamp without time zone, %s::timestamp without time zone);""",
                                          (acc.account_id, period_start, now))
                            pstart_balance = (cur.fetchone()[0] or 0) + account_balance
                            if acc.cost > pstart_balance:
                                cur.execute("SELECT shedulelog_blocked_fn(%s, %s, %s::timestamp without time zone, %s);", 
                                            (acc.account_id, acc.acctf_id, now, acc.cost))
                            cur.connection.commit()
                            
                        if acc.balance_blocked and (account_balance >= acc.cost or not acc.require_tarif_cost):
                            """Если пользователь отключён, но баланс уже больше разрешённой суммы-включить пользователя"""
                            cur.execute("""UPDATE billservice_account SET balance_blocked=False WHERE id=%s;""", (acc.account_id,))                            
                            cur.connection.commit()

                        reset_traffic = caches.traffictransmitservice_cache.by_id.get(acc.traffic_transmit_service_id, (None, None))[1]                        
                        prepaid_traffic_reset = shedl.prepaid_traffic_reset if shedl.prepaid_time_reset else acc.datetime
                        #if (reset_traffic or acc.traffic_transmit_service_id is None) and (shedl.prepaid_traffic_reset is None or shedl.prepaid_traffic_reset<period_start or acc.acctf_id!= shedl.accounttarif_id):
                        if (reset_traffic and prepaid_traffic_reset<period_start) or not acc.traffic_transmit_service_id or acc.acctf_id != shedl.accounttarif_id:
                            #(Если нужно сбрасывать трафик или нет услуги доступа по трафику) И
                            #(Никогда не сбрасывали трафик или последний раз сбрасывали в прошлом расчётном периоде или пользователь сменил тариф)
                            """(Если наступил новый расчётный период и нужно сбрасывать трафик) или если нет услуги с доступом по трафику или если сменился тарифный план"""
                            cur.execute("SELECT shedulelog_tr_reset_fn(%s, %s, %s::timestamp without time zone);", \
                                        (acc.account_id, acc.acctf_id, now))  
                            cur.connection.commit()
        
                        if (shedl.prepaid_traffic_accrued is None or shedl.prepaid_traffic_accrued<period_start) and acc.traffic_transmit_service_id:                          
                            #Начислить новый предоплаченный трафик
                            cur.execute("SELECT shedulelog_tr_credit_fn(%s, %s, %s, %s::timestamp without time zone);", 
                                        (acc.account_id, acc.acctf_id, acc.traffic_transmit_service_id, now))
                            cur.connection.commit()
                        
                        prepaid_time, reset_time = caches.timeaccessservice_cache.by_id.get(acc.time_access_service_id, (None, 0, None))[1:3]   
                        if (reset_time or acc.time_access_service_id is None) and (shedl.prepaid_time_reset is None or shedl.prepaid_time_reset<period_start or acc.acctf_id!=shedl.accounttarif_id):                        
                            #(Если нужно сбрасывать время или нет услуги доступа по времени) И                        
                            #(Никогда не сбрасывали время или последний раз сбрасывали в прошлом расчётном периоде или пользователь сменил тариф)                          
                            cur.execute("SELECT shedulelog_time_reset_fn(%s, %s, %s::timestamp without time zone);", 
                                        (acc.account_id, acc.acctf_id, now))                            
                            cur.connection.commit()        
                        if (shedl.prepaid_time_accrued is None or shedl.prepaid_time_accrued<period_start) and acc.time_access_service_id:
                            cur.execute("SELECT shedulelog_time_credit_fn(%s, %s, %s, %s, %s::timestamp without time zone);", 
                                        (acc.account_id, acc.acctf_id, acc.time_access_service_id, prepaid_time, now))
                            cur.connection.commit()
                        
                        if account_balance > 0:
                            for ots in caches.onetimeservice_cache.by_id.get(acc.tarif_id, []):
                                if 0: assert isinstance(ots, OneTimeServiceData)
                                if not caches.onetimehistory_cache.by_acctf_ots_id.has_key((acc.acctf_id, ots.id)):
                                    cur.execute("INSERT INTO billservice_onetimeservicehistory(accounttarif_id, onetimeservice_id, account_id, summ, datetime) VALUES(%s, %s, %s, %s, %s);", (acc.acctf_id, ots.id, acc.account_id, ots.cost, now,))
                                    cur.connection.commit()
                                    caches.onetimehistory_cache.by_acctf_ots_id[(acc.acctf_id, ots.id)] = (1,)
                                    #Списывам с баланса просроченные обещанные платежи
                    except Exception, ex:
                        logger.error("%s : internal exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                        if ex.__class__ in vars.db_errors: raise ex
                cur.connection.commit()
                #Делаем проводки по разовым услугам тем, кому их ещё не делали
                cur.execute("UPDATE billservice_transaction SET promise_expired = True, summ=-1*summ WHERE end_promise<now() and promise_expired=False;")
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
        result_params=speeds        
        if speed=='':            
            defaults = default            
            speeds   =  result_params            
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
            
            minimal_period = minimal_period[:6] if minimal_period else ["0/0","0/0","0/0","0/0","8","0/0"]            
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
                #print "corrected", result            
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
                        """Если у аккаунта не указан IPN IP, мы не можем производить над ним действия. Прпускаем."""                    
                        if not acc.tarif_active or acc.ipn_ip_address == '0.0.0.0': continue
                        accps = caches.accessparameters_cache.by_id.get(acc.access_parameters_id)
                        if (not accps) or (not accps.ipn_for_vpn): continue
                        if 0: assert isinstance(accps, AccessParametersData)
                        sended, recreate_speed = (None, False)
    
                        account_ballance = (acc.ballance or 0) + (acc.credit or 0)
                        period = caches.timeperiodaccess_cache.in_period[acc.tarif_id]# True/False
                        nas = caches.nas_cache.by_id[acc.nas_id]
                        if 0: assert isinstance(nas, NasData)
                        access_type = 'IPN'
                        #now = datetime.datetime.now()
                        now = dateAT
                        # Если на сервере доступа ещё нет этого пользователя-значит добавляем.
                        if not acc.ipn_added:
                            sended = cred(acc.account_id, acc.username,acc.password, access_type,
                                          acc.vpn_ip_address, acc.ipn_ip_address, 
                                          acc.ipn_mac_address, nas.ipaddress, nas.login, 
                                          nas.password, format_string=nas.user_add_action)
                            if sended is True: cur.execute("UPDATE billservice_account SET ipn_added=%s WHERE id=%s" % (True, acc.account_id))
                                
                        if (not acc.ipn_status) and (account_ballance>0 and period and not acc.disabled_by_limit and acc.account_status == 1 and not acc.balance_blocked):
                            #шлём команду, на включение пользователя, account_ipn_status=True
                            #ipn_added = acc.ipn_added
                            """Делаем пользователя enabled"""

                            sended = cred(acc.account_id, acc.username,acc.password, access_type,
                                          acc.vpn_ip_address, acc.ipn_ip_address, 
                                          acc.ipn_mac_address, nas.ipaddress, nas.login, 
                                          nas.password, format_string=nas.user_enable_action)
                            recreate_speed = True                        
                            if sended is True: cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s" % (True, acc.account_id))
                            
                        elif (acc.disabled_by_limit or account_ballance<=0 or period is False or acc.balance_blocked or not acc.account_status == 1) and acc.ipn_status:
                            #шлём команду на отключение пользователя,account_ipn_status=False
                            sended = cred(acc.account_id, acc.username,acc.password, access_type,
                                              acc.vpn_ip_address, acc.ipn_ip_address, 
                                              acc.ipn_mac_address, nas.ipaddress, nas.login, 
                                              nas.password, format_string=nas.user_disable_action)    
                            if sended is True: cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s", (False, acc.account_id,))
        
                        self.connection.commit()
    

                        account_limit_speed = caches.speedlimit_cache.by_account_id.get(acc.account_id, [])
                        #TODO: caches.defspeed_cache.by_id - нужно же брать по tarif_id!! Это верно??                            
                        accservices = caches.accountaddonservice_cache.by_account.get(acc.account_id, [])                            
                        if acc.username=='user':                                
                            pass                            
                        addonservicespeed=[]                            
                        for accservice in accservices:                                 
                            service = caches.addonservice_cache.by_id.get(accservice.service_id)                                
                            if not accservice.deactivated  and service.change_speed:                                                                        
                                addonservicespeed = (service.max_tx, service.max_rx, service.burst_tx, service.burst_rx, service.burst_treshold_tx, service.burst_treshold_rx, service.burst_time_tx, service.burst_time_rx, service.priority, service.min_tx, service.min_rx, 0, service.speed_units, service.change_speed_type)                                    
                                break                            
                        speed = self.create_speed(caches.defspeed_cache.by_id.get(acc.tarif_id), caches.speed_cache.by_id.get(acc.tarif_id, []),account_limit_speed, addonservicespeed, acc.ipn_speed, dateAT)                            
                

    
                        
                        newspeed = ''.join([unicode(spi) for spi in speed[:6]])
                        
                        ipnsp = caches.ipnspeed_cache.by_id.get(acc.account_id, IpnSpeedData(*(None,)*6))
                        if 0: assert isinstance(ipnsp, IpnSpeedData)
                        if newspeed != ipnsp.speed or recreate_speed:
                            #отправляем на сервер доступа новые настройки скорости, помечаем state=True

                            sended_speed = change_speed(vars.DICT,acc.account_id,acc.username,
                                                        acc.vpn_ip_address,acc.ipn_ip_address,
                                                        acc.ipn_mac_address,nas.ipaddress,
                                                        nas.type,nas.name,nas.login,nas.password,
                                                        access_type=access_type,
                                                        format_string=nas.ipn_speed_action,
                                                        speed=speed[:6])
                            cur.execute("SELECT accountipnspeed_ins_fn( %s, %s::character varying, %s, %s::timestamp without time zone);", (acc.account_id, newspeed, sended_speed, now,))
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
                    #print cacheMaster.cache
                    if counter == 0:
                        #allowedUsersChecker(allowedUsers, lambda: len(cacheMaster.cache.account_cache.data), ungraceful_save, flags)
                        #if not flags.allowedUsersCheck: continue
                        counter = 0
                        flags.allowedUsersCheck = True
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
    logger.lprint("SIGUSR1 recieved")
    with flags.cacheLock: flags.cacheFlag = True
    
def graceful_save():
    global cacheThr, threads, suicideCondition, vars
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    logger.lprint("Core - about to exit gracefully.")
    time.sleep(20)
    #pool.close()
    #time.sleep(2)
    rempid(vars.piddir, vars.name)
    logger.lprint("Core - exiting gracefully.")
    sys.exit()
    
def ungraceful_save():
    global cacheThr, threads, suicideCondition, vars
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    #rempid(vars.piddir, vars.name)
    print "Core: exiting"
    logger.lprint("Core exiting.")
    sys.exit()
    
def main():
    global caches, suicideCondition, threads, cacheThr, vars
    
    threads = []
    thrnames = [(check_vpn_access, 'Core VPN Thread'), (periodical_service_bill, 'Core Period. Bill Thread'), \
                (TimeAccessBill, 'Core Time Access Thread'), (limit_checker, 'Core Limit Thread'),\
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
            print 'Core: exiting'
            sys.exit()
        time.sleep(10)
        if not cacheMaster.read: 
            print 'caches still not read, maybe you should check the log'
      
    print 'caches ready'
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
    
    print "ebs: core: started"
    savepid(vars.piddir, vars.name)
    #main thread should not exit!
    while True:
        time.sleep(30)
        if not cacheThr.isAlive():
            print 'Core: exiting'
            sys.exit()
        


#===============================================================================


if __name__ == "__main__":
    if "-D" in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
       
    
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")
    
    try:
        
        vars = CoreVars()
        
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME)
        #create logger
        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file) 
        
        utilites.log_adapt = logger.log_adapt
        saver.log_adapt    = logger.log_adapt
        logger.lprint('core start')
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)
        
        cacheMaster = CacheMaster()
        flags = CoreFlags()
        flags.writeProf = logger.writeInfoP()
        suicideCondition = {}
        #function that returns number of allowed users
        #create allowedUsers
        if not globals().has_key('_1i'):
            _1i = lambda: ''
        allowedUsers = setAllowedUsers(_1i())        
        logger.info("Allowed users: %s", (allowedUsers(),))
        
        fMem = pfMemoize()    
        #--------------------------------------------------
        
        print "ebs: core: configs read, about to start"
        main()
        
    except Exception, ex:
        print 'Exception in core, exiting: ', repr(ex)
        logger.error('Exception in core, exiting: %s \n %s', (repr(ex), traceback.format_exc()))

