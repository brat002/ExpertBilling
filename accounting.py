#-*-coding=utf-8-*-
import psycopg2
import time, datetime
from utilites import disconnect, settlement_period_info
import dictionary
from threading import Thread
from utilites import in_period
import logging
import logging.config
import time
import os


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
            transaction_number=24
            n=(24*60*60)/transaction_number
            #time.sleep(n)
            
            #выбираем список тарифных планов у которых есть периодические услуги
            cur.execute("SELECT id, settlement_period_id  FROM billservice_tariff WHERE id in (SELECT tariff_id FROM billservice_tariff_periodical_services)")
            rows=cur.fetchall()
            print "SELECT TP"
            #перебираем тарифные планы
            for row in rows:
                print row
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
                SELECT b.id, b.name, b.cost, b.cash_method, c.name, c.time_start, c.length_in, c.autostart FROM billservice_tariff_periodical_services as p
                JOIN billservice_periodicalservice as b ON p.periodicalservice_id=b.id
		        JOIN billservice_settlementperiod as c ON c.id=b.settlement_period_id
                WHERE p.tariff_id='%s'
                """ % tariff_id)
                rows_ps=cur.fetchall()
                # По каждой периодической услуге делаем списания для каждого аккаунта
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
                        print ps_name, length_in_sp
                        period_start, period_end, delta = settlement_period_info(time_start_ps, length_in_sp)

                        if ps_cash_method=="GRADUAL":
                            """
                        # Смотрим сколько расчётных периодов закончилось со времени последнего снятия
                        # Если закончился один-снимаем всю сумму, указанную в периодической услуге
                        # Если закончилось более двух-значит в системе был сбой. Делаем последнюю транзакцию
                        # а остальные помечаем неактивными и уведомляем администратора
                            """
                            cur.execute("SELECT datetime FROM billservice_periodicalservicehistory WHERE service_id='%s' AND tarif_id='%s' AND account_id='%s' ORDER BY datetime DESC LIMIT 1" % (ps_id, tariff_id, account_id))
                            # Здесь нужно проверить сколько раз прошёл расчётный период
                            try:
                                last_checkout=cur.fetchone()[0]
                            except:
                                last_checkout=period_start
                                
                            if datetime.datetime.now()+datetime.timedelta(seconds=n)<=period_end:
                                #посчитать сколько осталось доснять до нужной суммы
                                pass
                            lc=last_checkout-period_start
                            nums, ost=divmod(lc.seconds,delta)
                            for i in xrange(nums-1):
                                #Делаем проводки со статусом Approved=True
                                pass
                            print "delta", delta
                            cash_summ=(float(n)*float(transaction_number)*float(ps_cost))/(float(delta)*float(transaction_number))
                            # Делаем проводку со статусом Approved
                            cur.execute("""
                                   INSERT INTO billservice_transaction(
                                   account_id, approved, tarif_id, summ, description, created)
                                   VALUES (%s, %s, %s, %s, %s, %s);
                                   """,(account_id, True, tariff_id,cash_summ, "AT_START", datetime.datetime.now()))
                            query="UPDATE billservice_account SET  ballance=ballance-%s WHERE id=%s" % (cash_summ, account_id)
                            print query
                            cur.execute(query)
                            cur.execute("""
                                   INSERT INTO billservice_periodicalservicehistory(service_id, tarif_id, account_id, summ, datetime) VALUES (%s, %s, %s, %s, %s);
                                   """, (ps_id,tariff_id,account_id, cash_summ, datetime.datetime.now()))

                        if ps_cash_method=="AT_START":
                            """
                            Смотрим когда в последний раз платили по услуге. Если в текущем расчётном периоде
                            не платили-производим снятие.
                            """
                            cur.execute("SELECT datetime FROM billservice_periodicalservicehistory WHERE service_id='%s' AND tarif_id='%s' AND account_id='%s' ORDER BY datetime DESC LIMIT 1" % (ps_id, tariff_id, account_id))
                            try:
                                last_checkout=cur.fetchone()[0]
                            except:
                                last_checkout=period_start
                            # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                            # Для последней проводки ставим статус Approved=True
                            # для всех сотальных False
                            if last_checkout<=period_start:
                                
                                lc=last_checkout-period_start
                                nums, ost=divmod(lc.seconds,delta)
                                for i in xrange(nums-1):
                                   cur.execute("""
                                   INSERT INTO billservice_transaction(
                                   account_id, approved, tarif_id, summ, description, created)
                                   VALUES (%s, %s, %s, %s, %s, %s);
                                   """,(account_id, False, tariff_id,ps_cost, "AT_START", datetime.datetime.now()))
                                   query="UPDATE billservice_account SET  ballance=ballance-%s WHERE id=%s" % (ps_cost, account_id)
                                   print "1 %s" % query
                                   cur.execute(query)
                                   cur.execute("""
                                   INSERT INTO billservice_periodicalservicehistory(service_id, tarif_id, account_id, summ, datetime) VALUES (%s, %s, %s, %s, %s);
                                   """, (ps_id,tariff_id,account_id, ps_cost, datetime.datetime.now()))
                                   
                                # Делаем проводку со статусом Approved
                                cur.execute("""
                                   INSERT INTO billservice_transaction(
                                   account_id, approved, tarif_id, summ, description, created)
                                   VALUES (%s, %s, %s, %s, %s, %s);
                                   """,(account_id, True, tariff_id,ps_cost, "AT_START", datetime.datetime.now()))
                                query="UPDATE billservice_account SET  ballance=ballance-%s WHERE id=%s" % (ps_cost, account_id)
                                print query
                                cur.execute(query)
                                cur.execute("""
                                   INSERT INTO billservice_periodicalservicehistory(service_id, tarif_id, account_id, summ, datetime) VALUES (%s, %s, %s, %s, %s);
                                   """, (ps_id,tariff_id,account_id, ps_cost, datetime.datetime.now()))


                        if ps_cash_method=="AT_END":
                           """
                           Смотрим завершился ли хотя бы один расчётный период.
                           Если завершился - считаем сколько уже их завершилось.
                           Для последнего делаем проводку со статусом Approved=True
                           для остальных со статусом False
                           """
                           cur.execute("SELECT datetime FROM billservice_periodicalservicehistory WHERE service_id='%s' AND tarif_id='%s' AND account_id='%s' ORDER BY datetime DESC LIMIT 1" % (ps_id, tariff_id, account_id))
                           try:
                                last_checkout=cur.fetchone()[0]
                           except:
                                last_checkout=period_start
                           # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                           # Для последней проводки ставим статус Approved=True
                           # для всех сотальных False
                           now=datetime.datetime.now()
                           if (now-period_start).seconds>=delta:

                                lc=last_checkout-period_start
                                nums, ost=divmod((period_end-last_checkout).seconds, delta)
                                for i in xrange(nums-1):
                                   cur.execute("""
                                   INSERT INTO billservice_transaction(
                                   account_id, approved, tarif_id, summ, description, created)
                                   VALUES (%s, %s, %s, %s, %s, %s);
                                   """,(account_id, False, tariff_id,ps_cost, "AT_END", datetime.datetime.now()))
                                   #делаем проводки со статусом Approved=False
                                   cur.execute("""
                                   UPDATE billservice_account SET  ballance=ballance-%s WHERE id=%s;
                                   """ % (ps_cost, account_id))
                                   cur.execute("""
                                   INSERT INTO billservice_periodicalservicehistory(service_id, tarif_id, account_id, summ, datetime) VALUES (%s, %s, %s, %s, %s);
                                   """, (ps_id,tariff_id,account_id, ps_cost, datetime.datetime.now()))

                                cur.execute("""
                                   INSERT INTO billservice_transaction(
                                   account_id, approved, tarif_id, summ, description, created)
                                   VALUES (%s, %s, %s, %s, %s, %s);
                                   """,(account_id, True, tariff_id,ps_cost, "AT_END", datetime.datetime.now()))
                                cur.execute("""
                                   UPDATE billservice_account SET  ballance=ballance-%s WHERE id=%s;
                                   """ % (ps_cost, account_id))
                                cur.execute("""
                                   INSERT INTO billservice_periodicalservicehistory(service_id, tarif_id, account_id, summ, datetime) VALUES (%s, %s, %s, %s, %s);
                                   """, (ps_id,tariff_id,account_id, ps_cost, datetime.datetime.now()))
            time.sleep(n)

                            
        
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

sess_dog = session_dog()
sess_dog.start()
psb=periodical_service_bill()
psb.start()
#logg_thread = LoggerThread()
#logg_thread.start()

#check_access()