#-*-coding=utf-8-*-
import psycopg2
from psycopg2.pool import PersistentConnectionPool
import time, datetime
from utilites import disconnect, settlement_period_info
import dictionary
from threading import Thread
from utilites import in_period
import logging
import logging.config
import time
import os
from db import transaction, ps_history, get_last_checkout

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn=PersistentConnectionPool(2,10,"dbname='mikrobill' user='mikrobill' host='localhost' password='1234'")

class check_access(Thread):
        def __init__ (self, dict, timeout=30):
            self.dict=dict
            self.timeout=timeout
            Thread.__init__(self)
            
        def check_period(self, rows):
            for row in rows:
                if in_period(row[0],row[1],row[2])==False:
                    return False
            return True
                
        def check_acces(self):
            """
            Функция сейчас применима только к поддерживающим POD NAS-ам
            Раз в 30 секунд происходит выборка всех пользователей
            OnLine, делается проверка,
            1. не вышли ли они за рамки временного диапазона
            2. Не ушли ли в нулевой балланс
            если срабатывает одно из двух условий-посылаем команду на отключение пользователя
            TO-DO: Переписать! Работает правильно.
            nas_id содержит в себе IP адрес. Сделано для уменьшения выборок в модуле core при старте сессии
            TO-DO: если NAS не поддерживает POD или в парметрах доступа ТП указан IPN - отсылать команды через SSH
            """
            connection = conn.getconn()
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur=connection.cursor()


            while True:
                time.sleep(self.timeout)
                cur.execute("""
                SELECT DISTINCT rs.account_id, rs.sessionid, rs.nas_id, rs.date_start, rs.date_end
                FROM radius_session as rs
                WHERE rs.disconnect_status is null AND disconnect_status is null AND rs.date_start is null AND date_end not in
                (SELECT rsess.date_end from radius_session as rsess WHERE rsess.sessionid=rs.sessionid and rsess.date_end is not null);
                """)
                rows=cur.fetchall()
                for row in rows:
                    account_id=row[0]
                    session_id=row[1]
                    nas_id=row[2]
                    
                    cur.execute("SELECT name, secret from nas_nas WHERE ipaddress='%s'" % nas_id)
                    row_n=cur.fetchone()
                    nas_name = row_n[0]
                    nas_secret = row_n[1]
                    result=''

                    cur.execute("SELECT username, (SELECT tarif_id FROM billservice_accounttarif WHERE datetime<now() LIMIT 1) as tarif_id, ballance FROM billservice_account WHERE id='%s'" % account_id)
                    rows_u = cur.fetchall()
                    for row_u in rows_u:
                        username=row_u[0]
                        tarif_id = row_u[1]
                        ballance=row_u[2]
                        if ballance>0:
                           #Информация для проверки периода
                           cur.execute("""SELECT time_start::timestamp without time zone, length, repeat_after FROM billservice_timeperiodnode WHERE id=(SELECT  timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id=(SELECT access_time_id FROM billservice_tariff WHERE id='%s'))""" % tarif_id)
                           #rows_t=cur.fetchall()
                           if self.check_period(rows=cur.fetchall())==False:
                                  result = disconnect(dict=self.dict, code=40, nas_secret=nas_secret, nas_ip=nas_id, nas_id=nas_name, username=username, session_id=session_id)
                        else:
                               result = disconnect(dict=self.dict, code=40, nas_secret=nas_secret, nas_ip=nas_id, nas_id=nas_name, username=username, session_id=session_id)
                    if result==True:
                        #Если удалось отключить - пишем в базу
                        disconnect_result='ACK'
                    elif result==False:
                        #Если не удалось отключить - или сессии не существовало
                        disconnect_result='NACK'
                    else:
                        disconnect_result=''
                    if disconnect_result=='ACK':
                        # Если сбросили сессию, значит она существовала и сервер доступа сам
                        # Пришлёт STOP пакет
                        cur.execute(
                        """
                        UPDATE radius_session SET disconnect_status=%s WHERE id=(
                        SELECT id
                        FROM radius_session WHERE sessionid=%s ORDER BY id DESC LIMIT 1);
                        """, (disconnect_result, session_id)
                        )
                    else:
                        # Если сессии не было, значит закрываем её
                        cur.execute(
                        """
                        UPDATE radius_session SET date_end=interrim_update, disconnect_status=%s WHERE id=(
                        SELECT id
                        FROM radius_session WHERE sessionid=%s ORDER BY id DESC LIMIT 1);
                        """, (disconnect_result, session_id)
                        )
                    
        def run(self):
            self.check_acces()
            

class session_dog(Thread):
    """
    Закрывает подвисшие сессии
    Подумать над реализацией для MySQL
    """
    def __init__ (self):
        Thread.__init__(self)

    def run(self):
        pass
        #cur.execute("UPDATE radius_session SET date_end=interrim_update WHERE interrim_update-date_start>= interval '00:01:00' and date_end is Null;")
        #cur.execute("UPDATE radius_session SET session_time=extract(epoch FROM date_end-date_start) WHERE session_time is Null;")
        

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
        connection = conn.getconn()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur=connection.cursor()
        while True:
            # Количество снятий в сутки
            transaction_number=24
            n=(24*60*60)/transaction_number
            #time.sleep(n)
            
            #выбираем список тарифных планов у которых есть периодические услуги
            cur.execute("SELECT id, settlement_period_id  FROM billservice_tariff WHERE id in (SELECT tariff_id FROM billservice_tariff_periodical_services)")
            rows=cur.fetchall()
            #print "SELECT TP"
            #перебираем тарифные планы
            for row in rows:
                #print row
                tariff_id=row[0]
                settlement_period_id=row[1]
                # Получаем список аккаунтов на ТП
                cur.execute("""
                SELECT a.account_id, a.datetime::timestamp without time zone, b.ballance
                FROM billservice_accounttarif as a
                LEFT JOIN billservice_account as b ON b.id=a.account_id
                WHERE datetime<now() and a.tarif_id='%s' and b.suspended=False
                """ % tariff_id)
                accounts=cur.fetchall()
                # Получаем параметры каждой перодической услуги в выбранном ТП
                cur.execute("""
                SELECT b.id, b.name, b.cost, b.cash_method, c.name, c.time_start::timestamp without time zone,
                c.length_in, c.autostart
                FROM billservice_tariff_periodical_services as p
                JOIN billservice_periodicalservice as b ON p.periodicalservice_id=b.id
		        JOIN billservice_settlementperiod as c ON c.id=b.settlement_period_id
                WHERE p.tariff_id='%s'
                """ % tariff_id)
                rows_ps=cur.fetchall()
                # По каждой периодической услуге из тарифного плана делаем списания для каждого аккаунта
                for row_ps in rows_ps:
                    ps_id = row_ps[0]
                    ps_name = row_ps[1]
                    ps_cost = row_ps[2]
                    ps_cash_method = row_ps[3]
                    name_sp=row_ps[4]
                    time_start_ps=row_ps[5]
                    length_in_sp=row_ps[6]
                    autostart_sp=row_ps[7]

                    for account in accounts:
                        account_id = account[0]
                        account_datetime = account[1]
                        account_ballance = account[2]
                        #Получаем данные из расчётного периода
                        if autostart_sp==True:
                           time_start_ps=account_datetime
                        #print ps_name, length_in_sp
                        period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=length_in_sp)

                        cur.execute("SELECT datetime::timestamp without time zone FROM billservice_periodicalservicehistory WHERE service_id=%s AND transaction_id=(SELECT id FROM billservice_transaction WHERE tarif_id=%s AND account_id=%s ORDER BY datetime DESC LIMIT 1) ORDER BY datetime DESC LIMIT 1;" % (ps_id, tariff_id, account_id))
                        now=datetime.datetime.now()
                        if ps_cash_method=="GRADUAL":
                            """
                        # Смотрим сколько расчётных периодов закончилось со времени последнего снятия
                        # Если закончился один-снимаем всю сумму, указанную в периодической услуге
                        # Если закончилось более двух-значит в системе был сбой. Делаем последнюю транзакцию
                        # а остальные помечаем неактивными и уведомляем администратора
                            """
                            last_checkout=get_last_checkout(cursor=cur, ps_id = ps_id, tarif = tariff_id, account = account_id)
                            # Здесь нужно проверить сколько раз прошёл расчётный период
                            if last_checkout==None:
                                last_checkout=period_start
                                
                            if (now-last_checkout).seconds>=n:
                                #Проверяем наступил ли новый период
                                if now-datetime.timedelta(seconds=n)<=period_start:
                                    # Если начался новый период
                                    # Находим когда начался прошльый период
                                    # Смотрим сколько денег должны были снять за прошлый период и производим корректировку
                                    #period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=length_in_sp, now=now-datetime.timedelta(seconds=n))
                                    pass
                                # Смотрим сколько раз уже должны были снять деньги
                                lc=now - last_checkout
                                nums, ost=divmod(lc.seconds,delta)
                                for i in xrange(nums-1):
                                    #Смотрим на какую сумму должны были снять денег и снимаем её
                                    pass
                                #print "delta", delta
                                cash_summ=(float(n)*float(transaction_number)*float(ps_cost))/(float(delta)*float(transaction_number))
                                # Делаем проводку со статусом Approved

                                transaction_id = transaction(cursor=cur,
                                account=account_id,
                                approved=True,
                                tarif = tariff_id,
                                summ=cash_summ,
                                description=u"Проводка по периодической услуге со нятием суммы в течении периода",
                                created = now)

                                ps_history(cursor=cur, ps_id=ps_id, transaction=transaction_id, created=now)

                        if ps_cash_method=="AT_START":
                            """
                            Смотрим когда в последний раз платили по услуге. Если в текущем расчётном периоде
                            не платили-производим снятие.
                            """
                            last_checkout=get_last_checkout(cursor=cur, ps_id = ps_id, tarif = tariff_id, account = account_id)
                            # Здесь нужно проверить сколько раз прошёл расчётный период
                            if last_checkout==None:
                                last_checkout=period_start
                            # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                            # Для последней проводки ставим статус Approved=True
                            # для всех сотальных False
                            # Если последняя проводка меньше или равно дате начала периода-делаем снятие
                            if last_checkout<=period_start:
                                
                                lc=last_checkout-period_start
                                nums, ost=divmod(lc.seconds, delta)
                                for i in xrange(nums-1):
                                    transaction_id = transaction(
                                    cursor=cur,
                                    account=account_id,
                                    approved=False,
                                    tarif = tariff_id,
                                    summ=ps_cost,
                                    description=u"Проводка по периодической услуге со нятием суммы в в начале периода",
                                    created = now)

                                    ps_history(cur, ps_id, transaction=transaction_id, created=now)
                                   
                                transaction_id = transaction(cursor=cur,
                                account=account_id,
                                approved=True,
                                tarif = tariff_id,
                                summ=ps_cost,
                                description=u"Проводка по периодической услуге со нятием суммы в начале периода",
                                created = now)

                                ps_history(cur, ps_id, transaction=transaction_id, created=now)
                                
                        if ps_cash_method=="AT_END":
                           """
                           Смотрим завершился ли хотя бы один расчётный период.
                           Если завершился - считаем сколько уже их завершилось.
                           Для последнего делаем проводку со статусом Approved=True
                           для остальных со статусом False
                           """
                           last_checkout=get_last_checkout(ps_id = ps_id, tarif = tariff_id, account = account_id)
                           # Здесь нужно проверить сколько раз прошёл расчётный период
                           if last_checkout==None:
                               last_checkout=period_start
                           # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                           # Для последней проводки ставим статус Approved=True
                           # для всех сотальных False
                           now=datetime.datetime.now()
                           # Если дата начала периода больше последнего снятия - делаем проводки
                           # Выражение верно т.к. новая проводка совершится каждый раз только после после перехода
                           #в новый период.
                           if period_start>last_checkout:

                                lc=last_checkout-period_start
                                nums, ost=divmod((period_end-last_checkout).seconds, delta)
                                for i in xrange(nums-1):
                                    transaction_id = transaction(cursor=cur,
                                    account=account_id,
                                    approved=False,
                                    tarif = tariff_id,
                                    summ=cash_summ,
                                    description=u"Проводка по периодической услуге со нятием суммы в конце периода",
                                    created = now)

                                    ps_history(cur, ps_id, transaction=transaction_id, created=now)

                                transaction_id = transaction(cursor=cur,
                                account=account_id,
                                approved=True,
                                tarif = tariff_id,
                                summ=cash_summ,
                                description=u"Проводка по периодической услуге со нятием суммы в конце периода",
                                created = now)
                                ps_history(cur, ps_id, transaction=transaction_id, created=now)
                                
            time.sleep(n)

class TimeAccessBill(Thread):
    """
    Услуга применима только для VPN доступа, когда точно известна дата авторизации
    и дата отключения пользователя
    """
    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        """
        По каждой записи делаем транзакции для польователя в соотв с его текущим тарифным планов
        """
        connection = conn.getconn()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur=connection.cursor()
        while True:
            cur.execute("""
            SELECT account_id, sessionid, session_time, interrim_update::timestamp without time zone
            FROM radius_session WHERE checkouted_by_time=False and date_start is NUll ORDER BY interrim_update ASC;
            """)
            rows=cur.fetchall()
            print "next loop"
            for row in rows:
                print "next row"
                account_id=row[0]
                session_id = row[1]
                session_time = row[2]
                interrim_update = row[3]
                #1. Ищем последнюю запись по которой была произведена оплата
                #2. Получаем данные из услуги "Доступ по времени" из текущего ТП пользователя
                #2. Проверяем сколько стоил трафик в начале сессии и не было ли смены периода.
                #TODO:2.1 Если была смена периода -посчитать сколько времени прошло до смены и после смены,
                # рассчитав соотв снятия.
                #2.2 Если снятия не было-снять столько, на сколько насидел пользователь
                cur.execute("""
                SELECT session_time FROM radius_session WHERE sessionid='%s' AND checkouted_by_time=True
                ORDER BY interrim_update DESC LIMIT 1
                """ %session_id)
                try:
                    old_time=cur.fetchone()[0]
                except:
                    old_time=0
                total_time=session_time-old_time
                cur.execute(
                """
                SELECT tacc.id, tacc.name
                FROM billservice_timeaccessservice as tacc
                JOIN billservice_tariff as tarif ON tarif.time_access_service_id=tacc.id
                WHERE tacc.id=(SELECT tarif_id FROM billservice_accounttarif WHERE datetime<now() AND account_id=%s ORDER BY datetime DESC LIMIT 1)
                """ % account_id
                )
                print "acc_id=", account_id
                ps_data=cur.fetchone()
                ps_id=ps_data[0]
                ps_name = ps_data[1]
                # Получаем список временных периодов и их стоимость у периодической услуги
                cur.execute(
                """
                SELECT tan.time_period_id, tan.cost
                FROM billservice_timeaccessnode as tan
                JOIN billservice_timeaccessservice_time_periods as tp ON tan.time_period_id=tp.timeaccessnode_id
                WHERE tp.timeaccessservice_id=%s
                """ % ps_id
                )
                periods=cur.fetchall()
                for period in periods:
                    period_id=period[0]
                    period_cost=period[1]
                    #получаем данные из периода чтобы проверить попала в него сессия или нет
                    cur.execute(
                    """
                    SELECT tpn.id, tpn.name, tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
                    FROM billservice_timeperiodnode as tpn
                    JOIN billservice_timeperiod_time_period_nodes as tptpn ON tpn.id=tptpn.timeperiodnode_id
                    WHERE tptpn.timeperiod_id=%s
                    """ % period_id
                    )
                    period_nodes_data=cur.fetchall()
                    for period_node in period_nodes_data:
                        period_id=period_node[0]
                        period_name = period_node[1]
                        period_start = period_node[2]
                        period_length = period_node[3]
                        repeat_after = period_node[4]
                        if in_period(time_start=period_start,length=period_length, repeat_after=repeat_after):
                            summ=(float(total_time)/60.000)*period_cost
                            print "summ=", summ
                            cur.execute("""
                                       INSERT INTO billservice_transaction(
                                       account_id, approved, tarif_id, summ, description, created)
                                       VALUES (%s, %s, %s, %s, %s, %s);
                                       """,(account_id, True, ps_id, summ, "TIME ACCESS", datetime.datetime.now()))
                            query="UPDATE billservice_account SET  ballance=ballance-%s WHERE id=%s" % (summ, account_id)
                            print u"Снятие денег за время %s" % query
                            cur.execute(query)
                            query="""UPDATE radius_session SET checkouted_by_time=True WHERE sessionid='%s' AND account_id='%s' AND interrim_update='%s'
                            """ % (session_id, account_id, interrim_update)
                            print query
                            cur.execute(query)
            time.sleep(30)

class TraficAccessBill(Thread):
    """
    Услуга применима только для VPN доступа, когда точно известна дата авторизации
    и дата отключения пользователя
    """
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        """
        По каждой записи делаем транзакции для польователя в соотв с его текущим тарифным планов
        """
        connection = conn.getconn()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur=connection.cursor()
        while True:
            cur.execute("""
            SELECT account_id, sessionid, bytes_in, bytes_out, interrim_update::timestamp without time zone
            FROM radius_session WHERE checkouted_by_trafic=False and date_start is NUll ORDER BY interrim_update ASC
            """)
            rows=cur.fetchall()
            print "next loop"
            for row in rows:
                print "next row"
                account_id=row[0]
                session_id = row[1]
                session_bytes_in = row[2]
                session_bytes_out = row[3]
                interrim_update = row[4]
                #1. Ищем последнюю запись по которой была произведена оплата
                #2. Получаем данные из услуги "Доступ по трафику" из текущего ТП пользователя
                #2. Проверяем сколько стоил трафик в начале сессии и не было ли смены периода.
                #TODO:2.1 Если была смена периода -посчитать сколько времени прошло до смены и после смены,
                # рассчитав соотв снятия.
                #2.2 Если снятия не было-снять столько, на сколько насидел пользователь
                cur.execute("""
                SELECT bytes_in, bytes_out FROM radius_session WHERE sessionid='%s' AND checkouted_by_trafic=True
                ORDER BY interrim_update DESC LIMIT 1
                """ % session_id)
                a=cur.fetchone()
                try:
                    old_bytes_in=a[0]
                    old_bytes_out=a[1]
                except:
                    old_bytes_in=0
                    old_bytes_out=0
                    # Создаём запись о трафике в таблице
                    cur.execute(
                    """
                    INSERT INTO billservice_summarytrafic(incomming_class_id,outgoing_class_id,
                    account_id, radius_session, date_start)
                    VALUES ((SELECT id FROM nas_trafficclass where weight='%s'),(SELECT id FROM nas_trafficclass where weight='%s'),'%s', '%s', '%s')
                    """ % (100,200, account_id, session_id, datetime.datetime.now())
                    )
                    
                total_bytes_in=session_bytes_in-old_bytes_in
                total_bytes_out=session_bytes_out-old_bytes_out
                print total_bytes_in,total_bytes_out
                cur.execute(
                """
                SELECT tacc.id, tacc.name
                FROM billservice_traffictransmitservice as tacc
                JOIN billservice_tariff as tarif ON tarif.traffic_transmit_service_id=tacc.id
                WHERE tacc.id=(SELECT tarif_id FROM billservice_accounttarif WHERE datetime<now() AND account_id=%s ORDER BY datetime DESC LIMIT 1)
                """ % account_id
                )
                print "acc_id=", account_id
                ps_data=cur.fetchone()
                ps_id=ps_data[0]
                ps_name = ps_data[1]
                # Получаем список временных периодов и их стоимость у периодической услуги
                cur.execute(
                """
                SELECT tc.weight, tn.cost, tnp.timeperiod_id, tc.id
                FROM billservice_traffictransmitnodes as tn
                JOIN nas_trafficclass as tc ON tc.id=tn.traffic_class_id
                JOIN billservice_traffictransmitnodes_time_period as tnp ON tnp.traffictransmitnodes_id=tn.id
                JOIN billservice_traffictransmitservice_traffic_nodes as tts ON tts.traffictransmitnodes_id=tn.id
                WHERE tts.traffictransmitservice_id=%s
                """ % ps_id
                )
                periods=cur.fetchall()
                for period in periods:
                    tc_weight=period[0]
                    traffic_cost=period[1]
                    period_id=period[2]
                    class_id=period[3]
                    
                    #получаем данные из периода чтобы проверить попала в него сессия или нет
                    cur.execute(
                    """
                    SELECT tpn.id, tpn.name, tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
                    FROM billservice_timeperiodnode as tpn
                    JOIN billservice_timeperiod_time_period_nodes as tptpn ON tpn.id=tptpn.timeperiodnode_id
                    WHERE tptpn.timeperiod_id=%s
                    """ % period_id
                    )
                    period_nodes_data=cur.fetchall()
                    for period_node in period_nodes_data:
                        period_id=period_node[0]
                        period_name = period_node[1]
                        period_start = period_node[2]
                        period_length = period_node[3]
                        repeat_after = period_node[4]
                        if in_period(time_start=period_start,length=period_length, repeat_after=repeat_after):
                            if tc_weight==100:
                                #Входяший
                                #Относительно клиента
                                summ=(float(total_bytes_in)/(1024*1024))*traffic_cost
                                print "aa",total_bytes_in, traffic_cost
                                print "summ=", summ
                                cur.execute("""
                                           INSERT INTO billservice_transaction(
                                           account_id, approved, tarif_id, summ, description, created)
                                           VALUES (%s, %s, %s, %s, %s, %s);
                                           """,(account_id, True, ps_id, summ, "TRAFFIC ACCESS", datetime.datetime.now()))
                                query="UPDATE billservice_account SET  ballance=ballance-%s WHERE id=%s" % (summ, account_id)
                                print u"Снятие денег за исходящий трафик. Класс 100 %s" % query
                                cur.execute(query)
                                query="""UPDATE radius_session SET checkouted_by_trafic=True WHERE sessionid='%s' AND account_id='%s' AND interrim_update='%s'
                                """ % (session_id, account_id, interrim_update)
                                print query
                                cur.execute(query)
                                query="""
                                    UPDATE billservice_summarytrafic
                                    SET incomming_bytes='%s', outgoing_bytes='%s',
                                    date_end='%s'
                                    WHERE radius_session='%s';
                                    """ % (session_bytes_in, session_bytes_out, datetime.datetime.now(), session_id)
                                cur.execute(query)
                            elif tc_weight==200:
                                #Исходящий Относительно клиента
                                summ=(float(total_bytes_out)/(1024*1024))*traffic_cost
                                print "summ=", summ
                                cur.execute("""
                                           INSERT INTO billservice_transaction(
                                           account_id, approved, tarif_id, summ, description, created)
                                           VALUES (%s, %s, %s, %s, %s, %s);
                                           """,(account_id, True, ps_id, summ, "TRAFFIC ACCESS", datetime.datetime.now()))
                                query="UPDATE billservice_account SET  ballance=ballance-%s WHERE id=%s" % (summ, account_id)
                                print u"Снятие денег за входящий трафик. Класс 200 %s" % query
                                cur.execute(query)
                                query="""UPDATE radius_session SET checkouted_by_trafic=True WHERE sessionid='%s' AND account_id='%s' AND interrim_update='%s'
                                """ % (session_id, account_id, interrim_update)
                                print query
                                cur.execute(query)

                            
                                query="""
                                    UPDATE billservice_summarytrafic
                                    SET incomming_bytes='%s', outgoing_bytes='%s',
                                    date_end='%s'
                                    WHERE radius_session='%s';
                                    """ % (session_bytes_in, session_bytes_out, datetime.datetime.now(), session_id)
                                cur.execute(query)
            time.sleep(30)


        
class LoggerThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        #specify logging config file
        logging.config.fileConfig("logging.conf")

        #create and start listener on port 9999
        t = logging.config.listen(9999)
        t.start()

        #create logger
        logger = logging.getLogger("simpleExample")

        #watch for existence of file named "f"
        #loop through the code while this file exists
        
        while os.path.isfile('f'):
            logger.debug("debug message")
            logger.info("info message")
            logger.warn("warn message")
            logger.error("error message")
            logger.critical("critical message")
            time.sleep(5)

        #cleanup
        logging.config.stopListening()
        t.join()
        
        
        
dict=dictionary.Dictionary("dicts\dictionary","dicts\dictionary.microsoft","dicts\dictionary.rfc3576")
cas = check_access(timeout=10, dict=dict)
cas.start()

traficaccessbill = TraficAccessBill()
traficaccessbill.start()
psb=periodical_service_bill()
psb.start()
time_access_bill = TimeAccessBill()
time_access_bill.start()

#check_access()