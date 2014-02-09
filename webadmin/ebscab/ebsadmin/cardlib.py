#-*-coding: utf-8 -*-
from django.db import connection
from billservice.models import Card, Account, SubAccount, AccountTarif, Transaction, TransactionType, AccountAddonService, TimePeriod, AddonServiceTarif, AddonService, AddonServiceTransaction
import datetime
from django.db.models import Q
from billservice.utility import settlement_period_info
from billservice.utility import in_period
from django.utils.translation import ugettext as _
from django.conf import settings

def activate_card(login, pin):
    status_ok = 1
    status_bad_userpassword = 2
    status_card_was_activated =3
    status_bad_card = 4
    now = datetime.datetime.now()
    cur=connection.cursor()
    if login and pin:

        return_status = 0
        
        card = Card.objects.filter(type=2, login=login, pin=pin, salecard__isnull=False, disabled=False)
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
          
        transaction.bill = _(u'Активация карты доступа')
        transaction.account=account
        transaction.accounttarif=ac
        transaction.type =  TransactionType.objects.get(internal_name= 'ACCESS_CARD')
        
        transaction.approved = True
        transaction.tarif=card.tarif
        transaction.summ=card.nominal
        transaction.created=now
        transaction.save()

        card.activated = now
        card.activated_by = account
        card.save()
        return status_ok
                
    return

def activate_pay_card(account_id,  card_id, pin):

    now = datetime.datetime.now()
    
    return_value = "CARD_NOT_FOUND"
    account = Account.objects.get(id=account_id)
    if pin and card_id and account_id:
        return_value = ''
        if settings.HOTSPOT_ONLY_PIN:
            card = Card.objects.filter(pin=pin,  disabled=False)
        else:
            card = Card.objects.filter(type=0, id=card_id, pin=pin,  disabled=False)
        if card:
            card = card[0]            
            if not card.salecard and not settings.HOTSPOT_ONLY_PIN:
                return_value = "CARD_NOT_SOLD"                
            elif card.activated: 
                return_value = "CARD_ALREADY_ACTIVATED"                
            elif card.start_date>now or card.end_date<now: 
                return_value =  "CARD_EXPIRED"
            if not return_value:           
    
                transaction = Transaction()
                  
                transaction.bill = _(u'Активация карты оплаты')
                transaction.account=account
                transaction.type = TransactionType.objects.get(internal_name='PAY_CARD')
                
                transaction.approved = True
                transaction.summ=card.nominal
                transaction.created=now
                transaction.save()            
                
                card.activated=now
                card.activated_by=account
                card.save()
                return_value = "CARD_ACTIVATED"
        else:
             return_value =  "CARD_NOT_FOUND"
            
              
    return return_value


def add_addonservice(account_id, service_id, subaccount_id=None, ignore_locks = False, activation_date = None):
    #Получаем параметры абонента
    account = Account.objects.filter(id=account_id)

    if not account:
        return 'ACCOUNT_DOES_NOT_EXIST'
            
    account = account[0]
    #print account_id
    now = datetime.datetime.now()
    accountaddonservices = AccountAddonService.objects.filter(account=account, service__id=service_id).filter(Q(deactivated__gt=now) | Q(deactivated__isnull=True))

    
    if accountaddonservices:
        return 'SERVICE_ARE_ALREADY_ACTIVATED'
            
    service = AddonService.objects.filter(id=service_id)

    if service==[]:
        return 'ADDON_SERVICE_DOES_NOT_EXIST'
            
    service = service[0]



    if service.change_speed and ignore_locks==False:


        aas = AccountAddonService.objects.filter(account = account, service__change_speed=True, deactivated__isnull=True)

        if aas:

            return "ALERADY_HAVE_SPEED_SERVICE"

    # Проверка на возможность активации услуги при наличии блокировок
    if not ignore_locks:
        if service.allow_activation==False and (account.ballance<=0 or account.balance_blocked==True or account.disabled_by_limit==True or account.status!=1):
            return "ACCOUNT_BLOCKED"
    
    tarif_service = AddonServiceTarif.objects.filter(service=service, tarif=account.get_account_tariff())
    #Получаем нужные параметры услуги из тарифного плана

    
    if ignore_locks==False and tarif_service==[]:
        return 'ADDONSERVICE_TARIF_DOES_NOT_ALLOWED'

    tarif_service=tarif_service[0]  
    

    if tarif_service.activation_count!=0 and ignore_locks==False:

        if tarif_service.activation_count_period:

            

            settlement_period = tarif_service.activation_count_period
            if settlement_period.autostart:
                settlement_period.time_start = account.get_accounttariff().datetime
                
            settlement_period_start, settlement_period_end, delta = settlement_period_info(settlement_period.time_start, settlement_period.length_in, settlement_period.length)
            
            aas = AccountAddonService.objects.filter(account=account, service=service, activated__gte=settlement_period_start, activated__lte=settlement_period_end).count()
        else:
            aas = AccountAddonService.objects.filter(account=account, service=service).count()
        
                
        if aas>=tarif_service.activation_count: return "TOO_MUCH_ACTIVATIONS"
        

    accountaddonservice = AccountAddonService()
    accountaddonservice.service = service
    accountaddonservice.account = account

    if activation_date:
        accountaddonservice.activated = activation_date
       
    else:
        accountaddonservice.activated = now
    
    accountaddonservice.save()
    return True
        
        
def del_addonservice(account_id, account_service_id):

    #Получаем нужные параметры аккаунта
    #connection.commit()
    account = Account.objects.filter(id=account_id)

    if not account:
        return 'ACCOUNT_DOES_NOT_EXIST'
            
            
    account = account[0]
    #Получаем нужные параметры услуги абонента
    
    accountservice = AccountAddonService.objects.filter(id=account_service_id)

    if not accountservice:
        return 'ACCOUNT_ADDON_SERVICE_DOES_NOT_EXIST'
    accountservice = accountservice[0]

    service = accountservice.service
    
    if service.cancel_subscription:
        
        if service.wyte_period:

            settlement_period = service.wyte_period

            settlement_period_start, settlement_period_end, delta = settlement_period_info(settlement_period.time_start, settlement_period.length_in, settlement_period.length)

        else:
            delta = 0
        now = datetime.datetime.now()
        
        if (((now-accountservice.activated).seconds+(now-accountservice.activated).days*86400)<delta) or (service.wyte_cost and delta == 0):

            ast = AddonServiceTransaction()
            ast.account = account
            ast.type = TransactionType.objects.get(internal_name='ADDONSERVICE_WYTE_PAY')
            ast.summ = service.wyte_cost
            ast.service = service
            ast.service_type = service.service_type
            ast.created = now
            if account.get_accounttarif():
                ast.accounttarif = account.get_accounttarif()
            ast.accountaddonservice = accountservice
            
            ast.save()
            
        #Отключаем услугу

        accountservice.deactivated=now
        accountservice.save()
        return True
    else:
        return 'NO_CANCEL_SUBSCRIPTION'
    return False