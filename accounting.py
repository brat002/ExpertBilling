#-*-coding=utf-8-*-

import time, datetime, os
from utilites import DAE, settlement_period_info, in_period, in_period_info,create_speed_string
import dictionary
from threading import Thread

from db import get_default_speed_parameters, get_speed_parameters,transaction, ps_history, get_last_checkout, time_periods_by_tarif_id

import settings
import psycopg2
from DBUtils.PooledDB import PooledDB

pool = PooledDB(
     mincached=6,
     maxcached=60,
     blocking=True,
     creator=psycopg2,
     dsn="dbname='%s' user='%s' host='%s' password='%s'" % (settings.DATABASE_NAME,
                                                            settings.DATABASE_USER,
                                                            settings.DATABASE_HOST,
                                                            settings.DATABASE_PASSWORD)
)


class check_vpn_access(Thread):
        def __init__ (self, dict, timeout=30):
            self.dict=dict
            self.timeout=timeout
            self.connection = pool.connection()
            Thread.__init__(self)

        def check_period(self, rows):
            for row in rows:
                if in_period(row[0],row[1],row[2])==True:
                    return True
            return False

        def create_speed(self, tarif_id, nas_type):
            defaults = get_default_speed_parameters(self.cur, tarif_id)
            speeds = get_speed_parameters(self.cur, tarif_id)
            result=[]
            i=0
            for speed in speeds:
                if in_period(speed[0],speed[1],speed[2])==True:
                    for s in speed[3:]:
                        if s==0:
                            res=0
                        elif s=='' or s==None:
                            res=defaults[i]
                        else:
                            res=s
                        result.append(res)
                        i+=1
            if speeds==[]:
                result=defaults

            return create_speed_string(result, nas_type, coa=False)

        def check_acces(self):
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



            while True:
                self.cur = self.connection.cursor()
                time.sleep(self.timeout)
                self.cur.execute("""
                SELECT rs.id, rs.account_id, rs.sessionid, rs.nas_id, rs.date_start, rs.date_end, rs.speed_string, lower(rs.framed_protocol),
                nas.name, nas.secret, nas.support_pod, nas.login, nas.password, nas.type, nas.support_coa,
                account.username, (SELECT tarif_id FROM billservice_accounttarif WHERE datetime<now() and account.id=account_id LIMIT 1) as tarif_id, (ballance+credit) as ballance, account.disabled_by_limit
                FROM radius_activesession as rs
                JOIN nas_nas as nas ON nas.ipaddress=rs.nas_id
                JOIN billservice_account as account ON account.id=rs.account_id
                WHERE (rs.session_status='ACTIVE' and rs.date_end is null) or (rs.date_end is null and rs.session_status!='ACTIVE');
                """)
                rows=self.cur.fetchall()
                for row in rows:
                    activesession_id=row[0]
                    account_id=row[1]
                    session_id=row[2]
                    nas_id=row[3]
                    speed_string=row[6]
                    access_type=row[7]
                    nas_name = row[8]
                    nas_secret = row[9]
                    nas_support_pod =row[10]
                    nas_login =row[11]
                    nas_password =row[12]
                    nas_type = row[13]
                    nas_coa = row[14]
                    result=None
                    username=row[15]
                    tarif_id = row[16]
                    ballance=row[17]
                    disabled_by_limit=row[18]

                    if ballance>0:
                       if self.check_period(time_periods_by_tarif_id(self.cur, tarif_id))==False or disabled_by_limit==True:
                              result = DAE(dict=self.dict, code=40, nas_secret=nas_secret, nas_ip=nas_id, nas_id=nas_name, username=username, session_id=session_id, login=nas_login, password=nas_password)
                       else:
                           """
                           Делаем проверку на то, изменилась ли скорость.
                           """
                           speed=self.create_speed(tarif_id, nas_type)
                           #print speed, speed_string
                           if speed_string!=speed:

                               coa_result=DAE(dict=self.dict, code=43, nas_secret=nas_secret, coa=nas_coa, nas_ip=nas_id, nas_id=nas_name, username=username, session_id=session_id, login=nas_login, password=nas_password, access_type=access_type, speed_string=speed)
                               print "coa_result=", coa_result
                               if coa_result==True:
                                   self.cur.execute(
                                            """
                                            UPDATE radius_activesession
                                            SET speed_string='%s'
                                            WHERE id=%s;
                                            """ % (speed, activesession_id)
                                            )
                               continue
                    else:
                        result = DAE(dict=self.dict, code=40, nas_secret=nas_secret, nas_ip=nas_id, nas_id=nas_name, username=username, session_id=session_id,  login=nas_login, password=nas_password)

                    if result==True: 
                        disconnect_result='ACK'
                    elif result==False:
                        disconnect_result='NACK'

                    if result is not None:
                        self.cur.execute(
                        """
                        UPDATE radius_activesession SET session_status=%s WHERE sessionid=%s;
                        """, (disconnect_result, session_id)
                        )

                self.connection.commit()
                self.cur.close()

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
        connection = pool.connection()
        cur = connection.cursor()
        while True:
              cur.execute("UPDATE radius_activesession SET session_time=extract(epoch FROM date_end-date_start), date_end=interrim_update, session_status='NACK' WHERE ((now()-interrim_update>=interval '00:03:00') or (now()-date_start>=interval '00:03:00' and interrim_update is Null)) and date_end is Null;")
              #cur.execute("UPDATE radius_activesession SET session_time=extract(epoch FROM date_end-date_start) WHERE session_time is Null;")
              connection.commit()
              time.sleep(30)


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
        cur = connection.cursor()
        while True:
            # Количество снятий в сутки
            transaction_number=24
            n=(24*60*60)/transaction_number

            #выбираем список тарифных планов у которых есть периодические услуги
            cur.execute("SELECT id, settlement_period_id, ps_null_ballance_checkout  FROM billservice_tariff WHERE id in (SELECT tariff_id FROM billservice_tariff_periodical_services)")
            rows=cur.fetchall()
            #print "SELECT TP"
            #перебираем тарифные планы
            for row in rows:
                #print row
                tariff_id=row[0]
                settlement_period_id=row[1]
                null_ballance_checkout=row[2]
                # Получаем список аккаунтов на ТП
                cur.execute("""
                SELECT a.account_id, a.datetime::timestamp without time zone, (b.ballance+b.credit) as ballance
                FROM billservice_accounttarif as a
                LEFT JOIN billservice_account as b ON b.id=a.account_id
                WHERE datetime<now() and a.tarif_id='%s' and b.suspended=True
                """ % tariff_id)
                accounts=cur.fetchall()
                # Получаем параметры каждой перодической услуги в выбранном ТП
                cur.execute("""
                SELECT b.id, b.name, b.cost, b.cash_method, c.name, c.time_start::timestamp without time zone,
                c.length, c.length_in, c.autostart
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
                    length_ps=row_ps[6]
                    length_in_sp=row_ps[7]
                    autostart_sp=row_ps[8]

                    for account in accounts:
                        account_id = account[0]
                        account_datetime = account[1]
                        account_ballance = account[2]
                        # Если балланс>0 или разрешено снятие денег при отрицательном баллансе
                        if account_ballance>0 or (null_ballance_checkout==True and account_ballance<=0):
                            #Получаем данные из расчётного периода
                            if autostart_sp==True:
                               time_start_ps=account_datetime
                            # Если в расчётном периоде указана длина в секундах-использовать её, иначе использовать предопределённые константы
                            if length_ps>0:
                                repeat_after=length_ps
                            else:
                                repeat_after=length_in_sp
                            #print ps_name, length_in_sp
                            period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=repeat_after)
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
                                    last_checkout=account_datetime

                                if (now-last_checkout).seconds>=n:
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
                                    nums, ost=divmod(lc.seconds,n)
                                    if nums>0:
                                        #Смотрим на какую сумму должны были снять денег и снимаем её
                                        cash_summ=cash_summ*nums
                                    #print "delta", delta
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
                                # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                                # Для последней проводки ставим статус Approved=True
                                # для всех сотальных False
                                # Если последняя проводка меньше или равно дате начала периода-делаем снятие
                                if last_checkout<period_start or (last_checkout is None and account_datetime<period_start):
                                    lc=last_checkout-period_start
                                    nums, ost=divmod(lc.seconds, n)
                                    for i in xrange(nums-1):
                                        transaction_id = transaction(
                                        cursor=cur,
                                        account=account_id,
                                        approved=True,
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
                               last_checkout=get_last_checkout(cursor=cur, ps_id = ps_id, tarif = tariff_id, account = account_id)
                               # Здесь нужно проверить сколько раз прошёл расчётный период

                               # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                               # Для последней проводки ставим статус Approved=True
                               # для всех сотальных False
                               now=datetime.datetime.now()
                               # Если дата начала периода больше последнего снятия или снятий не было и наступил новый период - делаем проводки
                               # Выражение верно т.к. новая проводка совершится каждый раз только после после перехода
                               #в новый период.
                               if period_start>last_checkout or (last_checkout==None and now-datetime.timedelta(seconds=n)<=period_start):

                                    lc=last_checkout-period_start
                                    nums, ost=divmod((period_end-last_checkout).seconds, n)
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
            connection.commit()
            time.sleep(60)

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
        connection = pool.connection()
        cur = connection.cursor()
        while True:
            cur.execute("""
            SELECT rs.account_id, rs.sessionid, rs.session_time, rs.interrim_update::timestamp without time zone, tacc.id, tacc.name, tarif.id
            FROM radius_session as rs
            JOIN billservice_accounttarif as acc_t ON acc_t.account_id=rs.account_id
            JOIN billservice_tariff as tarif ON tarif.id=acc_t.tarif_id
            JOIN billservice_timeaccessservice as tacc ON tacc.id=tarif.time_access_service_id
            WHERE rs.checkouted_by_time=False and rs.date_start is NUll and acc_t.datetime<now() ORDER BY rs.interrim_update ASC;
            """)
            rows=cur.fetchall()

            for row in rows:

                account_id=row[0]
                session_id = row[1]
                session_time = row[2]
                interrim_update = row[3]
                ps_id=row[4]
                ps_name = row[5]
                tarif_id = row[6]
                #1. Ищем последнюю запись по которой была произведена оплата
                #2. Получаем данные из услуги "Доступ по времени" из текущего ТП пользователя
                #TODO:2. Проверяем сколько стоил трафик в начале сессии и не было ли смены периода.
                #TODO:2.1 Если была смена периода -посчитать сколько времени прошло до смены и после смены,
                # рассчитав соотв снятия.
                #2.2 Если снятия не было-снять столько, на сколько насидел пользователь
                cur.execute("""
                SELECT session_time FROM radius_session WHERE sessionid='%s' AND checkouted_by_time=True
                ORDER BY interrim_update DESC LIMIT 1
                """ % session_id)
                try:
                    old_time=cur.fetchone()[0]
                except:
                    old_time=0
                total_time=session_time-old_time

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
                            if summ>0:
                                transaction(
                                cursor=cur,
                                account=account_id,
                                approved=True,
                                tarif=tarif_id,
                                summ=summ,
                                description="Снятие денег за время по RADIUS сессии %s" % session_id,
                                )
                                #print u"Снятие денег за время %s" % query

                query="""
                UPDATE radius_session
                SET checkouted_by_time=True
                WHERE sessionid='%s'
                AND account_id='%s'
                AND interrim_update='%s'
                """ % (session_id, account_id, interrim_update)
                cur.execute(query)
                connection.commit()

            time.sleep(30)

##class TraficAccessBill(Thread):
##    """
##    Услуга применима только для VPN доступа, когда точно известна дата авторизации
##    и дата отключения пользователя
##    """
##    def __init__(self):
##        Thread.__init__(self)
##
##    def run(self):
##        """
##        По каждой записи делаем транзакции для польователя в соотв с его текущим тарифным планов
##        """
##        connection = pool.connection()
##        cur = connection.cursor()
##        while True:
##            now=datetime.datetime.now()
##            cur.execute("""
##            SELECT rs.account_id, rs.sessionid, rs.bytes_in,
##            rs.bytes_out, rs.interrim_update::timestamp without time zone,
##            tacc.id, tacc.name, tarif.id, rs.nas_id
##            FROM radius_session as rs
##            JOIN billservice_accounttarif as acc_t ON acc_t.account_id=rs.account_id
##            JOIN billservice_tariff as tarif ON tarif.id=acc_t.tarif_id
##            JOIN billservice_traffictransmitservice as tacc ON tacc.id=tarif.traffic_transmit_service_id
##            WHERE rs.checkouted_by_trafic=False and rs.date_start is NUll AND acc_t.datetime<now() ORDER BY rs.interrim_update ASC;
##            """)
##            rows=cur.fetchall()
##
##            for row in rows:
##                account_id=row[0]
##                session_id = row[1]
##                session_bytes_in = row[2]
##                session_bytes_out = row[3]
##                interrim_update = row[4]
##                ps_id=row[5]
##                ps_name = row[6]
##                tarif_id = row[7]
##                nas_id = row[8]
##
##                cur.execute(
##                """
##                SELECT traffic_transmit_service_id, settlement_period_id
##                FROM billservice_tariff
##                WHERE id=%s;
##                """ % tarif_id
##                )
##                res=cur.fetchone()
##                trafic_transmit_service_id=res[0]
##                settlement_period_id=res[1]
##
##                cur.execute(
##                """
##                SELECT statistic_mode FROM billservice_tariff WHERE id=%s;
##                """ % tarif_id
##                )
##                tarif_mode=cur.fetchone()[0]=='ACCOUNTING'
##                #1. Ищем последнюю запись по которой была произведена оплата
##                #2. Получаем данные из услуги "Доступ по трафику" из текущего ТП пользователя
##                #2. Проверяем сколько стоил трафик в начале сессии и не было ли смены периода.
##                #TODO:2.1 Если была смена периода -посчитать сколько времени прошло до смены и после смены,
##                # рассчитав соотв снятия.
##                #2.2 Если снятия не было-снять столько, на сколько насидел пользователь с начала сессии
##                cur.execute("""
##                SELECT bytes_in, bytes_out FROM radius_session WHERE sessionid='%s' AND checkouted_by_trafic=True
##                ORDER BY interrim_update DESC LIMIT 1
##                """ % session_id)
##                a=cur.fetchone()
##                try:
##                    old_bytes_in=a[0]
##                    old_bytes_out=a[1]
##                    cur.execute(
##                    """
##                    UPDATE billservice_summarytrafic
##                    SET incomming_bytes='%s', outgoing_bytes='%s', date_end='%s'
##                    WHERE account_id='%s' and radius_session='%s';
##                    """ % (total_bytes_in, total_bytes_out, now, account_id, session_id)
##                    )
##                except:
##                    old_bytes_in=0
##                    old_bytes_out=0
##                    cur.execute("""INSERT INTO billservice_summarytrafic(
##                                account_id, tarif_id, nas_id,
##                                radius_session, date_start)
##                                VALUES ('%s', '%s', (SELECT id FROM nas_nas WHERE ipaddress='%s'), '%s', '%s')""" % (account_id, tarif_id, nas_id,session_id,now)
##                                )
##
##
##                total_bytes_in=session_bytes_in-old_bytes_in
##                total_bytes_out=session_bytes_out-old_bytes_out
##                in_octets_summ=0
##                out_octets_summ=0
##                #Производим вычисления для дифференциализации оплаты трафика
##                #Если в тарифном плане указан расчётный период
##                if settlement_period_id:
##                    cur.execute(
##                                """
##                                SELECT time_start::timestamp without time zone, length_in, autostart FROM billservice_settlementperiod WHERE id=%s;
##                                """ % settlement_period_id
##                                )
##
##                    settlement_period=cur.fetchone()
##                    if settlement_period is not None:
##                        sp_time_start=settlement_period[0]
##                        sp_length=settlement_period[1]
##
##                        if settlement_period[2]==False:
##                            # Если у расчётного периода стоит параметр Автостарт-за началшо расчётногопериода принимаем
##                            # дату привязки тарифного плана пользователю
##                            cur.execute("""
##                                SELECT a.datetime::timestamp without time zone
##                                FROM billservice_accounttarif as a
##                                LEFT JOIN billservice_account as b ON b.id=a.account_id
##                                WHERE datetime<'%s' WHERE a.account_id=%s
##                                """ % (stream_date, account_id))
##                            sp_time_start=cur.fetchone()[0]
##
##                        settlement_period_start, settlement_period_end, deltap = settlement_period_info(time_start=sp_time_start, repeat_after=sp_length, now=interrim_update)
##                        # Смотрим сколько уже наработал за текущий расчётный период по этому тарифному плану
##                        cur.execute(
##                        """
##                        SELECT sum(incomming_bytes), sum(outgoing_bytes)
##                        FROM billservice_summarytrafic
##                        WHERE account_id=%s and tarif_id=%s and date_start between '%s' and '%s'
##                        """ % (account_id, tarif_id, settlement_period_start, settlement_period_end)
##                        )
##                        in_octets_summ, out_octets_summ=cur.fetchone()
##
##                # Получаем список временных периодов и их стоимость у периодической услуги
##                cur.execute(
##                """
##                SELECT tc.weight, tn.cost, tn.edge_start, tn.edge_end, tnp.timeperiod_id, tc.id
##                FROM billservice_traffictransmitnodes as tn
##                JOIN nas_trafficclass as tc ON tc.id=tn.traffic_class_id
##                JOIN billservice_traffictransmitnodes_time_period as tnp ON tnp.traffictransmitnodes_id=tn.id
##                JOIN billservice_traffictransmitservice_traffic_nodes as tts ON tts.traffictransmitnodes_id=tn.id
##                WHERE tts.traffictransmitservice_id=%s and (tc.weight=100 or tc.weight=200)
##                """ % ps_id
##                )
##                periods=cur.fetchall()
##                for period in periods:
##                    tc_weight=period[0]
##                    traffic_cost=period[1]
##                    trafic_edge_start=period[2]
##                    trafic_edge_end=period[3]
##                    period_id=period[4]
##                    class_id=period[5]
##
##                    #получаем данные из периода чтобы проверить попала в него сессия или нет
##                    cur.execute(
##                    """
##                    SELECT tpn.id, tpn.name, tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
##                    FROM billservice_timeperiodnode as tpn
##                    JOIN billservice_timeperiod_time_period_nodes as tptpn ON tpn.id=tptpn.timeperiodnode_id
##                    WHERE tptpn.timeperiod_id=%s
##                    """ % period_id
##                    )
##                    period_nodes_data=cur.fetchall()
##                    for period_node in period_nodes_data:
##                        period_id=period_node[0]
##                        period_name = period_node[1]
##                        period_start = period_node[2]
##                        period_length = period_node[3]
##                        repeat_after = period_node[4]
##                        if in_period(time_start=period_start,length=period_length, repeat_after=repeat_after):
##                            #in_octets_summ, out_octets_summ
##                            if (tc_weight==100 and tarif_mode) and ((in_octets_summ>=trafic_edge_start and in_octets_summ<=trafic_edge_end) or (trafic_edge_start==0 and trafic_edge_end==0) or (trafic_edge_start==0 and in_octets_summ<=trafic_edge_start) or (in_octets_summ>=trafic_edge_start and trafic_edge_start==0)):
##                                #Входяший
##                                #Относительно клиента
##                                summ=(float(total_bytes_in)/(1024*1024))*traffic_cost
##                                if summ>0 and tarif_mode:
##                                    transaction(
##                                    cursor=cur,
##                                    account=account_id,
##                                    approved=True,
##                                    tarif=tarif_id,
##                                    summ=summ,
##                                    description="Снятие денег за входящий трафик по RADIUS сессии %s" % session_id,
##                                    )
##                                    print 'bytes_in checkout'
##                            elif (tc_weight==200 and tarif_mode) and ((out_octets_summ>=trafic_edge_start and out_octets_summ<=trafic_edge_end) or (trafic_edge_start==0 and trafic_edge_end==0) or (trafic_edge_start==0 and out_octets_summ<=trafic_edge_start) or (out_octets_summ>=trafic_edge_start and trafic_edge_start==0)):
##                                #Исходящий Относительно клиента
##                                summ=(float(total_bytes_out)/(1024*1024))*traffic_cost
##                                if summ>0:
##                                    transaction(
##                                        cursor=cur,
##                                        account=account_id,
##                                        approved=True,
##                                        tarif=tarif_id,
##                                        summ=summ,
##                                        description="Снятие денег за исходящий трафик по RADIUS сессии %s" % session_id,
##                                        )
##                                    print 'bytes_out checkout'
##
##
##
##                query="""
##                UPDATE radius_session
##                SET checkouted_by_trafic=True
##                WHERE sessionid='%s'
##                AND account_id='%s'
##                AND interrim_update='%s'
##                """ % (session_id, account_id, interrim_update)
##                cur.execute(query)
##
##
##                connection.commit()
##            time.sleep(30)

class NetFlowAggregate(Thread):
    """
    TO-DO: Вынести в NetFlow коллектор
    """
    """
    Алгоритм для агрегации трафика:
    Формируем таблицу с агрегированным трафиком

    1. Берём строку из netflowstream_raw
    2. Смотрим есть ли похожая строка в netflowstream за последнюю минуту-полторы и не производилось ли по ней списание.
    2.1 Если есть и списание не производилось-суммируем количество байт
    2.2 Если есть и списание производилось или если нет -пишем новую строку
    3. УДаляем из netflowstream_raw строку или помечаем, что он адолжна быть удалена.

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
        connection = pool.connection()
        cur = connection.cursor()
        while True:
            cur.execute(
            """
            SELECT nf.id, ba.id,
            tariff.id, nf.nas_id, nf.date_start, nf.src_addr, nf.traffic_class_id,
            nf.dst_addr, nf.octets, nf.src_port, nf.dst_port, nf.protocol, tariff.id, 
            tariff.traffic_transmit_service_id, trafficclass.store
            FROM billservice_rawnetflowstream as nf
            LEFT JOIN billservice_account as ba ON ba.virtual_ip_address=nf.src_addr OR ba.virtual_ip_address=nf.dst_addr OR ba.ipn_ip_address=nf.src_addr OR ba.ipn_ip_address=nf.dst_addr
            JOIN billservice_accounttarif as account_tariff ON account_tariff.id=(SELECT id FROM billservice_accounttarif as at WHERE at.account_id=ba.id and at.datetime<nf.date_start ORDER BY datetime DESC LIMIT 1)
            JOIN billservice_tariff as tariff ON tariff.id=account_tariff.tarif_id
            JOIN nas_trafficclass as trafficclass ON trafficclass.id=nf.traffic_class_id
            WHERE nf.fetched=False;
            """
            )
            raw_streams=cur.fetchall()
            """
            Берём строку, ищем пользователя, у которого адрес совпадает или с dst или с src.
            Если сервер доступа в тарифе подразумевает обсчёт сессий через NetFlow помечаем строку "для обсчёта"

            """

            for stream in raw_streams:
                tarif_id=stream[12]
                traffic_transmit_service=stream[13]
                store=stream[14]
                tarif_mode=False
                account_id=stream[1]
                tarif_id=stream[2]
                
                if traffic_transmit_service:

                #Выбираем временыне интервалы из услуги по трафику
                    cur.execute(
                    """
                    SELECT tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
                    FROM billservice_timeperiodnode as tpn
                    JOIN billservice_traffictransmitnodes_time_nodes as ttntp ON ttntp.timeperiodnode_id=tpn.id
		            JOIN billservice_traffictransmitnodes as ttns ON ttns.id=ttntp.traffictransmitnodes_id
                    WHERE ttns.traffic_transmit_service_id=%s
                    """ % traffic_transmit_service
                    )

                    periods=cur.fetchall()
                    #Нужно ли списывать деньги за этот трафик
                    tarif_mode=self.check_period(periods)
                    
                if account_id is not None:
                    # Если пользователь
                    cur.execute(
                    """
                    SELECT id
                    FROM billservice_netflowstream
                    WHERE nas_id='%s' and account_id=%s and
                    tarif_id=%s and
                    '%s' - date_start < interval '00:01:40' and
                    src_addr='%s' and traffic_class_id='%s' and
                    dst_addr='%s' and
                    src_port='%s' and
                    dst_port='%s' and
                    protocol='%s' and
                    checkouted=False and
                    for_checkout='%s' ORDER BY id DESC LIMIT 1
                    """ % (stream[3], account_id, tarif_id, stream[4], stream[5], stream[6], stream[7],stream[9], stream[10],stream[11], tarif_mode)
                    )
                    row_for_update=cur.fetchone()
                    if row_for_update:
                        print 'updating'
                        cur.execute(
                        """
                        UPDATE billservice_netflowstream SET octets=octets+%s WHERE id=%s
                        """ % (stream[8], stream[0])
                        )
                    else:
                        print 'inserting'
                        cur.execute(
                        """
                        INSERT INTO billservice_netflowstream(
                        nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id,
                        dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                        VALUES ('%s', '%s', '%s', '%s', '%s', '%s',
                        '%s', '%s', '%s', '%s', '%s', '%s', '%s');
                        """ % (stream[3], account_id, tarif_id, stream[4],stream[5], stream[6], stream[7],stream[8],stream[9], stream[10], stream[11], False, tarif_mode)
                        )


                    cur.execute(
                    """
                    DELETE FROM billservice_rawnetflowstream WHERE id=%s
                    """ % stream[0]
                    )
                else:
                    cur.execute(
                    """
                    UPDATE billservice_rawnetflowstream SET fetched=True WHERE id=%s
                    """ % stream[0]
                    )                    
            connection.commit()
            time.sleep(60)


class NetFlowBill(Thread):
    """
    WHILE TRUE
    берём строки с for_checkout=True и checkouted=False и по каждой строке производим начисления
    timeout(120 seconds)

    """

    def __init__(self):
        Thread.__init__(self)

    def get_actual_cost(self, cur, trafic_transmit_service_id, traffic_class_id, octets_summ, stream_date):
        """
        Метод возвращает актуальную цену для направления трафика для пользователя:
        
        """
        cur.execute(
        """
        SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
        FROM billservice_traffictransmitnodes as ttsn
        JOIN billservice_traffictransmitnodes_traffic_class as tcn ON tcn.traffictransmitnodes_id=ttsn.id
        JOIN billservice_traffictransmitnodes_time_nodes as tns ON tns.traffictransmitnodes_id=ttsn.id
        JOIN billservice_timeperiodnode AS tpn on tpn.id=timeperiodnode_id
        WHERE ((ttsn.edge_start>=%s and ttsn.edge_end<=%s) or (ttsn.edge_start>=%s and ttsn.edge_end=0 ) ) and ttsn.traffic_transmit_service_id=%s and tcn.trafficclass_id=%s;
        """ % (octets_summ,octets_summ,octets_summ,trafic_transmit_service_id, traffic_class_id)
        )

        trafic_transmit_nodes=cur.fetchall()
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
                if from_start<min_from_start or min_from_start==0:
                    min_from_start=from_start
                    cost=trafic_cost
        return cost


    def run(self):
        connection = pool.connection()
        cur = connection.cursor()

        while True:
            cur.execute(
            """
            SELECT nf.id, nf.account_id, nf.tarif_id, nf.date_start::timestamp without time zone, nf.traffic_class_id, nf.octets, bs_acc.username, traficclass.direction
            FROM billservice_netflowstream as nf
            JOIN billservice_account as bs_acc ON bs_acc.id=nf.account_id
            JOIN nas_trafficclass as traficclass ON traficclass.id=nf.traffic_class_id
            WHERE for_checkout=True and checkouted=False;
            """
            )
            rows=cur.fetchall()
            for row in rows:
                nf_id=row[0]
                account_id=row[1]
                tarif_id=row[2]
                stream_date=row[3]
                traffic_class_id=row[4]
                octets=row[5]
                username=row[6]
                nf_direction=row[7]
                s=False
                cur.execute(
                """
                SELECT tarif.traffic_transmit_service_id, tarif.settlement_period_id, transmitservice.cash_method, transmitservice.period_check
                FROM billservice_tariff as tarif
                JOIN billservice_traffictransmitservice as transmitservice ON transmitservice.id=tarif.traffic_transmit_service_id
                WHERE tarif.id=%s;
                """ % tarif_id
                )
                res=cur.fetchone()
                trafic_transmit_service_id=res[0]
                settlement_period_id=res[1]
                cash_method=res[2]
                period_check=res[3]

                if trafic_transmit_service_id:
                    #Если в тарифном плане указан расчётный период
                    if settlement_period_id:
                        cur.execute(
                        """
                        SELECT time_start::timestamp without time zone, length_in, autostart FROM billservice_settlementperiod WHERE id=%s;
                        """ % settlement_period_id
                        )
                        settlement_period=cur.fetchone()
                        if settlement_period is not None:
                            sp_time_start=settlement_period[0]
                            sp_length=settlement_period[1]

                        if settlement_period[2]==False:
                            # Если у расчётного периода стоит параметр Автостарт-за начало расчётного периода принимаем
                            # дату привязки тарифного плана пользователю
                            cur.execute("""
                                SELECT a.datetime::timestamp without time zone
                                FROM billservice_accounttarif as a
                                LEFT JOIN billservice_account as b ON b.id=a.account_id
                                WHERE datetime<'%s' WHERE a.account_id=%s
                                """ % (stream_date, account_id))
                            sp_time_start=cur.fetchone()[0]

                        settlement_period_start, settlement_period_end, deltap = settlement_period_info(time_start=sp_time_start, repeat_after=sp_length, now=stream_date)
                        # Смотрим сколько уже наработал за текущий расчётный период по этому тарифному плану
                        cur.execute(
                            """
                            SELECT sum(octets)
                            FROM billservice_netflowstream
                            WHERE tarif_id=%s and account_id=%s and checkouted=True and date_start between '%s' and '%s'
                            """ % ( tarif_id, account_id, settlement_period_start, settlement_period_end)
                            )
                        octets_summ=cur.fetchone()[0]
                    else:
                        octets_summ=0

                trafic_cost=self.get_actual_cost(cur,trafic_transmit_service_id, traffic_class_id, octets_summ, stream_date)
                """
                Использован т.н. дифференциальный подход к начислению денег за трафик
                Тарифный план позволяет указать по какой цене считать трафик
                в зависимости от того сколько этого трафика уже накачал пользователь за расчётный период
                """
                print 1
                if cash_method=="MAX":
                    print 2
                    if period_check=="SP_START" and settlement_period_id:
                        print 3
                        """
                        Если в тарифном плане указан расчётный период.
                        Находим направление по которому больше всего скачал этот пользователь с начала расчтного периода
                        если совпало-снимаем деньги.
                        """
                        cur.execute(
                            """
                            SELECT sum(octets)
                            FROM billservice_netflowstream as netflowstream, nas_trafficclass as trafficclass
                            WHERE  trafficclass.id=netflowstream.traffic_class_id and trafficclass.direction="OUTPUT" and tarif_id=%s and account_id=%s and date_start between '%s' and '%s'
                            GROUP BY direction
                            """ % ( tarif_id, account_id, settlement_period_start, settlement_period_end)
                            )
                        output=cur.fetchone()[0]
                        
                        cur.execute(
                            """
                            SELECT sum(octets)
                            FROM billservice_netflowstream as netflowstream, nas_trafficclass as trafficclass
                            WHERE  trafficclass.id=netflowstream.traffic_class_id and trafficclass.direction="INPUT" and tarif_id=%s and account_id=%s and date_start between '%s' and '%s'
                            GROUP BY direction
                            """ % ( tarif_id, account_id, settlement_period_start, settlement_period_end)
                            )
                        input=cur.fetchone()[0]
                        
                        #s = nf_direction == max(input,output) and True or False
                        if (input>output and nf_direction=='INPUT') or (input<output and nf_direction=='OUTPUT'): 
                            s=True
                            print 4
                            
                        
                    elif period_check=="AG_START":
                        print 5
                        """
                        Находим направление по которому больше всего скачал этот пользователь за текущую агрегацию
                        если совпало-снимаем деньги.
                        """

                        cur.execute(
                            """
                            SELECT sum(octets)
                            FROM billservice_netflowstream as netflowstream, nas_trafficclass as trafficclass
                            WHERE  trafficclass.id=netflowstream.traffic_class_id and trafficclass.direction="OUTPUT" and tarif_id=%s and account_id=%s and checkouted=False
                            GROUP BY direction
                            """ % ( tarif_id, account_id)
                            )
                        output=cur.fetchone()[0]
                        
                        cur.execute(
                            """
                            SELECT sum(octets)
                            FROM billservice_netflowstream as netflowstream, nas_trafficclass as trafficclass
                            WHERE  trafficclass.id=netflowstream.traffic_class_id and trafficclass.direction="INPUT" and tarif_id=%s and account_id=%s and checkouted=False
                            GROUP BY direction
                            """ % ( tarif_id, account_id)
                            )
                        input=cur.fetchone()[0]
                        
                        #s = nf_direction == max(input,output) and True or False
                        if (input>output and nf_direction=='INPUT') or (input<output and nf_direction=='OUTPUT'): 
                            s=True
                            print 6
                else:
                    s=None       
                    print 7     
                       
                    
                summ=(trafic_cost*octets)/(1024*1024)
                if summ>0 and (s==True or s==None):
                    #Производим списывание денег
                    transaction(
                    cursor=cur,
                    account=account_id,
                    approved=True,
                    tarif=tarif_id,
                    summ=summ,
                    description=u"Снятие денег за трафик у пользователя %s" % username,
                    )

                cur.execute(
                """
                UPDATE billservice_netflowstream
                SET checkouted=True
                WHERE id=%s;
                """ % nf_id
                )


            connection.commit()
            time.sleep(120)

class limit_checker(Thread):
    """
    Проверяет исчерпание лимитов. если лимит исчерпан-ставим соотв галочку в аккаунте
    """
    def __init__ (self):
        Thread.__init__(self)

    def run(self):
        connection = pool.connection()
        cur = connection.cursor()
        while True:
            """
            Выбираем тарифные планы, у которых есть лимиты
            """
            cur.execute(
            """
            SELECT tarif.id, account.id, acctt.datetime, sp.time_start, sp.length, sp.length_in, sp.autostart
            FROM billservice_tariff as tarif
            JOIN billservice_accounttarif as acctt ON acctt.tarif_id=tarif.id and acctt.datetime=(SELECT datetime FROM billservice_accounttarif WHERE account_id=acctt.account_id and datetime<now() ORDER BY datetime DESC LIMIT 1)
            JOIN billservice_account as account ON account.id=acctt.account_id
            JOIN billservice_tariff_traffic_limit as ttl ON ttl.tariff_id=tarif.id
            LEFT JOIN billservice_settlementperiod as sp ON sp.id=tarif.settlement_period_id
            WHERE account.status='Enabled' ORDER BY account.id ASC;
            """
            )
            account_tarifs=cur.fetchall()
            oldid=-1
            for account_tarif in account_tarifs:
                tarif_id=account_tarif[0]
                account_id=account_tarif[1]
                tarif_start=account_tarif[2]
                tarif_sp_start=account_tarif[3]
                tarif_sp_length=account_tarif[4]
                tarif_sp_length_in=account_tarif[5]
                tarif_autostart_sp=account_tarif[6]

                if oldid==account_id and block:
                    """
                    Если у аккаунта уже есть одно превышение лимита
                    то больше для него лимиты не проверяем
                    """
                    continue
                #Выбираем лимит для аккаунта
                cur.execute(
                """
                SELECT ttl.trafficlimit_id, tl.size, tl.mode, sp.time_start, sp.length, sp.length_in, sp.autostart
                FROM billservice_tariff_traffic_limit as ttl
                JOIN billservice_trafficlimit as tl ON tl.id=ttl.trafficlimit_id
                LEFT JOIN billservice_settlementperiod as sp ON sp.id=tl.settlement_period_id
                WHERE ttl.tariff_id=%s;
                """ % tarif_id
                )
                limit=cur.fetchone()
                limit_id, limit_size, limit_mode, sp_time_start, sp_length, sp_length_in, autostart_sp=limit
                if tarif_sp_length:
                    st_tarif_period_length=tarif_sp_length
                elif tarif_sp_length_in:
                    st_tarif_period_length=tarif_sp_length_in

                if sp_length:
                    settlement_period_length=sp_length
                else:
                    settlement_period_length=sp_length_in

                #Если в лимите указан период
                autostart_sp, tarif_autostart_sp
                if autostart_sp!=None:
                    period_length=settlement_period_length
                    if autostart_sp==True:
                        settlement_period_start=tarif_start

                    elif autostart_sp==False:
                        period_start=sp_time_start
                #иначе берём данные о расчётном периоде из тарифного плана
                elif tarif_autostart_sp:
                    period_length=st_tarif_period_length
                    if tarif_autostart_sp==True:
                        settlement_period_start=tarif_start
                    elif tarif_autostart_sp==False:
                        settlement_period_start=sp_time_start
                else:
                    #если и там не указан-пропускаем цикл
                    continue

                settlement_period_start, settlement_period_end, delta = settlement_period_info(time_start=settlement_period_start, repeat_after=period_length, now=datetime.datetime.now())
                #если нужно считать количество трафика за последнеие N секунд, а не за рачётный период, то переопределяем значения
                if limit_mode==True:
                    settlement_period_start=datetime.datetime.now()-datetime.timedelta(seconds=delta)
                    settlement_period_end=datetime.datetime.now()
                block=False

                """
                Так как методы хранения нетфлоу и радиус статистики отличаются,
                то делаем проверку и выбираем данные из нужной в каждом случае таблицы
                """
                cur.execute(
                """
                SELECT
                (SELECT sum(octets) as s FROM billservice_netflowstream
                WHERE traffic_class_id=tcl.id and account_id=%s and date_start>'%s' and date_start<'%s') as size
                FROM billservice_trafficlimit_traffic_class as tc
                JOIN nas_trafficclass as tcl ON tcl.id=tc.trafficclass_id
                JOIN nas_trafficclass_trafficnode as tctn ON tctn.trafficclass_id=tc.trafficclass_id
                JOIN nas_trafficnode as tn ON tn.id=tctn.trafficnode_id
                WHERE tc.trafficlimit_id=%s
                """ % (account_id, settlement_period_start, settlement_period_end, limit_id)
                )
                tsize=0
                sizes=cur.fetchall()

                for size in sizes:
                    if size[0]!=None:
                        tsize+=size[0]

                if tsize>limit_size*1024:
                   block=True


                oldid=account_id
                #пишем в базу состояние пользователя
                cur.execute(
                """
                UPDATE billservice_account
                SET disabled_by_limit=%s
                WHERE id=%s;
                """ % (block, account_id)
                )


            time.sleep(10)


class service_dog(Thread):
    """
    Для каждого пользователя по тарифному плану в конце расчётного периода производит
    1. Доснятие суммы
    2. Сброс предоплаченного времени (не сделано)
    3. Сброс предоплаченного трафика (не сделано)
    алгоритм
    1. выбираем всех пользователей с текущими тарифными планами,
    у которых указан расчётный период и галочка "делать доснятие"
    2. Считаем сколько денег было взято по транзакциям.
    3. Если сумма меньше цены тарифного плана-делаем транзакцию, в которой снимаем деньги.
    """
    def __init__ (self):
        Thread.__init__(self)

    def run(self):
        connection = pool.connection()
        cur = connection.cursor()
        while True:
              #cur.execute("UPDATE radius_activesession SET date_end=interrim_update, session_status='NACK' WHERE now()-interrim_update>= interval '00:03:00' and date_end is Null;")
              #cur.execute("UPDATE radius_activesession SET session_time=extract(epoch FROM date_end-date_start) WHERE session_time is Null;")
              time.sleep(10)

class ipn_service(Thread):
    """
    Тред должен:
    1. Проверять не изменилась ли скорость для IPN клиентов и меня её на сервере доступа
    2. Если балланс клиента стал меньше 0 - отключать, если уже не отключен (параметр ipn_status в account) и включать, если отключен (ipn_status) и баланс стал больше 0
    3. Если клиент вышел за рамки разрешённого временного диапазона в тарифном плане-отключать 
    """
    def __init__ (self):
        Thread.__init__(self)
        self.connection = pool.connection()
        self.cur = connection.cursor()
        
    def check_period(self, rows):
        for row in rows:
            if in_period(row[0],row[1],row[2])==True:
                return True
        return False

    def create_speed(self, tarif_id, nas_type):
        defaults = get_default_speed_parameters(self.cur, tarif_id)
        speeds = get_speed_parameters(self.cur, tarif_id)
        result=[]
        i=0
        for speed in speeds:
            if in_period(speed[0],speed[1],speed[2])==True:
                for s in speed[3:]:
                    if s==0:
                        res=0
                    elif s=='' or s==None:
                        res=defaults[i]
                    else:
                        res=s
                    result.append(res)
                    i+=1
        if speeds==[]:
            result=defaults

        return create_speed_string(result, nas_type, coa=False)


    def run(self):

        while True:
            cur.execute(
                        """
                        SELECT account.id, account.username, account.ipn_ip_address, account.ipn_mac_address, 
                            (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
                            account.ipn_status, tariff.id,
                            nas."type", nas.user_enable_action, nas.user_disable_action, nas."login", nas."password", nas."ipaddress",
                            accessparameters.access_type, accessparameters.access_time_id, ipn_speed.speed, ipn_speed.static, ipn_speed.state
                        FROM billservice_account as account
                        JOIN billservice_accounttarif as accounttarif on accounttarif.id=(SELECT id FROM billservice_accounttarif WHERE account_id=account.id and datetime<now() ORDER BY datetime DESC LIMIT 1)
                        JOIN billservice_tariff as tariff ON tariff.id=accounttarif.tarif_id
                        JOIN billservice_accessparameters as accessparameters ON accessparameters.id=tariff.access_parameters_id
                        JOIN nas_nas as nas ON nas.id=accessparameters.nas_id
                        LEFT JOIN billservice_accountipnspeed as ipn_speed ON ipn_speed.account_id=account.id
                        WHERE account.status='Enabled' and accessparameters.access_type='IPN'
                        ;
                        """
                        )
            rows=cur.fetchall()
            for row in rows:
                account_id = row[0]
                account_username = row[1]
                account_ipaddress = row[2]
                account_mac = row[3]
                account_ballance=row[4]
                account_disabled_by_limit=row[5]
                account_ipn_status=row[6]
                tarif_id=row[7]
                nas_type=row[8]
                nas_user_enable=row[9]
                nas_user_disable=row[10]
                nas_login=row[11]
                nas_password=row[12]
                nas_ipaddress=row[13]
                access_type=row[14]
                access_time_id=row[15]
                ipn_speed=row[16]
                ipn_static=row[17]
                ipn_state=row[18]
                allow=None
               
                period=self.check_period(time_periods_by_tarif_id(cur, tarif_id))

                if account_ballance>0 and period==True and account_ipn_status==False:
                    #шлём команду, на включение пользователя, account_ipn_status=True
                    allow=True                  
                elif (account_disabled_by_limit==True or account_ballance<=0 or period==False) and account_ipn_status==True:
                    #шлём команду на отключение пользователя,account_ipn_status=False
                    allow=False
                
               
                speed=self.create_speed(tarif_id, nas_type)
                if speed!=ipn_speed and ipn_static==False:
                    #отправляем на сервер доступа новые настройки скорости, помечаем state=True
                    pass
                elif speed!=ipn_speed and ipn_static==True and ipn_state==False:
                    #отправляем на сервер доступа настройки скорости, помечаем state True
                    pass

                if allow==True:
                    #шлём разрешающий запрос
                    pass
                
                if allow==False:
                    #шлём запрещающий запрос
                    pass
                
                
            self.connection.commit()   
            time.sleep(60)
              
if __name__ == "__main__":

    dict=dictionary.Dictionary("dicts/dictionary","dicts/dictionary.microsoft","dicts/dictionary.rfc3576")
#===============================================================================
    cas = check_vpn_access(timeout=60, dict=dict)
    cas.start()

#    traficaccessbill = TraficAccessBill()
#    traficaccessbill.start()

    psb=periodical_service_bill()
    psb.start()

    time_access_bill = TimeAccessBill()
    time_access_bill.start()

    nfagg=NetFlowAggregate()
    nfagg.start()

    nfbill=NetFlowBill()
    nfbill.start()

    sess_dog=session_dog()
    sess_dog.start()

    lmch=limit_checker()
    lmch.start()
#===============================================================================
