#-*-coding=utf-8-*-

from daemonize import daemonize
from encodings import idna, ascii
import time, datetime, os, sys, gc, traceback

from utilites import parse_custom_speed, cred, create_speed_string, change_speed, PoD, get_active_sessions, rosClient, SSHClient,settlement_period_info, in_period, in_period_info,create_speed_string
import dictionary
from threading import Thread
import threading
try:
    import mx.DateTime
except:
    print 'cannot import mx'
from db import Object as Object
from db import delete_transaction, get_default_speed_parameters, get_speed_parameters,transaction, ps_history, get_last_checkout, time_periods_by_tarif_id, set_account_deleted
from db import dbRoutine
import Pyro.core
import Pyro.protocol
import Pyro.constants
import hmac
import hashlib
import zlib
from hashlib import md5
import psycopg2
import psycopg2.extras
from marshal import dumps, loads
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import psycopg2
import IPy
from IPy import intToIp
import asyncore
from collections import deque
from collections import defaultdict
from threading import Lock
from threading import Semaphore
from copy import deepcopy
from copy import copy
#import SocketServer
#from SocketServer import ThreadingTCPServer
#from SocketServer import StreamRequestHandler

from chartprovider.bpplotadapter import bpplotAdapter
from chartprovider.bpcdplot import cdDrawer

import ConfigParser

config = ConfigParser.ConfigParser()

from DBUtils.PooledDB import PooledDB

rules={
       
        'allow_pptp':u"""/ppp profile add name=internet only-one=yes use-compression=no use-encryption=yes use-vj-compression=yes local-address=%s;/interface pptp-server server set enabled=yes authentication=%s default-profile=internet;
        """,
        'allow_radius':u"""
        /ppp aaa set accounting=yes use-radius=yes interim-update=%s; /radius add address=%s disabled=no secret=%s timeout=3000;""",
        'smtp_protect' : u"""
        /ip firewall filter

add chain=forward protocol=tcp dst-port=25 src-address-list=spammer
action=drop comment="BLOCK SPAMMERS OR INFECTED USERS"

add chain=forward protocol=tcp dst-port=25 connection-limit=30,32 limit=50,5 action=add-src-to-address-list
address-list=spammer address-list-timeout=30m comment="Detect and add-list SMTP virus or spammers"

/system script
add name="spammers" source=":log error \"----------Users detected like \
    SPAMMERS -------------\";
\n:foreach i in \[/ip firewall address-list find \
    list=spammer\] do={:set usser \[/ip firewall address-list get \$i \
    address\];
\n:foreach j in=\[/ip hotspot active find address=\$usser\] \
    do={:set ip \[/ip hotspot active get \$j user\];
\n:log error \$ip;
\n:log \
    error \$usser} };" policy=ftp,read,write,policy,test,winbox  """,
    
    "malicious_trafic":"""
    
    /ip firewall filter
add chain=forward connection-state=established comment="allow established connections"  
add chain=forward connection-state=related comment="allow related connections"
add chain=forward connection-state=invalid action=drop comment="drop invalid connections"  

add chain=virus protocol=tcp dst-port=135-139 action=drop comment="Drop Blaster Worm" 
add chain=virus protocol=udp dst-port=135-139 action=drop comment="Drop Messenger Worm"    
add chain=virus protocol=tcp dst-port=445 action=drop comment="Drop Blaster Worm" 
add chain=virus protocol=udp dst-port=445 action=drop comment="Drop Blaster Worm" 
add chain=virus protocol=tcp dst-port=593 action=drop comment="________" 
add chain=virus protocol=tcp dst-port=1024-1030 action=drop comment="________" 
add chain=virus protocol=tcp dst-port=1080 action=drop comment="Drop MyDoom" 
add chain=virus protocol=tcp dst-port=1214 action=drop comment="________" 
add chain=virus protocol=tcp dst-port=1363 action=drop comment="ndm requester" 
add chain=virus protocol=tcp dst-port=1364 action=drop comment="ndm server" 
add chain=virus protocol=tcp dst-port=1368 action=drop comment="screen cast" 
add chain=virus protocol=tcp dst-port=1373 action=drop comment="hromgrafx" 
add chain=virus protocol=tcp dst-port=1377 action=drop comment="cichlid" 
add chain=virus protocol=tcp dst-port=1433-1434 action=drop comment="Worm" 
add chain=virus protocol=tcp dst-port=2745 action=drop comment="Bagle Virus" 
add chain=virus protocol=tcp dst-port=2283 action=drop comment="Drop Dumaru.Y" 
add chain=virus protocol=tcp dst-port=2535 action=drop comment="Drop Beagle" 
add chain=virus protocol=tcp dst-port=2745 action=drop comment="Drop Beagle.C-K" 
add chain=virus protocol=tcp dst-port=3127-3128 action=drop comment="Drop MyDoom" 
add chain=virus protocol=tcp dst-port=3410 action=drop comment="Drop Backdoor OptixPro"
add chain=virus protocol=tcp dst-port=4444 action=drop comment="Worm" 
add chain=virus protocol=udp dst-port=4444 action=drop comment="Worm" 
add chain=virus protocol=tcp dst-port=5554 action=drop comment="Drop Sasser" 
add chain=virus protocol=tcp dst-port=8866 action=drop comment="Drop Beagle.B" 
add chain=virus protocol=tcp dst-port=9898 action=drop comment="Drop Dabber.A-B" 
add chain=virus protocol=tcp dst-port=10080 action=drop comment="Drop MyDoom.B" 
add chain=virus protocol=tcp dst-port=12345 action=drop comment="Drop NetBus" 
add chain=virus protocol=tcp dst-port=17300 action=drop comment="Drop Kuang2" 
add chain=virus protocol=tcp dst-port=27374 action=drop comment="Drop SubSeven" 
add chain=virus protocol=tcp dst-port=65506 action=drop comment="Drop PhatBot, Agobot, Gaobot"
add chain=forward action=jump jump-target=virus comment="jump to the virus chain"
add chain=forward action=accept protocol=tcp dst-port=80 comment="Allow HTTP" 
add chain=forward action=accept protocol=tcp dst-port=25 comment="Allow SMTP" 
add chain=forward protocol=tcp comment="allow TCP"
add chain=forward protocol=icmp comment="allow ping"
add chain=forward protocol=udp comment="allow udp"
add chain=forward action=drop comment="drop everything else"

 """,
    'gateway':u"""
    /ip firewall nat add chain=srcnat src-address=0.0.0.0/0 action=masquerade
    """
        
       }

#redirect_std("core", redirect=config.get("stdout", "redirect"))
#from mdi.helpers import Object as Object

   
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

    def create_speed(self, tarif_id, nas_type):
        defaults = get_default_speed_parameters(self.cur, tarif_id)
        speeds = get_speed_parameters(self.cur, tarif_id)
        for speed in speeds:
            if in_period(speed['time_start'],speed['length'],speed['repeat_after'])==True:
                defaults = comparator(defaults, speed)
                return defaults
        return defaults

    def remove_sessions(self):

        self.cur.execute("""
            SELECT id, name, "type", ipaddress, secret, "login", "password", reset_action FROM nas_nas;
            """)
        nasses=self.cur.fetchall()


        for nas in nasses:
            sessions = get_active_sessions(nas)
            #print sessions
            for session in sessions:
                self.cur.execute("""
                                 SELECT account.id, account.vpn_ip_address, account.ipn_ip_address, account.ipn_mac_address, radius.sessionid as  sessionid
                                 FROM radius_activesession as radius 
                                 JOIN billservice_account as account ON radius.account_id=account.id
                                 WHERE account.username=%s
                                 """ , (session['name'],))
                account = self.cur.fetchone()
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

            self.cur.execute("""
                             UPDATE radius_activesession
                             SET session_time=extract(epoch FROM date_end-date_start), date_end=interrim_update, session_status='ACK'
                             WHERE date_end is Null and nas_id=%s;""", (nas['ipaddress'],))
            self.connection.commit()


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
        self.connection = pool.connection()
        self.connection._con._con.set_client_encoding('UTF8')
        while True:            
            try:
                self.cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                #Закрываем подвисшие сессии
                self.cur.execute("UPDATE radius_activesession SET session_time=extract(epoch FROM date_end-date_start), date_end=interrim_update, session_status='NACK' WHERE ((now()-interrim_update>=interval '00:06:00') or (now()-date_start>=interval '00:03:00' and interrim_update IS Null)) AND date_end IS Null;")
                self.connection.commit()
                #TODO: make nas_nas.ipadress UNIQUE and INDEXed
                '''self.cur.execute("""
                                 SELECT rs.id as id, 
                                 rs.account_id as account_id, 
                                 rs.sessionid as session,  
                                 rs.speed_string as speed_string, 
                                 lower(rs.framed_protocol) as access_type,
                                 nas.name as nas_name, 
                                 nas.ipaddress as nas_ip, 
                                 nas.secret as nas_secret, 
                                 nas.login as nas_login, 
                                 nas.password as nas_password, 
                                 nas.type as nas_type,
                                 account.username as username, 
                                 (SELECT tarif_id FROM billservice_accounttarif WHERE datetime<now() and account.id=account_id LIMIT 1) as tarif_id, 
                                 (ballance+credit) as balance, 
                                 account.disabled_by_limit as disabled_by_limit, 
                                 account.vpn_speed as vpn_speed, 
                                 nas.reset_action as reset_action, 
                                 nas.vpn_speed_action as speed_action,
                                 account.status as account_status,
                                 account.vpn_ip_address as vpn_ip_address,  
                                 account.ipn_ip_address as ipn_ip_address, 
                                 account.ipn_mac_address as ipn_mac_address,
                                 tarif.active as tarif_status
                                 FROM radius_activesession as rs
                                 JOIN nas_nas as nas ON nas.ipaddress=rs.nas_id
                                 JOIN billservice_account as account ON account.id=rs.account_id
                                 JOIN billservice_tariff as tarif ON tarif.id=get_tarif(account.id)
                                 WHERE rs.date_end is null;
                                 """)'''
                self.cur.execute('''SELECT rs.id AS id, 
                                 rs.account_id AS account_id, 
                                 rs.sessionid AS session,  
                                 rs.speed_string AS speed_string, 
                                 lower(rs.framed_protocol) AS access_type,
                                 nas.name AS nas_name, 
                                 nas.ipaddress AS nas_ip, 
                                 nas.secret AS nas_secret, 
                                 nas.login AS nas_login, 
                                 nas.password AS nas_password, 
                                 nas.type AS nas_type,
                                 account.username AS username, 
                                 get_tarif(account.id) AS tarif_id, 
                                 (ballance+credit) AS balance, 
                                 account.disabled_by_limit AS disabled_by_limit, 
                                 account.vpn_speed AS vpn_speed, 
                                 nas.reset_action AS reset_action, 
                                 nas.vpn_speed_action AS speed_action,
                                 account.status AS account_status,
                                 account.vpn_ip_address AS vpn_ip_address,  
                                 account.ipn_ip_address AS ipn_ip_address, 
                                 account.ipn_mac_address AS ipn_mac_address,
                                 (SELECT tarif.active FROM billservice_tariff AS tarif WHERE tarif.id=get_tarif(account.id)) AS tarif_status,
                                (((account.allow_vpn_null=False and account.ballance+account.credit>=0) or (account.allow_vpn_null=True)) 
                                OR 
                                ((account.allow_vpn_block=False and account.balance_blocked=False and account.disabled_by_limit=False and account.status=True) or (account.allow_vpn_null=True))) as status
                                 FROM radius_activesession AS rs
                                 JOIN nas_nas AS nas ON nas.ipaddress=rs.nas_id
                                 JOIN billservice_account AS account ON account.id=rs.account_id
                                 WHERE rs.date_end IS NULL;''')
    
                rows=self.cur.fetchall()
                self.cur.close()
                self.cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                for row in rows:
                    result=None
                    #print row['balance']
                    """
                    allow_vpn_bull
                    allow_vpn_block
                    
                    (((account.allow_vpn_null=False and account.ballance+account.credit>=0) or (account.allow_vpn_null=True)) 
                    OR 
                    ((account.allow_vpn_block=False and account.balance_blocked=False and account.disabled_by_limit=False and account.status=True) or (account.allow_vpn_null=True)))=True 
                    """
                    if row['status']==True and self.check_period(time_periods_by_tarif_id(self.cur, row['tarif_id']))==True and row['tarif_status']==True:
                        """
                            Делаем проверку на то, изменилась ли скорость.
                            """
                        #print "check"
                        if row['vpn_speed']=='':
                            speed=self.create_speed(row['tarif_id'], row['nas_type'])
                        else:
                            speed=parse_custom_speed(row['vpn_speed']) 
                        newspeed=''
                        for key in speed:
                            newspeed+=unicode(speed[key])
                        #print row
                        #print row['speed_string'],"!!!", newspeed, type(row['speed_string']), type(newspeed)
                        if row['speed_string']!=newspeed:
                            print "set speed", newspeed
                            coa_result=change_speed(dict=dict, account_id=row['account_id'], 
                                                    account_name=str(row['username']), 
                                                    account_vpn_ip=row['vpn_ip_address'], 
                                                    account_ipn_ip=row['ipn_ip_address'], 
                                                    account_mac_address=row['ipn_mac_address'], 
                                                    access_type=str(row['access_type']), 
                                                    nas_ip=str(row['nas_ip']), 
                                                    nas_type=row['nas_type'], 
                                                    nas_name=str(row['nas_name']), 
                                                    nas_secret=str(row['nas_secret']), 
                                                    nas_login=str(row['nas_login']), 
                                                    nas_password=row['nas_password'], 
                                                    session_id=str(row['session']), 
                                                    format_string=str(row['speed_action']),
                                                    speed=speed)                           
    
                            if coa_result==True:
                                self.cur.execute("""
                                    UPDATE radius_activesession
                                    SET speed_string=%s
                                    WHERE id=%s;
                                    """ , (newspeed, row['id'],))
                    else:
                        result = PoD(dict=dict,
                                     account_id=row['account_id'], 
                                     account_name=str(row['username']), 
                                     account_vpn_ip=row['vpn_ip_address'], 
                                     account_ipn_ip=row['ipn_ip_address'], 
                                     account_mac_address=row['ipn_mac_address'], 
                                     access_type=str(row['access_type']), 
                                     nas_ip=row['nas_ip'], 
                                     nas_type=row['nas_type'], 
                                     nas_name=row['nas_name'], 
                                     nas_secret=row['nas_secret'], 
                                     nas_login=row['nas_login'], 
                                     nas_password=row['nas_password'], 
                                     session_id=str(row['session']), 
                                     format_string=str(row['reset_action'])
                                 )
    
                    if result==True:
                        disconnect_result=u'ACK'
                    elif result==False:
                        disconnect_result=u'NACK'
    
                    if result is not None:
                        self.cur.execute("""
                            UPDATE radius_activesession SET session_status=%s WHERE sessionid=%s;
                            """, (disconnect_result, row['session'],))
    
                self.connection.commit()
                self.cur.close()
    
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
        self.connection = pool.connection()
        self.connection._con._con.set_client_encoding('UTF8')
        while True:      
            
            try:
                self.cur = self.connection.cursor()
                # Количество снятий в сутки
                #TODO: toconfig!
                transaction_number=24
                n=(86400)/transaction_number
    
                #выбираем список тарифных планов у которых есть периодические услуги
                self.cur.execute("""SELECT id, settlement_period_id, ps_null_ballance_checkout  
                                 FROM billservice_tariff  as tarif
                                 WHERE id in (SELECT tarif_id FROM billservice_periodicalservice) AND tarif.active=True""")
                rows=self.cur.fetchall()
                #print "SELECT TP"
                #перебираем тарифные планы
                for row in rows:
                    #self.connection.commit()
                    #print row
                    tariff_id, settlement_period_id, null_ballance_checkout=row
    
                    # Получаем список аккаунтов на ТП
                    '''self.cur.execute("""
                                     SELECT a.account_id, a.datetime::timestamp without time zone, (b.ballance+b.credit) as ballance
                                     FROM billservice_account as b
                                     JOIN billservice_accounttarif as a ON a.id=
                                     (SELECT id FROM billservice_accounttarif WHERE account_id=b.id and datetime<now() ORDER BY datetime DESC LIMIT 1)
                                     WHERE a.tarif_id=%d and b.suspended=False
                                     """ % tariff_id)'''
                    '''SELECT a.account_id, max(a.datetime), max((b.ballance+b.credit)) as ballance
                                     FROM billservice_account as b
                                     JOIN billservice_accounttarif as a ON 
                                     a.account_id=b.id
                                     WHERE a.tarif_id=%d and b.suspended=False AND a.datetime < now() GROUP BY a.account_id ORDER BY a.account_id'''
                    self.cur.execute("""SELECT a.account_id,  max(a.datetime), max((SELECT max((b.ballance+b.credit)) AS ballance FROM billservice_account as b WHERE a.account_id=b.id AND b.suspended=False)) as ballance
                                     FROM  billservice_accounttarif as a 
                                     WHERE a.tarif_id=%s  AND a.datetime < now() GROUP BY a.account_id ORDER BY a.account_id""",  (tariff_id,))
                    accounts=self.cur.fetchall()
                    # Получаем параметры каждой перодической услуги в выбранном ТП
                    '''self.cur.execute("""
                                     SELECT b.id, b.name, b.cost, b.cash_method, c.name, c.time_start::timestamp without time zone,
                                     c.length, c.length_in, c.autostart
                                     FROM  billservice_periodicalservice as b
                                     JOIN billservice_settlementperiod as c ON c.id=b.settlement_period_id
                                     WHERE b.tarif_id=%d
                                     """ % tariff_id)'''
                    self.cur.execute("""SELECT b.id, b.name, b.cost, b.cash_method, c.name, c.time_start,
                                     c.length, c.length_in, c.autostart
                                     FROM billservice_periodicalservice as b 
                                     JOIN billservice_settlementperiod as c ON c.id=b.settlement_period_id
                                     WHERE b.tarif_id=%s;""" , (tariff_id,))
                    rows_ps=self.cur.fetchall()
                    self.cur.close()
                    self.cur = self.connection.cursor()
                    # По каждой периодической услуге из тарифного плана делаем списания для каждого аккаунта
                    for row_ps in rows_ps:
                        ps_id, ps_name, ps_cost, ps_cash_method, name_sp, time_start_ps, length_ps, length_in_sp, autostart_sp=row_ps
                        #print "new ps"
                        for account in accounts:
                            #self.connection.commit()
                            account_id = account[0]
                            #print "account_id for ps", ps_id, account_id
                            account_datetime = account[1]
                            account_ballance = account[2]
                            # Если балланс>0 или разрешено снятие денег при отрицательном баллансе
                            if account_ballance>0 or null_ballance_checkout==True:
                                #Получаем данные из расчётного периода
                                if autostart_sp==True:
                                    time_start_ps=account_datetime
                                # Если в расчётном периоде указана длина в секундах-использовать её, иначе использовать предопределённые константы
                                period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=length_in_sp, repeat_after_seconds=length_ps)
                                #self.cur.execute("SELECT datetime::timestamp without time zone FROM billservice_periodicalservicehistory WHERE service_id=%s AND transaction_id=(SELECT id FROM billservice_transaction WHERE tarif_id=%s AND account_id=%s ORDER BY datetime DESC LIMIT 1) ORDER BY datetime DESC LIMIT 1;", (ps_id, tariff_id, account_id,))
                                now=datetime.datetime.now()
                                if ps_cash_method=="GRADUAL":
                                    """
                                    # Смотрим сколько расчётных периодов закончилось со времени последнего снятия
                                    # Если закончился один-снимаем всю сумму, указанную в периодической услуге
                                    # Если закончилось более двух-значит в системе был сбой. Делаем последнюю транзакцию
                                    # а остальные помечаем неактивными и уведомляем администратора
                                    """
                                    last_checkout=get_last_checkout(cursor=self.cur, ps_id = ps_id, tarif = tariff_id, account = account_id)
    
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
                                        # Делаем проводку со статусом Approved
                                        transaction_id = transaction(cursor=self.cur, account=account_id, approved=True, type='PS_GRADUAL', tarif = tariff_id, summ=cash_summ, description=u"Проводка по периодической услуге со cнятием суммы в течении периода", created = now)
                                        ps_history(cursor=self.cur, ps_id=ps_id, transaction=transaction_id, created=now)
    
                                if ps_cash_method=="AT_START":
                                    """
                                    Смотрим когда в последний раз платили по услуге. Если в текущем расчётном периоде
                                    не платили-производим снятие.
                                    """
                                    last_checkout=get_last_checkout(cursor=self.cur, ps_id = ps_id, tarif = tariff_id, account = account_id)
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
                                            summ=ps_cost*nums
                                        
                                             
                                        #TODO: MAKE ACID!!!   
                                        transaction_id = transaction(cursor=self.cur,
                                                                     account=account_id,
                                                                     approved=True,
                                                                     type='PS_AT_START',
                                                                     tarif = tariff_id,
                                                                     summ = summ,
                                                                     description=u"Проводка по периодической услуге со нятием суммы в начале периода",
                                                                     created = now)
                                        ps_history(self.cur, ps_id, transaction=transaction_id, created=now)
                                        #self.connection.commit()
                                if ps_cash_method=="AT_END":
                                    """
                                   Смотрим завершился ли хотя бы один расчётный период.
                                   Если завершился - считаем сколько уже их завершилось.
    
                                   для остальных со статусом False
                                   """
                                    last_checkout=get_last_checkout(cursor=self.cur, ps_id = ps_id, tarif = tariff_id, account = account_id)
    
                                    if last_checkout is None:
                                        first_time=True
                                        last_checkout=now
                                    else:
                                        first_time=False
    
                                    # Здесь нужно проверить сколько раз прошёл расчётный период
    
                                    # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                                    # Для последней проводки ставим статус Approved=True
                                    # для всех остальных False
                                    now=datetime.datetime.now()
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
                                        transaction_id = transaction(cursor=self.cur,
                                                                     account=account_id,
                                                                     approved=True,
                                                                     type='PS_AT_END',
                                                                     tarif = tariff_id,
                                                                     summ=summ,
                                                                     description=descr,
                                                                     created = now)
                                        ps_history(self.cur, ps_id, transaction=transaction_id, created=now)
                                        #self.connection.commit()
                        self.connection.commit()
                        self.cur.close()
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

        while True:

            
            try:
                self.connection = pool.connection()
                self.connection._con._con.set_client_encoding('UTF8')
                self.cur = self.connection.cursor()
                '''self.cur.execute("""
                                 SELECT rs.account_id, rs.sessionid, rs.session_time, rs.interrim_update::timestamp without time zone, tacc.id, tarif.id, acc_t.id
                                 FROM radius_session as rs
                                 JOIN billservice_accounttarif as acc_t ON acc_t.account_id=rs.account_id
                                 JOIN billservice_tariff as tarif ON tarif.id=acc_t.tarif_id
                                 JOIN billservice_timeaccessservice as tacc ON tacc.id=tarif.time_access_service_id
                                 WHERE rs.checkouted_by_time=False and rs.date_start is NUll and acc_t.datetime<rs.interrim_update and tarif.active=True ORDER BY rs.interrim_update ASC;
                                 """)'''
                self.cur.execute("""SELECT rs.account_id, rs.sessionid, rs.session_time, rs.interrim_update,tarif.time_access_service_id, tarif.id, acc_t.id
                                 FROM radius_session AS rs
                                 JOIN billservice_accounttarif AS acc_t ON acc_t.account_id=rs.account_id
                                 JOIN billservice_tariff AS tarif ON tarif.id=acc_t.tarif_id
                                 WHERE (NOT rs.checkouted_by_time) and (rs.date_start IS NULL) AND (tarif.active) AND (acc_t.datetime < rs.interrim_update) AND (tarif.time_access_service_id NOTNULL)
                                 ORDER BY rs.interrim_update ASC;""")
                rows=self.cur.fetchall()
    
                for row in rows:
                    account_id, session_id, session_time, interrim_update, ps_id, tarif_id, accountt_tarif_id = row
                    #1. Ищем последнюю запись по которой была произведена оплата
                    #2. Получаем данные из услуги "Доступ по времени" из текущего ТП пользователя
                    #TODO:2. Проверяем сколько стоил трафик в начале сессии и не было ли смены периода.
                    #TODO:2.1 Если была смена периода -посчитать сколько времени прошло до смены и после смены,
                    # рассчитав соотв снятия.
                    #2.2 Если снятия не было-снять столько, на сколько насидел пользователь
                    self.cur.execute("""
                                     SELECT session_time FROM radius_session WHERE sessionid=%s AND checkouted_by_time=True
                                     ORDER BY interrim_update DESC LIMIT 1
                                     """, (session_id,))
                    try:
                        old_time=self.cur.fetchone()[0]
                    except:
                        old_time=0
                    total_time=session_time-old_time
    
                    self.cur.execute(
                        """
                        SELECT id, size FROM billservice_accountprepaystime WHERE account_tarif_id=%s
                        """, (accountt_tarif_id,))
    
                    try:
                        prepaid_id, prepaid=self.cur.fetchone()
                    except:
                        prepaid=0
                        prepaid_id=-1
    
                    if prepaid>0:
                        if prepaid>=total_time:
                            total_time=0
                            prepaid=prepaid-total_time
                        elif total_time>=prepaid:
                            total_time=total_time-prepaid
                            prepaid=0
                        self.cur.execute("""UPDATE billservice_accountprepaystime SET size=%s WHERE id=%s""", (prepaid, prepaid_id,))
    
    
                    # Получаем список временных периодов и их стоимость у периодической услуги
                    '''self.cur.execute("""
                        SELECT tan.time_period_id, tan.cost
                        FROM billservice_timeaccessnode as tan
                        JOIN billservice_timeperiodnode as tp ON tan.time_period_id=tp.id
                        WHERE tan.time_access_service_id=%s
                        """ % ps_id)'''
                    self.cur.execute("""SELECT tan.time_period_id, tan.cost
                        FROM billservice_timeaccessnode as tan
                        WHERE (tan.time_period_id is not NULL) AND (tan.time_access_service_id=%s)""", (ps_id,))
                    periods=self.cur.fetchall()
                    for period in periods:
                        period_id=period[0]
                        period_cost=period[1]
                        #получаем данные из периода чтобы проверить попала в него сессия или нет
                        '''self.cur.execute(
                            """
                            SELECT tpn.id, tpn.name, tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
                            FROM billservice_timeperiodnode as tpn
                            JOIN billservice_timeperiod_time_period_nodes as tptpn ON tpn.id=tptpn.timeperiodnode_id
                            WHERE tptpn.timeperiod_id=%s
                            """ % period_id)'''
                        self.cur.execute("""SELECT tpn.id, tpn.name, tpn.time_start, tpn.length, tpn.repeat_after
                            FROM billservice_timeperiodnode as tpn
                            WHERE (%s IN (SELECT tptpn.timeperiod_id from billservice_timeperiod_time_period_nodes as tptpn WHERE tpn.id=tptpn.timeperiodnode_id))""", (period_id,))
                        period_nodes_data=self.cur.fetchall()
                        for period_node in period_nodes_data:
                            period_id=period_node[0]
                            period_name = period_node[1]
                            period_start = period_node[2]
                            period_length = period_node[3]
                            repeat_after = period_node[4]
                            if in_period(time_start=period_start,length=period_length, repeat_after=repeat_after):
                                summ=(float(total_time)/60.000)*period_cost
                                if summ>0:
                                    transaction(
                                        cursor=self.cur,
                                        type='TIME_ACCESS',
                                        account=account_id,
                                        approved=True,
                                        tarif=tarif_id,
                                        summ=summ,
                                        description=u"Снятие денег за время по RADIUS сессии %s" % session_id,
                                    )
                                    #print u"Снятие денег за время %s" % query
    

                    self.cur.execute("""
                         UPDATE radius_session
                         SET checkouted_by_time=True
                         WHERE sessionid=%s
                         AND account_id=%s
                         AND interrim_update=%s
                         """, (unicode(session_id), account_id, interrim_update,))
                    self.connection.commit()

                    
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)

            self.cur.close()
            self.connection.close()
            gc.collect()
            time.sleep(30)

class NetFlowAggregate(Thread):
    """
    TO-DO: Вынести в NetFlow коллектор
    Алгоритм для агрегации трафика:
    Формируем таблицу с агрегированным трафиком

    1. Берём строку из netflowstream_raw
    2. Смотрим есть ли похожая строка в netflowstream за последнюю минуту-полторы и не производилось ли по ней списание.
    2.1 Если есть и списание не производилось-суммируем количество байт
    2.2 Если есть и списание производилось или если нет -пишем новую строку
    3. УДаляем из netflowstream_raw строку или помечаем, что она должна быть удалена.

    WHILE TRUE
    timeout(120 seconds)
    произвести агрегирование по новым строкам.
    """

    def __init__(self):
        Thread.__init__(self)

    def check_period(self, rows):
        for row in rows:
            if in_period(row[0],row[1],row[2])==True:
                return True
        return False

    def run(self):
        while True:
            try:
                connection = pool.connection()
                connection._con._con.set_client_encoding('UTF8')
                cur = connection.cursor()
                ts_pool={}
                
                '''cur.execute(
                    """
                    SELECT nf.id, 
                    nf.nas_id, nf.date_start, nf.traffic_class_id, nf.direction, nf.src_addr, 
                    nf.dst_addr, nf.octets, nf.src_port, nf.dst_port, nf.protocol, ba.id, ba.nas_id,
                    tariff.active, tariff.traffic_transmit_service_id, tariff.id, trafficclass.store
                    FROM billservice_rawnetflowstream as nf
                    LEFT JOIN billservice_account as ba ON ba.vpn_ip_address=nf.src_addr OR ba.vpn_ip_address=nf.dst_addr OR ba.ipn_ip_address=nf.src_addr OR ba.ipn_ip_address=nf.dst_addr
                    LEFT JOIN billservice_accounttarif as account_tariff ON account_tariff.id=(SELECT id FROM billservice_accounttarif as at WHERE at.account_id=ba.id and at.datetime<now() ORDER BY datetime DESC LIMIT 1)
                    LEFT JOIN billservice_tariff as tariff ON tariff.id=account_tariff.tarif_id
                    LEFT JOIN nas_trafficclass as trafficclass ON trafficclass.id=nf.traffic_class_id
                    WHERE nf.fetched=False;
                    """)'''
                cur.execute("""SELECT nf.id, 
                    nf.nas_id, nf.account_id, nf.date_start, nf.traffic_class_id, nf.direction, nf.src_addr, 
                    nf.dst_addr, nf.octets, nf.src_port, nf.dst_port, nf.protocol, nf.store,
                    tariff.active, tariff.traffic_transmit_service_id, tariff.id
                    FROM billservice_rawnetflowstream as nf
                    LEFT JOIN billservice_tariff as tariff ON (tariff.id = (select tarif_id from billservice_accounttarif where account_id=nf.account_id  and datetime<nf.date_start ORDER BY datetime DESC LIMIT 1))
                    WHERE nf.fetched=False LIMIT 40000;""")
                raw_streams=cur.fetchall()
    
                """
                Берём строку, ищем пользователя, у которого адрес совпадает или с dst или с src.
                Если сервер доступа в тарифе подразумевает обсчёт сессий через NetFlow помечаем строку "для обсчёта"
                """
                for stream in raw_streams:
                    nf_id, nas_id, account_id, date_start, traffic_class_id, direction, src_addr, dst_addr, octets, src_port, dst_port, protocol, store, \
                         tarif_status, traffic_transmit_service, tarif_id = stream
    
                    if tarif_id==None:
                        cur.execute(
                            """
                            DELETE FROM billservice_rawnetflowstream WHERE id=%s;
                            """, (nf_id,))
                        continue
                    connection.commit()
                    tarif_mode=False
                    #print nf_id
                    #Если у тарифа нет услуги доступа по трафику, значит метим статистику
                    if traffic_transmit_service:
                    #Выбираем временные интервалы из услуги по трафику
                        '''cur.execute(
                            """
                            SELECT tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
                            FROM billservice_timeperiodnode as tpn
                            JOIN billservice_timeperiod_time_period_nodes as timeperiod_timenodes ON timeperiod_timenodes.timeperiodnode_id=tpn.id
                            JOIN billservice_traffictransmitnodes_time_nodes as ttntp ON ttntp.timeperiod_id=timeperiod_timenodes.timeperiod_id
                            JOIN billservice_traffictransmitnodes as ttns ON ttns.id=ttntp.traffictransmitnodes_id
                            WHERE ttns.traffic_transmit_service_id=%s
                            """ % traffic_transmit_service)'''
                        #Кэшируем данные проверки
                        if not ts_pool.has_key(traffic_transmit_service):
                            cur.execute("""SELECT tpn.time_start, tpn.length, tpn.repeat_after
                                FROM billservice_timeperiodnode as tpn
                                WHERE (id IN 
                                (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id IN 
                                (SELECT timeperiod_id FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id IN 
                                (SELECT id FROM billservice_traffictransmitnodes WHERE traffic_transmit_service_id=%s))))""", (traffic_transmit_service,))
        
                            periods=cur.fetchall()
                            ts_pool[traffic_transmit_service] = self.check_period(periods)
                       
                        tarif_mode = ts_pool[traffic_transmit_service]
    
                    cur.execute(
                        """
                        INSERT INTO billservice_netflowstream(
                        nas_id, account_id, tarif_id, direction,date_start, src_addr, traffic_class_id,
                        dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s);
                        """, (nas_id, account_id, tarif_id, direction, date_start,src_addr, traffic_class_id, dst_addr, octets,src_port, dst_port, protocol, False, tarif_mode,)
                        )
    
    
                    connection.commit()
                    if store==True:
                        cur.execute(
                            """
                            UPDATE billservice_rawnetflowstream SET fetched=True WHERE id=%s
                            """, (nf_id,))
                    else:
                        cur.execute(
                            """
                            DELETE FROM billservice_rawnetflowstream WHERE id=%s;
                            """, (nf_id,))
    
                    connection.commit()
                del raw_streams  
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)

            cur.close()
            connection.close()
            gc.collect()
            time.sleep(60)



class Picker(object):
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
        for l in self.picker.get_list():
            #Производим списывание денег
            transaction(
                cursor=cur,
                type='NETFLOW_BILL',
                account=l['account'],
                approved=True,
                tarif=l['tarif'],
                summ=l['summ'],
                description=u"",
            )
            connection.commit()
        connection.commit()
        cur.close()
        
class NetFlowRoutine(Thread):
    '''Thread that handles NetFlow statistic packets and bills according to them'''
    def __init__ (self):
        Thread.__init__(self)
        

    def get_actual_cost(self, trafic_transmit_service_id, traffic_class_id, direction, octets_summ, stream_date):
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
        trafic_transmit_nodes = TRTRNodesCache((trafic_transmit_service_id, traffic_class_id))
        cost=0
        min_from_start=0
        # [0] - ttsn.id, [1] - ttsn.cost, [2] - ttsn.edge_start, [3] - ttsn.edge_end, [4] - tpn.time_start, [5] - tpn.length, [6] - tpn.repeat_after
        for node in trafic_transmit_nodes:
            #'d': '9' - in_direction, '10' - out_direction
            if node[d]:
                trafic_transmit_node_id=node[0]
                trafic_cost=node[1]
                trafic_edge_start=node[2]
                trafic_edge_end=node[3]
    
                period_start=node[4]
                period_length=node[5]
                repeat_after=node[6]
                tnc, tkc, from_start,result=in_period_info(time_start=period_start,length=period_length, repeat_after=repeat_after, now=stream_date)
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
        del trafic_transmit_nodes
        return cost




    
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global curATCache
        global curAT_acIdx
        global curAT_date
        global curAT_lock
        global nfIncomingQueue
        global tpnInPeriod
        global prepaysCache
        cacheAT = None
        dateAT = datetime.datetime(2000, 1, 1)
        sumPick = Picker()
        pstartD = time.time()
        while True:
            try:
                try:
                    #if caches were renewed, renew local copies
                    if curAT_date > dateAT:
                        curAT_lock.acquire()
                        #cacheAT = deepcopy(curATCache)
                        #account-tarif cach indexed by account_id
                        cacheAT = deepcopy(curAT_acIdx)
                        #settlement_period cache
                        cacheSP  = deepcopy(curSPCache)
                        #traffic_transmit_service
                        cacheTTS = deepcopy(curTTSCache)
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
                
                #iterate through them
                for flow in flows:
                    #get account id and get a record from cache based on it
                    acct = cacheAT.get(flow[20])
                    #get collection date
                    stream_date = datetime.datetime.fromtimestamp(flow[21])
                    #if no line in cache, or the collection date is younger then accounttarif creation date
                    #get an acct record from teh database
                    if (not acct) or (not acct[3] <= stream_date):
                        cur = connection.cursor()
                        cur.execute("""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, ba.suspended, ba.created, ba.disabled_by_limit, ba.balance_blocked
                        FROM billservice_account as ba
                        LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                        LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id WHERE ba.id=%s;""", (stream_date, flow[19],))
                        acct = cur.fetchone()
                        cur.close()
                        
                    #if no tarif_id    
                    if acct[4] == None:
                        continue
                    
                    tarif_mode = False
                    #if traffic_transmit_service_id is OK
                    if acct[7]:
                        tarif_mode = tpnInPeriod[acct[7]]
                        
                    #if tarif_mode is False or tarif.active = False
                    #write statistics without billing it
                    if (not tarif_mode) or (not acct[10]):
                        cur = connection.cursor()
                        cur.execute(
                        """
                        INSERT INTO billservice_netflowstream(
                        nas_id, account_id, tarif_id, direction,date_start, src_addr, traffic_class_id,
                        dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s);
                        """, (flow[11], flow[20], acct[4], flow[23], stream_date,intToIp(flow[0],4), "{"+','.join([str(cls) for cls in flow[22]])+"}", intToIp(flow[1],4), flow[6],flow[9], flow[10], flow[13], False, False,)
                        )
                        connection.commit()
                        cur.close()
                        continue
                    
                    s = false
                    #if traffic_transmit_service_id is OK
                    if acct[7]:
                        #if settlement_period_id is OK
                        if acct[9]:
                            #get a line from Settlement Period cache                            
                            #[0] - id, [1] - time_start, [2] - length, [3] - length_in, [4] - autostart
                            spInf = cacheSP[acct[9]]
                            #if 'autostart'
                            if spInf[4]:
                                #start = accounttarif.datetime
                                sp_time_start=acct[3]
                                
                            #stream_date = datetime.datetime.fromtimestamp(flow[20])
                            settlement_period_start, settlement_period_end, deltap = settlement_period_info(time_start=spInf[1], repeat_after=spInf[3], repeat_after_seconds=spInf[2], now=stream_date)
                            octets_summ=0
                            #loop throungh classes in 'classes' tuple
                            for tclass in flow[22]:
                                #acct[7] - traffic_transmit_service_id
                                #flow[23] - direction
                                trafic_cost=self.get_actual_cost(acct[7], tclass, flow[23], octets_summ, stream_date)
                                if direction=="INPUT":
                                    d = 5
                                elif direction=="OUTPUT":
                                    d = 6
                                else:
                                    d = 6
                                #get a record from prepays cache
                                #keys: traffic_transmit_service_id, accounttarif.id, trafficclass
                                prepInf =  prepaysCache.get((acct[7], acct[11],tclass))
                                
                                octets = flow[6]
                                if prepInf:
                                    #d = 5: chacs whether in_direction is True; d = 6: whether out_direction
                                    if prepInf[d]:
                                        #[0] - prepais.id, [1] - prepais.size
                                        prepaid_id = prepInf[0]
                                        prepaid  = prepInf[1]
                                        prepHnd = prepaid
                                        if prepaid>0:                            
                                            if prepaid>=octets:
                                                prepaid=prepaid-octets
                                                octets=0
                                            elif octets>=prepaid:
                                                octets=octets-prepaid
                                                prepaid=abs(prepaid-octets)
            
                                            cur = connection.cursor()
                                            cur.execute("""UPDATE billservice_accountprepaystrafic SET size=size-%s WHERE id=%s""", (prepaid, prepaid_id,))
                                            connection.commit()
                                            cur.close()
                                            #if the cache didn't change in meantime, save changes in cache
                                            if prepHnd == prepInf[1]:
                                                prepInf[1] = prepInf[1] - prepaid
            
                                summ=(trafic_cost*octets)/(1024000)
            
                                if summ>0:
                                    #account_id, tariff_id, summ
                                    pays.add_summ(flow[20], acct[4], summ)
                                    
                                #insert statistics
                                cur = connection.cursor()
                                cur.execute(
                                """
                                INSERT INTO billservice_netflowstream(
                                nas_id, account_id, tarif_id, direction,date_start, src_addr, traffic_class_id,
                                dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                                VALUES (%s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s);
                                """, (flow[11], flow[20], acct[4], flow[23], stream_date,intToIp(flow[0],4), "{"+','.join([str(cls) for cls in flow[22]])+"}", intToIp(flow[1],4), flow[6],flow[9], flow[10], flow[13], True, False,)
                                )
                                connection.commit()
                                cur.close()
                                
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + repr(ex)
                else:
                    print self.getName() + ": exception: " + repr(ex)
                    
class NetFlowBill(Thread):
    """
    WHILE TRUE
    берём строки с for_checkout=True и checkouted=False и по каждой строке производим начисления
    timeout(120 seconds)

    """
    class Picker(object):
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


    def __init__(self):
        #self.connection = pool.getconn()
        #self.connection = psycopg2.connect(dsn)
        #self.connection.set_client_encoding('UTF8')
        #self.cur = self.connection.cursor()
        #self.conn = True
        Thread.__init__(self)

    def get_actual_cost(self, trafic_transmit_service_id, traffic_class_id, direction, octets_summ, stream_date):
        """
        Метод возвращает актуальную цену для направления трафика для пользователя:
        """

        if direction=="INPUT":
            d = "in_direction=True"
        elif direction=="OUTPUT":
            d = "out_direction=True"
        else:
            return 0
        #TODO: check whether differentiated traffic billing us used <edge_start>=0; <edge_end>='infinite'
        #print (octets_summ, octets_summ, octets_summ, trafic_transmit_service_id, traffic_class_id, d)
        """self.cur.execute('''SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start, tpn.length, tpn.repeat_after
            FROM billservice_traffictransmitnodes as ttsn
            JOIN billservice_timeperiodnode AS tpn on tpn.id IN 
            (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id IN 
            (SELECT timeperiod_id FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=ttsn.id))
            WHERE ((ttsn.edge_start>='%s' AND ttsn.edge_end<='%s') OR (ttsn.edge_start>='%s' AND ttsn.edge_end='0' ))
            AND (ttsn.traffic_transmit_service_id='%s') 
            AND (ttsn.id IN (SELECT traffictransmitnodes_id FROM billservice_traffictransmitnodes_traffic_class WHERE trafficclass_id='%s'))
            AND ttsn.%s;''' % (octets_summ/(1024000), octets_summ/(1024000), octets_summ/(1024000), trafic_transmit_service_id, traffic_class_id, d,))"""

        self.cur.execute('''SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start, tpn.length, tpn.repeat_after
            FROM billservice_traffictransmitnodes as ttsn
            JOIN billservice_timeperiodnode AS tpn on tpn.id IN 
            (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id IN 
            (SELECT timeperiod_id FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=ttsn.id))
            WHERE (ttsn.traffic_transmit_service_id='%s') 
            AND (ttsn.id IN (SELECT traffictransmitnodes_id FROM billservice_traffictransmitnodes_traffic_class WHERE trafficclass_id='%s'))
            AND ttsn.%s;''' % (trafic_transmit_service_id, traffic_class_id, d,))
        trafic_transmit_nodes=self.cur.fetchall()
        cost=0
        min_from_start=0
        for node in trafic_transmit_nodes:
            trafic_transmit_node_id=node[0]
            trafic_cost=node[1]
            trafic_edge_start=node[2]
            trafic_edge_end=node[3]

            period_start=node[4]
            period_length=node[5]
            repeat_after=node[6]
            tnc, tkc, from_start,result=in_period_info(time_start=period_start,length=period_length, repeat_after=repeat_after, now=stream_date)
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
        del trafic_transmit_nodes
        return cost




    def run(self):
        self.connection = pool.connection()
        self.connection._con._con.set_client_encoding('UTF8')
        while True:            
            try:
                self.cur = self.connection.cursor()
                a=time.clock()

                self.cur.execute(
                    """
                    SELECT nf.id, nf.account_id, nf.tarif_id, nf.date_start::timestamp without time zone, nf.traffic_class_id, nf.direction, nf.octets, bs_acc.username, 
                    tarif.traffic_transmit_service_id, tarif.settlement_period_id, transmitservice.cash_method, transmitservice.period_check, accounttarif.id, accounttarif.datetime::timestamp without time zone,
                    settlementperiod.time_start::timestamp without time zone, settlementperiod.length_in, settlementperiod.length, settlementperiod.autostart
                    FROM billservice_netflowstream as nf
                    JOIN billservice_account as bs_acc ON bs_acc.id=nf.account_id
                    JOIN nas_trafficclass as traficclass ON traficclass.id=nf.traffic_class_id
                    JOIN billservice_tariff as tarif ON tarif.id=nf.tarif_id
                    JOIN billservice_traffictransmitservice as transmitservice ON transmitservice.id=tarif.traffic_transmit_service_id
                    JOIN billservice_accounttarif as accounttarif ON accounttarif.id=
                    (SELECT id FROM billservice_accounttarif WHERE tarif_id=tarif.id and account_id=nf.account_id and datetime<nf.date_start ORDER BY datetime DESC LIMIT 1)
                    LEFT JOIN billservice_settlementperiod as settlementperiod ON settlementperiod.id = tarif.settlement_period_id
                    WHERE for_checkout=True and checkouted=False and tarif.active=True ORDER BY nf.account_id ASC LIMIT 10000;
                    """)
                rows=self.cur.fetchall()
    
                pays=self.Picker()
    
                for row in rows:
                    """
                    TO-DO: Пробегаемся по всем записям. Суммируем суммы денег для одного пользователя и разом списываем всю сумму
                    """
                    nf_id, \
                         account_id,\
                         tarif_id, \
                         stream_date, \
                         traffic_class_id,\
                         direction, \
                         octets, \
                         username, \
                         trafic_transmit_service_id, \
                         settlement_period_id, \
                         cash_method, \
                         period_check, \
                         accounttarif_id,\
                         accounttarif_datetime, \
                         sp_time_start, \
                         sp_length_in, \
                         sp_length, \
                         sp_autostart = row
                    s=False
                    #print nf_id
    
                    if trafic_transmit_service_id:
                        #Если в тарифном плане указан расчётный период
                        if settlement_period_id:
                            if sp_autostart==True:
                                # Если у расчётного периода стоит параметр Автостарт-за начало расчётного периода принимаем
                                # дату привязки тарифного плана пользователю
                                sp_time_start=accounttarif_datetime
    
                            #print "before SP", time.clock()-b
                            settlement_period_start, settlement_period_end, deltap = settlement_period_info(time_start=sp_time_start, repeat_after=sp_length_in, repeat_after_seconds=sp_length, now=stream_date)
    
                            #Смотрим сколько уже наработал за текущий расчётный период по этому тарифному плану
                            
                            '''self.cur.execute(
                                """
                                SELECT sum(octets)
                                FROM billservice_netflowstream
                                WHERE tarif_id=%s and account_id=%s and checkouted=True and date_start between %s and %s
                                """ , ( tarif_id, account_id, settlement_period_start, settlement_period_end,))'''
    
                            #octets_summ=self.cur.fetchone()[0] or 0
                            octets_summ=0
                        else:
                            octets_summ=0
                        #LOOP for every class
                        trafic_cost=self.get_actual_cost(trafic_transmit_service_id, traffic_class_id, direction, octets_summ, stream_date)
    
                        """
                        Использован т.н. дифференциальный подход к начислению денег за трафик
                        Тарифный план позволяет указать по какой цене считать трафик
                        в зависимости от того сколько этого трафика уже накачал пользователь за расчётный период
                        """
    
    
                        if direction=="INPUT":
                            d = "in_direction=True"
                        elif direction=="OUTPUT":
                            d = "out_direction=True"
                        else:
                            d = "out_direction=True"
                        #alt?    
                        
    
                        query="""
                             SELECT prepais.id, prepais.size 
                             FROM billservice_accountprepaystrafic as prepais
                             JOIN billservice_prepaidtraffic as prepaidtraffic ON prepaidtraffic.id=prepais.prepaid_traffic_id
                             JOIN billservice_prepaidtraffic_traffic_class ON billservice_prepaidtraffic_traffic_class.prepaidtraffic_id=prepaidtraffic.id
                             WHERE prepais.size>0 and prepais.account_tarif_id=%s and billservice_prepaidtraffic_traffic_class.trafficclass_id=%s and prepaidtraffic.traffic_transmit_service_id=%s and prepaidtraffic.%s""" % (accounttarif_id,traffic_class_id, trafic_transmit_service_id, d)
                        self.cur.execute(query)
    
                        try:
                            prepaid_id, prepaid=self.cur.fetchone()
                        except Exception, e:
                            prepaid=0
                            prepaid_id=-1
                        if prepaid>0:
                            if prepaid>=octets:
                                prepaid=prepaid-octets
                                octets=0
                            elif octets>=prepaid:
                                octets=octets-prepaid
                                prepaid=0
    
    
                            self.cur.execute("""UPDATE billservice_accountprepaystrafic SET size=%s WHERE id=%s""", (prepaid, prepaid_id,))
    
                        summ=(trafic_cost*octets)/(1024000)
    
                        if summ>0:
                            pays.add_summ(account_id, tarif_id, summ)
    
                    #till here
                    self.cur.execute(
                        """
                        UPDATE billservice_netflowstream
                        SET checkouted=True
                        WHERE id=%s;
                        """, (nf_id,))
    
                rows=None
    
                for l in pays.get_list():
                    #Производим списывание денег
                    transaction(
                        cursor=self.cur,
                        type='NETFLOW_BILL',
                        account=l['account'],
                        approved=True,
                        tarif=l['tarif'],
                        summ=l['summ'],
                        description=u"",
                    )
                    self.connection.commit()
                self.connection.commit()

            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)
                
            
            self.cur.close()
            #self.connection.close()
            gc.collect()
            time.sleep(45)
        #connection.close()


class limit_checker(Thread):
    """
    Проверяет исчерпание лимитов. если лимит исчерпан-ставим соотв галочку в аккаунте
    """
    def __init__ (self):
        Thread.__init__(self)

    def run(self):
        self.connection = pool.connection()
        self.connection._con._con.set_client_encoding('UTF8')
        while True:
            
            try:
                self.cur = self.connection.cursor()
                """
                Выбираем тарифные планы, у которых есть лимиты
                """
                self.cur.execute(
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
                    ORDER BY account.id ASC;
                    """)
                account_tarifs=self.cur.fetchall()
                self.cur.close()
                self.cur = self.connection.cursor()
                oldid=-1
                for row in account_tarifs:
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
                              autostart_sp = row 
                    #print "limit check", account_id
                    if in_direction==out_direction==False:
                        continue
                    
                    if limit_id==None:
                        #пишем в базу состояние пользователя
                        self.cur.execute(
                            """
                            UPDATE billservice_account
                            SET disabled_by_limit=%s
                            WHERE id=%s;
                            """, (False, account_id,))
    
                        continue
    
                    if oldid==account_id and block:
                        """
                        Если у аккаунта уже есть одно превышение лимита
                        то больше для него лимиты не проверяем
                        """
                        continue
    
                    if autostart_sp==True:
                        sp_start=account_start
                    else:
                        sp_start = sp_time_start
    
                    settlement_period_start, settlement_period_end, delta = settlement_period_info(time_start=sp_start, repeat_after=sp_length_in, repeat_after_seconds=sp_length)
    
                    #если нужно считать количество трафика за последнеие N секунд, а не за рачётный период, то переопределяем значения
                    if limit_mode==True:
                        settlement_period_start=datetime.datetime.now()-datetime.timedelta(seconds=delta)
                        settlement_period_end=datetime.datetime.now()
    
                    block=False
    
                    d=''
                    if in_direction:
                        d+=" 'INPUT'"
                    if out_direction:
                        if in_direction:
                            d+=","
                        d+="'OUTPUT'"
    
                    self.connection.commit()
                    self.cur.execute("""
                         SELECT sum(octets) as size FROM billservice_netflowstream as nf
                         JOIN billservice_trafficlimit_traffic_class as tltc ON tltc.trafficclass_id=nf.traffic_class_id
                         WHERE nf.account_id=%s and tltc.trafficlimit_id=%s and date_start>%s and date_start<%s and nf.direction in (%s)
    
                         """, (account_id, limit_id, settlement_period_start, settlement_period_end, d,))
    
                    tsize=0
                    sizes=self.cur.fetchall()
                    self.cur.close()
                    self.cur = self.connection.cursor()
                    for size in sizes:
                        if size[0]!=None:
                            tsize+=size[0]
    
                    if tsize>limit_size*1024:
                        block=True
    
                    #Если у тарифного плана нет лимитов-снимаем отметку disabled_by_limit
    
                    oldid=account_id
                    if disabled_by_limit!=block:
                        #пишем в базу состояние пользователя
                        self.cur.execute(
                            """
                            UPDATE billservice_account
                            SET disabled_by_limit=%s
                            WHERE id=%s;
                            """ , (block, account_id,))
    
    
                self.connection.commit()
                #print self.getName() + " threadend"
                self.cur.close()
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
        
        
        self.connection = pool.connection()
        self.connection._con._con.set_client_encoding('UTF8')
        while True:
            
            try:
                self.cur = self.connection.cursor()
                self.cur.execute(
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
                self.cur.close()
                self.cur = self.connection.cursor()
                for row in rows:
                    (shedulelog_id, accounttarif_id_shedulelog, account_id, account_balance_blocked, account_balance,ballance_checkout, prepaid_traffic_reset, prepaid_time_reset,
                     time_start, length, length_in, autostart, accounttarif_id, acct_datetime, tarif_id,
                     reset_tarif_cost, cost, traffic_transmit_service_id, time_access_service_id,
                     reset_traffic, reset_time, balance_blocked, prepaid_traffic_accrued, prepaid_time_accrued) = row
    
                    if shedulelog_id==None:
                        shedulelog_id=-1
    
                    if time_start is not None:
                        if autostart:
                            time_start=acct_datetime
    
                        period_start, period_end, delta = settlement_period_info(time_start=time_start, repeat_after=length_in, repeat_after_seconds=length)
                        #prev_period_start, prev_period_end, prev_delta = settlement_period_info(time_start=time_start, repeat_after=length_in, repeat_after_seconds=length, prev=True)
                    else:
                        time_start = acct_datetime
                        period_start = acct_datetime
                        delta = 86400*365*365
                        #WTF???
    
                    #нужно производить в конце расчётного периода
                    if ballance_checkout==None: ballance_checkout = acct_datetime
                    if ballance_checkout<period_start:
                        #Снять сумму до стоимости тарифного плана
                        if reset_tarif_cost:
                            self.cur.execute(
                                """
                                SELECT sum(summ)
                                FROM billservice_transaction
                                WHERE created > %s and created< %s and account_id=%s and tarif_id=%s;
                                """, (period_start, period_end, account_id, tarif_id,))
                            summ=self.cur.fetchone()[0]
                            if summ==None:
                                summ=0
    
                            if cost>summ:
                                s=cost-summ
                                transaction(
                                    cursor=self.cur,
                                    type='END_PS_MONEY_RESET',
                                    account=account_id,
                                    approved=True,
                                    tarif=tarif_id,
                                    summ=s,
                                    description=u"Доснятие денег до стоимости тарифного плана у %s" % account_id,
                                )
    
    
                            self.cur.execute("UPDATE billservice_shedulelog SET ballance_checkout=now() WHERE account_id=%s RETURNING id;", (account_id,))
                            shedulelog_id =self.cur.fetchone()
                            #print "shedulelog_id", shedulelog_id
    
                            if shedulelog_id==None:
                                self.cur.execute("""
                                                 INSERT INTO billservice_shedulelog(account_id, accounttarif_id, ballance_checkout) values(%s, %s, now());
                                                 """, (account_id, accounttarif_id,))
    
    
                        #Если балланса не хватает - отключить пользователя
                    self.connection.commit()
                    
                    if (balance_blocked is None or balance_blocked<=period_start) and cost>=account_balance and account_balance_blocked==False:
                        #print "balance blocked1", ballance_checkout, period_start, cost, account_balance
                        #В начале каждого расчётного периода
                        self.cur.execute(
                            """
                            UPDATE billservice_account SET balance_blocked=True WHERE id=%s and ballance+credit<%s;
                            """, (account_id, cost,))
    
    
                        self.cur.execute("""
                                         UPDATE billservice_shedulelog SET balance_blocked = now() WHERE account_id=%s RETURNING id;
                                         """, (account_id,))
    
                        if self.cur.fetchone()==None:
                            self.cur.execute("""
                                             INSERT INTO billservice_shedulelog(account_id, accounttarif_id,balance_blocked) values(%s, %s, now()); 
                                             """, (account_id, accounttarif_id,))
                    if account_balance_blocked==True and account_balance>=cost:
                        """
                        Если пользователь отключён, но баланс уже больше разрешённой суммы-включить пользователя
                        """
                        #Иначе Убираем отметку
                        #print "balance blocked2"
                        self.cur.execute(
                            """
                            UPDATE billservice_account SET balance_blocked=False WHERE id=%s;
                            """, (account_id,))                            
    
                    self.connection.commit()
                    if prepaid_traffic_reset is None: prepaid_traffic_reset = acct_datetime
                    if (prepaid_traffic_reset<period_start and reset_traffic==True) or traffic_transmit_service_id is None or accounttarif_id!=accounttarif_id_shedulelog:
                        """
                        (Если наступил новый расчётный период и нужно сбрасывать трафик) или если нет услуги с доступом по трафику или если сменился тарифный план
                        """
                        self.cur.execute(
                            """
                            DELETE FROM billservice_accountprepaystrafic WHERE account_tarif_id=%s;
                            """ % accounttarif_id)
    
                        self.cur.execute("UPDATE billservice_shedulelog SET prepaid_traffic_reset=now() WHERE account_id=%s RETURNING id;", (account_id,))
                        if self.cur.fetchone()==None:
                            self.cur.execute("""
                                             INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_reset) values(%s, %s, now()) ;
                                             """, (account_id, accounttarif_id,))    
                    self.connection.commit()
    
                    if (prepaid_traffic_accrued is None or prepaid_traffic_accrued<period_start) and traffic_transmit_service_id:                          
                        #Начислить новый предоплаченный трафик
                        self.cur.execute(
                            """
                            SELECT id, size
                            FROM billservice_prepaidtraffic
                            WHERE traffic_transmit_service_id=%s;
                            """, (traffic_transmit_service_id,))
    
                        prepais=self.cur.fetchall()
                        u=False
                        for prepaid_traffic_id, size in prepais:
                            u=True
                            #print "SET PREPAID TRAFIC"
                            self.cur.execute(
                                """
                                UPDATE billservice_accountprepaystrafic SET size=size+%s, datetime=now()
                                WHERE account_tarif_id=%s and prepaid_traffic_id=%s RETURNING id;
                                """, (size, accounttarif_id, prepaid_traffic_id,))
                            if self.cur.fetchone() is None:
                                #print 'INSERT'
                                #print accounttarif_id, prepaid_traffic_id, size
                                self.cur.execute(
                                    """
                                    INSERT INTO billservice_accountprepaystrafic (account_tarif_id, prepaid_traffic_id, size, datetime)
                                    VALUES(%s, %s, %f*1024000, now());
                                    """ % (accounttarif_id, prepaid_traffic_id, size,))                            
                        if u==True:
                            self.cur.execute("UPDATE billservice_shedulelog SET prepaid_traffic_accrued=now() WHERE account_id=%s RETURNING id;", (account_id,))
                            if self.cur.fetchone()==None:
                                self.cur.execute("""
                                                 INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_accrued) values(%s, %s, now()) ;
                                                 """, (account_id, accounttarif_id,))  
                    self.connection.commit() 
                    self.cur.close()
                    self.cur = self.connection.cursor()
                    if (prepaid_time_reset is None or prepaid_time_reset<period_start) and time_access_service_id  or accounttarif_id!=accounttarif_id_shedulelog:
    
                        if reset_time:
                            #снять время и начислить новое
                            self.cur.execute(
                                """
                                DELETE FROM billservice_accountprepaystime
                                WHERE account_tarif_id=%s;
                                """, (accounttarif_id,))
    
                            self.cur.execute("UPDATE billservice_shedulelog SET prepaid_time_reset=now() WHERE account_id=%s RETURNING id;", (account_id,))
                            if self.cur.fetchone()==None:
                                self.cur.execute("""
                                                 INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_reset) values(%s, %s, now()) ;
                                                 """, (account_id, accounttarif_id,))        
                            self.connection.commit()    
    
                    if (prepaid_time_accrued is None or prepaid_time_accrued<period_start) and time_access_service_id:
    
                        self.cur.execute(
                            """
                            UPDATE billservice_accountprepaystime
                            SET size=size+(SELECT prepaid_time FROM billservice_timeaccessservice WHERE id=%s),
                            datetime=now()
                            WHERE account_tarif_id=%s RETURNING id;
                            """, (time_access_service_id, accounttarif_id,))
                        if self.cur.fetchone()==None:
                            self.cur.execute(
                                """
                                INSERT INTO billservice_accountprepaystime(account_tarif_id, size, datetime,prepaid_time_service_id)
                                VALUES(%s, (SELECT prepaid_time FROM billservice_timeaccessservice WHERE id=%s), now(), %s);
                                """, (accounttarif_id, time_access_service_id, time_access_service_id,))
    
    
    
                        self.cur.execute("UPDATE billservice_shedulelog SET prepaid_time_accrued=now() WHERE account_id=%s RETURNING id;", (account_id,))
                        if self.cur.fetchone()==None:
                            cur.execute("""
                                        INSERT INTO billservice_shedulelog(account_id, accounttarif_id,prepaid_time_accrued) values(%s, %s, now()) ;
                                        """, (account_id, accounttarif_id,))
                self.connection.commit()
                    
                #Делаем проводки по разовым услугам тем, кому их ещё не делали
                self.cur.execute("""
                                 SELECT account.id as account_id, service.id as service_id, service.name as service_name, service.cost as service_cost, tarif.id as tarif_id, (SELECT id FROM billservice_accounttarif
                                 WHERE account_id=account.id and datetime<now() ORDER BY datetime DESC LIMIT 1) as accounttarif
                                 FROM billservice_account as account
                                 JOIN billservice_tariff as tarif ON tarif.id=get_tarif(account.id)
                                 JOIN billservice_onetimeservice as service ON service.tarif_id=tarif.id
                                 LEFT JOIN billservice_onetimeservicehistory as oth ON oth.accounttarif_id=(SELECT id FROM billservice_accounttarif
                                 WHERE account_id=account.id and datetime<now() ORDER BY datetime DESC LIMIT 1) and service.id=oth.onetimeservice_id
                                 WHERE (account.ballance+account.credit)>0 and oth.id is Null;
                                 """)
                rows = self.cur.fetchall()
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
    
                    self.connection.commit()

            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)

            self.cur.close()
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

    def create_speed(self, tarif_id):
        defaults = get_default_speed_parameters(self.cur, tarif_id)
        speeds = get_speed_parameters(self.cur, tarif_id)
        for speed in speeds:
            if in_period(speed['time_start'], speed['length'], speed['repeat_after'])==True:
                defaults = comparator(defaults, speed)
                return defaults

        #print "speed_result=", defaults
        return defaults


    def run(self):
        self.connection = pool.connection()
        self.connection._con._con.set_client_encoding('UTF8')
        while True:             
            try:
                self.cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
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
                    WHERE accessparameters.ipn_for_vpn=True and account.ipn_ip_address!='0.0.0.0'
                    ;""")
                rows=self.cur.fetchall()
                for row in rows:
                    #print "check ipn"
                    sended=None
                    recreate_speed = False
                    period=self.check_period(time_periods_by_tarif_id(self.cur, row['tarif_id']))
                    #print period
                    if row['account_ipn_status']==False and row['ballance']>0 and period==True and row['account_disabled_by_limit']==False and row['account_status']==True and row['account_balance_blocked']==False:
                        #print u"ВКЛЮЧАЕМ",row['account_username']
                        #шлём команду, на включение пользователя, account_ipn_status=True
                        if row['ipn_added']==False:
                            """
                            Если на сервере доступа ещё нет этого пользователя-значит добавляем. В следующем проходе делаем пользователя enabled
                            """
                            sended = cred(account_id=row['account_id'], account_name=row['account_username'], 
                                          access_type='IPN',
                                          account_vpn_ip=row['account_vpn_ip_address'], account_ipn_ip=row['account_ipn_ip_address'], 
                                          account_mac_address=row['account_ipn_mac_address'], nas_ip=row['nas_ipaddress'], nas_login=row['nas_login'], 
                                          nas_password=row['nas_password'], format_string=row['nas_user_add'])
                            if sended == True: self.cur.execute("UPDATE billservice_account SET ipn_added=%s WHERE id=%s" % (True, row['account_id']))
                        else:
                            sended = cred(account_id=row['account_id'], account_name=row['account_username'], 
                                          access_type='IPN',
                                          account_vpn_ip=row['account_vpn_ip_address'], account_ipn_ip=row['account_ipn_ip_address'], 
                                          account_mac_address=row['account_ipn_mac_address'], nas_ip=row['nas_ipaddress'], nas_login=row['nas_login'], 
                                          nas_password=row['nas_password'], format_string=row['nas_user_enable'])
                            recreate_speed = True
                    
                            if sended == True: self.cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s" % (True, row['account_id']))
                    elif (row['account_disabled_by_limit']==True or row['ballance']<=0 or period==False or row['account_balance_blocked']==True or row['account_status']==False) and row['account_ipn_status']==True:
    
                        #шлём команду на отключение пользователя,account_ipn_status=False
                        #print u"ОТКЛЮЧАЕМ",row['account_username']
                        sended = cred(account_id=row['account_id'], account_name=row['account_username'], \
                                      access_type='IPN', \
                                      account_vpn_ip=row['account_vpn_ip_address'], account_ipn_ip=row['account_ipn_ip_address'], \
                                      account_mac_address=row['account_ipn_mac_address'], nas_ip=row['nas_ipaddress'], nas_login=row['nas_login'], \
                                      nas_password=row['nas_password'], format_string=row['nas_user_disable'])
    
                        if sended == True: self.cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s", (False, row['account_id'],))
    
    
                    self.connection.commit()
                    #print account_ipn_speed
                    if row['account_ipn_speed']=='' or row['account_ipn_speed']==None:
    
                        speed=self.create_speed(row['tarif_id'])
                    else:
                        speed = parse_custom_speed(row['account_ipn_speed'])
    
    
                    newspeed=''
                    for key in speed:
                        newspeed+=unicode(speed[key])
    
                    #print newspeed, row['ipn_speed'],row['ipn_state']
                    #print newspeed!=row['ipn_speed'] or row['ipn_state']==False
                    if newspeed!=row['ipn_speed'] or (row['ipn_state']==False and newspeed!=row['ipn_speed']) or recreate_speed==True:
                        #print u"МЕНЯЕМ НАСТРОЙКИ СКОРОСТИ НА СЕВРЕРЕ ДОСТУПА", speed
                        #отправляем на сервер доступа новые настройки скорости, помечаем state=True
    
                        sended_speed = change_speed(dict=dict, account_id=row['account_id'], 
                                                    account_name=row['account_username'], 
                                                    account_vpn_ip=row['account_vpn_ip_address'], 
                                                    account_ipn_ip=row['account_ipn_ip_address'], 
                                                    account_mac_address=row['account_ipn_mac_address'], 
                                                    access_type='IPN', 
                                                    nas_ip=row['nas_ipaddress'], 
                                                    nas_type=row['nas_type'], 
                                                    nas_name=row['nas_name'], 
                                                    nas_secret='', 
                                                    nas_login=row['nas_login'], 
                                                    nas_password=row['nas_password'], 
                                                    format_string=row['nas_ipn_speed'],
                                                    speed=speed)    
                        data_for_save=''
                        #print speed
    
                        self.cur.execute("UPDATE billservice_accountipnspeed SET speed=%s, state=%s WHERE account_id=%s RETURNING id;", (newspeed, sended_speed, row['account_id'],))
                        id = self.cur.fetchone()
                        #print 'id=', id
                        if id==None:
                            self.cur.execute("INSERT INTO billservice_accountipnspeed(account_id, speed, state, datetime) VALUES( %s, %s, %s , now());", (row['account_id'], unicode(newspeed), sended_speed,))
    
                self.connection.commit()
                self.cur.close()
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + str(ex)
                else:
                    print self.getName() + ": exception: " + str(ex)
                    traceback.print_exc(file=sys.stdout)

            
            #self.connection.close()
            gc.collect()
            time.sleep(60)


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
        global prepaysCache
        global TRTRNodesCache
        while True:             
            try:
                cur = connection.cursor()
                cur.execute("""SELECT tpn.time_start, tpn.length, tpn.repeat_after, ttns.traffic_transmit_service_id
                            FROM billservice_timeperiodnode AS tpn
                            JOIN billservice_timeperiod_time_period_nodes AS timeperiod_timenodes ON timeperiod_timenodes.timeperiodnode_id=tpn.id
                            JOIN billservice_traffictransmitnodes_time_nodes AS ttntp ON ttntp.timeperiod_id=timeperiod_timenodes.timeperiod_id
                            JOIN billservice_traffictransmitnodes AS ttns ON ttns.id=ttntp.traffictransmitnodes_id;""")
                tpns = cur.fetchall()
                cur.close()
                tmpPerTP = defaultdict(lambda: False)
                #calculates whether traffic_transmit_service fits in any oh the periods
                for tpn in tpns:
                    tmpPerTP[tpn[3]] = tmpPerTP[tpn[3]] or in_period(tpn[0], tpn[1], tpn[2])
                tpnInPeriod = tmpPerTP
                
                cur = connection.cursor()
                cur.execute("""SELECT prepais.id, prepais.size, prepais.account_tarif_id, prept_tc.trafficclass_id, prepaidtraffic.traffic_transmit_service_id, prepaidtraffic.in_direction, prepaidtraffic.out_direction
                             FROM billservice_accountprepaystrafic as prepais
                             JOIN billservice_prepaidtraffic as prepaidtraffic ON prepaidtraffic.id=prepais.prepaid_traffic_id
                             JOIN billservice_prepaidtraffic_traffic_class AS prept_tc ON prept_tc.prepaidtraffic_id=prepaidtraffic.id
                             WHERE prepais.size>0""")
                prepTp = cur.fetchall()
                cur.close()
                if prepTp:
                    #prepaisTmp = defaultdict(lambda: defaultdict(defaultdict(list)))
                    prepaysTmp = defaultdict(list)
                    #keys: traffic_transmit_service_id, accounttarif.id, trafficclass
                    for prep in prepTp:
                        #prepaisTmp[prep[4]][prep[2]][prep[3]].append([prep[0], prep[1], prep[5], prep[6]])
                        prepaysTmp[(prep[4],prep[2],prep[3])].append([prep[0], prep[1], prep[5], prep[6]])
                    #print prepaisTmp
                    prepaysCache = prepaysTmp
                    
                cur = connection.cursor()
                cur.execute("""SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start, tpn.length, tpn.repeat_after,
                ARRAY(SELECT trafficclass_id FROM billservice_traffictransmitnodes_traffic_class WHERE traffictransmitnodes_id=ttsn.id) as classes, ttsn.traffic_transmit_service_id, ttsn.in_direction, ttsn.out_direction
                FROM billservice_traffictransmitnodes as ttsn
                JOIN billservice_timeperiodnode AS tpn on tpn.id IN 
                (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id IN 
                (SELECT timeperiod_id FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=ttsn.id));""")
                trtrnodsTp = cur.fetchall()
                cur.close()
                #trafnodesTmp = defaultdict(lambda: defaultdict(list))
                trafnodesTmp = defaultdict(list)
                #keys: traffictransmitservice, trafficclass
                for trnode in trtrnodsTp:
                    for classnd in trnode[7]:
                        #trafnodesTmp[trnode[9]][classnd].append(trnode)
                        trafnodesTmp[(trnode[8],classnd)].append(trnode)
                TRTRNodesCache = trafnodesTmp
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
[8]  - bt.cost,bt.reset_tarif_cost, 
[9]  - bt.settlement_period_id, 
[10] - bt.active, 
[11] - act.id, 
[12] - ba.suspended, 
[13] - ba.created, 
[14] - ba.disabled_by_limit, 
[15] - ba.balance_blocked, 
[16] - ba.nas_id, 
[17] - ba.vpn_ip_address, 
[18] - ba.ipn_ip_address,
[19] - ba.ipn_mac_address, 
[20] - ba.assign_ipn_ip_from_dhcp, 
[21] - ba.ipn_status, 
[22] - ba.ipn_speed, 
[23] - ba.vpn_speed, 
[24] - ba.ipn_added, 
[25] - bt.ps_null_ballance_checkout, 
[26] - bt.deleted, 
[27] - bt.allow_express_pay,
[28] - ba.status, 
'''
class AccountServiceThread(Thread):
    '''Handles simultaniously updated READ ONLY caches connected to account-tarif tables'''
    def __init__ (self):
        Thread.__init__(self)
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global curATCache
        global curAT_acIdx
        global curAT_tfIdx
        global curAT_date
        global curAT_lock
        global curSPCache
        #global curTCCache
        global curTTSCache
        global curTCTTSSP_lock
        while True:             
            try:
                cur = connection.cursor()
                tmpDate = datetime.datetime.now()
                cur.execute("""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, ba.suspended, ba.created, ba.disabled_by_limit, ba.balance_blocked, ba.nas_id, ba.vpn_ip_address, ba.ipn_ip_address,ba.ipn_mac_address, ba.assign_ipn_ip_from_dhcp, ba.ipn_status, ba.ipn_speed, ba.vpn_speed, ba.ipn_added, bt.ps_null_ballance_checkout, bt.deleted, bt.allow_express_pay, ba.status 
                    FROM billservice_account as ba
                    LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                    LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id;""", (tmpDate,))
                #list cache
                accts = cur.fetchall()
                cur.close()
                #index on account_id, directly links to tuples
                tmpacIdx = {}
                #index on tariff_id
                tmptfIdx = defaultdict(list)
                i = 0
                for acct in accts:
                    tmpacIdx[acct[0]]  = acct
                    if acct[4]:
                        tmptfIdx[acct[4]].append(acct)
                        #tmptfIdx[acct[4]].append(i)
                    #i += 1
                '''curAT_lock.acquire()
                curATCache  = accts
                curAT_acIdx = tmpacIdx
                curAT_tfIdx = tmptfIdx
                #maybe use binary date?
                curAT_date  = tmpDate
                curAT_lock.release()'''
                
                cur = connection.cursor()
                cur.execute("""SELECT id, reset_traffic, cash_method, period_check FROM billservice_traffictransmitservice;""")
                ttssTp = cur.fetchall()
                cur.execute("""SELECT id, time_start, length, length_in, autostart FROM billservice_settlementperiod;""")
                spsTp = cur.fetchall()
                #traffic_transmit_service cache, indexed by id
                tmpttsC = {}
                #settlement period cache, indexed by id
                tmpsC = {}
                for tts in ttssTp:
                    tmpttsC[tts[0]] = tts
                for sps in spsTp:
                    tmpsC[sps[0]] = sps
                
                #renew global cache links
                curAT_lock.acquire()
                curATCache  = accts
                curAT_acIdx = tmpacIdx
                curAT_tfIdx = tmptfIdx
                curSPCache = tmpsC
                curTTSCache = tmpttsC
                curAT_date  = tmpDate
                curAT_lock.release()
            except Exception, ex:
                if isinstance(ex, psycopg2.OperationalError):
                    print self.getName() + ": database connection is down: " + repr(ex)
                else:
                    print self.getName() + ": exception: " + repr(ex)
            
            gc.collect()
            time.sleep(180)
            
class NfAServStarter(Thread):
        def __init__ (self, addr_):
            self.addr_ = addr_
            Thread.__init__(self)

        def run(self):
            #server = ThreadingUDPServer(self.address, self.handler)
            #server.serve_forever()
            
            NfAsyncUDPServer(self.addr_)            
            while 1: 
                asyncore.poll(0.010)
                
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
        self.bind(addr_)
        self.set_reuse_addr()

    def handle_connect(self):
        #print 'New packet'
        pass    
    #TODO: add login of sending '0' when queue is too long
    def handle_read_event (self):
        try:
            data, addr = self.socket.recvfrom(8192)
            self.socket.sendto(str(len(data)), addr)
            nfIncomingQueue.append(data)
            print len(nfIncomingQueue)
        except:            
            traceback.print_exc()
            return
        #self.handle_readfrom(data, addr)


    def handle_readfrom(self,data, address):
        pass
    def writable(self):
        return (0)
    """def writable (self):
        return len(self.outbuf)

    def sendto (self, data, addr):
        self.outbuf.append((data, addr))
        self.initiate_send()

    def initiate_send(self):
        b = self.outbuf
        while len(b):
            data, addr = b[0]
            del b[0]
            try:
                result = self.socket.sendto (data, addr)
                if result != len(data):
                    self.log('Sent packet truncated to %d bytes' % result)
            except socket.error, why:
                if why[0] == EWOULDBLOCK:
                    return
                else:
                    raise socket.error, why"""

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
        #print "acceptident-----------------"
        #print conn
        #print hash

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
                #print conn.utoken
                #print obj.id
                #print conn
                #Pyro.protocol.DefaultConnValidator.acceptIdentification(self, tcpserver, conn, hash, challenge)
                return(1,0)
            else:
                #print "DENIED-----------------"
                #print conn
                #print obj.id
                conn.utoken = ''
                return (0,Pyro.constants.DENIED_SECURITY)
        except Exception, ex:
            #rint "acceptidentificationerror---------------: ", ex
            #print conn
            conn.utoken = ''
            return (0,Pyro.constants.DENIED_SECURITY)

    def checkIP(self, ipstr, hostsstr):
        #print "checkIP----"
        #print hostsstr
        #print ipstr
        userIP = IPy.IP(ipstr)
        #print "presplit"
        hosts = hostsstr.split(', ')
        #print "hosts====="
        #print hosts
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
                    if func.__name__ == "flush":
                        caller.cur.close()
                        caller.db_connection.close()
                        caller.db_connection = pool.connection()
                        caller.db_connection._con._con.set_client_encoding('UTF8')
                        caller.cur = caller.db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
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
            cur.execute("""SELECT account.id as account_id, account.username as username, account.ipn_ip_address as ipn_ip_address,
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
            print "actions", row
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
    
            sended = cred(account_id=row['account_id'], account_name=row['username'], access_type = row['access_type'],
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
        listcur.close()
        listconnection.close()
        return retres

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
        print result
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
            self.create("UPDATE billservice_systemuser SET last_login=now() WHERE id=%s;" , (obj.id,))
            self.commit()
            #Pyro.constants.

            return True
        else:
            return False

    @authentconn
    def test(self, cur=None, connection=None):
        pass

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




def main():
    if "-D" not in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
    dict=dictionary.Dictionary("dicts/dictionary", "dicts/dictionary.microsoft","dicts/dictionary.mikrotik","dicts/dictionary.rfc3576")
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
    

    threads=[]
    #threads.append(NfAServStarter(coreAddr))
    threads.append(AccountServiceThread())
    threads.append(CacheServiceThread())
    threads.append(RPCServer())
    threads.append(check_vpn_access())
    #threads.append(periodical_service_bill())
    threads.append(TimeAccessBill())
    #threads.append(NetFlowAggregate())
    #threads.append(NetFlowBill())
    threads.append(NetFlowRoutine())
    #threads.append(limit_checker())
    threads.append(ipn_service())
    #threads.append(settlement_period_service_dog())
    
    i= range(len(threads))
    for th in threads:	
        th.start()
        time.sleep(1)
        
    NfAsyncUDPServer(coreAddr)            
    while 1: 
        asyncore.poll(0.010)
    """while True:
        #print pool
        #print pool._connections
        for t in threads:
            #time.sleep(1)
            #print t
            #print 'thread status', t.getName(), t.isAlive()
            if not t.isAlive():
                print 'restarting thread', t.getName(), str(t)
                #t.__init__()
                #t.start()
                print 'thread status', t.getName(), t.isAlive()
        time.sleep(15)"""


#===============================================================================
import socket
if socket.gethostname() not in ['dmitry-desktop','dolphinik','sserv.net','sasha', 'iserver','kenny','billing', 'medusa', 'Billing.NemirovOnline']:
    import sys
    print "License key error. Exit from application."
    sys.exit(1)
    
if __name__ == "__main__":

    config.read("/opt/ebs/data/ebs_config.ini")

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
    nfIncomingQueue = deque()
    nfQueueLock = Lock()
    curATCache  = {}
    curAT_acIdx = {}
    curAT_tfIdx = {}
    curAT_acctIdx = {}
    curAT_date  = None
    curAT_lock  = Lock()
    tpnInPeriod = None
    #curTCCache = {}
    curTTSCache = {}
    curSPCache = {}
    #curTCTTSSP_date = None
    curTCTTSSP_lock = Lock()
    prepaysCache = {}
    prepays_lock = Lock()
    TRTRNodesCache = {}
    
    
    
    main()

