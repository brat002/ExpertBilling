#-*-coding=utf-8-*-
import psycopg2
import time
from utilites import disconnect, settlement_period_info
import dictionary
from threading import Thread
from utilites import in_period

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect("dbname='mikrobill' user='mikrobill' host='localhost' password='1234'")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
except:
    print "I am unable to connect to the database"

class check_access(Thread):
        def __init__ (self, dict, timeout=30):
            self.dict=dict
            self.timeout=timeout
            Thread.__init__(self)
            
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
            
            while True:
                time.sleep(self.timeout)
                cur.execute("SELECT account_id, sessionid, nas_id FROM radius_session WHERE date_end is Null;")
                rows=cur.fetchall()
                for row in rows:
                    account_id=row[0]
                    session_id=row[1]
                    nas_id=row[2]
                    
                    cur.execute("SELECT name, secret from nas_nas WHERE ipaddress='%s'" % nas_id)
                    row_n=cur.fetchone()
                    nas_name = row_n[0]
                    nas_secret = row_n[1]
                    

                    cur.execute("SELECT username, tarif_id, ballance FROM billservice_account WHERE id='%s'" % account_id)
                    rows_u = cur.fetchall()
                    for row_u in rows_u:
                        username=row_u[0]
                        tarif_id = row_u[1]
                        ballance=row_u[2]
                        if ballance>0:
                           #Информация для проверки периода
                           cur.execute("""SELECT time_start, length, repeat_after FROM billservice_timeperiodnode WHERE id=(SELECT  timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id=(SELECT access_time_id FROM billservice_tariff WHERE id='%s'))""" % tarif_id)
                           rows_t=cur.fetchall()
                           for row_t in rows_t:
                               if in_period(row_t[0],row_t[1],row_t[2])==False:
                                  print disconnect(dict=self.dict, code=40, nas_secret=nas_secret, nas_ip=nas_id, nas_id=nas_name, username=username, session_id=session_id)
                               
                        else:
                               print disconnect(dict=self.dict, code=40, nas_secret=nas_secret, nas_ip=nas_id, nas_id=nas_name, username=username, session_id=session_id)
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
        cur.execute("UPDATE radius_session SET date_end=interrim_update WHERE interrim_update-date_start>= interval '00:01:00' and date_end is Null;")


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
        while True:
            # Количество снятий в неделю
            transaction_number=7
            n=(24*60*60*7)/transaction_number
            time.sleep(n)
            #выбираем список тарифных планов у которых есть периодические услуги
            cur.execute("SELECT id, settlement_period_id  FROM billservice_tariff WHERE id in (SELECT tariff_id FROM billservice_tariff_periodical_services)")
            rows=cur.fetchall()
            #перебираем тарифные планы
            for row in rows:
                tariff_id=row[0]
                settlement_period_id=row[1]
                # Получаем список аккаунтов на ТП
                cur.execute("""
                SELECT a.account_id, a.datetime, b.ballance FROM billservice_accounttarif as a
                LEFT JOIN billservice_account as b ON b.id=a.account_id
                WHERE datetime<now() and a.tarif_id='%s'
                """ % tariff_id)
                accounts=cur.fetchall()
                # Получаем параметры каждой перодической услуги в выбранном ТП
                cur.execute("""
                SELECT b.id, b.name, b.cost,b.cash_method FROM billservice_tariff_periodical_services as p
                JOIN billservice_periodicalservice as b ON p.periodicalservice_id=b.id
                WHERE p.tariff_id='%s'
                """ % tariff_id)
                rows_ps=cur.fetchall()
                # По каждой периодической услуге делаем списания для каждого аккаунта
                for row_ps in rows_ps:
                    ps_id = row[0]
                    ps_name = row[1]
                    ps_cost = row[2]
                    ps_cash_method = row[3]
                    for account in accounts:
                        account_id = account[0]
                        account_datetime = account[1]
                        account_ballance = account[2]
                        if ps_cash_method=="GRADUAL":
                            """
                            TO-DO:
                            Проверяем вместится ли ещё один временной промежуток снятия до конца
                            расчётного периода. Если не влезет-смотрим сколько уже денег сняли
                            и считаем оставшуюся для снятия сумму. Иначе снимает очередную порцию.
                            """
                            #Получаем данные из расчётного периода
                            cur.execute("SELECT name, time_start, length, length_in, autostart FROM billservice_settlementperiod WHERE id='%s'" % settlement_period_id)
                            row_sp=cur.fetchall()
                            name_sp=row[0]
                            time_start_ps=row[1]
                            length_sp=row[2]
                            length_id_sp=row[3]
                            autostart_sp=row[4]
                            if autostart_sp==True:
                                time_start_ps=account_datetime
                            period_start, period_end, delta = settlement_period_info(time_start_ps, length_in)

                            cash_summ=(float(ps_cost)/float(delta))/float()
                            
        
        
        
        
dict=dictionary.Dictionary("dicts\dictionary","dicts\dictionary.microsoft","dicts\dictionary.rfc3576")
cas = check_access(timeout=10, dict=dict)
cas.start()

sess_dog = session_dog()
sess_dog.start()

#check_access()