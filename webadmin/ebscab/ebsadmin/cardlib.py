#-*-coding: utf-8 -*-
from django.db import connection
from billservice.models import Card, Account, SubAccount, AccountTarif, Transaction, AccountAddonService
import datetime

def activate_card(login, pin):
    status_ok = 1
    status_bad_userpassword = 2
    status_card_was_activated =3
    status_bad_card = 4
    now = datetime.datetime.now()
    cur=connection.cursor()
    if login and pin:

        return_status = 0
        
        card = Card.objects.filter(type=2, login=login, pin=pin, sold__isnot=None, disabled=False)
        if not card: 
            return  status_bad_userpassword      
        if len(card)>1:
            return  status_bad_card
        card=card[0]
        if card.activated or card.start_date>now or card.end_date<now: 
            return  status_card_was_activated
  

        account = Account()
        account.username = login
        account.password = pin
        account.status = 1
        account.created = now
        account.allow_webcab = True
        account.allow_expresscards = True
        account.save()
        
        subaccount = SubAccount()
        subaccount.account = account
        subaccount.username = login
        subaccount.password = pin
        subaccount.ipv4_vpn_pool = card.ippool
        subaccount.nas = card.nas
        subaccount.save()

        ac = AccountTarif()
        ac.account=account
        ac.tarif = card.tarif
        ac.datetime = now
        ac.save()

        transaction = Transaction()
          
        transaction.bill = u'Активация карты доступа'
        transaction.account=account
        transaction.accounttarif=ac
        transaction.type = 'ACCESS_CARD'
        
        transaction.approved = True
        transaction.tarif=card.tarif
        transaction.summ=card.nominal*(-1)
        transaction.created=now
        transaction.save()

        return status_ok
                
    return

def activate_pay_card(account_id, serial, card_id, pin):
    status_ok = 1
    status_bad_userpassword = 2
    status_card_was_activated =3
    now = datetime.datetime.now()


    if serial and pin and card_id and account_id:
        return_value = ''
        card = Card.objects.filter(type=0, id=card_id, pin=pin, series=serial, disabled=False)
        if not card:
            return_value =  "CARD_NOT_FOUND"                
        elif card.sold is None: 
            return_value = "CARD_NOT_SOLD"                
        elif card.activated: 
            return_value = "CARD_ALREADY_ACTIVATED"                
        elif card.start_date>now or card.end_date<now: 
            return_value =  "CARD_EXPIRED"
        if not return_value:           
            cur.execute(u"""
            INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created, promise, end_promise)
            VALUES('Активация карты оплаты', %s, 'PAY_CARD', True, %s, %s*(-1),'', %s, False, Null);
            """, (account_id, card["tarif_id"], card['nominal'], now))            
            
            transaction = Transaction()
              
            transaction.bill = u'Активация карты оплаты'
            transaction.account__id=account_id
            transaction.type = 'PAY_CARD'
            
            transaction.approved = True
            transaction.summ=card.nominal*(-1)
            transaction.created=now
            transaction.save()            
            
            card.sold=now
            card.activated_by__id=account_id
            card.save()
            return_value = "CARD_ACTIVATED"
            
              
        return return_value


def add_addonservice(account_id, service_id, subaccount_id=None, ignore_locks = False, activation_date = None):
    #Получаем параметры абонента
    account = Account.objects.filter(id=account_id)

    if account==[]:
        return 'ACCOUNT_DOES_NOT_EXIST'
            
    account = account[0]
    #print account_id
    
    sql = "SELECT id FROM billservice_accountaddonservice WHERE account_id=%s and service_id=%s and (deactivated>now() or deactivated is Null)" % (account_id, service_id, )
    cur.execute(sql)
    connection.commit()
    result=[]
    r=cur.fetchall()

    if r!=[]:
        return 'SERVICE_ARE_ALREADY_ACTIVATED'
            

            
    #Получаем нужные параметры услуги
    sql = "SELECT id, name, allow_activation,timeperiod_id, change_speed FROM billservice_addonservice WHERE id = %s" % service_id
    cur.execute(sql)
    connection.commit()
    result=[]
    r=cur.fetchall()
    if len(r)>1:
        raise Exception

    if r==[]:
        return 'ADDON_SERVICE_DOES_NOT_EXIST'
            
    service = Object(r[0]) 

    sql = "SELECT time_start, length, repeat_after FROM billservice_timeperiodnode WHERE id IN (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id=%s)" % service.timeperiod_id

    cur.execute(sql)
    connection.commit()

    timeperiods = map(Object, cur.fetchall())

    res = False
    for timeperiod in timeperiods:
        if res==True or in_period(timeperiod.time_start, timeperiod.length, timeperiod.repeat_after):
            res=True

    if res == False and ignore_locks==False:
        return "NOT_IN_PERIOD"

    if service.change_speed and ignore_locks==False:

        try:
            cur.execute("SELECT id FROM billservice_accountaddonservice WHERE deactivated is Null and service_id IN (SELECT id FROM billservice_addonservice WHERE change_speed=True) and account_id=%s" % account.id)

        except Exception, e:
            logger.error("Can not add addonservice for account %s, %s", (account_id, e))
        if cur.fetchall():

            return "ALERADY_HAVE_SPEED_SERVICE"

    # Проверка на возможность активации услуги при наличии блокировок
    if not ignore_locks:
        if service.allow_activation==False and (account.ballance<=0 or account.balance_blocked==True or account.disabled_by_limit==True or account.status!=1):
            return "ACCOUNT_BLOCKED"
    

    #Получаем нужные параметры услуги из тарифного плана
    sql = "SELECT id, activation_count, activation_count_period_id FROM billservice_addonservicetarif WHERE tarif_id=%s and service_id = %s" % (account.tarif_id, service_id)
    #print account.tarif_id, service_id
    cur.execute(sql)
    connection.commit()
    result=[]
    r=cur.fetchall()
    if len(r)>1:
        raise Exception

    if r==[]:
        return 'ADDONSERVICE_TARIF_DOES_NOT_ALLOWED'

    tarif_service = Object(r[0]) 

    if tarif_service.activation_count!=0 and ignore_locks==False:

        if tarif_service.activation_count_period_id:

            sql = "SELECT time_start, length, length_in, autostart  FROM billservice_settlementperiod WHERE id = %s" % tarif_service.activation_count_period_id

            cur.execute(sql)
            connection.commit()
            result=[]
            r=cur.fetchall()
            if len(r)>1:
                raise Exception
    
            if r==[]:
                return None

            settlement_period = Object(r[0]) 
            if settlement_period.autostart:
                settlement_period.time_start = account.accounttarif_date
                
            settlement_period_start, settlement_period_end, delta = settlement_period_info(settlement_period.time_start, settlement_period.length_in, settlement_period.length)
            
            sql = "SELECT count(*) as cnt FROM billservice_accountaddonservice WHERE account_id=%s and service_id=%s and activated>'%s' and activated<'%s'" % (account.id, service.id, settlement_period_start, settlement_period_end,)
        else:
            sql = "SELECT count(*) as cnt FROM billservice_accountaddonservice WHERE account_id=%s and service_id=%s" % (account.id, service.id,)
        
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return None
                
        activations_count = Object(r[0]) 
        if activations_count.cnt>=tarif_service.activation_count: return "TOO_MUCH_ACTIVATIONS"
        
    #   log_string = u"Пользователь %s создал запись %s в таблице таблице %s" % (add_data['USER_ID'][0], str(model.__dict__).decode('unicode-escape').encode('utf-8'), table)
    log_string = u"""Пользователь %s добавил пользователю %s подключаемую услугу %s""" % (add_data['USER_ID'][0], account_id, service.name)
    
    #cur.execute(u"""INSERT INTO billservice_log(systemuser_id, "text", created) VALUES(%s, %s, now())""", (add_data['USER_ID'][1],log_string,))
    self.insert_log_action(add_data['USER_ID'][1],log_string)
    if activation_date:
        sql = "INSERT INTO billservice_accountaddonservice(service_id, account_id, activated) VALUES(%s,%s,'%s')" % (service.id, account.id, activation_date)
    else:
        sql = "INSERT INTO billservice_accountaddonservice(service_id, account_id, activated) VALUES(%s,%s,now())" % (service.id, account.id,)
    try:
        cur.execute(sql)
        connection.commit()
        return True
    except Exception, e:
        logger.error("Error add addonservice to account, %s", e)
        connection.rollback()
        return False
        