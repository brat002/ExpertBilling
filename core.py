#-*-coding=utf-8-*-

import IPy
import hmac
import zlib
import hashlib
import asyncore
import threading
import dictionary
import ConfigParser
import signal
import psycopg2, psycopg2.extras
import time, datetime, os, sys, gc, traceback
import Pyro.core, Pyro.protocol, Pyro.constants

from IPy import intToIp
from hashlib import md5
from decimal import Decimal
from constants import rules
from copy import copy, deepcopy
from db import Object as Object
from daemonize import daemonize
from marshal import dumps, loads
from encodings import idna, ascii
from threading import Thread, Lock
from DBUtils.PooledDB import PooledDB
from collections import deque, defaultdict
from chartprovider.bpcdplot import cdDrawer
from chartprovider.bpplotadapter import bpplotAdapter
from utilites import create_speed_string, change_speed, PoD, get_active_sessions
from utilites import rosClient, SSHClient,settlement_period_info, in_period, in_period_info
from utilites import parse_custom_speed, parse_custom_speed_lst, cred, allowedUsersChecker, setAllowedUsers
from db import delete_transaction, get_default_speed_parameters, get_speed_parameters, dbRoutine
from db import transaction, ps_history, get_last_checkout, time_periods_by_tarif_id, set_account_deleted

try:    import mx.DateTime
except: print 'cannot import mx'

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

config = ConfigParser.ConfigParser()

def comparator(d, s):
    for key in s:
        if s[key]!='' and s[key]!='Null' and s[key]!='None':
            d[key]=s[key] 
    return d

class check_vpn_access(Thread):
    def __init__ (self):
        #self.dict=dict
        #self.timeout=timeout
        
          
        Thread.__init__(self)

    def check_period(self, rows):
        for row in rows:
            if in_period(row['time_start'],row['length'],row['repeat_after'])==True:
                return True
        return False

    """def create_speed_(self, tarif_id, nas_type):
        defaults = get_default_speed_parameters(self.cur, tarif_id)
        speeds = get_speed_parameters(self.cur, tarif_id)
        for speed in speeds:
            if in_period(speed['time_start'],speed['length'],speed['repeat_after'])==True:
                defaults = comparator(defaults, speed)
                return defaults
        return defaults"""
    
    def create_speed(self, decRec, spRec, date_):
        defaults = decRec
        speeds = spRec
        min_from_start=0
        f_speed = None
        for speed in speeds:
            #if in_period(speed['time_start'],speed['length'],speed['repeat_after'])==True:
            '''if fMem.in_period_(speed[6], speed[7], speed[8], date_)[3]:
                for i in range(6):
                    speedi = speed[i]
                    if (speedi != '') and (speedi != 'None') and (speedi != 'Null'):
                        defaults[i] = speedi
                return defaults'''

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
    
    def remove_sessions(self, cur, connection):

        cur.execute("""
            SELECT id, name, "type", ipaddress, secret, "login", "password", reset_action FROM nas_nas;
            """)
        nasses=cur.fetchall()

        #ASK 100%
        #SAVE RESULTS INTO A DICTIONARY!
        for nas in nasses:
            sessions = get_active_sessions(nas)
            #print sessions
            for session in sessions:
                cur.execute("""
                            SELECT account.id, account.vpn_ip_address, account.ipn_ip_address, account.ipn_mac_address, radius.sessionid as  sessionid
                            FROM radius_activesession as radius 
                            JOIN billservice_account as account ON radius.account_id=account.id
                            WHERE account.username=%s
                            """ , (session['name'],))
                account = cur.fetchone()
                connection.commit()
                #print "account", account
                if account is not None:
                    #print 'send pod'
                    res = PoD(dict=dict,
                              account_id=account['id'], 
                              account_name=str(session['name']), 
                              account_vpn_ip=account['vpn_ip_address'], 
                              account_ipn_ip=account['ipn_ip_address'], 
                              account_mac_address=account['ipn_mac_address'], 
                              access_type=str(session['service']), 
                              nas_ip=nas['ipaddress'], 
                              nas_type=nas['type'], 
                              nas_name=nas['name'], 
                              nas_secret=nas['secret'], 
                              nas_login=nas['login'], 
                              nas_password=nas['password'], 
                              session_id=str(account['sessionid']), 
                              format_string=str(nas['reset_action'])
                          )

            cur.execute("""
                             UPDATE radius_activesession
                             SET session_time=extract(epoch FROM date_end-date_start), date_end=interrim_update, session_status='ACK'
                             WHERE date_end is Null and nas_id=%s;""", (nas['ipaddress'],))
            connection.commit()


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
        global tp_asInPeriod
        global curNasCache,curNas_ipIdx, curAT_acIdx, curDefSpCache, curNewSpCache
        global curAT_date, curAT_lock
        cacheAT = None
        dateAT = datetime.datetime(2000, 1, 1)
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        while True:            
            try:

                try:
                    #if caches were renewed, renew local copies
                    if curAT_date > dateAT:
                        curAT_lock.acquire()
                        #account-tarif cach indexed by account_id
                        cacheAT = copy(curAT_acIdx)
                        #nas cache
                        #cacheNas  = copy(curNasCache)
                        cacheNas = copy(curNas_ipIdx)
                        #default speed cache
                        cacheDefSp = copy(curDefSpCache)
                        #current speed cache
                        cacheNewSp = copy(curNewSpCache)
                        
                        c_tp_asInPeriod = copy(tp_asInPeriod)
                        #date of renewal
                        dateAT = deepcopy(curAT_date)
                        curAT_lock.release()
                    else:
                        time.sleep(10)
                        continue
                except Exception, ex:
                    print "Vpn speed thread exception: ", repr(ex)
                   
                cur = connection.cursor()
                #close frosen sessions
                now = datetime.datetime.now()
                cur.execute("UPDATE radius_activesession SET session_time=extract(epoch FROM date_end-date_start), date_end=interrim_update, session_status='NACK' WHERE ((%s-interrim_update>=interval '00:06:00') or (%s-date_start>=interval '00:03:00' and interrim_update IS Null)) AND date_end IS Null;", (now, now,))
                connection.commit()

                #TODO: make nas_nas.ipadress UNIQUE and INDEXed
                
                cur.execute("""SELECT rs.id,rs.account_id,rs.sessionid,rs.speed_string,
                                    lower(rs.framed_protocol) AS access_type,rs.nas_id
                                    FROM radius_activesession AS rs WHERE rs.date_end IS NULL;
                                 """)
                rows=cur.fetchall()
                connection.commit()
                for row in rows:
                    try:
                        result=None
                        nasRec = cacheNas[str(row[5])]
                        acct = cacheAT.get(row[1])
                        '''
                        [0]  - id, 
                        [1]  - type, 
                        [2]  - name, 
                        [3]  - ipaddress, 
                        [4]  - secret, 
                        [5]  - login, 
                        [6]  - password, 
                        [7]  - allow_pptp, 
                        [8]  - allow_pppoe, 
                        [9]  - allow_ipn, 
                        [10] - user_add_action, 
                        [11] - user_enable_action, 
                        [12] - user_disable_action, 
                        [13] - user_delete_action, 
                        [14] - vpn_speed_action, 
                        [15] - ipn_speed_action, 
                        [16] - reset_action, 
                        [17] - confstring, 
                        [18] - multilink
                        '''
                        acc_status, allow_vpn_null,allow_vpn_block = acct[29:32]
                        disabled_by_limit, balance_blocked = acct[15:17]
                        acstatus = (((not allow_vpn_null) and (acct[1]+acct[2] >0) or (allow_vpn_null)) \
                                    and \
                                    ((allow_vpn_null) or ((not allow_vpn_block) and (not balance_blocked) and (not disabled_by_limit) and (acc_status))))
                        #print row['balance']
                        """
                        allow_vpn_null
                        allow_vpn_block
                        
                        (((account.allow_vpn_null=False and account.ballance+account.credit>=0) or (account.allow_vpn_null=True)) 
                        OR 
                        ((account.allow_vpn_block=False and account.balance_blocked=False and account.disabled_by_limit=False and account.status=True) or (account.allow_vpn_null=True)))=True 
                        """
                        tarif_id = acct[4]
                        tarif_status = acct[11]
                        if acstatus and c_tp_asInPeriod[tarif_id] and tarif_status:
                            #chech whether speed changed
                            vpn_speed = acct[24]
                            if vpn_speed=='':
                                
                                speed=self.create_speed(list(cacheDefSp.get(tarif_id,[])), cacheNewSp.get(tarif_id, []), dateAT)
                            else:
                                speed=parse_custom_speed_lst(vpn_speed)
                            
                            newspeed=''
                            newspeed = ''.join([unicode(spi) for spi in speed[:6]])
                                
                            #print row
                            #print row['speed_string'],"!!!", newspeed, type(row['speed_string']), type(newspeed)
                            if row[3]!=newspeed:
                                #print "set speed", newspeed
                                coa_result=change_speed(dict=dict, account_id=row[1], 
                                                        account_name=str(acct[32]), 
                                                        account_vpn_ip=str(acct[18]), 
                                                        account_ipn_ip=str(acct[19]), 
                                                        account_mac_address=str(acct[20]), 
                                                        access_type=str(row[4]), 
                                                        nas_ip=str(nasRec[3]), 
                                                        nas_type=nasRec[1], 
                                                        nas_name=str(nasRec[2]), 
                                                        nas_secret=str(nasRec[4]), 
                                                        nas_login=str(nasRec[5]), 
                                                        nas_password=nasRec[6], 
                                                        session_id=str(row[2]), 
                                                        format_string=str(nasRec[14]),
                                                        speed=speed[:6])                           
        
                                if coa_result==True:
                                    cur.execute("""UPDATE radius_activesession
                                                   SET speed_string=%s WHERE id=%s;
                                                """ , (newspeed, row[0],))
                                    connection.commit()
                        else:
                            result = PoD(dict=dict,
                                         account_id=row[1], 
                                         account_name=str(acct[32]), 
                                         account_vpn_ip=str(acct[18]), 
                                         account_ipn_ip=str(acct[19]), 
                                         account_mac_address=acct[20], 
                                         access_type=str(row[4]), 
                                         nas_ip=str(nasRec[3]), 
                                         nas_type=nasRec[1], 
                                         nas_name=str(nasRec[2]), 
                                         nas_secret=str(nasRec[4]), 
                                         nas_login=str(nasRec[5]), 
                                         nas_password=nasRec[6], 
                                         session_id=str(row[2]), 
                                         format_string=str(nasRec[16])
                                     )
        
                        if result==True:
                            disconnect_result='ACK'
                        elif result==False:
                            disconnect_result='NACK'
        
                        if result is not None:
                            cur.execute("""UPDATE radius_activesession SET session_status=%s WHERE sessionid=%s;
                                        """, (disconnect_result, row[2],))
                            connection.commit()                            
                    
                    except Exception, ex:
                        print "Vpn thread row exec exception: ", repr(ex)
                    
                connection.commit()   
                cur.close()    
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)
                #gc.collect()
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
        global curAT_date,curAT_lock
        global curAT_tfIdx, curPerTarifCache, curPersSetpCache
        global fMem
        dateAT = datetime.datetime(2000, 1, 1)
        while True: 
            try:
                try:
                    #if caches were renewed, renew local copies
                    if curAT_date > dateAT:
                        curAT_lock.acquire()
                        #cacheAT = deepcopy(curATCache)
                        #account-tarif cach indexed by account_id
                        cacheAT = copy(curAT_tfIdx)
                        #settlement_period cache
                        cachePerTarif  = copy(curPerTarifCache)
                        #traffic_transmit_service
                        cachePerSetp = copy(curPersSetpCache)
                        #date of renewal
                        
                        cacheSuspP = copy(curSuspPerCache)
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
                #transactions per day
                #TODO: toconfig!
                transaction_number=24
                n=(86400)/transaction_number
    
                
                '''self.cur.execute("""SELECT id, settlement_period_id, ps_null_ballance_checkout  
                                 FROM billservice_tariff  as tarif
                                 WHERE id in (SELECT tarif_id FROM billservice_periodicalservice) AND tarif.active=True""")
                rows=self.cur.fetchall()'''
                #get a list of tarifs with periodical services
                rows = cachePerTarif
                #print "SELECT TP"
                #loop through tarifs
                for row in rows:
                    #self.connection.commit()
                    #print row
                    tariff_id, settlement_period_id, null_ballance_checkout=row

                    #get accounts for tarif
                    accounts = cacheAT.get(tariff_id, [])
                    #get periodical services data
                    rows_ps = cachePerSetp.get(tariff_id,[])
                    #debit every account for tarif on every periodical service
                    for row_ps in rows_ps:
                        ps_id, ps_name, ps_cost, ps_cash_method, name_sp, time_start_ps, length_ps, length_in_sp, autostart_sp, tmtarif_id=row_ps
                        #print "new ps"
                        for account in accounts:
                            #if account.suspended
                            '''if account[13]:
                                continue'''
                            
                            accounttarif_id = account[12]
                            account_id = account[0]
                            
                            susp_per_mlt = 1
                            
                            if cacheSuspP.has_key(account_id):
                                susp_per_mlt = 0
                                #continue
                            
                            #self.connection.commit()
                            
                            account_datetime = account[3]
                            account_ballance = account[1] + account[2]
                            if account_ballance>0 or null_ballance_checkout==True:
                                if autostart_sp==True:
                                    time_start_ps=account_datetime
                                #Если в расчётном периоде указана длина в секундах-использовать её, иначе использовать предопределённые константы
                                #period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=length_in_sp, repeat_after_seconds=length_ps)
                                period_start, period_end, delta = fMem.settlement_period_(time_start_ps, length_in_sp, length_ps, dateAT)
                                #self.cur.execute("SELECT datetime::timestamp without time zone FROM billservice_periodicalservicehistory WHERE service_id=%s AND transaction_id=(SELECT id FROM billservice_transaction WHERE tarif_id=%s AND account_id=%s ORDER BY datetime DESC LIMIT 1) ORDER BY datetime DESC LIMIT 1;", (ps_id, tariff_id, account_id,))
                                now=datetime.datetime.now()
                                #now = dateAT
                                if ps_cash_method=="GRADUAL":
                                    """
                                    # Смотрим сколько расчётных периодов закончилось со времени последнего снятия
                                    # Если закончился один-снимаем всю сумму, указанную в периодической услуге
                                    # Если закончилось более двух-значит в системе был сбой. Делаем последнюю транзакцию
                                    # а остальные помечаем неактивными и уведомляем администратора
                                    """
                                    last_checkout=get_last_checkout(cursor=cur, ps_id = ps_id, accounttarif = accounttarif_id)
                                    
                                    if last_checkout==None:
                                        last_checkout=account_datetime
                                    #print "last checkout", last_checkout
                                    if (now-last_checkout).seconds+(now-last_checkout).days*86400>=n:
                                        #print "GRADUAL"
                                        #Проверяем наступил ли новый период
                                        if now-datetime.timedelta(seconds=n)<=period_start:
                                            # Если начался новый период
                                            # Находим когда начался прошльый период
                                            # Смотрим сколько денег должны были снять за прошлый период и производим корректировку
                                            #period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=length_in_sp, now=now-datetime.timedelta(seconds=n))
                                            pass
                                        # Смотрим сколько раз уже должны были снять деньги
                                        cash_summ=((float(n)*float(transaction_number)*float(ps_cost))/(float(delta)*float(transaction_number)))
                                        lc=now - last_checkout
                                        nums, ost=divmod(lc.seconds+lc.days*86400,n)
                                        #Нижеследующая функция добавляет много проблем. Временно отключена
                                        if True==False and nums>0 and (account_ballance>0 or (null_ballance_checkout==True and account_ballance<=0)):
                                            """
                                            Если стоит галочка "Снимать деньги при нулевом балансе", значит не списываем деньги на тот период, 
                                            пока денег на счету не было
                                            """
                                            #Смотрим на какую сумму должны были снять денег и снимаем её
                                            cash_summ=cash_summ*nums
                                        #make an approved transaction
                                        cash_summ = cash_summ * susp_per_mlt
                                        transaction_id = transaction(cursor=cur, account=account_id, approved=True, type='PS_GRADUAL', tarif = tariff_id, summ=cash_summ, description=u"Проводка по периодической услуге со cнятием суммы в течении периода", created = now)
                                        ps_history(cursor=cur, ps_id=ps_id, accounttarif=accounttarif_id, transaction=transaction_id, created=now)
                                    connection.commit()
                                if ps_cash_method=="AT_START":
                                    """
                                    Смотрим когда в последний раз платили по услуге. Если в текущем расчётном периоде
                                    не платили-производим снятие.
                                    """
                                    last_checkout=get_last_checkout(cursor=cur, ps_id = ps_id, accounttarif = accounttarif_id)
                                    # Здесь нужно проверить сколько раз прошёл расчётный период
                                    # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                                    # Для последней проводки ставим статус Approved=True
                                    # для всех сотальных False
                                    # Если последняя проводка меньше или равно дате начала периода-делаем снятие
                                    summ=0
                                    if last_checkout is None:
                                        first_time=True
                                        last_checkout=now
                                    else:
                                        first_time=False
                                    #print first_time==True or last_checkout<period_start
                                    if first_time==True or last_checkout<period_start:
    
                                        lc=period_start-last_checkout
                                        #Смотрим сколько раз должны были снять с момента последнего снятия
                                        nums, ost=divmod(lc.seconds+lc.days*86400, delta)
                                        if (account_ballance<=0 and null_ballance_checkout==True) or account_ballance>0:
                                            summ=ps_cost
                                            
                                        if False and nums>0 and (account_ballance>0 or (null_ballance_checkout==True and account_ballance<=0)):
                                            #Временно отключено,т.к. нигде не хранится чётких отметок с какого до какого момента у пользователя небыло денег
                                            #и с каколго до какого момента у пользователя стояла отметка "не списывать деньги по период.услугам"
                                            """
                                            Если не стоит галочка "Снимать деньги при нулевом балансе", значит не списываем деньги на тот период, 
                                            пока денег на счету не было
                                            """
                                            #Смотрим на какую сумму должны были снять денег и снимаем её
                                            summ = ps_cost*nums                                        
                                             
                                        #TODO: MAKE ACID!!!
                                        summ = summ * susp_per_mlt
                                        transaction_id = transaction(cursor=cur,
                                                                     account=account_id,
                                                                     approved=True,
                                                                     type='PS_AT_START',
                                                                     tarif = tariff_id,
                                                                     summ = summ,
                                                                     description=u"Проводка по периодической услуге со нятием суммы в начале периода",
                                                                     created = now)
                                        ps_history(cursor=cur, ps_id=ps_id, accounttarif=accounttarif_id, transaction=transaction_id, created=now)
                                    connection.commit()
                                if ps_cash_method=="AT_END":
                                    """
                                    Смотрим завершился ли хотя бы один расчётный период.
                                    Если завершился - считаем сколько уже их завершилось.
    
                                    для остальных со статусом False
                                    """
                                    last_checkout=get_last_checkout(cursor=cur, ps_id = ps_id, accounttarif = accounttarif_id)
                                    self.connection.commit()
                                    if last_checkout is None:
                                        first_time=True
                                        last_checkout=now
                                    else:
                                        first_time=False
                                    # Здесь нужно проверить сколько раз прошёл расчётный период
    
                                    # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                                    # Для последней проводки ставим статус Approved=True
                                    # для всех остальных False
                                    # Если дата начала периода больше последнего снятия или снятий не было и наступил новый период - делаем проводки

                                    summ=0
                                    if period_start>last_checkout or first_time==True: 
    
                                        if first_time==False:
                                            lc=period_start-last_checkout
                                            #rem
                                            #nums, ost=divmod((period_end-last_checkout).seconds+(period_end-last_checkout).days*86400, delta)
                                            le = period_end-last_checkout
                                            nums, ost=divmod(le.seconds+le.days*86400, delta)
    
                                            summ=ps_cost
                                            if False and  nums>0 and (account_ballance>0 or (null_ballance_checkout==True and account_ballance<=0)):
                                                summ=ps_cost*nums
                                            if (account_ballance<=0 and null_ballance_checkout==True) or account_ballance>0:
                                                summ=ps_cost
                                            descr=u"Проводка по периодической услуге со снятием суммы в конце периода"
                                        else:
                                            summ=0
                                            descr=u"Фиктивная проводка по периодической услуге со снятием суммы в конце периода"                                        
                                            
                                        #TODO: MAKE ACID!!!
                                        summ = summ * susp_per_mlt
                                        transaction_id = transaction(cursor=cur,
                                                                     account=account_id,
                                                                     approved=True,
                                                                     type='PS_AT_END',
                                                                     tarif = tariff_id,
                                                                     summ=summ,
                                                                     description=descr,
                                                                     created = now)
                                        ps_history(cursor=cur, ps_id=ps_id, accounttarif=accounttarif_id, transaction=transaction_id, created=now)
                                    connection.commit()
                connection.commit()
                cur.close()
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)
            gc.collect()
            
            
            #self.connection.close()
            time.sleep(180)
            
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
        global curAT_date,curAT_lock
        global curAT_acctIdx, curTimeAccNCache, curTimePerNCache
        global fMem
        dateAT = datetime.datetime(2000, 1, 1)
        while True:            
            try:
                try:
                    #if caches were renewed, renew local copies
                    if curAT_date > dateAT:
                        curAT_lock.acquire()
                        #cacheAT = deepcopy(curATCache)
                        #account-tarif cach indexed by account_id
                        #cacheAT = deepcopy(curAT_acctIdx)
                        #settlement_period cache
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
                    continue
                
                cur = connection.cursor()
                '''self.cur.execute("""
                                 SELECT rs.account_id, rs.sessionid, rs.session_time, rs.interrim_update::timestamp without time zone, tacc.id, tarif.id, acc_t.id
                                 FROM radius_session as rs
                                 JOIN billservice_accounttarif as acc_t ON acc_t.account_id=rs.account_id
                                 JOIN billservice_tariff as tarif ON tarif.id=acc_t.tarif_id
                                 JOIN billservice_timeaccessservice as tacc ON tacc.id=tarif.time_access_service_id
                                 WHERE rs.checkouted_by_time=False and rs.date_start is NUll and acc_t.datetime<rs.interrim_update and tarif.active=True ORDER BY rs.interrim_update ASC;
                                 """)'''
                cur.execute("""SELECT rs.account_id, rs.sessionid, rs.session_time, rs.interrim_update,tarif.time_access_service_id, tarif.id, acc_t.id
                                 FROM radius_session AS rs
                                 JOIN billservice_accounttarif AS acc_t ON acc_t.account_id=rs.account_id
                                 JOIN billservice_tariff AS tarif ON tarif.id=acc_t.tarif_id
                                 WHERE (NOT rs.checkouted_by_time) and (rs.date_start IS NULL) AND (tarif.active) AND (acc_t.datetime < rs.interrim_update) AND (tarif.time_access_service_id NOTNULL)
                                 ORDER BY rs.interrim_update ASC;""")
                rows=cur.fetchall()
                connection.commit()
                for row in rows:
                    #1. Ищем последнюю запись по которой была произведена оплата
                    #2. Получаем данные из услуги "Доступ по времени" из текущего ТП пользователя
                    #TODO:2. Проверяем сколько стоил трафик в начале сессии и не было ли смены периода.
                    #TODO:2.1 Если была смена периода -посчитать сколько времени прошло до смены и после смены,
                    # рассчитав соотв снятия.
                    #2.2 Если снятия не было-снять столько, на сколько насидел пользователь
                    account_id, session_id, session_time, interrim_update, ps_id, tarif_id, accountt_tarif_id = row

                    execute("""SELECT session_time FROM radius_session WHERE sessionid=%s AND checkouted_by_time=True
                               ORDER BY interrim_update DESC LIMIT 1
                            """, (session_id,))
                    try:
                        old_time=cur.fetchone()[0]
                    except:
                        old_time=0
                    
                    total_time=session_time-old_time
    
                    cur.execute(
                        """
                        SELECT id, size FROM billservice_accountprepaystime WHERE account_tarif_id=%s
                        """, (accountt_tarif_id,))
                    
                    try:
                        prepaid_id, prepaid=cur.fetchone()
                    except:
                        prepaid=0
                        prepaid_id=-1
                    connection.commit()
                    if prepaid>0:
                        if prepaid>=total_time:
                            total_time=0
                            prepaid=prepaid-total_time
                        elif total_time>=prepaid:
                            total_time=total_time-prepaid
                            prepaid=0
                        cur.execute("""UPDATE billservice_accountprepaystime SET size=%s WHERE id=%s""", (prepaid, prepaid_id,))
                        connection.commit()
    
                    '''self.cur.execute("""
                        SELECT tan.time_period_id, tan.cost
                        FROM billservice_timeaccessnode as tan
                        JOIN billservice_timeperiodnode as tp ON tan.time_period_id=tp.id
                        WHERE tan.time_access_service_id=%s
                        """ % ps_id)'''
                    '''self.cur.execute("""SELECT tan.time_period_id, tan.cost
                        FROM billservice_timeaccessnode as tan
                        WHERE (tan.time_period_id is not NULL) AND (tan.time_access_service_id=%s)""", (ps_id,))
                    periods=self.cur.fetchall()'''
                    #get the list of time periods and their cost
                    now = datetime.datetime.now()
                    periods = cacheTimeAccN.get(ps_id, [])
                    for period in periods:
                        period_id=period[0]
                        period_cost=period[1]
                        '''self.cur.execute(
                            """
                            SELECT tpn.id, tpn.name, tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
                            FROM billservice_timeperiodnode as tpn
                            JOIN billservice_timeperiod_time_period_nodes as tptpn ON tpn.id=tptpn.timeperiodnode_id
                            WHERE tptpn.timeperiod_id=%s
                            """ % period_id)'''
                        '''self.cur.execute("""SELECT tpn.id, tpn.name, tpn.time_start, tpn.length, tpn.repeat_after
                            FROM billservice_timeperiodnode as tpn
                            WHERE (%s IN (SELECT tptpn.timeperiod_id from billservice_timeperiod_time_period_nodes as tptpn WHERE tpn.id=tptpn.timeperiodnode_id))""", (period_id,))
                        period_nodes_data=self.cur.fetchall()'''
                        #get period nodes and check them
                        period_nodes_data = cacheTimePerN.get(period_id,[])
                        for period_node in period_nodes_data:
                            period_id, period_name =period_node[0:2]
                            period_start, period_length, repeat_after = period_node[2:5]
                            #if in_period(time_start=period_start,length=period_length, repeat_after=repeat_after):
                            if fMem.in_period_(period_start,period_length,repeat_after, dateAT)[3]:
                                summ=(float(total_time)/60.000)*period_cost
                                if summ>0:
                                    transaction(
                                        cursor=cur,
                                        type='TIME_ACCESS',
                                        account=account_id,
                                        approved=True,
                                        tarif=tarif_id,
                                        summ=summ,
                                        description=u"Снятие денег за время по RADIUS сессии %s" % session_id,
                                        created=now
                                    )
                                    connection.commit()

                    cur.execute("""UPDATE radius_session SET checkouted_by_time=True
                                   WHERE sessionid=%s AND account_id=%s AND interrim_update=%s
                                """, (unicode(session_id), account_id, interrim_update,))
                    connection.commit()
                    
                connection.commit()
                cur.close()
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)

            gc.collect()
            time.sleep(60)


class Picker(object):
    __slots__= ('data',)
    def __init__(self):
        self.data={}      

    def add_summ(self, account, tarif, summ):
        if self.data.has_key(account):
            self.data[account]['summ']+=summ
        else:
            self.data[account]={'tarif':tarif, 'summ':summ}

    def get_list(self):
        for key in self.data:
            yield {'account':key, 'tarif':self.data[key]['tarif'], 'summ': self.data[key]['summ']}

#maybe save if database errors???
class DepickerThread(Thread):
    '''Thread that takes a Picker object and executes transactions'''
    def __init__ (self, picker):
        self.picker = picker
        Thread.__init__(self)
        
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        cur = connection.cursor()
        now = datetime.datetime.now()
        for l in self.picker.get_list():
            #debit accounts
            transaction(
                cursor=cur,
                type='NETFLOW_BILL',
                account=l['account'],
                approved=True,
                tarif=l['tarif'],
                summ=l['summ'],
                description=u"",
                created=now
            )
            connection.commit()
        cur.close()
        
class NetFlowRoutine(Thread):
    '''Thread that handles NetFlow statistic packets and bills according to them'''
    def __init__ (self):
        Thread.__init__(self)
        

    def get_actual_cost(self, trafic_transmit_service_id, traffic_class_id, direction, octets_summ, stream_date, cTRTRNodesCache):
        """
        Метод возвращает актуальную цену для направления трафика для пользователя:
        """
        if direction=="INPUT":
            #d = "in_direction=True"
            d = 9
        elif direction=="OUTPUT":
            #d = "out_direction=True"
            d = 10
        else:
            return 0
        #TODO: check whether differentiated traffic billing us used <edge_start>=0; <edge_end>='infinite'
        #print (octets_summ, octets_summ, octets_summ, trafic_transmit_service_id, traffic_class_id, d)
        #trafic_transmit_nodes=self.cur.fetchall()
        trafic_transmit_nodes = cTRTRNodesCache.get((trafic_transmit_service_id, traffic_class_id), [])
        cost=0
        min_from_start=0
        # [0] - ttsn.id, [1] - ttsn.cost, [2] - ttsn.edge_start, [3] - ttsn.edge_end, [4] - tpn.time_start, [5] - tpn.length, [6] - tpn.repeat_after
        for node in trafic_transmit_nodes:
            #'d': '9' - in_direction, '10' - out_direction
            if node[d]:
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
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')

        global curAT_acIdx
        global curAT_date,curAT_lock
        global nfIncomingQueue
        global tpnInPeriod, curSPCache, curTTSCache
        global prepaysCache, TRTRNodesCache
        global store_na_tarif, store_na_account        
        cacheAT = None
        dateAT = datetime.datetime(2000, 1, 1)
        sumPick = Picker()
        pstartD = time.time()
        oldAcct = defaultdict(list)
        cur = connection.cursor()
        while True:
            try:                
                try:
                    #if caches were renewed, renew local copies
                    if curAT_date > dateAT:
                        curAT_lock.acquire()
                        #cacheAT = deepcopy(curATCache)
                        #account-tarif cach indexed by account_id
                        cacheAT = copy(curAT_acIdx)
                        #settlement_period cache
                        cacheSP  = copy(curSPCache)
                        #traffic_transmit_service
                        cacheTTS = copy(curTTSCache)
                        
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
                if sumPick.data and (time.time() > pstartD + 60.0):
                    #start thread that cleans Picker
                    depickThr = DepickerThread(sumPick)
                    depickThr.start()
                    sumPick = Picker()
                    pstartD = time.time()
                    
                #if deadlocks arise add locks
                #pop flows
                try:
                    flows = loads(nfIncomingQueue.popleft())
                except Exception, ex:
                    time.sleep(2)
                    continue
                #print flows
                #iterate through them
                for flow in flows:
                    #get account id and get a record from cache based on it
                    acct = cacheAT.get(flow[20])
                    #get collection date
                    stream_date = datetime.datetime.fromtimestamp(flow[21])
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
                    if (tarif_id == None) or (not (acct[11] or store_na_tarif)) or (not (acct[29] or store_na_account)):
                        continue
                    
                    tarif_mode = False
                    
                    tts_id = acct[7]
                    #if traffic_transmit_service_id is OK
                    if tts_id:
                        tarif_mode = c_tpnInPeriod[tts_id]
                        
                    #if tarif_mode is False or tarif.active = False
                    #write statistics without billing it
                    if not (tarif_mode and acct[11] and acct[29]):
                        #cur = connection.cursor()
                        cur.execute(
                        """
                        INSERT INTO billservice_netflowstream(
                        nas_id, account_id, tarif_id, direction,date_start, src_addr, traffic_class_id,
                        dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s);
                        """, (flow[11], flow[20], tarif_id, flow[23], stream_date,intToIp(flow[0],4), "{"+','.join([str(cls) for cls in flow[22]])+"}", intToIp(flow[1],4), flow[6],flow[9], flow[10], flow[13], False, False,)
                        )
                        connection.commit()
                        #cur.close()
                        continue
                    
                    s = False
                    #if traffic_transmit_service_id is OK
                    if tts_id:
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
                        for tclass in flow[22]:
                            #acct[7] - traffic_transmit_service_id
                            #flow[23] - direction
                            f_direction = flow[23]
                            trafic_cost=self.get_actual_cost(tts_id, tclass, f_direction, octets_summ, stream_date, c_TRTRNodesCache)
                            """
                            Использован т.н. дифференциальный подход к начислению денег за трафик
                            Тарифный план позволяет указать по какой цене считать трафик
                            в зависимости от того сколько этого трафика уже накачал пользователь за расчётный период
                            """
                            #direction
                            
                            if f_direction=="INPUT":
                                d = 2
                            elif f_direction=="OUTPUT":
                                d = 3
                            else:
                                d = 3
                            #get a record from prepays cache
                            #keys: traffic_transmit_service_id, accounttarif.id, trafficclass
                            prepInf =  c_prepaysCache.get((tts_id, acct[12],tclass))
                            
                            octets = flow[6]
                            if prepInf:
                                #d = 5: chacs whether in_direction is True; d = 6: whether out_direction
                                if prepInf[d]:
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
        
                                        #cur = connection.cursor()
                                        cur.execute("""UPDATE billservice_accountprepaystrafic SET size=size-%s WHERE id=%s""", (prepaid, prepaid_id,))
                                        connection.commit()
                                        #cur.close()
                                        '''
                                        #if the cache didn't change in meantime, save changes in cache
                                        if prepHnd == prepInf[1]:
                                            prepInf[1] = prepInf[1] - prepaid
                                        '''
            
                            summ=(trafic_cost*octets)/(1024000)
        
                            if summ>0:
                                #account_id, tariff_id, summ
                                sumPick.add_summ(flow[20], acct[4], summ)
                                    
                                #insert statistics
                    #cur = connection.cursor()
                    cur.execute(
                    """
                    INSERT INTO billservice_netflowstream(
                    nas_id, account_id, tarif_id, direction,date_start, src_addr, traffic_class_id,
                    dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                    VALUES (%s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s);
                    """, (flow[11], flow[20], tarif_id, flow[23], stream_date,intToIp(flow[0],4), "{"+','.join([str(cls) for cls in flow[22]])+"}", intToIp(flow[1],4), flow[6],flow[9], flow[10], flow[13], True, False,)
                    )
                    connection.commit()
                    #cur.close()
                                
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + repr(ex)
                else:
                    print self.getName() + ": exception: " + repr(ex)
                    


class limit_checker(Thread):
    """
    Проверяет исчерпание лимитов. если лимит исчерпан-ставим соотв галочку в аккаунте
    """
    def __init__ (self):
        Thread.__init__(self)
 
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global curATCache, curAT_tfIdx
        global curAT_date, curAT_lock
        global curSPCache, curTLimitCache       
        cacheAT = None
        dateAT = datetime.datetime(2000, 1, 1)
        
        
        while True:            
            try:
                
                try:
                    #if caches were renewed, renew local copies
                    if curAT_date > dateAT:
                        curAT_lock.acquire()
                        #cacheAT = deepcopy(curATCache)
                        #account-tarif cach indexed by account_id
                        cacheAT = copy(curATCache)
                        #settlement_period cache
                        cacheSP  = copy(curSPCache)
                        #traffic_transmit_service
                        cacheTLimit = copy(curTLimitCache)
                        #date of renewal
                        dateAT = deepcopy(curAT_date)
                        curAT_lock.release()
                    else:
                        time.sleep(10)
                        continue
                except:
                    time.sleep(1)
                    continue
                #cur = self.connection.cursor()
                #get tarifs with limits
                '''self.cur.execute(
                    """
                    SELECT account.id, account.disabled_by_limit, acctt.datetime::timestamp without time zone,  
                    tlimit.id, tlimit.size, tlimit.mode, tlimit.in_direction, tlimit.out_direction,
                    sp.time_start::timestamp without time zone, sp.length, sp.length_in, sp.autostart
                    FROM billservice_tariff as tarif
                    JOIN billservice_accounttarif as acctt ON acctt.tarif_id=tarif.id 
                    AND acctt.datetime=
                    (SELECT datetime FROM billservice_accounttarif WHERE account_id=acctt.account_id and datetime<now() ORDER BY datetime DESC LIMIT 1)
                    JOIN billservice_account as account ON account.id=acctt.account_id
                    LEFT JOIN billservice_trafficlimit as tlimit ON tlimit.tarif_id = tarif.id
                    LEFT JOIN billservice_settlementperiod as sp ON sp.id = tlimit.settlement_period_id
                    WHERE tarif.active=True
                    ORDER BY account.id ASC;
                    """)
                account_tarifs=self.cur.fetchall()
                self.connection.commit()'''
                #self.cur.close()
                #self.cur = self.connection.cursor()
                #!if tarif.id not in limitcache.keys()
                oldid=-1
                """for row in account_tarifs:
                    account_id, \
                              disabled_by_limit,\
                              account_start, \
                              limit_id, \
                              limit_size, \
                              limit_mode, \
                              in_direction, \
                              out_direction, \
                              sp_time_start, \
                              sp_length, \
                              sp_length_in, \
                              autostart_sp = row"""
                cur = connection.cursor()
                for acct in cacheAT:
                    
                    account_id = acct[0]
                    tarif_id = acct[4]
                    limitRecs = cacheTLimit.get(tarif_id)
                    disabled_by_limit = acct[15]
                    if not limitRecs:
                        if disabled_by_limit:
                            cur.execute(
                                """
                                UPDATE billservice_account
                                SET disabled_by_limit=%s
                                WHERE id=%s;
                                """, (False, account_id,))
                            connection.commit()
                        continue
                    
                    for limitRec in limitRecs:
                        lr_in_dir  = limitRec[5]
                        lr_out_dir = limitRec[6]
                        
                        if lr_in_dir==lr_out_dir==False:
                            continue
                        block=False
                        
                        if oldid==account_id and block:
                            """
                            Если у аккаунта уже есть одно превышение лимита
                            то больше для него лимиты не проверяем
                            """
                            continue
                        
                        #get settlement period record
                        spRec = cacheSP[limitRec[3]]
                        '''if autostart_sp==True:
                            sp_start=account_start
                        else:
                            sp_start = sp_time_start'''
                        #if autostart - start time = acct.datetime
                        if spRec[4]:
                            sp_start = acct[3]
                        else:
                            sp_start = spRec[1]
                        #settlement_period_start, settlement_period_end, delta = settlement_period_info(time_start=sp_start, repeat_after=sp_length_in, repeat_after_seconds=sp_length)
                        settlement_period_start, settlement_period_end, delta = settlement_period_info(sp_start, spRec[3], spRec[2], dateAT)
                        #если нужно считать количество трафика за последнеие N секунд, а не за рачётный период, то переопределяем значения
                        now= dateAT
                        limit_mode = limitRec[7]
                        if limit_mode==True:
                            settlement_period_start=now-datetime.timedelta(seconds=delta)
                            settlement_period_end=now
        
                        
                        #limitRec[5] - in_direction
                        d=""
                        if lr_in_dir:
                            d+=" 'INPUT'"
                        if lr_out_dir:
                            if lr_in_dir:
                                d+=","
                            d+="'OUTPUT'"
        
                        connection.commit()
                        #В запрос ниже НЕЛЬЗЯ менять символ подстановки на , ,т.к. тогда неправильно форматируется d
                        #acct[0] = account_id, limitRec[0] = limit_id
                        cur.execute("""
                             SELECT sum(octets) as size FROM billservice_netflowstream as nf 
                             WHERE nf.account_id=%s AND nf.traffic_class_id && ARRAY((SELECT tltc.trafficclass_id 
                             FROM billservice_trafficlimit_traffic_class as tltc 
                             WHERE tltc.trafficlimit_id=%s)) 
                             AND (date_start>'%s' AND date_start<'%s') and nf.direction in (%s)  
                             """ % (account_id, limitRec[0], settlement_period_start, settlement_period_end, d,))
        
                        tsize=0
                        sizes=cur.fetchone()
                        connection.commit()
    
                        #print "sizes", sizes
                        if sizes[0]!=None:
                            tsize=sizes[0]
                        #limitRec[4] - limit_size
                        if tsize>Decimal("%s" % limitRec[4]):
                            block=True
    
                        #print "block", block, tsize>Decimal("%s" % limitRec[4]), tsize, limitRec[4]
    
        
                        #Если у тарифного плана нет лимитов-снимаем отметку disabled_by_limit
                        #account_id
                        oldid=account_id
                        #acct[15] - disabled_by_limit
                        if disabled_by_limit!=block:
                            cur.execute(
                                """
                                UPDATE billservice_account
                                SET disabled_by_limit=%s
                                WHERE id=%s;
                                """ , (block, account_id,))
                            connection.commit()
    
                connection.commit()
                #print self.getName() + " threadend"
                cur.close()
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)

            
            #self.connection.close()
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
        #self.connection = pool.connection()
        #self.connection._con._con.set_client_encoding('UTF8')
        #self.cur = self.connection.cursor()
        Thread.__init__(self)


    def stop(self):
        """
        Stop the thread
        """


    def run(self):
        """
        Сделать привязку к пользователю через billservice_accounttarif
        """ 
        
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global curATCache, curShedLogCache, curSPCache, curTimeAccSrvCache, curTTSCache
        global curOneTimeSrvCache, curOTSHistCache
        global fMem
        global curAT_date, curAT_lock
        dateAT = datetime.datetime(2000, 1, 1)
        while True:
            try:
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
                '''self.cur.execute(
                    """
                    SELECT shedulelog.id, shedulelog.accounttarif_id, account.id, account.balance_blocked, (account.ballance+account.credit) as balance, 
                    shedulelog.ballance_checkout::timestamp without time zone, 
                    shedulelog.prepaid_traffic_reset::timestamp without time zone, 
                    shedulelog.prepaid_time_reset::timestamp without time zone,
                    sp.time_start::timestamp without time zone, sp.length, 
                    sp.length_in,sp.autostart, accounttarif.id, 
                    accounttarif.datetime::timestamp without time zone,  
                    tariff.id, tariff.reset_tarif_cost , tariff.cost, tariff.traffic_transmit_service_id, 
                    tariff.time_access_service_id, traffictransmit.reset_traffic, timeaccessservice.reset_time,
                    shedulelog.balance_blocked::timestamp without time zone, 
                    shedulelog.prepaid_traffic_accrued::timestamp without time zone, 
                    shedulelog.prepaid_time_accrued::timestamp without time zone
                    FROM billservice_account as account
                    LEFT JOIN billservice_shedulelog as shedulelog on shedulelog.account_id=account.id
                    JOIN billservice_tariff as tariff ON tariff.id=get_tarif(account.id)
                    JOIN billservice_accounttarif AS accounttarif ON accounttarif.id=(SELECT id FROM billservice_accounttarif
                    WHERE account_id=account.id and tarif_id=tariff.id and  datetime<now() ORDER BY datetime DESC LIMIT 1)
                    LEFT JOIN billservice_settlementperiod as sp ON sp.id=tariff.settlement_period_id
                    LEFT JOIN billservice_traffictransmitservice as traffictransmit ON traffictransmit.id=tariff.traffic_transmit_service_id
                    LEFT JOIN billservice_timeaccessservice as timeaccessservice ON timeaccessservice.id=tariff.time_access_service_id
                    WHERE account.status=True and tariff.active=True;
                    """)
    
                rows=self.cur.fetchall()
                self.connection.commit()
                self.cur.close()
                self.cur = self.connection.cursor()'''
                '''
                for row in rows:
                    (shedulelog_id, accounttarif_id_shedulelog, account_id, account_balance_blocked, account_balance,ballance_checkout, prepaid_traffic_reset, prepaid_time_reset,
                     time_start, length, length_in, autostart, accounttarif_id, acct_datetime, tarif_id,
                     reset_tarif_cost, cost, traffic_transmit_service_id, time_access_service_id,
                     reset_traffic, reset_time, balance_blocked, prepaid_traffic_accrued, prepaid_time_accrued) = row
                '''
                for acct in cacheAT:
                    #account.status=True and tariff.active=True
                    if not (acct[29] or acct[11]):
                        continue
                    account_id = acct[0]
                    ballance_checkout, balance_blocked = (None, None)
                    prepaid_traffic_reset, prepaid_traffic_accrued, accounttarif_id_shedulelog = (None, None, None)
                    prepaid_time_reset, prepaid_time_accrued = (None, None)
                    shedlRec = cacheShedLog.get(account_id)
                    
                    if shedlRec==None:
                        shedulelog_id=-1
                    else:
                        shedulelog_id    = shedlRec[0]
                        ballance_checkout = shedlRec[2]                        
                        prepaid_traffic_reset, prepaid_traffic_accrued = shedlRec[3:5]                        
                        prepaid_time_reset, prepaid_time_accrued       = shedlRec[5:7]
                        balance_blocked            = shedlRec[7]
                        accounttarif_id_shedulelog = shedlRec[8]
                        
                    acct_datetime = acct[3]
                    period_end = None
                    time_start = None
                    now = datetime.datetime.now()
                    #if tariff has settlement_period_id
                    setper_id = acct[10]
                    if setper_id:
                        setpRec = cacheSetP.get(setper_id)
                        #if autostart:
                        if setpRec[4]:
                            time_start=acct_datetime
                        else:
                            time_start = setpRec[1]
                        #time_start, length_in, length
                        period_start, period_end, delta = fMem.settlement_period_(time_start, setpRec[3], setpRec[2], dateAT)
                        '''if time_start is not None:
                        if autostart:
                            time_start=acct_datetime    
                        period_start, period_end, delta = settlement_period_info(time_start=time_start, repeat_after=length_in, repeat_after_seconds=length)'''
                       
                    else:
                        time_start = acct_datetime
                        period_start = acct_datetime
                        delta = 86400*365*365
                        
                    tarif_id = acct[4]
                    accounttarif_id = acct[12]
                    #нужно производить в конце расчётного периода
                    if ballance_checkout==None: ballance_checkout = acct_datetime
                    if ballance_checkout<period_start:
                        #Снять сумму до стоимости тарифного плана
                        #!!! ASK ABOUT period_end!!!
                        #acct[9] - reset_tarif_cost
                        if acct[9] and period_end:
                            cur.execute(
                                """
                                SELECT sum(summ)
                                FROM billservice_transaction
                                WHERE created > %s and created< %s and account_id=%s and tarif_id=%s;
                                """, (period_start, period_end, account_id, tarif_id,))
                            summ=cur.fetchone()[0]
                            if summ==None:
                                summ=0
    
                            if cost>summ:
                                s=cost-summ
                                transaction(
                                    cursor=cur,
                                    type='END_PS_MONEY_RESET',
                                    account=account_id,
                                    approved=True,
                                    tarif=tarif_id,
                                    summ=s,
                                    description=u"Доснятие денег до стоимости тарифного плана у %s" % account_id,
                                    created=now
                                )
    
    
                            cur.execute("UPDATE billservice_shedulelog SET ballance_checkout=%s WHERE account_id=%s RETURNING id;", (now,account_id,))
                            shedulelog_id =cur.fetchone()
                            if shedulelog_id==None:
                                cur.execute("""INSERT INTO billservice_shedulelog(account_id, accounttarif_id, ballance_checkout) values(%s, %s, %s);
                                            """, (account_id, accounttarif_id, now))
    
    
                    connection.commit()
                    account_balance = acct[1] + acct[2]
                    account_balance_blocked = acct[16]
                    cost = acct[8]
                    #Если балланса не хватает - отключить пользователя
                    if (balance_blocked is None or balance_blocked<=period_start) and cost>=account_balance and account_balance_blocked==False:
                        #print "balance blocked1", ballance_checkout, period_start, cost, account_balance
                        cur.execute("""UPDATE billservice_account SET balance_blocked=True WHERE id=%s and ballance+credit<%s;
                                    """, (account_id, cost,))
    
    
                        cur.execute("""UPDATE billservice_shedulelog SET balance_blocked = %s WHERE account_id=%s RETURNING id;
                                    """, (now, account_id,))
    
                        if cur.fetchone()==None:
                            cur.execute("""INSERT INTO billservice_shedulelog(account_id, accounttarif_id,balance_blocked) values(%s, %s, %s); 
                                        """, (account_id, accounttarif_id, now,))
                    if account_balance_blocked==True and account_balance>=cost:
                        """
                        Если пользователь отключён, но баланс уже больше разрешённой суммы-включить пользователя
                        """
                        #print "balance blocked2"
                        cur.execute(
                            """
                            UPDATE billservice_account SET balance_blocked=False WHERE id=%s;
                            """, (account_id,))                            
    
                    connection.commit()
                    
                    traffic_transmit_service_id = acct[7]
                    reset_traffic = None
                    if traffic_transmit_service_id != None:
                        ttsRec= cacheTTS.get(traffic_transmit_service_id)
                        reset_traffic = ttsRec[1]
                    
                    
                    if prepaid_traffic_reset is None: prepaid_traffic_reset = acct_datetime
                    if (prepaid_traffic_reset<period_start and reset_traffic==True) or traffic_transmit_service_id is None or accounttarif_id!=accounttarif_id_shedulelog:
                        """
                        (Если наступил новый расчётный период и нужно сбрасывать трафик) или если нет услуги с доступом по трафику или если сменился тарифный план
                        """
                        cur.execute("""DELETE FROM billservice_accountprepaystrafic WHERE account_tarif_id=%s;
                                    """ % accounttarif_id)
    
                        cur.execute("UPDATE billservice_shedulelog SET prepaid_traffic_reset=%s WHERE account_id=%s RETURNING id;", (now, account_id,))
                        if cur.fetchone()==None:
                            cur.execute("""INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_reset) values(%s, %s, %s) ;
                                        """, (account_id, accounttarif_id, now,))    
                    connection.commit()
    
                    if (prepaid_traffic_accrued is None or prepaid_traffic_accrued<period_start) and traffic_transmit_service_id:                          
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
                                               VALUES(%s, %s, %f*1024000, '%s');
                                            """ % (accounttarif_id, prepaid_traffic_id, size, now,))
                            connection.commit()
                            
                        if u==True:
                            cur.execute("UPDATE billservice_shedulelog SET prepaid_traffic_accrued=%s WHERE account_id=%s RETURNING id;", (now, account_id,))
                            if cur.fetchone()==None:
                                cur.execute("""INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_accrued) values(%s, %s, %s) ;
                                            """, (account_id, accounttarif_id, now,))  
                    connection.commit() 
                    
                    time_access_service_id = acct[6]
                    reset_time = None
                    prepaid_time = 0
                    if time_access_service_id:
                        taccsRec = cacheTAccS.get(time_access_service_id)
                        reset_time    = taccsRec[2]
                        prepaid_time  = taccsRec[1]
                    if (prepaid_time_reset is None or prepaid_time_reset<period_start) and time_access_service_id  or accounttarif_id!=accounttarif_id_shedulelog:
                        #снять время и начислить новое
                        if reset_time:
                            cur.execute("""DELETE FROM billservice_accountprepaystime WHERE account_tarif_id=%s;
                                        """, (accounttarif_id,))    
                            cur.execute("UPDATE billservice_shedulelog SET prepaid_time_reset=%s WHERE account_id=%s RETURNING id;", (now, account_id,))
                            if cur.fetchone()==None:
                                cur.execute("""INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_reset) values(%s, %s, %s) ;
                                            """, (account_id, accounttarif_id,now,))        
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
                                transaction_id = transaction(
                                                             cursor=cur,
                                                             type='ONETIME_SERVICE',
                                                             account=account_id,
                                                             approved=True,
                                                             tarif=tarif_id,
                                                             summ=ots[2],
                                                             description=u"Снятие денег по разовой услуге %s" % ots[1],
                                                             created=now
                                                             )
                                cur.execute("INSERT INTO billservice_onetimeservicehistory(accounttarif_id,onetimeservice_id, transaction_id,datetime) VALUES(%s, %s, %s, %s);", (accounttarif_id, ots_id, transaction_id,now,))
                                connection.commit()
                                cacheOTSHist[(accounttarif_id, ots_id)] = (1,)
                        
                connection.commit()
                #Делаем проводки по разовым услугам тем, кому их ещё не делали
                #to select good accounttarifs:
                #select distinct order by datetime and datetime < dateAT
                #onetimeservice??
                '''self.cur.execute("""
                                 SELECT account.id as account_id, service.id as service_id, service.name as service_name, service.cost as service_cost, tarif.id as tarif_id, (SELECT id FROM billservice_accounttarif
                                 WHERE account_id=account.id and datetime<now() ORDER BY datetime DESC LIMIT 1) as accounttarif
                                 FROM billservice_account as account
                                 JOIN billservice_tariff as tarif ON tarif.id=get_tarif(account.id)
                                 JOIN billservice_onetimeservice as service ON service.tarif_id=tarif.id
                                 LEFT JOIN billservice_onetimeservicehistory as oth ON oth.accounttarif_id=(SELECT id FROM billservice_accounttarif
                                 WHERE account_id=account.id and datetime<now() ORDER BY datetime DESC LIMIT 1) and service.id=oth.onetimeservice_id
                                 WHERE (account.ballance+account.credit)>0 and oth.id is Null and tarif.active=True;
                                 """)
                rows = self.cur.fetchall()
                self.connection.commit()
                #print "onetime", rows
                for row in rows:
                    account_id, service_id, service_name, cost, tarif_id, accounttarif_id = row
                    transaction_id = transaction(
                        cursor=self.cur,
                        type='ONETIME_SERVICE',
                        account=account_id,
                        approved=True,
                        tarif=tarif_id,
                        summ=cost,
                        description=u"Снятие денег по разовой услуге %s" % service_name
                    )
                    self.cur.execute("INSERT INTO billservice_onetimeservicehistory(accounttarif_id,onetimeservice_id, transaction_id,datetime) VALUES(%s, %s, %s, now());", (accounttarif_id, service_id, transaction_id,))
    
                    self.connection.commit()'''

            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)

            #self.cur.close()
            #self.connection.close()
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

    '''def create_speed(self, tarif_id):
        defaults = get_default_speed_parameters(self.cur, tarif_id)
        speeds = get_speed_parameters(self.cur, tarif_id)
        for speed in speeds:
            if in_period(speed['time_start'], speed['length'], speed['repeat_after'])==True:
                defaults = comparator(defaults, speed)
                return defaults

        #print "speed_result=", defaults
        return defaults'''
    
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
        global tp_asInPeriod
        global curNasCache,curATCache
        global curAccParCache,curDefSpCache,curNewSpCache
        global curAT_date,curAT_lock
        cacheAT = None
        dateAT = datetime.datetime(2000, 1, 1)
        while True:             
            try:
                '''self.cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
                self.cur.execute("""SELECT account.id as account_id,
                    account.username as account_username, 
                    account.ipn_ip_address as account_ipn_ip_address, 
                    account.vpn_ip_address as account_vpn_ip_address, 
                    account.ipn_mac_address as account_ipn_mac_address ,
                    (account.ballance+account.credit) as ballance, 
                    account.disabled_by_limit as account_disabled_by_limit, 
                    account.balance_blocked as account_balance_blocked,
                    account.ipn_status as account_ipn_status, 
                    account.ipn_speed as account_ipn_speed, 
                    account.ipn_added as ipn_added,
                    account.status as account_status,
                    tariff.id as tarif_id, nas.name as nas_name,
                    nas."type" as nas_type, nas.user_enable_action as nas_user_enable, 
                    nas.user_disable_action as nas_user_disable,
                    nas.ipn_speed_action as nas_ipn_speed, 
                    nas.user_add_action as nas_user_add,
                    nas."login" as nas_login, nas."password" as nas_password, 
                    nas."ipaddress" as nas_ipaddress,
                    accessparameters.access_time_id as access_time_id, 
                    ipn_speed_table.speed as ipn_speed, 
                    ipn_speed_table.state as ipn_state,
                    accessparameters.access_type as access_type
                    FROM billservice_account as account
                    JOIN billservice_tariff as tariff ON tariff.id=get_tarif(account.id)
                    JOIN billservice_accessparameters as accessparameters ON accessparameters.id=tariff.access_parameters_id
                    JOIN nas_nas as nas ON nas.id=account.nas_id
                    LEFT JOIN billservice_accountipnspeed as ipn_speed_table ON ipn_speed_table.account_id=account.id
                    WHERE accessparameters.ipn_for_vpn=True and account.ipn_ip_address!='0.0.0.0' and tariff.active=True
                    ;""")'''
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
                    if (not accpRec) or (not accpRec[9]):
                        continue
                    #print "check ipn"
                    sended=None
                    recreate_speed = False
                    #period=self.check_period(time_periods_by_tarif_id(self.cur, row['tarif_id']))
                    #print period
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
                    
                    #print account_ipn_speed
                    if account_ipn_speed=='' or account_ipn_speed==None:    
                        speed=self.create_speed(list(cacheDefSp[tarif_id]), cacheNewSp[tarif_id], dateAT)
                    else:
                        speed = parse_custom_speed_lst(account_ipn_speed)
                    #print speed
                    
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
                    if newspeed!=ipn_speed or (ipn_state==False and newspeed!=ipn_speed) or recreate_speed==True:
                        #print u"МЕНЯЕМ НАСТРОЙКИ СКОРОСТИ НА СЕВРЕРЕ ДОСТУПА", speed
                        #отправляем на сервер доступа новые настройки скорости, помечаем state=True
                        sended_speed = change_speed(dict, 
                                                    account_id,account_name,account_vpn_ip, \
                                                    account_ipn_ip,account_mac_address, \
                                                    access_type, \
                                                    nas_ipaddress,nas_type,nas_name,\
                                                    nas_login,nas_password,\
                                                    format_string=nas_ipn_speed, \
                                                    speed=speed[:6])
                        data_for_save=''
                        #print speed
    
                        cur.execute("UPDATE billservice_accountipnspeed SET speed=%s, state=%s WHERE account_id=%s RETURNING id;", (newspeed, sended_speed, account_id,))
                        id = cur.fetchone()
                        #print 'id=', id
                        if id==None:
                            cur.execute("INSERT INTO billservice_accountipnspeed(account_id, speed, state, datetime) VALUES( %s, %s, %s, %s);", (account_id, unicode(newspeed), sended_speed, now,))
    
                connection.commit()
                cur.close()
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)
                    traceback.print_exc(file=sys.stdout)

            
            #self.connection.close()
            gc.collect()
            time.sleep(120)


#periodical function memoize class
class pfMemoize(object):
    __slots__ = ('periodCache', 'settlementCache')
    def __init__(self):
        self.periodCache = {}
        self.settlementCache = {}
        
    def in_period_(self, time_start, length, repeat_after, date_):
        res = self.periodCache.get((time_start, length, repeat_after, date_))
        if res==None:
            res = in_period_info(time_start, length, repeat_after, date_)
            self.periodCache[(time_start, length, repeat_after, date_)] = res
        return res
    
    def settlement_period_(self, time_start, length, repeat_after, stream_date):
        #settlement_period_info(time_start, repeat_after='', repeat_after_seconds=0,  now=None,
        res = self.settlementCache.get((time_start, length, repeat_after, stream_date))
        if res==None:
            res = settlement_period_info(time_start, length, repeat_after, stream_date)
            self.settlementCache[(time_start, length, repeat_after, stream_date)] = res
        return res
  
'''
class Cacher(object):
    __slots__ = (execList, curATCache,curAT_acIdx,curAT_tfIdx, curSPCache, curTLimitCache, curSuspPerCache,
                 curNasCache,curTTSCache, curDefSpCache, curNewSpCache, curPerTarifCache, curPersSetpCache,
                 curTimeAccNCache, curTimePerNCache, curTimeAccSrvCache, )
    def __init__(self):
        pass
'''

class CacheServiceThread(Thread):
    '''Handles various non-simultaneous caches'''
    def __init__ (self):
        Thread.__init__(self)
    def check_period(self, rows):
        for row in rows:
            if in_period(row[0],row[1],row[2])==True:
                return True
        return False
    
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global tpnInPeriod
        global tp_asInPeriod
        global prepaysCache
        global TRTRNodesCache
        global fMem
        global curAT_lock
        global curAT_date
        if curAT_date == None:
            time.sleep(4)
        while True:             
            try:
                
                curAT_lock.acquire()
                dateAT = deepcopy(curAT_date)
                curAT_lock.release()
                cur = connection.cursor()
                cur.execute("""SELECT tpn.time_start, tpn.length, tpn.repeat_after, ttns.traffic_transmit_service_id
                            FROM billservice_timeperiodnode AS tpn
                            JOIN billservice_timeperiod_time_period_nodes AS timeperiod_timenodes ON timeperiod_timenodes.timeperiodnode_id=tpn.id
                            JOIN billservice_traffictransmitnodes_time_nodes AS ttntp ON ttntp.timeperiod_id=timeperiod_timenodes.timeperiod_id
                            JOIN billservice_traffictransmitnodes AS ttns ON ttns.id=ttntp.traffictransmitnodes_id;""")
                connection.commit()
                tpns = cur.fetchall()
                cur.close()
                tmpPerTP = defaultdict(lambda: False)
                #calculates whether traffic_transmit_service fits in any oh the periods
                for tpn in tpns:
                    tmpPerTP[tpn[3]] = tmpPerTP[tpn[3]] or fMem.in_period_(tpn[0], tpn[1], tpn[2], dateAT)[3]
                tpnInPeriod = tmpPerTP
                del tpns, tmpPerTP
                cur = connection.cursor()
                cur.execute("""SELECT tpn.time_start::timestamp without time zone as time_start, tpn.length as length, tpn.repeat_after as repeat_after, bst.id
                    FROM billservice_timeperiodnode as tpn
                    JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
                    JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
                    JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id""")
                tpnaps = cur.fetchall()
                connection.commit()
                cur.close()
                tmpPerAPTP = defaultdict(lambda: False)
                for tpnap in tpnaps:
                    tmpPerAPTP[tpnap[3]] = tmpPerAPTP[tpnap[3]] or fMem.in_period_(tpnap[0], tpnap[1], tpnap[2], dateAT)[3]
                tp_asInPeriod = tmpPerAPTP
                del tpnaps, tmpPerAPTP
                cur = connection.cursor()
                cur.execute("""SELECT prepais.id, prepais.size, prepais.account_tarif_id, prept_tc.trafficclass_id, prepaidtraffic.traffic_transmit_service_id, prepaidtraffic.in_direction, prepaidtraffic.out_direction
                             FROM billservice_accountprepaystrafic as prepais
                             JOIN billservice_prepaidtraffic as prepaidtraffic ON prepaidtraffic.id=prepais.prepaid_traffic_id
                             JOIN billservice_prepaidtraffic_traffic_class AS prept_tc ON prept_tc.prepaidtraffic_id=prepaidtraffic.id
                             WHERE prepais.size>0""")
                prepTp = cur.fetchall()
                cur.close()
                #prepaysTmp = defaultdict(list)
                prepaysTmp = {}
                if prepTp:                    
                    #keys: traffic_transmit_service_id, accounttarif.id, trafficclass
                    for prep in prepTp:
                        prepaysTmp[(prep[4],prep[2],prep[3])] = [prep[0], prep[1], prep[5], prep[6]]
                    prepaysCache = prepaysTmp
                del prepTp, prepaysTmp
                cur = connection.cursor()
                cur.execute("""SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start, tpn.length, tpn.repeat_after,
                               ARRAY(SELECT trafficclass_id FROM billservice_traffictransmitnodes_traffic_class WHERE traffictransmitnodes_id=ttsn.id) as classes, ttsn.traffic_transmit_service_id, ttsn.in_direction, ttsn.out_direction
                               FROM billservice_traffictransmitnodes as ttsn
                               JOIN billservice_timeperiodnode AS tpn on tpn.id IN 
                               (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id IN 
                               (SELECT timeperiod_id FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=ttsn.id));
                            """)
                trtrnodsTp = cur.fetchall()
                connection.commit()
                cur.close()
                trafnodesTmp = defaultdict(list)
                #keys: traffictransmitservice, trafficclass
                for trnode in trtrnodsTp:
                    for classnd in trnode[7]:
                        trafnodesTmp[(trnode[8],classnd)].append(trnode)
                TRTRNodesCache = trafnodesTmp
                del trtrnodsTp, trafnodesTmp
            except Exception, ex: 
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + repr(ex)
                else:
                    print self.getName() + ": exception: " + repr(ex)
            
            gc.collect()
            time.sleep(300)


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
        global caches, fMem, sendFlag, nfIncomingQueue
        global curATCache,curAT_acIdx,curAT_tfIdx
        global curAT_date, curAT_lock
        global curSPCache, curTLimitCache, curSuspPerCache
        global curNasCache, curNas_ipIdx, curTTSCache
        global curDefSpCache, curNewSpCache, curShedLogCache
        global curPerTarifCache, curPersSetpCache
        global curTimeAccNCache, curTimePerNCache, curTimeAccSrvCache
        global curOneTimeSrvCache, curAccParCache, curIPNSpCache, curOTSHistCache
        global tpnInPeriod, tp_asInPeriod, prepaysCache, TRTRNodesCache
        i_fMem = 0
        while True:
            a = time.clock()
            try:
                cur = connection.cursor()
                ptime =  time.time()
                ptime = ptime - (ptime % 20)
                tmpDate = datetime.datetime.fromtimestamp(ptime)
                cur.execute("""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, FALSE, ba.created, ba.disabled_by_limit, ba.balance_blocked, ba.nas_id, ba.vpn_ip_address, ba.ipn_ip_address,ba.ipn_mac_address, ba.assign_ipn_ip_from_dhcp, ba.ipn_status, ba.ipn_speed, ba.vpn_speed, ba.ipn_added, bt.ps_null_ballance_checkout, bt.deleted, bt.allow_express_pay, ba.status, ba.allow_vpn_null, ba.allow_vpn_block, ba.username, ba.password  
                    FROM billservice_account as ba
                    LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                    LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id;""", (tmpDate,))
                #list cache
                
                accts = cur.fetchall()
                allowedUsersChecker(allowedUsers, lambda: len(accts))
                #connection.commit()
                #cur.close()
                #index on account_id, directly links to tuples

                    #i += 1
                #cur = connection.cursor()
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
                cur.execute("""SELECT id, settlement_period_id, ps_null_ballance_checkout  
                                 FROM billservice_tariff  as tarif
                                 WHERE id in (SELECT tarif_id FROM billservice_periodicalservice) AND tarif.active=True""")
                perTarTp = cur.fetchall()
                cur.execute("""SELECT b.id, b.name, b.cost, b.cash_method, c.name, c.time_start,
                                     c.length, c.length_in, c.autostart, b.tarif_id
                                     FROM billservice_periodicalservice as b 
                                     JOIN billservice_settlementperiod as c ON c.id=b.settlement_period_id;""")
                psspTp = cur.fetchall()
                cur.execute("""
                        SELECT tan.time_period_id, tan.cost, tan.time_access_service_id
                        FROM billservice_timeaccessnode as tan
                        JOIN billservice_timeperiodnode as tp ON tan.time_period_id=tp.id;""")
                timeaccnTp = cur.fetchall()
                #connection.commit()
                cur.execute("""
                            SELECT tpn.id, tpn.name, tpn.time_start, tpn.length, tpn.repeat_after, tptpn.timeperiod_id 
                            FROM billservice_timeperiodnode as tpn
                            JOIN billservice_timeperiod_time_period_nodes as tptpn ON tpn.id=tptpn.timeperiodnode_id;""")
                timeperndTp = cur.fetchall()
                cur.execute("""SELECT id, tarif_id, "name", settlement_period_id, size, in_direction, out_direction, "mode" FROM billservice_trafficlimit;""")
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
                cur.execute("""SELECT tpn.time_start, tpn.length, tpn.repeat_after, ttns.traffic_transmit_service_id
                            FROM billservice_timeperiodnode AS tpn
                            JOIN billservice_timeperiod_time_period_nodes AS timeperiod_timenodes ON timeperiod_timenodes.timeperiodnode_id=tpn.id
                            JOIN billservice_traffictransmitnodes_time_nodes AS ttntp ON ttntp.timeperiod_id=timeperiod_timenodes.timeperiod_id
                            JOIN billservice_traffictransmitnodes AS ttns ON ttns.id=ttntp.traffictransmitnodes_id;""")
                tpnsTp = cur.fetchall()
                cur.execute("""SELECT tpn.time_start::timestamp without time zone as time_start, tpn.length as length, tpn.repeat_after as repeat_after, bst.id
                    FROM billservice_timeperiodnode as tpn
                    JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
                    JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
                    JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id""")
                tpnapsTp = cur.fetchall()
                cur.execute("""SELECT prepais.id, prepais.size, prepais.account_tarif_id, prept_tc.trafficclass_id, prepaidtraffic.traffic_transmit_service_id, prepaidtraffic.in_direction, prepaidtraffic.out_direction
                             FROM billservice_accountprepaystrafic as prepais
                             JOIN billservice_prepaidtraffic as prepaidtraffic ON prepaidtraffic.id=prepais.prepaid_traffic_id
                             JOIN billservice_prepaidtraffic_traffic_class AS prept_tc ON prept_tc.prepaidtraffic_id=prepaidtraffic.id
                             WHERE prepais.size>0 AND (ARRAY[prepais.account_tarif_id] && get_cur_acct(%s));""", (tmpDate,))
                prepTp = cur.fetchall()
                cur.execute("""SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start, tpn.length, tpn.repeat_after,
                               ARRAY(SELECT trafficclass_id FROM billservice_traffictransmitnodes_traffic_class WHERE traffictransmitnodes_id=ttsn.id) as classes, ttsn.traffic_transmit_service_id, ttsn.in_direction, ttsn.out_direction
                               FROM billservice_traffictransmitnodes as ttsn
                               JOIN billservice_timeperiodnode AS tpn on tpn.id IN 
                               (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id IN 
                               (SELECT timeperiod_id FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=ttsn.id));
                            """)
                trtrnodsTp = cur.fetchall()
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
                tmpPerTP = defaultdict(lambda: False)
                #calculates whether traffic_transmit_service fits in any oh the periods
                for tpn in tpnsTp:
                    tmpPerTP[tpn[3]] = tmpPerTP[tpn[3]] or fMem.in_period_(tpn[0], tpn[1], tpn[2], tmpDate)[3]
                    
                tmpPerAPTP = defaultdict(lambda: False)
                for tpnap in tpnapsTp:
                    tmpPerAPTP[tpnap[3]] = tmpPerAPTP[tpnap[3]] or fMem.in_period_(tpnap[0], tpnap[1], tpnap[2], tmpDate)[3]
                    
                prepaysTmp = {}
                if prepTp:                    
                    #keys: traffic_transmit_service_id, accounttarif.id, trafficclass
                    for prep in prepTp:
                        prepaysTmp[(prep[4],prep[2],prep[3])] = [prep[0], prep[1], prep[5], prep[6]]
                    prepaysCache = prepaysTmp
                    
                trafnodesTmp = defaultdict(list)
                #keys: traffictransmitservice, trafficclass
                for trnode in trtrnodsTp:
                    for classnd in trnode[7]:
                        trafnodesTmp[(trnode[8],classnd)].append(trnode)
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
                tpnInPeriod = tmpPerTP
                tp_asInPeriod = tmpPerAPTP
                prepaysCache = prepaysTmp
                TRTRNodesCache = trafnodesTmp
                curAT_date  = tmpDate
                curAT_lock.release()
                #del accts, tmpacIdx, tmptfIdx, tmpspC, tmpttsC, tmpnasC, tmpdsC, tmpnsC, tmpDate
                #del ttssTp, spsTp, nasTp, defspTmp, nspTmp
                i_fMem += 1
                if i_fMem == 3:
                    i_fMem = 0
                    fMem.settlementCache = {}
                    fMem.periodCache = {}
                    
                if len(nfIncomingQueue) > 1000:
                    if not sendFlag or sendFlag!='SLP!':
                        sendFlag = 'SLP!'
                        #print "sf set!"
                        #print "incoming queue len: ", len(nfIncomingQueue)
                else:
                    if sendFlag and sendFlag=='SLP!':
                        sendFlag = ''
                        #print "sf unset!"
                        #print "incoming queue len: ", len(nfIncomingQueue)
                        
                #print "ast time :", time.clock() - a
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + repr(ex)
                else:
                    print self.getName() + ": exception: " + repr(ex)
            
            gc.collect()
            time.sleep(180)
            

class NfAsyncUDPServer(asyncore.dispatcher):
    ac_out_buffer_size = 8096*10
    ac_in_buffer_size = 8096*10
    
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
    #TODO: add login of sending '0' when queue is too long
    def handle_read_event (self):
        try:
            data, addr = self.socket.recvfrom(8192)
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
        print 'uncaptured python exception, closing channel %s' % `self`
        self.close()
    
    def handle_close(self):
        self.close()
        
class hostCheckingValidator(Pyro.protocol.DefaultConnValidator):
    def __init__(self):
        Pyro.protocol.DefaultConnValidator.__init__(self)
        '''self.connection = pool.connection()
    #print dir(self.connection)
    self.connection._con._con.set_client_encoding('UTF8')
    self.cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)'''



    def acceptIdentification(self, tcpserver, conn, hash, challenge):
        try:
            for val in tcpserver.implementations.itervalues():
                if val[1] == 'rpc':
                    serv = val[0]
                    break

            user, mdpass = hash.split(':', 1)
            try:
                obj = serv.get("SELECT * FROM billservice_systemuser WHERE username='%s';" % user)
                val[0].connection.commit()
            except Exception, ex:
                print "acceptIdentification error: ", ex
                conn.utoken = ''
                return (0,Pyro.constants.DENIED_SERVERTOOBUSY)
            #print obj.id
            #print obj.host
            hostOk = self.checkIP(conn.addr[0], str(obj.host))

            if hostOk and (obj.password == mdpass):
                #print "accepted---------------------------------"
                tmd5 = hashlib.md5(str(conn.addr[0]))
                tmd5.update(str(conn.addr[1]))
                tmd5.update(tcpserver.hostname)
                conn.utoken = tmd5.digest()
                try:
                    conn.db_connection = pool.connection()
                    conn.db_connection._con._con.set_client_encoding('UTF8')
                    conn.cur = conn.db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
                except Exception, ex:
                    print "acceptIdentification create connection error: ", ex
                    conn.utoken = ''
                    return (0,Pyro.constants.DENIED_SERVERTOOBUSY)
                #Pyro.protocol.DefaultConnValidator.acceptIdentification(self, tcpserver, conn, hash, challenge)
                return(1,0)
            else:
                #print "DENIED-----------------"
                conn.utoken = ''
                return (0,Pyro.constants.DENIED_SECURITY)
        except Exception, ex:
            conn.utoken = ''
            return (0,Pyro.constants.DENIED_SECURITY)

    def checkIP(self, ipstr, hostsstr):
        #print "checkIP----"
        #user IP
        userIP = IPy.IP(ipstr)
        #allowed hosts
        hosts = hostsstr.split(', ')
        hostOk = False
        for host in hosts:
            #print host
            iprange = host.split('-')
            if len(iprange) == 1:
                if iprange[0].find('/') != -1:
                    hostOk = userIP in IPy.IP(iprange[0])
                else:
                    hostOk = hostOk or (userIP == IPy.IP(iprange[0]))
            else:
                hostOk = hostOk or ((userIP >= IPy.IP(iprange[0])) and (userIP <= IPy.IP(iprange[1])))
            if hostOk:
                break
        return hostOk

    def createAuthToken(self, authid, challenge, peeraddr, URI, daemon):
        #print "createAuthToken_serv"
        # authid is what mungeIdent returned, a tuple (login, hash-of-password)
        # we return a secure auth token based on the server challenge string.
        return authid

    def mungeIdent(self, ident):
        #print "mungeIdent_serv"
        # ident is tuple (login, password), the client sets this.
        # we don't like to store plaintext passwords so store the md5 hash instead.
        return ident
    

def authentconn(func):
    def relogfunc(*args, **kwargs):
        try:
            if args[0].getLocalStorage().caller:
                caller = args[0].getLocalStorage().caller
                if args[0].getLocalStorage().caller.utoken:                
                    '''if func.__name__ == "flush":
                        caller.cur.close()
                        caller.db_connection.close()
                        caller.db_connection = pool.connection()
                        caller.db_connection._con._con.set_client_encoding('UTF8')
                        caller.cur = caller.db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)'''
                    #print args
                    #print kwargs
                    
                    kwargs['connection'] = caller.db_connection
                    kwargs['cur'] = caller.cur
                    res =  func(*args, **kwargs)
                    #if func.__name__ == "commit":
                    #    caller.cur.close()
                    #    caller.db_connection.close()
                    #    caller.db_connection = pool.connection()
                    #    caller.db_connection._con._con.set_client_encoding('UTF8')
                    #    caller.cur = caller.db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    return res
                else:
                    return None
            else:
                return func(*args, **kwargs)
        except Exception, ex:
            if isinstance(ex, psycopg2.OperationalError):
                print args[0].getName() + ": (RPC Server) database connection is down: " + str(ex)
            else:
                #print args[0].getName() + ": exception: " + str(ex)
                raise ex

    return relogfunc

class RPCServer(Thread, Pyro.core.ObjBase):

    def __init__ (self):
        Thread.__init__(self)
        Pyro.core.ObjBase.__init__(self)
        self.connection = pool.connection()
        self.connection._con._con.set_isolation_level(1)
        self.connection._con._con.set_client_encoding('UTF8')
        self.cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  
        self.ticket = ''
        #self._cddrawer = cdDrawer()



    def run(self):
        #from Pyro.config import PYRO_COMPRESSION
        #print "compr",Pyro.config.PYRO_COMPRESSION
        Pyro.config.PYRO_COMPRESSION=True
        
        Pyro.config.PYRO_DETAILED_TRACEBACK = 1
        Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

        Pyro.core.initServer()
        daemon=Pyro.core.Daemon()
        #daemon.adapter.setIdentification = setIdentification
        daemon.setNewConnectionValidator(hostCheckingValidator())
        daemon.connect(self,"rpc")
        daemon.requestLoop()


    @authentconn
    def testCredentials(self, host, login, password, cur=None, connection=None):
        try:
            #print host, login, password
            a=SSHClient(host, 22,login, password)
            a.close()
        except Exception, e:
            print e
            return False
        return True

    @authentconn
    def configureNAS(self, id, pptp_enable,auth_types_pap, auth_types_chap, auth_types_mschap2, pptp_ip, radius_enable, radius_server_ip,interim_update, configure_smtp, configure_gateway,protect_malicious_trafic, cur=None, connection=None):
        cur.execute("SELECT ipaddress, login, password, secret FROM nas_nas WHERE id=%s" % id)
        row = cur.fetchone()
        connection.commit()
        #print row
        confstring = ''
        #print 1
        if pptp_enable:
            auth_types=''
            #print 2
            if auth_types_pap==auth_types_chap==auth_types_mschap2:
                #print 3
                auth_types="pap, chap, mschap2"
            else:    
                if auth_types_pap==True:
                    auth_types='pap'
                    
                if auth_types_chap==True and auth_types_pap==True:
                    auth_types+=','
                    
                if auth_types_chap==True:
                    auth_types+='chap'
                    
                if auth_types_mschap2==True and (auth_types_chap==True or auth_types_pap==True):
                    auth_types+=','
                    
                if auth_types_mschap2==True:
                    auth_types+='mschap2'
                
            confstring = unicode(rules['allow_pptp'] % (pptp_ip, auth_types))
            #print 4
            #print rules['allow_pptp'] % (pptp_ip, auth_types)
            
        if radius_enable==True:
            #print rules['allow_radius'],{'interim_update': interim_update, 'secret':row['secret'], 'server_ip':radius_server_ip}
            #print rules['allow_radius'] % {'interim_update': interim_update, 'secret':row['secret'], 'server_ip':radius_server_ip}
            data = rules['allow_radius'] % (interim_update, row['secret'], radius_server_ip)
            #print data
            confstring+=unicode(data)
            #print 5
            
        if configure_smtp==True:
            confstring+=rules['smtp_protect']
            #print 6
            
        if configure_gateway==True:
            confstring+=rules['gateway']
            #print 7
        
        if protect_malicious_trafic==True:
        
            confstring+=rules['malicious_trafic']
            #print 8
        
        #print confstring
        try:
            a=SSHClient(row["ipaddress"], 22,row["login"], row["password"])
            #print configuration
            a.send_command(confstring)
            a.close()
        except Exception, e:
            print e
            return False
        return True


    @authentconn
    def accountActions(self, account_id, action, cur=None, connection=None):

        if type(account_id) is not list:
            account_id=[account_id]
            
        for account in account_id:
            cur.execute("""SELECT account.id as account_id, account.username as username, account.password as password, account.ipn_ip_address as ipn_ip_address,
                             account.vpn_ip_address as vpn_ip_address, account.ipn_mac_address as  ipn_mac_address,
                             nas.login as nas_login, nas.password as nas_password, nas.ipaddress as nas_ipaddress,
                             nas.user_add_action as user_add_action, nas.user_delete_action as user_delete_action, 
                             nas.user_enable_action as user_enable_action, nas.user_disable_action as user_disable_action, ap.access_type as access_type 
                             FROM billservice_account as account
                             JOIN nas_nas as nas ON nas.id = account.nas_id
                             JOIN billservice_tariff as tarif on tarif.id = get_tarif(account.id)
                             JOIN billservice_accessparameters as ap ON ap.id=tarif.access_parameters_id
                             WHERE account.id=%s
                             """, (account,))
    
            row = cur.fetchone()
            connection.commit()
            #print "actions", row
            #print action
            if row==None:
                return False
    
            if row['ipn_ip_address']=="0.0.0.0":
                return False
    
            if action=='disable':
                command = row['user_disable_action']
            elif action=='enable':
                command = row['user_enable_action']
            elif action=='create':
                command = row['user_add_action']
            elif action =='delete':
                command = row['user_delete_action']
            #print command
    
            sended = cred(account_id=row['account_id'], account_name=row['username'], account_password=row['password'], access_type = row['access_type'],
                          account_vpn_ip=row['vpn_ip_address'], account_ipn_ip=row['ipn_ip_address'], 
                          account_mac_address=row['ipn_mac_address'], nas_ip=row['nas_ipaddress'], nas_login=row['nas_login'], 
                          nas_password=row['nas_password'], format_string=command)
 
            if action=='create' and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (True, True, row['account_id']))
                
            elif action=='create' and sended==False:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))
            
            if action =='delete'  and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))
            elif action =='delete'  and sended==False:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))

            if action=='disable' and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s", (False, row['account_id'],))
                
            if action=='enable' and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s", (True, row['account_id'],))
        
        connection.commit()

#            if sended==False:
#                cur.execute("UPDATE billservice_account SET ipn_status=%s", (ipn_status,))
        del account_id
        del row
        del account
        return sended

        
    @authentconn
    def get_object(self, name, cur=None, connection=None):
        try:
            model = models.__getattribute__(name)()
        except:
            return None


        return model

    @authentconn
    def transaction_delete(self, ids, cur=None, connection=None):
        for i in ids:
            #print "delete %s transaction" % i
            delete_transaction(cur, int(i))
        connection.commit()

        return
    @authentconn
    def flush(self, cur=None, connection=None):
        pass
    
    @authentconn
    def get(self, sql, cur=None, connection=None):
        #print sql
        if not cur:
            cur = self.cur
        cur.execute(sql)
        #connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return None
        return Object(r[0])

    @authentconn
    def get_list(self, sql, cur=None, connection=None):
        #print sql
        listconnection = pool.connection()
        listconnection._con._con.set_client_encoding('UTF8')
        listcur = listconnection.cursor()
        listcur.execute(sql)
        retres = listcur.fetchall()
        listconnection.commit()
        listcur.close()
        listconnection.close()
        return retres

    @authentconn
    def pay(self, account, sum, document, cur=None, connection=None):
        
        o = Object()
        o.account_id = account
        o.type_id = "MANUAL_TRANSACTION"
        o.approved = True
        o.description = ""
        o.summ = sum * (-1)
        o.bill = document
        o.created = datetime.datetime.now()
        try:
            sql = o.save("billservice_transaction")
            #sql = "INSERT INTO billservice_transaction(account_id, type_id, approved, description, bill, summ, created) VALUES(%s,'%s', True, '', '%s',%s, '%s') RETURNING id;" % (account, "MANUAL_TRANSACTION", document, sum*(-1), datetime.datetime.now())
            cur.execute(sql)
            id=cur.fetchall()[0]
            connection.commit()
            return Object(id)
        except Exception, e:
            print e
            return False
    
    @authentconn
    def createAccountTarif(self, account, tarif, datetime, cur=None, connection=None):
        
        o = Object()
        o.account_id = account
        o.tarif_id=tarif
        o.datetime = datetime
        try:
            #sql = "UPDATE billservice_account SET ballance = ballance - %f WHERE id = %d;" % (sum*(-1), account)
            sql = o.save("billservice_accounttarif")
            
            cur.execute(sql)
            connection.commit()
            return True
        except Exception, e:
            print e
            return False

    @authentconn
    def dbaction(self, fname, *args, **kwargs):
        return dbRoutine.execRoutine(fname, *args, **kwargs)
    
    @authentconn
    def delete(self, model, table, cur=None, connection=None):
        sql = model.delete(table)
        cur.execute(sql)
        #connection.commit()
        del sql
        return

    @authentconn
    def iddelete(self, id, table, cur=None, connection=None):

        cur.execute("DELETE FROM %s where id=%d" % (table, id))
        del table
        del id
        #connection.commit()
        return

    @authentconn
    def command(self, sql, cur=None, connection=None):

        cur.execute(sql)
        #connection.commit()
        del sql
        return         

    @authentconn
    def commit(self, cur=None, connection=None):
        connection.commit()

    @authentconn
    def makeChart(self, *args, **kwargs):
        kwargs['cur']=None
        kwargs['connection']=None
        listconnection = pool.connection()
        listconnection._con._con.set_client_encoding('UTF8')
        listcur = listconnection.cursor()
        bpplotAdapter.rCursor = listcur
        cddrawer = cdDrawer()
        imgs = cddrawer.cddraw(*args, **kwargs)
        listconnection.commit()
        listcur.close()
        listconnection.close()
        gc.collect()
        return imgs

    @authentconn
    def rollback(self, cur=None, connection=None):
        connection.rollback()

    @authentconn
    def sql(self, sql, return_response=True, pickler=False, cur=None, connection=None):
        #print self.ticket
        cur.execute(sql)
        #connection.commit()

        #print dir(connection)
        result=[]
        a=time.clock()
        if return_response:
            result = map(Object, cur.fetchall())
        #print "Query length=", time.clock()-a
        if pickler:
            output = open('data.pkl', 'wb')
            b=time.clock()-a

            pickle.dump(result, output)
            output.close()
            #print "Pickle length=", time.clock()-a
        return result

    @authentconn
    def get_models(self, table='', fields = [], where={}, cur=None, connection=None):
        cur.execute("SELECT %s FROM %s WHERE %s ORDER BY id ASC;" % (",".join(fields) or "*", table, " AND ".join("%s=%s" % (wh, where[wh]) for wh in where) or 'id>0'))
        
        a=time.clock()
        result = map(Object, cur.fetchall())
        return result


    @authentconn
    def get_model(self, id, table='', fields = [], cur=None, connection=None):
        #print "SELECT %s from %s WHERE id=%s ORDER BY id ASC;" % (",".join(fields) or "*", table, id)
        cur.execute("SELECT %s from %s WHERE id=%s ORDER BY id ASC;" % (",".join(fields) or "*", table, id))
        result=[]
        result = map(Object, cur.fetchall())
        return result[0]
    
    @authentconn    
    def get_notsold_cards(self, cards, cur=None, connection=None):
        if len(cards)>0:
            crd = "(" + ",".join(cards) + ")"
        else:
            crd = "(0)" 
        
        cur.execute("SELECT * FROM billservice_card WHERE id IN %s AND sold is Null;" % crd)
        result = map(Object, cur.fetchall())
        return result
    
    @authentconn
    def get_operator(self, cur=None, connection=None):
        cur.execute("SELECT * FROM billservice_operator LIMIT 1;")
        result = Object(cur.fetchone())
        return result
    
    @authentconn
    def get_operator_info(self, cur=None, connection=None):
        cur.execute("SELECT operator.*, bankdata.bank as bank, bankdata.bankcode as bankcode, bankdata.rs as rs FROM billservice_operator as operator JOIN billservice_bankdata as bankdata ON bankdata.id=operator.bank_id LIMIT 1")
        result = Object(cur.fetchone())
        return result

    @authentconn
    def get_dealer_info(self, id, cur=None, connection=None):
        cur.execute("SELECT dealer.*, bankdata.bank as bank, bankdata.bankcode as bankcode, bankdata.rs as rs FROM billservice_dealer as dealer JOIN billservice_bankdata as bankdata ON bankdata.id=dealer.bank_id WHERE dealer.id=%s", (id, ))
        result = Object(cur.fetchone())
        return result


    @authentconn      
    def get_bank_for_operator(self, operator, cur=None, connection=None):
        cur.execute("SELECT * FROM billservice_bankdata WHERE id=(SELECT bank_id FROM billservice_operator WHERE id=%s)", (operator,))
        result = map(Object, cur.fetchall())
        return result[0]
    
    @authentconn      
    def get_cards_nominal(self, cur=None, connection=None):
        cur.execute("SELECT nominal FROM billservice_card GROUP BY nominal")
        result = map(Object, cur.fetchall())
        return result
    
    @authentconn 
    def get_accounts_for_tarif(self, tarif_id, cur=None, connection=None):
        cur.execute("""SELECT acc.*, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name 
        FROM billservice_account AS acc 
        WHERE %s=get_tarif(acc.id) ORDER BY acc.username ASC;""", (tarif_id,))
        result = map(Object, cur.fetchall())
        return result

    @authentconn 
    def get_tariffs(self, cur=None, connection=None):
        cur.execute("SELECT id, name, active, get_tariff_type(id) AS ttype FROM billservice_tariff ORDER BY ttype, name;")
        result = map(Object, cur.fetchall())
        return result
    
    
    @authentconn  
    def delete_card(self, id, cur=None, connection=None):
        cur.execute("DELETE FROM billservice_card WHERE sold is Null and id=%s", (id,))
        return
    
    @authentconn  
    def get_next_cardseries(self, cur=None, connection=None):
        cur.execute("SELECT MAX(series) as series FROM billservice_card")
        result = cur.fetchone()['series']
        if result==None:
            result=0
        else:
            result+=1
        #print result
        return result
    
    @authentconn
    def sql_as_dict(self, sql, return_response=True, cur=None, connection=None):
        #print sql
        cur.execute(sql)
        result=[]
        a=time.clock()
        if return_response:

            result =cur.fetchall()
        #print "Query length=", time.clock()-a
        return result


    @authentconn
    def transaction(self, sql, cur=None, connection=None):
        cur.execute(sql)
        id = cur.fetchone()['id']
        return id

    @authentconn
    def save(self, model, table, cur=None, connection=None):
        sql = model.save(table)
        #print sql
        cur.execute(sql)
        id = cur.fetchone()['id']
        return id

    @authentconn
    def connection_request(self, username, password, cur=None, connection=None):
        try:
            obj = self.get("SELECT * FROM billservice_systemuser WHERE username=%s",(username,))
            self.commit()
        except Exception, e:
            print e
            return False
        #print "connection_____request"
        #print self.getProxy()
        if obj is not None and obj.password==password:
            self.create("UPDATE billservice_systemuser SET last_login=%s WHERE id=%s;" , (datetime.datetime.now(), obj.id,))
            self.commit()
            #Pyro.constants.

            return True
        else:
            return False

    @authentconn
    def test(self, cur=None, connection=None):
        pass

    @authentconn
    def get_allowed_users(self, cur=None, connection=None):
        return allowedUsers()
    
    @authentconn
    def pod(self, session, cur=None, connection=None):
        print "Start POD"
        cur.execute("""
                    SELECT nas.ipaddress as nas_ip, nas.type as nas_type, nas.name as nas_name, nas.secret as nas_secret, nas.login as nas_login, nas.password as nas_password,
                    nas.reset_action as reset_action, account.id as account_id, account.username as account_name, account.vpn_ip_address as vpn_ip_address,
                    account.ipn_ip_address as ipn_ip_address, account.ipn_mac_address as ipn_mac_address, session.framed_protocol as framed_protocol
                    FROM radius_activesession as session
                    JOIN billservice_account as account ON account.id=session.account_id
                    JOIN nas_nas as nas ON nas.id=account.nas_id
                    WHERE  session.sessionid='%s'
                    """ % session)

        row = cur.fetchone()
        connection.commit()
        return PoD(dict=dict,
            account_id=row['account_id'], 
            account_name=str(row['account_name']), 
            account_vpn_ip=row['vpn_ip_address'], 
            account_ipn_ip=row['ipn_ip_address'], 
            account_mac_address=row['ipn_mac_address'], 
            access_type=str(row['framed_protocol']), 
            nas_ip=row['nas_ip'], 
            nas_type=row['nas_type'], 
            nas_name=row['nas_name'], 
            nas_secret=row['nas_secret'], 
            nas_login=row['nas_login'], 
            nas_password=row['nas_password'], 
            session_id=str(session), 
            format_string=str(row['reset_action'])
        )






def stop_async():
    del NfAsyncUDPServer
    
    
def main():
    global curAT_date
    
    dict=dictionary.Dictionary("dicts/dictionary", "dicts/dictionary.microsoft","dicts/dictionary.mikrotik","dicts/dictionary.rfc3576")
    try:
        signal.signal(signal.SIGUSR1, stop_async)
    except:
        pass

    threads=[]

    #threads.append(CacheServiceThread())
    threads.append(RPCServer())
    threads.append(check_vpn_access())
    threads.append(periodical_service_bill())
    threads.append(TimeAccessBill())

    threads.append(NetFlowRoutine())
    threads.append(NetFlowRoutine())
    threads.append(NetFlowRoutine())
    threads.append(limit_checker())
    threads.append(ipn_service())
    threads.append(settlement_period_service_dog())
    
    cacheThr = AccountServiceThread()
    cacheThr.start()
    
    while curAT_date == None:
        time.sleep(0.2)
        
    #i= range(len(threads))
    for th in threads:	
        th.start()
        time.sleep(0.5)
        
    NfAsyncUDPServer(coreAddr)            
    while 1: 
        asyncore.poll(0.010)


#===============================================================================
import socket
if socket.gethostname() not in ['dmitry-desktop','dolphinik','sserv.net','sasha', 'iserver','kenny','billing', 'medusa', 'Billing.NemirovOnline']:
    import sys
    print "License key error. Exit from application."
    sys.exit(1)
    
if __name__ == "__main__":
    if "-D" not in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
    config.read("ebs_config.ini")
    if config.get("core_nf", "usock") == '0':
        coreHost = config.get("core_nf_inet", "host")
        corePort = int(config.get("core_nf_inet", "port"))
        coreAddr = (coreHost, corePort)
    elif config.get("core_nf", "usock") == '1':
        coreHost = config.get("core_nf_unix", "host")
        corePort = 0
        coreAddr = (coreHost,)
    else:
        raise Exception("Config '[core_nf] -> usock' value is wrong, must be 0 or 1")
    
    
    store_na_tarif   = False
    store_na_account = False
    if (config.get("core", "store_na_tarif")  =='True') or (config.get("core", "store_na_tarif")  =='1'):
        store_na_tarif   = True
    if (config.get("core", "store_na_account")=='True') or (config.get("core", "store_na_account")=='1'):
        store_na_account = True
        
    pool = PooledDB(
        mincached=13,
        maxcached=30,
        blocking=True,
        #maxusage=20, 
        creator=psycopg2,
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"),
                                                               config.get("db", "username"),
                                                               config.get("db", "host"),
                                                               config.get("db", "password"))
       )

    #--------------------------------------------------------
    #quequ for Incoming packet lists
    nfIncomingQueue = deque()
    #lock for nfIncomingQueue operations
    nfQueueLock = Lock()

    #last cache renewal date
    curAT_date  = None
    #lock for cache operations
    curAT_lock  = Lock()
    
    sendFlag = ''
    
    #function that returns number of allowed users
    #create allowedUsers
    allowedUsers = setAllowedUsers(pool.connection(), "license.lic")
    
    allowedUsers()
    fMem = pfMemoize()

    
    
    
    main()

