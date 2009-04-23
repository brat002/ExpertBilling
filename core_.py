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
from utilites import rosClient, SSHClient,settlement_period_info, in_period, in_period_info

from utilites import create_speed_string, change_speed, PoD, get_active_sessions, get_corrected_speed
from db import delete_transaction, get_default_speed_parameters, get_speed_parameters, dbRoutine
from db import transaction, transaction_noret, ps_history, get_last_checkout, time_periods_by_tarif_id 
from db import timetransaction, transaction, set_account_deleted, get_limit_speed

try:    import mx.DateTime
except: print 'cannot import mx'

from classes.cacheutils import CacheMaster
from classes.core_cache import *

from classes.core_class.RadiusSession import RadiusSession
from classes.core_class.BillSession import BillSession

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)



def comparator(d, s):
    for key in s:
        if s[key]!='' and s[key]!='Null' and s[key]!='None':
            d[key]=s[key] 
    return d

class check_vpn_access(Thread):
    def __init__ (self):          
        Thread.__init__(self)

    def create_speed(self, decRec, spRec, date_):
        defaults = decRec
        speeds = spRec
        min_from_start=0
        f_speed = None
        for speed in speeds:
            tnc, tkc, from_start,result = fMem.in_period_(speed[6], speed[7], speed[8], date_)
            if result==True and (from_start<min_from_start or min_from_start==0):
                min_from_start=from_start
                f_speed=speed
        #print "f_speed=", f_speed                
        if f_speed != None:
            for i in range(6):
                speedi = f_speed[i]
                if (speedi != '') and (speedi != 'None') and (speedi != 'Null'):
                    defaults[i] = speedi
        return defaults


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
        global cacheMaster, suicideCondition
        dateAT = datetime.datetime(2000, 1, 1)
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        caches = None
        while True:            
            try:
                if suicideCondition[self.__class__.__name__]: break
                a = time.clock()

                if cacheMaster.date > dateAT:
                    cacheMaster.lock.acquire()
                    try:
                        caches = cacheMaster.cache
                        dateAT = deepcopy(cacheMaster.date)
                    except Exception, ex:
                        logger.error("Vpn cache exception: %s", repr(ex))
                    finally:
                        cacheMaster.lock.release()
                if not caches:
                    time.sleep(10)
                    continue
                assert isinstance(caches, CoreCaches)             
                   
                cur = connection.cursor()
                #close frozen sessions
                now = datetime.datetime.now()
                cur.execute("""UPDATE radius_activesession 
                               SET session_time=extract(epoch FROM date_end-date_start), date_end=interrim_update, session_status='NACK' 
                               WHERE ((now()-interrim_update>=interval '00:06:00') or (now()-date_start>=interval '00:03:00' and interrim_update IS Null)) AND date_end IS Null;
                               UPDATE radius_activesession SET session_status='ACK' WHERE (date_end IS NOT NULL) AND (session_status='ACTIVE');""")
                connection.commit()
                cur.execute("""SELECT rs.id,rs.account_id,rs.sessionid,rs.speed_string,
                                    lower(rs.framed_protocol) AS access_type,rs.nas_id
                                    FROM radius_activesession AS rs WHERE rs.date_end IS NULL;""")
                rows=cur.fetchall()
                connection.commit()
                for row in rows:
                    try:
                        rsRec = RadiusSession(*row)
                        result=None
                        nasRec = caches.nas_cache.by_id.get(str(rsRec.nas_id))
                        accRec = caches.account_cache.by_account.get(rsRec.account_id)
                        if not nasRec or not accRec:
                            continue
                        
                        assert isinstance(nasRec, NasData)
                        assert isinstance(accRec, AccountData)
                        acstatus = (((not accRec.allow_vpn_null) and (accRec.balance + accRec.credit > 0)) or accRec.allow_vpn_null) \
                                    and \
                                    (accRec.allow_vpn_null or ((accRec.allow_vpn_block or accRec.balance_blocked or accRec.disabled_by_limit) and accRec.account_status))

                        if acstatus and caches.timeperiodaccess_cache.in_period(accRec.tarif_id):
                            #chech whether speed has changed
                            if accRec.vpn_speed=='':
                                account_limit_speed = get_limit_speed(cur, rsRec.account_id)
                                connection.commit()
                                speed = self.create_speed(list(caches.defspeed_cache.by_id.get(accRec.tarif_id,[])), caches.speed_cache.by_id.get(accRec.tarif_id, []), dateAT)
                                speed = get_corrected_speed(speed[:6], account_limit_speed)
                            else:
                                speed=parse_custom_speed_lst(vpn_speed)

                            newspeed = ''.join([unicode(spi) for spi in speed[:6]])
                            if row[3]!=newspeed:
                                #print "set speed", newspeed
                                coa_result=change_speed(dict, rsRec.account_id, str(accRec.username), str(accRec.vpn_ip_address), str(accRec.ipn_ip_address), 
                                                        str(accRec.ipn_mac_address), str(nasRec.ipaddress),nasRec.type, str(nasRec.name),
                                                        str(nasRec.login), str(nasRec.password), nas_secret=str(nasRec.secret),
                                                        session_id=str(rsRec.sessionid), access_type=str(rsRec.access_type),format_string=str(nasRec.vpn_speed_action),
                                                        speed=speed[:6])                           
        
                                if coa_result==True:
                                    cur.execute("""UPDATE radius_activesession SET speed_string=%s WHERE id=%s;
                                                """ , (newspeed, rsRec.id,))
                                    connection.commit()
                        else:
                            result = PoD(dict,rsRec.account_id, str(accRec.username),str(accRec.vpn_ip_address), str(accRec.ipn_ip_address), 
                                         str(accRec.ipn_mac_address),str(rsRec.access_type),str(nasRec.ipaddress), nas_type=nasRec.type, 
                                         nas_name=str(nasRec.name),nas_secret=str(nasRec.secret),nas_login=str(nasRec.login), 
                                         nas_password=str(nasRec.password),session_id=str(rsRec.sessionid), format_string=str(nasRec.reset_action))
        
                        if   result is True:
                            disconnect_result='ACK'
                        elif result is False:
                            disconnect_result='NACK'
                            
                        if result is not None:
                            cur.execute("""UPDATE radius_activesession SET session_status=%s WHERE sessionid=%s;
                                        """, (disconnect_result, rsRec.sessionid,))
                            connection.commit()                            
                    
                    except Exception, ex:
                        logger.error("%s: row exec exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                    
                connection.commit()   
                cur.close()
                logger.info("VPNALIVE: VPN thread run time: %s", time.clock() - a)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            time.sleep(60)

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

    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global cacheMaster, fMem, suicideCondition, transaction_number
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
                        logger.error("Vpn cache exception: %s", repr(ex))
                    finally:
                        cacheMaster.lock.release()                
                assert isinstance(caches, CoreCaches)

                cur = connection.cursor()
                #transactions per day              
                n=(86400)/transaction_number
                n_delta = datetime.timedelta(seconds=n)
                now=datetime.datetime.now()
                #get a list of tarifs with periodical services & loop                
                for row in caches.periodicaltarif_cache:
                    tariff_id, settlement_period_id = row
                    #debit every account for tarif on every periodical service
                    for ps in caches.periodicalsettlement_cache.by_id.get(tariff_id,[]):
                        assert isinstance(ps, PeriodicalServiceSettlementData)
                        for account in caches.account_cache.by_tarif.get(tariff_id,[]):
                            assert isinstance(account, AccountData)
                            try:
                                if account.acctf_id is None: continue
                                susp_per_mlt = 0 if cacheSuspP.has_key(account.account_id) else 1
                                account_ballance = account.ballance + account.credit
                                time_start_ps = account.datetime if ps.autostart else ps.time_start
                                #Если в расчётном периоде указана длина в секундах-использовать её, иначе использовать предопределённые константы
                                period_start, period_end, delta = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, dateAT)                                
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
                                    last_checkout = get_last_checkout(cur, ps.ps_id, account.acctf_id)                                    
                                    if last_checkout is None and ps.created is None:
                                        last_checkout = period_start
                                    elif last_checkout is None and ps_created is not None:
                                        if ps_created < period_start:
                                            last_checkout = period_start
                                        else:
                                            last_checkout = ps.created

                                    if (now - last_checkout).seconds + (now - last_checkout).days*86400 >= n:
                                        #Проверяем наступил ли новый период
                                        if now - datetime.timedelta(seconds=n) <= period_start:
                                            # Если начался новый период
                                            # Находим когда начался прошльый период
                                            # Смотрим сколько денег должны были снять за прошлый период и производим корректировку
                                            #period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=length_in_sp, now=now-datetime.timedelta(seconds=n))
                                            pass
                                        
                                        # Смотрим сколько раз уже должны были снять деньги
                                        lc = now - last_checkout
                                        last_checkout_seconds = lc.seconds + lc.days*86400
                                        nums, ost=divmod(last_checkout_seconds,n)
                                        #description = ps.ps_name
                                        
                                        chk_date = last_checkout + n_delta
                                        if nums>1:
                                            #Смотрим на какую сумму должны были снять денег и снимаем её
                                            while chk_date <= now:    
                                                period_start, period_end, delta = fMem.settlement_period_(time_start_ps, ps.length_in, ps.length, chk_date)                                            
                                                cash_summ = (float(n) * transaction_number * ps.cost) / (delta * transaction_number)
                                                cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::double precision, %s::timestamp without time zone, %s);", (ps.ps_id, account.acctf_id, account.account_id, 'PS_GRADUAL', cash_summ, chk_date, ps.condition))
                                                connection.commit()
                                                chk_date += n_delta
                                        else:
                                            #make an approved transaction
                                            cash_summ = susp_per_mlt * (float(n) * transaction_number * ps.cost) / (delta * transaction_number)
                                            if (ps.condition==1 and account_ballance<=0) or (ps.condition==2 and account_ballance>0):
                                                #ps_condition_type 0 - Всегда. 1- Только при положительном балансе. 2 - только при орицательном балансе
                                                cash_summ = 0
                                            ps_history(cur, ps.ps_id, account.acctf_id, account.account_id, 'PS_GRADUAL', cash_summ, chk_date)
                                    connection.commit()
                                    
                                if ps.cash_method == "AT_START":
                                    """
                                    Смотрим когда в последний раз платили по услуге. Если в текущем расчётном периоде
                                    не платили-производим снятие.
                                    """
                                    last_checkout=get_last_checkout(cur, ps.ps_id, account.acctf_id)
                                    # Здесь нужно проверить сколько раз прошёл расчётный период
                                    # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                                    # Для последней проводки ставим статус Approved=True
                                    # для всех сотальных False
                                    # Если последняя проводка меньше или равно дате начала периода-делаем снятие
                                    summ = 0
                                    if last_checkout is None:
                                        first_time = True
                                        last_checkout = now
                                    else:
                                        first_time = False
                                        
                                    if first_time or last_checkout < period_start:    
                                        lc = period_start - last_checkout
                                        #Смотрим сколько раз должны были снять с момента последнего снятия
                                        nums, ost = divmod(lc.seconds + lc.days*86400, delta)
                                        #description=ps_name
                                        cash_summ =ps.cost
                                        chk_date = last_checkout + s_delta
                                        if nums > 1:
                                            """
                                            Если не стоит галочка "Снимать деньги при нулевом балансе", значит не списываем деньги на тот период, 
                                            пока денег на счету не было
                                            """
                                            #Смотрим на какую сумму должны были снять денег и снимаем её                                            
                                            while chk_date <= now:
                                                if ps.created and ps.created >= chk_date:
                                                    cash_summ=0
                                                cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::double precision, %s::timestamp without time zone, %s);", (ps.ps_id, account.acctf_id, account.account_id, 'PS_AT_START', cash_summ, chk_date, ps.condition))                                                
                                                connection.commit()
                                                chk_date += s_delta
                                        else:
                                            summ = cash_summ * susp_per_mlt
                                            if (ps.condition==1 and account_ballance<=0) or (ps.condition==2 and account_ballance>0):
                                                #ps_condition_type 0 - Всегда. 1- Только при положительном балансе. 2 - только при орицательном балансе
                                                summ = 0
                                            ps_history(cur, ps.ps_id, account.acctf_id, account.account_id, 'PS_AT_START', summ, chk_date)
                                    connection.commit()
                                if ps_cash_method=="AT_END":
                                    """
                                    Смотрим завершился ли хотя бы один расчётный период.
                                    Если завершился - считаем сколько уже их завершилось.    
                                    для остальных со статусом False
                                    """
                                    last_checkout=get_last_checkout(cur, ps.ps_id, account.acctf_id)
                                    connection.commit()
                                    if last_checkout is None:
                                        first_time = True
                                        last_checkout = now
                                    else:
                                        first_time = False
                                        
                                    # Здесь нужно проверить сколько раз прошёл расчётный период    
                                    # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                                    # Для последней проводки ставим статус Approved=True
                                    # для всех остальных False
                                    # Если дата начала периода больше последнего снятия или снятий не было и наступил новый период - делаем проводки

                                    summ = 0
                                    if first_time: 
                                        chk_date = now 
                                        cash_summ = 0
                                        #descr=u"Фиктивная проводка по периодической услуге со снятием суммы в конце периода"
                                    elif period_start>last_checkout:
                                        lc = period_start - last_checkout
                                        le = period_end - last_checkout
                                        nums, ost = divmod(le.seconds + le.days*86400, delta)
                                        summ = ps.cost
                                        chk_date = last_checkout + s_delta
                                        if nums > 1:                                                
                                            cash_summ = ps.cost
                                            while chk_date <= now:
                                                if ps.created and ps.created>chk_date:
                                                    cash_summ=0
                                                cur.execute("SELECT periodicaltr_fn(%s,%s,%s, %s::character varying, %s::double precision, %s::timestamp without time zone, %s);", (ps.ps_id, account.acctf_id, account.account_id, 'PS_AT_END', cash_summ, chk_date, ps.condition))
                                                connection.commit()
                                                chk_date += s_delta                                          
                                            
                                        if (ps.condition==1 and account_ballance<=0) or (ps.condition==2 and account_ballance>0):
                                            #ps_condition_type 0 - Всегда. 1- Только при положительном балансе. 2 - только при орицательном балансе
                                            cash_summ = 0                                            
                                        summ = cash_summ * susp_per_mlt
                                        ps_history(cur, ps.ps_id, account.acctf_id, account.account_id, 'PS_AT_END', summ, chk_date)
                                    connection.commit()
                            except Exception, ex:
                                if not  isinstance(ex, psycopg2.OperationalError or isinstance(ex, psycopg2.InterfaceError)):
                                    logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                                else: raise ex
                connection.commit()
                cur.close()
                logger.info("PSALIVE: Period. service thread run time: %s", time.clock() - a)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            gc.collect()
            time.sleep(180-(time.clock()-a_)-random.randint(10, 120))
            
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
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global fMem, suicideCondition, cacheMaster
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        while True:
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
                        logger.error("%s: cache exception: %s", (self.getName(), repr(ex)))
                    finally:
                        cacheMaster.lock.release()

                assert isinstance(caches, CoreCaches)
                """
                try:
                    #if caches were renewed, renew local copies
                    if curAT_date > dateAT:
                        curAT_lock.acquire()
                        cacheTimeAccN  = copy(curTimeAccNCache)
                        #traffic_transmit_service
                        cacheTimePerN = copy(curTimePerNCache)
                        #date of renewal
                        dateAT = deepcopy(curAT_date)
                        curAT_lock.release()
                    else:
                        time.sleep(10)
                        continue
                except:
                    try:
                        curAT_lock.release()
                    except: pass
                    time.sleep(1)
                    continue"""
                
                cur = connection.cursor()
                cur.execute("""SELECT rs.id, rs.account_id, rs.sessionid, rs.session_time, rs.interrim_update,tarif.time_access_service_id, tarif.id, acc_t.id 
                                 FROM radius_session AS rs
                                 JOIN billservice_accounttarif AS acc_t ON acc_t.account_id=rs.account_id AND (SELECT status FROM billservice_account where id=rs.account_id) 
                                 JOIN billservice_tariff AS tarif ON tarif.id=acc_t.tarif_id
                                 WHERE (NOT rs.checkouted_by_time) and (rs.date_start IS NULL) AND (tarif.active) AND (acc_t.datetime < rs.interrim_update) AND (tarif.time_access_service_id NOTNULL)
                                 ORDER BY rs.interrim_update ASC;""")
                rows=cur.fetchall()
                connection.commit()
                for row in rows:
                    rs = BillSession(*row)
                    #1. Ищем последнюю запись по которой была произведена оплата
                    #2. Получаем данные из услуги "Доступ по времени" из текущего ТП пользователя
                    #TODO:2. Проверяем сколько стоил трафик в начале сессии и не было ли смены периода.
                    #TODO:2.1 Если была смена периода -посчитать сколько времени прошло до смены и после смены,
                    # рассчитав соотв снятия.
                    #2.2 Если снятия не было-снять столько, на сколько насидел пользователь
                    #rs_id,  account_id, session_id, session_time, interrim_update, ps_id, tarif_id, accountt_tarif_id = row
                    cur.execute("""SELECT session_time FROM radius_session WHERE sessionid=%s AND checkouted_by_time IS TRUE 
                                   ORDER BY interrim_update DESC LIMIT 1""", (session_id,))
                    old_time = cur.fetchone()
                    old_time = old_time[0] if old_time else 0
                    
                    total_time = rs.session_time - old_time
    
                    cur.execute("""SELECT id, size FROM billservice_accountprepaystime WHERE account_tarif_id=%s""", (accountt_tarif_id,))
                    result = cur.fetchone()
                    connection.commit()
                    prepaid_id, prepaid = result if result else (0, -1)                    
                    if prepaid > 0:
                        if prepaid >= total_time:
                            total_time = 0
                            prepaid = prepaid - total_time
                        elif total_time >= prepaid:
                            total_time = total_time - prepaid
                            prepaid = 0
                        cur.execute("""UPDATE billservice_accountprepaystime SET size=%s WHERE id=%s""", (prepaid, prepaid_id,))
                        connection.commit()
                    #get the list of time periods and their cost
                    now = datetime.datetime.now()
                    #periods = cacheTimeAccN.get(ps_id, [])
                    for period in caches.timeaccessnode_cache.by_id.get(rs.taccs_id, []):
                        assert isinstance(period, TimeAccessNodeData)
                        #period_id, period_cost=period[0:2]
                        #get period nodes and check them
                        #period_nodes_data = cacheTimePerN.get(period_id,[])
                        for pnode in caches.timeperiodnode_cache.by_id.get(period.time_period_id, []):
                            assert isinstance(pnode, TimePeriodNodeData)
                            #period_id, period_name =period_node[0:2]
                            #period_start, period_length, repeat_after = period_node[2:5]
                            #if in_period(time_start=period_start,length=period_length, repeat_after=repeat_after):
                            if fMem.in_period_(pnode.time_start,pnode.length,pnode.repeat_after, dateAT)[3]:
                                summ = (float(total_time)/60) * period_cost
                                if summ > 0:
                                    timetransaction(cur, rs.taccs_id, rs.acctf_id, rs.account_id, rs.id, summ, now)
                                    connection.commit()
                    cur.execute("""UPDATE radius_session SET checkouted_by_time=True
                                   WHERE sessionid=%s AND account_id=%s AND interrim_update=%s
                                """, (unicode(rs.sessionid), rs.account_id, rs.interrim_update,))
                    connection.commit()                    
                connection.commit()
                cur.close()
                logger.info("TIMEALIVE: Time access thread run time: %s", time.clock() - a)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))

            gc.collect()
            time.sleep(60)



class limit_checker(Thread):
    """
    Проверяет исчерпание лимитов. если лимит исчерпан-ставим соотв галочку в аккаунте
    """
    def __init__ (self):
        Thread.__init__(self)
 
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global suicideCondition, cacheMaster, fMem   
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        while True:            
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
                        logger.error("%s: cache exception: %s", (self.getName(), repr(ex)))
                    finally:
                        cacheMaster.lock.release()

                assert isinstance(caches, CoreCaches)
                
                oldid = -1
                cur = connection.cursor()
                for acc in caches.account_cache.data:
                    assert isinstance(acc, AccountData)
                    limits = caches.trafficlimit_cache.by_id.get(acc.tarif_id, [])
                    if not limits:
                        if acc.disabled_by_limit:
                            cur.execute("""UPDATE billservice_account SET disabled_by_limit=False WHERE id=%s;""", (acc.account_id,))
                        cur.execute("""DELETE FROM billservice_accountspeedlimit WHERE account_id=%s;""", (acc.account_id,))
                        connection.commit()
                        continue
                    block, speed_changed = (False, False)
                    for limit in limits:
                        assert isinstance(limit, TrafficLimitData)
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
                        assert isinstance(sp, SettlementPeriodData)
                        
                        sp_defstart = acc.datetime if sp.autostart else sp.time_start
                        sp_start, sp_end, delta = fMem.settlement_period_(sp_defstart, sp.length_in, sp.length, dateAT)
                        if sp_start < acc.datetime: sp_start = acc.datetime
                        #если нужно считать количество трафика за последнеие N секунд, а не за рачётный период, то переопределяем значения
                        if limit.mode:
                            now = dateAT
                            sp_start = now - datetime.timedelta(seconds=delta)
                            sp_end = now
                        
                        connection.commit()        
                        cur.execute("""SELECT sum(bytes) AS size FROM billservice_groupstat
                                       WHERE group_id=%s AND account_id=%s AND datetime>%s AND datetime<%s
                                    """ , (limit.group_id, acc.account_id, sp_start, sp_end,)) 
                        sizes = cur.fetchone()
                        connection.commit()
                        
                        tsize = sizes[0] if sizes[0] else 0
                        limit_size = Decimal("%s" % limit.size)
                        if tsize > limit_size and limit_action==0:
                            block = True
                            cur.execute("""DELETE FROM billservice_accountspeedlimit WHERE account_id=%s;""", (account_id,))                            
                        elif tsize > limit_size and limit.action == 1:
                            #Меняем скорость
                            cur.execute("SELECT speedlimit_ins_fn(%s, %s);", (limit.speedlimit_id, acc.account_id,))
                            speed_changed, block = (True, False)
                        elif tsize < limit_size:
                            cur.execute("""DELETE FROM billservice_accountspeedlimit WHERE account_id=%s;""", (acc.account_id,))
                        connection.commit()
                        
                        oldid = account_id
                        if acc.disabled_by_limit != block:
                            cur.execute("""UPDATE billservice_account SET disabled_by_limit=%s WHERE id=%s;
                                        """ , (block, acc.account_id,))
                            connection.commit()
                            logger.info("set user %s new limit %s state %s", (acc.account_id, limit.trafficlimit_id, block))
    
                connection.commit()
                cur.close()                
                logger.info("LMTALIVE: %s: run time: %s", (self.getName(), time.clock() - a))
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            gc.collect()
            time.sleep(110)          


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
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global fMem, suicideCondition, cacheMaster
        dateAT = datetime.datetime(2000, 1, 1)
        caches = None
        while True:
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
                        logger.error("%s: cache exception: %s", (self.getName(), repr(ex)))
                    finally:
                        cacheMaster.lock.release()

                assert isinstance(caches, CoreCaches)
                
                try:
                    #if caches were renewed, renew local copies
                    if curAT_date > dateAT:
                        curAT_lock.acquire()
                        cacheAT = copy(curATCache)
                        #account-tarif cach indexed by account_id
                        #cacheAT = deepcopy(curAT_acctIdx)
                        #settlement_period cache
                        cacheSetP = copy(curSPCache)
                        cacheShedLog  = copy(curShedLogCache)
                        #traffic_transmit_service
                        cacheTTS = copy(curTTSCache)                        
                        cacheTAccS = copy(curTimeAccSrvCache)                        
                        cacheOTSrv = copy(curOneTimeSrvCache)                        
                        cacheOTSHist = copy(curOTSHistCache)
                        #date of renewal
                        dateAT = deepcopy(curAT_date)
                        curAT_lock.release()
                    else:
                        time.sleep(10)
                        continue
                except:                    
                    try:
                        curAT_lock.release()
                    except: pass
                    time.sleep(1)
                    continue
                
                cur = connection.cursor()
                for acc in caches.account_cache.data:
                    try:
                        assert isinstance(acc, AccountData)
                        shedl = caches.shedulelog_cache.by_id.get(acc.account_id)
                        if not shedl: shedl = ShedulelogData(-1, *(None,)*8)
                        assert isinstance(shedl, ShedulelogData)
                        time_start, period_end = (None, None)
                        now = datetime.datetime.now()
                        if not acc.settlement_period_id:
                            time_start, period_start, delta = (acc.datetime, acc.datetime, 86400*365*365)
                        else:
                            sp = caches.settlementperiod_cache.by_id.get(acc.settlement_period_id)
                            assert isinstance(sp, SettlementPeriodData)
                            time_start = acc.datetime if sp.autostart else sp.time_start
                            period_start, period_end, delta = fMem.settlement_period_(time_start, sp.length_in, sp.length, dateAT)
                            #Если начало расчётного периода осталось в прошлом тарифном плане-за начало расчётного периода принимаем начало тарифного плана
                            if period_start < acc.datetime: period_start = acc.datetime                            
    
                        #account_balance_blocked = acct[16]
                        #нужно производить в конце расчётного периода
                        ballance_checkout = shedl.ballance_checkout if shedl.balance_blocked else acc.datetime
                        
                        if ballance_checkout < period_start and acc.reset_tarif_cost and period_end and acc.cost > 0:
                            #Снять сумму до стоимости тарифного плана                   
                            #Считаем сколько было списано по услугам                   
                            tnc, tkc, delta = settlement_period_info(time_start, sp.length_in, sp.length, dateAT, prev=True)
                            #Считаем сколько было списано по услугам
                            cur.execute("""SELECT transaction_sum(%s, %s, %s::timestamp without time zone, %s::timestamp without time zone);""",
                                        (acc.account_id, acc.acctf_id, tnc, tkc))
                            summ = cur.fetchone()[0] or 0    
                            if cost > summ:
                                pay_summ = cost-summ
                                transaction(cursor=cur,account=acc.account_id,approved=True,type='END_PS_MONEY_RESET',
                                            summ=pay_summ,created=now,tarif=acc.tarif_id,accounttarif=accounttarif_id,
                                            description=u"Доснятие денег до стоимости тарифного плана у %s" % acc.account_id)
                            cur.execute("SELECT shedulelog_co_fn(%s, %s, %s::timestamp without time zone);", (acc.account_id, acc.acctf_id, now,))
                            connection.commit()

                        account_balance = acc.ballance + acc.credit   
                        #Если балланса не хватает - отключить пользователя
                        if (shedl.balance_blocked is None or shedl.balance_blocked<=period_start) and acc.cost>=account_balance and acc.cost != 0 and not acc.balance_blocked:
                            cur.execute("""SELECT transaction_block_sum(%s, %s::timestamp without time zone, %s::timestamp without time zone);""",
                                          (acc.account_id, period_start, now))
                            pstart_balance = (cur.fetchone()[0] or 0) + account_balance
                            if cost > pstart_balance:
                                cur.execute("SELECT shedulelog_blocked_fn(%s, %s, %s::timestamp without time zone, %s);", 
                                            (acc.account_id, acc.acctf_id, now,acc.cost))
                            connection.commit()
                        if acc.balance_blocked and account_balance>=cost:
                            """Если пользователь отключён, но баланс уже больше разрешённой суммы-включить пользователя"""
                            cur.execute("""UPDATE billservice_account SET balance_blocked=False WHERE id=%s;""", (acc.account_id,))                            
                            connection.commit()

                        reset_traffic = caches.traffictransmitservice_cache.by_id.get(acc.traffic_transmit_service_id, (None, None))[1]                        
                        prepaid_traffic_reset = shedl.prepaid_traffic_reset if shedl.prepaid_time_reset else acc.datetime
                        if (reset_traffic or acc.traffic_transmit_service_id is None) and (shedl.prepaid_traffic_reset is None or shedl.prepaid_traffic_reset<period_start or acc.acctf_id!= shedl.accounttarif_id):
                            #(Если нужно сбрасывать трафик или нет услуги доступа по трафику) И
                            #(Никогда не сбрасывали трафик или последний раз сбрасывали в прошлом расчётном периоде или пользователь сменил тариф)
                            """(Если наступил новый расчётный период и нужно сбрасывать трафик) или если нет услуги с доступом по трафику или если сменился тарифный план"""
                            cur.execute("SELECT shedulelog_tr_reset_fn(%s, %s, %s::timestamp without time zone);", 
                                        (acc.account_id, acc.acctf_id, now))  
                            connection.commit()
        
                        if (shedl.prepaid_traffic_accrued is None or shedl.prepaid_traffic_accrued<period_start) and acc.traffic_transmit_service_id:                          
                            #Начислить новый предоплаченный трафик
                            cur.execute("""SELECT id, size FROM billservice_prepaidtraffic WHERE traffic_transmit_service_id=%s;
                                        """, (traffic_transmit_service_id,))
        
                            prepais=cur.fetchall()
                            connection.commit()
                            u=False
                            for prepaid_traffic_id, size in prepais:
                                u=True
                                #print "SET PREPAID TRAFIC"
                                cur.execute("""UPDATE billservice_accountprepaystrafic SET size=size+%s, datetime=%s
                                               WHERE account_tarif_id=%s and prepaid_traffic_id=%s RETURNING id;
                                            """, (size, now, accounttarif_id, prepaid_traffic_id,))
                                if cur.fetchone() is None:
                                    cur.execute("""INSERT INTO billservice_accountprepaystrafic (account_tarif_id, prepaid_traffic_id, size, datetime) 
                                                   VALUES(%s, %s, %f*1048576, '%s');
                                                """ % (accounttarif_id, prepaid_traffic_id, size, now,))
                                connection.commit()
                                
                            if u==True:
                                cur.execute("UPDATE billservice_shedulelog SET prepaid_traffic_accrued=%s WHERE account_id=%s RETURNING id;", (now, account_id,))
                                if cur.fetchone()==None:
                                    cur.execute("""INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_accrued) values(%s, %s, %s) ;
                                                """, (account_id, accounttarif_id, now,))  
                        connection.commit() 
                        
                        prepaid_time, reset_time = caches.timeaccessservice_cache.by_id.get(acc.time_access_service_id, (None, 0, None))[1:3]   
                        if (reset_time or acc.time_access_service_id is None) and (shedl.prepaid_time_reset is None or shedl.prepaid_time_reset<period_start or acc.acctf_id!=shedl.accounttarif_id):                        
                            #(Если нужно сбрасывать время или нет услуги доступа по времени) И                        
                            #(Никогда не сбрасывали время или последний раз сбрасывали в прошлом расчётном периоде или пользователь сменил тариф)                          
                            cur.execute("SELECT shedulelog_tr_reset_fn(%s, %s, %s::timestamp without time zone);", 
                                        (acc.account_id, acc.acctf_id, now))                            
                            connection.commit()        
                        if (prepaid_time_accrued is None or prepaid_time_accrued<period_start) and time_access_service_id:
        
                            cur.execute("""UPDATE billservice_accountprepaystime
                                           SET size=size+%s,datetime=%s WHERE account_tarif_id=%s RETURNING id;
                                        """, (prepaid_time,now, accounttarif_id,))
                            if cur.fetchone()==None:
                                cur.execute("""INSERT INTO billservice_accountprepaystime(account_tarif_id, size, datetime,prepaid_time_service_id) VALUES(%s, %s, %s, %s);
                                            """, (accounttarif_id, prepaid_time, now, time_access_service_id,))    
                            cur.execute("UPDATE billservice_shedulelog SET prepaid_time_accrued=%s WHERE account_id=%s RETURNING id;", (now,account_id,))
                            if cur.fetchone()==None:
                                cur.execute("""INSERT INTO billservice_shedulelog(account_id, accounttarif_id,prepaid_time_accrued) values(%s, %s, %s) ;
                                            """, (account_id, accounttarif_id,now))
                        
                        if account_balance > 0:
                            onetimesvs = cacheOTSrv.get(tarif_id, [])
                            for ots in onetimesvs:
                                ots_id = ots[0]
                                if not cacheOTSHist.has_key((accounttarif_id, ots_id)):
                                    cur.execute("INSERT INTO billservice_onetimeservicehistory(accounttarif_id, onetimeservice_id, account_id, summ, datetime) VALUES(%s, %s, %s, %s, %s);", (accounttarif_id, ots_id, account_id,ots[2], now,))
                                    connection.commit()
                                    cacheOTSHist[(accounttarif_id, ots_id)] = (1,)
                        #Списывам с баланса просроченные обещанные платежи
                    except Exception, ex:
                        logger.error("%s : internal exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                connection.commit()
                #Делаем проводки по разовым услугам тем, кому их ещё не делали
                cur.execute("UPDATE billservice_transaction SET promise_expired = True, summ=-1*summ WHERE end_promise<now() and promise_expired=False;")
                logger.info("SPALIVE: %s run time: %s", time.clock() - a)
            except Exception, ex:
                logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))

            gc.collect()
            time.sleep(120)

class ipn_service(Thread):
    """
    Тред должен:
    1. Проверять не изменилась ли скорость для IPN клиентов и менять её на сервере доступа
    2. Если балланс клиента стал меньше 0 - отключать, если уже не отключен (параметр ipn_status в account) и включать, если отключен (ipn_status) и баланс стал больше 0
    3. Если клиент вышел за рамки разрешённого временного диапазона в тарифном плане-отключать
    """
    def __init__ (self):
        Thread.__init__(self)

    def check_period(self, rows):
        for row in rows:
            if in_period(row['time_start'], row['length'], row['repeat_after'])==True:
                return True
        return False

    def create_speed(self, decRec, spRec, date_):
        defaults = decRec
        speeds = spRec
        min_from_start=0
        f_speed = None
        for speed in speeds:
            #if in_period(speed['time_start'],speed['length'],speed['repeat_after'])==True:
            tnc, tkc, from_start,result = fMem.in_period_(speed[6], speed[7], speed[8], date_)
            if from_start<min_from_start or min_from_start==0:
                        min_from_start=from_start
                        f_speed=speed
                        
        if f_speed != None:
            for i in range(6):
                    speedi = f_speed[i]
                    if (speedi != '') and (speedi != 'None') and (speedi != 'Null'):
                        defaults[i] = speedi
        return defaults

    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global tp_asInPeriod, suicideCondition
        global curNasCache,curATCache
        global curAccParCache,curDefSpCache,curNewSpCache
        global curAT_date,curAT_lock
        cacheAT = None
        dateAT = datetime.datetime(2000, 1, 1)
        while True:             
            try:
                if suicideCondition[self.__class__.__name__]: break
                a = time.clock()
                try:
                    #if caches were renewed, renew local copies
                    if curAT_date > dateAT:
                        curAT_lock.acquire()
                        #account-tarif cach indexed by account_id
                        cacheAT = copy(curATCache)
                        #nas cache
                        cacheNas  = copy(curNasCache)
                        #default speed cache
                        cacheAccp = copy(curAccParCache)
                        #current speed cache
                        cacheDefSp = copy(curDefSpCache)
                        cacheNewSp = copy(curNewSpCache)
                        
                        c_tp_asInPeriod = copy(tp_asInPeriod)
                        #date of renewal
                        dateAT = deepcopy(curAT_date)
                        curAT_lock.release()
                    else:
                        time.sleep(10)
                        continue
                except Exception, ex:
                    print "Ipn speed thread exception: ", repr(ex)
                cur = connection.cursor()
                cur.execute("""SELECT id, account_id, speed, state, static, datetime FROM billservice_accountipnspeed;""")
                
                ipnspTp=cur.fetchall()
                connection.commit()
                acc_ipn_sps = {} # {account_id:(id, account_id, speed, state, static, datetime),}
                for ipns in ipnspTp:
                    """
                    Индексируем параметры скорости по Acount_id
                    """
                    acc_ipn_sps[ipns[1]] = ipns                  
                
                #for row in rows:
                for acct in cacheAT:
                    #print acct
                    #print "acct", acct
                    #if tariff not active
                    if not acct[11]:
                        continue
                    account_vpn_ip, account_ipn_ip, account_mac_address  = acct[18:21]
                    if account_ipn_ip == '0.0.0.0':
                        """
                        Если у аккаунта не указан IPN IP, мы не можем производить над ним действия. Прпускаем.
                        """
                        continue                    
                    #acct[5]- access_parameter_id
                    accpRec = cacheAccp.get(acct[5])
                    #accessparameters.ipn_for_vpn==True
                    #print accpRec
                    if (not accpRec) or (not accpRec[9]):
                        continue
                    #print "check ipn"
                    sended=None
                    recreate_speed = False
                    tarif_id= acct[4]
                    account_id = acct[0]
                    account_password = acct[33]
                    account_ballance = acct[1]+acct[2]                    
                    account_disabled_by_limit, account_balance_blocked = acct[15:17]
                    account_ipn_status = acct[22]
                    account_status = acct[29]
                    account_name = acct[32]                    
                    period = c_tp_asInPeriod[tarif_id]# True/False
                    nasRec = cacheNas[acct[17]]
                    nas_ipaddress = nasRec[3]
                    nas_login, nas_password = nasRec[5:7]
                    nas_user_add, nas_user_enable, nas_user_disable = nasRec[10:13]
                    access_type = 'IPN'
                    now = datetime.datetime.now()
                    #if row['account_ipn_status']==False and row['ballance']>0 and period==True and row['account_disabled_by_limit']==False and row['account_status']==True and row['account_balance_blocked']==False:
                    if (not account_ipn_status) and  (account_ballance>0) and period and (not account_disabled_by_limit) and account_status and (not account_balance_blocked):
                        #print u"ВКЛЮЧАЕМ",row['account_username']
                        #шлём команду, на включение пользователя, account_ipn_status=True
                        ipn_added = acct[25]
                        if ipn_added==False:
                            """
                            Если на сервере доступа ещё нет этого пользователя-значит добавляем. В следующем проходе делаем пользователя enabled
                            """
                            sended = cred(account_id, account_name, 
                                          account_password, access_type,
                                          account_vpn_ip, account_ipn_ip, 
                                          account_mac_address, nas_ipaddress, nas_login, 
                                          nas_password, format_string=nas_user_add)
                            if sended == True: cur.execute("UPDATE billservice_account SET ipn_added=%s WHERE id=%s" % (True, account_id))
                        else:
                            sended = cred(account_id, account_name, 
                                          account_password, access_type,
                                          account_vpn_ip, account_ipn_ip, 
                                          account_mac_address, nas_ipaddress, nas_login, 
                                          nas_password, format_string=nas_user_enable)
                            recreate_speed = True
                    
                            if sended == True: cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s" % (True, account_id))
                    elif (account_disabled_by_limit==True or account_ballance<=0 or period==False or account_balance_blocked==True or account_status==False) and account_ipn_status==True:
    
                        #шлём команду на отключение пользователя,account_ipn_status=False
                        #print u"ОТКЛЮЧАЕМ",row['account_username']
                        sended = cred(account_id, account_name, \
                                      account_password, access_type,
                                      account_vpn_ip, account_ipn_ip, \
                                      account_mac_address, nas_ipaddress, nas_login, \
                                      nas_password, format_string=nas_user_disable)
    
                        if sended == True: cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s", (False, account_id,))
    
                    connection.commit()
                    account_ipn_speed = acct[23]
                    
                    #print account_id

                    #print "account_limit_speed", account_limit_speed
                    if account_ipn_speed=='' or account_ipn_speed==None:    
                        account_limit_speed = get_limit_speed(cur, account_id)
                        connection.commit()
                        speed=self.create_speed(list(cacheDefSp[tarif_id]), cacheNewSp[tarif_id], dateAT)
                        speed = get_corrected_speed(speed[:6], account_limit_speed)
                    else:
                        speed = parse_custom_speed_lst(account_ipn_speed)
                    #print "speed",speed
                    #print "corrected_speed=", 
                    
                    
                    
                    newspeed=''
                    newspeed = ''.join([unicode(spi) for spi in speed[:6]])
                    
                    ipn_speed = None
                    ipn_state = None
                    accipnRec = acc_ipn_sps.get(account_id)
                    if accipnRec:
                        ipn_speed = accipnRec[2]
                        ipn_state = accipnRec[3]
                    
                    nas_type,nas_name = nasRec[1:3]
                    nas_ipn_speed = nasRec[15]
                    #print newspeed, row['ipn_speed'],row['ipn_state']
                    #print newspeed!=row['ipn_speed'] or row['ipn_state']==False

                    if newspeed!=ipn_speed or ipn_state==False or recreate_speed==True:
                        #print u"МЕНЯЕМ НАСТРОЙКИ СКОРОСТИ НА СЕВРЕРЕ ДОСТУПА", speed
                        #отправляем на сервер доступа новые настройки скорости, помечаем state=True
                        sended_speed = change_speed(dict, 
                                                    account_id,account_name,account_vpn_ip, \
                                                    account_ipn_ip,account_mac_address, \
                                                    nas_ipaddress,nas_type,nas_name,\
                                                    nas_login,nas_password,\
                                                    format_string=nas_ipn_speed, access_type=access_type,\
                                                    speed=speed[:6])
                        data_for_save=''
                        #print speed
                        #print "speed sended=", sended_speed
                        cur.execute("UPDATE billservice_accountipnspeed SET speed=%s, state=%s WHERE account_id=%s RETURNING id;", (newspeed, sended_speed, account_id,))
                        id = cur.fetchone()
                        #print 'id=', id
                        if id==None:
                            cur.execute("INSERT INTO billservice_accountipnspeed(account_id, speed, state, datetime) VALUES( %s, %s, %s, %s);", (account_id, unicode(newspeed), sended_speed, now,))
    
                connection.commit()
                cur.close()
                logger.info("IPN thread run time: %s", time.clock() - a)
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    logger.error("%s : database connection is down: %s", (self.getName(), repr(ex)))
                else:
                    logger.error("%s : exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))


            
            #self.connection.close()
            gc.collect()
            time.sleep(120)


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
        for dct in self.dicts: dct.clean()
  



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
[13] - FALSE, 
[14] - ba.created, 
[15] - ba.disabled_by_limit, 
[16] - ba.balance_blocked, 
[17] - ba.nas_id, 
[18] - ba.vpn_ip_address, 
[19] - ba.ipn_ip_address,
[20] - ba.ipn_mac_address, 
[21] - ba.assign_ipn_ip_from_dhcp, 
[22] - ba.ipn_status, 
[23] - ba.ipn_speed, 
[24] - ba.vpn_speed, 
[25] - ba.ipn_added, 
[26] - bt.ps_null_ballance_checkout, 
[27] - bt.deleted, 
[28] - bt.allow_express_pay,
[29] - ba.status, 
[30] - ba.allow_vpn_null
[31] - ba.allow_vpn_block
[32] - ba.username,
[33] - ba.password
'''
class AccountServiceThread(Thread):
    '''Handles simultaniously updated READ ONLY caches connected to account-tarif tables'''
    def __init__ (self):
        Thread.__init__(self)
        
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        i_fMem = 0
        while True:
            if suicideCondition[self.__class__.__name__]: break            
            try: 
                run_time = time.clock()
                cur = connection.cursor()
                renewCaches(cur)
                i_fMem += 1
                if i_fMem == 5:                  
                    i_fMem = 0
                    #nullify caches
                    fMem.settlementCache = {}
                    fMem.periodCache = {}                    
                logger.info("ast time : %s", time.clock() - run_time)
            except Exception, ex:
                logger.error("%s : #30310004 : %s", (self.getName(), repr(ex)))
                
            gc.collect()
            time.sleep(100)
            
    def run2(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global fMem, sendFlag, nfIncomingQueue
        global curATCache,curAT_acIdx,curAT_tfIdx
        global curAT_date, curAT_lock
        global curSPCache, curTLimitCache, curSuspPerCache
        global curNasCache, curNas_ipIdx, curTTSCache
        global curDefSpCache, curNewSpCache, curShedLogCache
        global curPerTarifCache, curPersSetpCache
        global curTimeAccNCache, curTimePerNCache, curTimeAccSrvCache
        global curOneTimeSrvCache, curAccParCache, curIPNSpCache, curOTSHistCache
        global tp_asInPeriod, allowedUsers
        i_fMem = 0
        while True:
            if suicideCondition[self.__class__.__name__]: break
            a = time.clock()
            try:                
                cur = connection.cursor()
                ptime =  time.time()
                ptime = ptime - (ptime % 20)
                tmpDate = datetime.datetime.fromtimestamp(ptime)
                cur.execute("""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, FALSE, ba.created, ba.disabled_by_limit, ba.balance_blocked, ba.nas_id, ba.vpn_ip_address, ba.ipn_ip_address,ba.ipn_mac_address, ba.assign_ipn_ip_from_dhcp, ba.ipn_status, ba.ipn_speed, ba.vpn_speed, ba.ipn_added, bt.ps_null_ballance_checkout, bt.deleted, bt.allow_express_pay, ba.status, ba.allow_vpn_null, ba.allow_vpn_block, ba.username, ba.password  
                    FROM billservice_account as ba
                    LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                    LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id WHERE ba.status AND bt.active;""", (tmpDate,))
                #list cache
                
                accts = cur.fetchall()
                allowedUsersChecker(allowedUsers, lambda: len(accts))
 
                cur.execute("""SELECT id, reset_traffic, cash_method, period_check FROM billservice_traffictransmitservice;""")
                
                ttssTp = cur.fetchall()
                #connection.commit()
                cur.execute("""SELECT id, time_start, length, length_in, autostart FROM billservice_settlementperiod;""")
                
                spsTp = cur.fetchall()
                #connection.commit()
                cur.execute("""SELECT id, type, name, ipaddress, secret, login, password, allow_pptp, allow_pppoe, allow_ipn, user_add_action, user_enable_action, user_disable_action, user_delete_action, vpn_speed_action, ipn_speed_action, reset_action, confstring, multilink FROM nas_nas;""")
                nasTp = cur.fetchall()
                cur.execute("""
                   SELECT 
                    accessparameters.max_limit,accessparameters.burst_limit,
                    accessparameters.burst_treshold, accessparameters.burst_time,
                    accessparameters.priority, accessparameters.min_limit,
                    tariff.id
                    FROM billservice_accessparameters as accessparameters
                    JOIN billservice_tariff as tariff ON tariff.access_parameters_id=accessparameters.id;
                    """)
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
                nspTmp = cur.fetchall()
                #connection.commit()
                cur.execute("""SELECT id, settlement_period_id  
                                 FROM billservice_tariff  as tarif
                                 WHERE id in (SELECT tarif_id FROM billservice_periodicalservice) AND tarif.active=True""")
                perTarTp = cur.fetchall()
                cur.execute("""SELECT b.id, b.name, b.cost, b.cash_method, c.name, c.time_start,
                                     c.length, c.length_in, c.autostart, b.tarif_id, b.condition, b.created
                                     FROM billservice_periodicalservice as b 
                                     JOIN billservice_settlementperiod as c ON c.id=b.settlement_period_id;""")
                #b.condition 0 - При любом балансе. 1- Только при положительном балансе. 2 - только при орицательном балансе
                
                psspTp = cur.fetchall()
                cur.execute("""
                        SELECT tan.time_period_id, tan.cost, tan.time_access_service_id
                        FROM billservice_timeaccessnode as tan
                        JOIN billservice_timeperiodnode as tp ON tan.time_period_id=tp.id;""")
                timeaccnTp = cur.fetchall()
                cur.execute("""
                            SELECT tpn.id, tpn.name, tpn.time_start, tpn.length, tpn.repeat_after, tptpn.timeperiod_id 
                            FROM billservice_timeperiodnode as tpn
                            JOIN billservice_timeperiod_time_period_nodes as tptpn ON tpn.id=tptpn.timeperiodnode_id;""")
                timeperndTp = cur.fetchall()
                cur.execute("""SELECT trafficlimit.id, trafficlimit.tarif_id, trafficlimit."name", 
                                    trafficlimit.settlement_period_id, trafficlimit.size, trafficlimit.group_id, 
                                    trafficlimit."mode", trafficlimit.action,
                                    speedlimit.id
                                    FROM billservice_trafficlimit as trafficlimit
                                    LEFT JOIN billservice_speedlimit as speedlimit ON speedlimit.limit_id=trafficlimit.id
                                    ORDER BY trafficlimit.size DESC;""") # DESC Критично!
                #action = 0:block
                #action = 1:change speed
                tlimitsTp = cur.fetchall()
                cur.execute("""SELECT id,account_id, ballance_checkout, prepaid_traffic_reset,prepaid_traffic_accrued, 
                                      prepaid_time_reset, prepaid_time_accrued, balance_blocked, accounttarif_id 
                                      FROM billservice_shedulelog;""")
                shllTp = cur.fetchall()
                cur.execute("""SELECT id, prepaid_time, reset_time FROM billservice_timeaccessservice;""")
                taccsTp = cur.fetchall()
                cur.execute("""SELECT id, tarif_id, cost FROM billservice_onetimeservice;""")
                otsTp = cur.fetchall()
                cur.execute("""SELECT id, access_type, access_time_id, max_limit, min_limit, 
                               burst_limit,burst_treshold,burst_time, priority, ipn_for_vpn FROM billservice_accessparameters;""")
                #make through "defaultspeed"
                accpsTp = cur.fetchall()
                cur.execute("""SELECT id, account_id, speed, state, static, datetime FROM billservice_accountipnspeed;""")
                ipnspTp = cur.fetchall()
                cur.execute("""SELECT id, accounttarif_id, onetimeservice_id FROM billservice_onetimeservicehistory WHERE ARRAY[accounttarif_id] && get_cur_acct(%s);""", (tmpDate,))
                otshTp = cur.fetchall()
                cur.execute("""SELECT id, account_id FROM billservice_suspendedperiod WHERE (%s BETWEEN start_date AND end_date)""", (tmpDate,))
                suspsTp = cur.fetchall()

                cur.execute("""SELECT tpn.time_start::timestamp without time zone as time_start, tpn.length as length, tpn.repeat_after as repeat_after, bst.id
                    FROM billservice_timeperiodnode as tpn
                    JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
                    JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
                    JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id""")
                tpnapsTp = cur.fetchall()
                connection.commit()
                cur.close()
                
                tmpacIdx = {}
                #index on accounttarif.id
                tmpacctIdx = {}
                #index on tariff_id
                tmptfIdx = defaultdict(list)
                i = 0
                for acct in accts:
                    tmpacIdx[acct[0]]  = acct
                    if acct[4]:
                        tmptfIdx[acct[4]].append(acct)
                    if acct[12]:
                        tmpacctIdx[acct[11]] = acct

                tmpPerAPTP = defaultdict(lambda: False)
                for tpnap in tpnapsTp:
                    tmpPerAPTP[tpnap[3]] = tmpPerAPTP[tpnap[3]] or fMem.in_period_(tpnap[0], tpnap[1], tpnap[2], tmpDate)[3]
                    
                prepaysTmp = {}    
                #traffic_transmit_service cache, indexed by id
                tmpttsC = {}
                #settlement period cache, indexed by id
                tmpspC = {}
                #nas cache, indexed by ID
                tmpnasC = {}
                
                tmpnasipC = {}
                # default speed cache
                tmpdsC = {}
                #nondef speed cache
                tmpnsC       = defaultdict(list)
                tmppsspC     = defaultdict(list)                
                tmptimeaccC  = defaultdict(list)                
                tmptimepernC = defaultdict(list)                
                tmptlimitC   = defaultdict(list)
                
                tmpshlC = {}
                tmptaccsC = {}
                tmpotsC = defaultdict(list)
                tmpipnsC = {}
                tmpaccpC = {}
                tmpotshC = {}
                tmpsusppC = {}
                
                for tts in ttssTp:
                    tmpttsC[tts[0]] = tts
                for sps in spsTp:
                    tmpspC[sps[0]] = sps
                for nas in nasTp:
                    tmpnasC[nas[0]] = nas
                    tmpnasipC[str(nas[3])] = nas
                for ds in defspTmp:
                    tmpdsC[ds[6]] = ds
                for ns in nspTmp:
                    tmpnsC[ns[9]].append(ns)
                for pssp in psspTp:
                    tmppsspC[pssp[9]].append(pssp)
                for timeaccn in timeaccnTp:
                    tmptimeaccC[timeaccn[2]].append(timeaccn)
                for timepern in timeperndTp:
                    tmptimepernC[timepern[5]].append(timepern)                    
                for tlimit in tlimitsTp:
                    tmptlimitC[tlimit[1]].append(tlimit)
                for shl in shllTp:
                    tmpshlC[shl[1]] = shl
                for tacc in taccsTp:
                    tmptaccsC[tacc[0]] = tacc
                for ipns in ipnspTp:
                    tmpipnsC[ipns[1]] = ipns
                for ots in otsTp:
                    tmpotsC[ots[1]].append(ots)
                for otsh in otshTp:
                    tmpotshC[(otsh[1], otsh[2])] = otsh
                for accp in accpsTp:
                    tmpaccpC[accp[0]] = accp
                for susp in suspsTp:
                    tmpsusppC[susp[1]] = suspsTp
                #renew global cache links
                curAT_lock.acquire()
                curATCache    = accts
                curAT_acIdx   = tmpacIdx
                curAT_tfIdx   = tmptfIdx
                curAT_acctIdx = tmpacctIdx
                curSPCache = tmpspC
                curTTSCache = tmpttsC
                curNasCache = tmpnasC
                curNas_ipIdx = tmpnasipC
                curDefSpCache = tmpdsC
                curNewSpCache = tmpnsC
                curPerTarifCache = perTarTp
                curPersSetpCache = tmppsspC
                curTimeAccNCache = tmptimeaccC
                curTimePerNCache = tmptimepernC
                curTLimitCache = tmptlimitC
                curShedLogCache = tmpshlC
                curTimeAccSrvCache = tmptaccsC
                curAccIPNSpCache = tmpipnsC
                curOneTimeSrvCache = tmpotsC
                curOTSHistCache = tmpotshC
                curAccParCache = tmpaccpC
                curSuspPerCache = tmpsusppC
                curIPNSpCache = tmpipnsC                
                tp_asInPeriod = tmpPerAPTP
                curAT_date  = tmpDate
                curAT_lock.release()
                #del accts, tmpacIdx, tmptfIdx, tmpspC, tmpttsC, tmpnasC, tmpdsC, tmpnsC, tmpDate
                #del ttssTp, spsTp, nasTp, defspTmp, nspTmp
                #every cacheRenewalTime*3
                i_fMem += 1
                if i_fMem == 3:                  
                    i_fMem = 0
                    #nullify caches
                    fMem.settlementCache = {}
                    fMem.periodCache = {}
                    #reread runtime options
                    config.read("ebs_config_runtime.ini")
                    logger.setNewLevel(int(config.get("core", "log_level")))
                    
                logger.info("ast time : %s", time.clock() - a)
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + repr(ex)
                else:
                    print self.getName() + ": exception: " + repr(ex)
            
            gc.collect()
            time.sleep(100)
            


def renewCaches(cur):
    ptime =  time.time()
    ptime = ptime - (ptime % 20)
    cacheDate = datetime.datetime.fromtimestamp(ptime)
    try:
        caches = CoreCaches(cacheDate, fMem)
        caches.getdata(cur)
        cur.connection.commit()
        caches.reindex()
    except Exception, ex:
        if isinstance(ex, psycopg2.DatabaseError):
            logger.error('#30310001 renewCaches attempt failed due to database error: %s', repr(ex))
        else: 
            logger.error('#30310002 renewCaches attempt failed due to error: %s', repr(ex))
    else:
        cacheMaster.read = True
            
    with cacheMaster.lock:
        cacheMaster.cache = caches
        cacheMaster.date = cacheDate
    

def SIGTERM_handler(signum, frame):
    logger.lprint("SIGTERM recieved")
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
    
def graceful_save():
    global cacheThr, threads, suicideCondition
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    logger.lprint("Core - about to exit gracefully.")
    time.sleep(20)
    pool.close()
    time.sleep(2)
    logger.lprint("Core - exiting gracefully.")
    sys.exit()
    
def main():
    global caches, suicideCondition, threads, cacheThr
    
    dict=dictionary.Dictionary("dicts/dictionary", "dicts/dictionary.microsoft","dicts/dictionary.mikrotik","dicts/dictionary.rfc3576")

    threads = []
    thrnames = [(check_vpn_access, 'Core VPN Thread'), (periodical_service_bill, 'Core Period. Bill Thread'), \
                (TimeAccessBill, 'Core Time Access Thread'), (limit_checker, 'Core Limit Thread'),\
                (settlement_period_service_dog, 'Core Settlement Per. Thread'), (ipn_service, 'Core IPN Thread')]

    print "ONLY VPN THREAD!!!"
    thrnames = [(check_vpn_access, 'Core VPN Thread')]
    for thClass, thName in thrnames:
        threads.append(thClass())
        threads[-1].setName(thName)
    
    cacheThr = AccountServiceThread()
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.setName('Core AccountServiceThread')
    cacheThr.start()
    
    while cacheMaster.date == None:
        time.sleep(0.2)
        if not cacheThr.isAlive:
            logger.error('Exception in core cache thread, exiting!%s', '')
            sys.exit()
        
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
    
    print "ebs: core: started"
    #main thread should not exit!
    while True:
        time.sleep(300)
        


#===============================================================================


if __name__ == "__main__":
    if "-D" in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
        
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")

    #create logger
    logger = isdlogger.isdlogger(config.get("core", "log_type"), loglevel=int(config.get("core", "log_level")), ident=config.get("core", "log_ident"), filename=config.get("core", "log_file")) 
    
    utilites.log_adapt = logger.log_adapt
    saver.log_adapt    = logger.log_adapt
    logger.lprint('core start')
    
    try:
        transaction_number = int(config.get("core", 'transaction_number'))
        pool = PooledDB(
            mincached=7,  maxcached=20,
            blocking=True,creator=psycopg2,
            dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"),config.get("db", "username"),
                                                                   config.get("db", "host"),config.get("db", "password")))
        '''
        #last cache renewal date
        curAT_date  = None
        #lock for cache operations
        curAT_lock  = Lock()'''
        
        cacheMaster = CacheMaster()
        cacheMaster.date = None
        flags = {}
        
        suicideCondition = {}
        #function that returns number of allowed users
        #create allowedUsers
        allowedUsers = setAllowedUsers(pool.connection(), "license.lic")
        
        logger.info("Allowed users: %s", (allowedUsers(),))
        
        fMem = pfMemoize()    
        
        #--------------------------------------------------
        
        print "ebs: core: configs read, about to start"
        main()
        
    except Exception, ex:
        print 'Exception in core, exiting: ', repr(ex)
        logger.error('Exception in core, exiting: %s', repr(ex))

