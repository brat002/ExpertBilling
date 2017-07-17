#-*- coding=UTF-8 -*-
import os, sys

import datetime
from billservice.models import Account, Transaction
from django.conf import settings

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django import template
import decimal
import time
"""
https://service.someprv.ru:8443/payment_app.cgi?command=check&txn_id=1234567&account=4957835959&sum=10.45

<?xml version="1.0" encoding="UTF-8"?>
<response>
<osmp_txn_id>1234567</osmp_txn_id>
<result>0</result>
<comment></comment>
</response>

https://service.someprv.ru:8443/payment_app.cgi?command=pay&txn_id=1234567&txn_date=20090815120133&account=4957835959&sum=10.45

<?xml version="1.0" encoding="UTF-8"?>
<response>
<osmp_txn_id>1234567</osmp_txn_id>
<prv_txn>2016</prv_txn>
<sum>10.45</sum>
<result>0</result>
<comment>OK</comment>
</response>

"""

from functools import wraps

def http_basic_auth(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        from django.contrib.auth import authenticate, login
        if request.META.has_key('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':', 1)
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
        return func(request, *args, **kwargs)
    return _decorator

#s@http_basic_auth
def payment(request):
    if False and request.META.get("REMOTE_ADDR") not in ['1.1.1.1']:
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <osmp_txn_id>%s</osmp_txn_id>
        <result>7</result>
        <comment>У вас нет доступа к этому сервису</comment>
        </response>
        """ % request.GET.get('txn_id', 0)
        return HttpResponse(response)
    

    contract= request.GET.get('account')
    amount = request.GET.get('sum')
    action = request.GET.get('command')
    txn_date = request.GET.get("txn_date")
    reciept = request.GET.get("txn_id")
    
    if not (contract or amount or action not in ['check','pay']):
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <osmp_txn_id>%s</osmp_txn_id>
        <result>300</result>
        <comment>Ошибка передачи параметров</comment>
        </response>
        """ % reciept
        return HttpResponse(response)
    
    try:
        amount = decimal.Decimal(amount)
    except:
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <osmp_txn_id>%s</osmp_txn_id>
        <result>300</result>
        <comment>Введённая сумма не является числом</comment>
        </response>
        """ % reciept
        return HttpResponse(response)
    if amount<=0:
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <osmp_txn_id>%s</osmp_txn_id>
        <result>241</result>
        <comment>Введённая сумма слишком мала</comment>
        </response>
        """ % reciept
        return HttpResponse(response)      
    
    #print contract
    try:
        account = Account.objects.get(username=contract)
    except Exception, e:
        print e
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <osmp_txn_id>%s</osmp_txn_id>
        <result>4</result>
        <comment>Договор не найден</comment>
        </response>
        """ % reciept
        return HttpResponse(response)
        
    if action=='check':
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <osmp_txn_id>%s</osmp_txn_id>
        <result>0</result>
        <comment>Договор найден</comment>
        </response>
        """ % reciept
        return HttpResponse(response)
    
    if action=='pay':
        if not (txn_date and reciept):
            response=u"""<?xml version="1.0" encoding="utf-8"?>
            <response>
            <osmp_txn_id>%s</osmp_txn_id>
            <result>300</result>
            <comment>Ошибка передачи параметров.</comment>
            </response>
            """ % reciept
            return HttpResponse(response)
        try:
            payment_date = datetime.datetime(*time.strptime(txn_date, "%Y%m%d%H%M%S")[0:5])
        except Exception, e:
            print e
            import traceback
            response=u"""<?xml version="1.0" encoding="utf-8"?>
            <response>
            <osmp_txn_id>%s</osmp_txn_id>
            <result>300</result>
            <comment>Ошибка передачи параметров. смотри дату.</comment>
            </response>
            """ % reciept
            return HttpResponse(response)
        
        try:    
            model=Transaction()
            model.summ=amount
            model.account=account
            model.approved=True
            model.created=payment_date
            model.promise=False
            model.bill=reciept
            model.description=u"Автоматический платёж через систему OSMP пользовательские провайдеры %s" % reciept

            model.type_id='OSMP_CUSTOM_BILL'
            model.save()
            response=u"""<?xml version="1.0" encoding="utf-8"?>
            <response>
            <osmp_txn_id>%s</osmp_txn_id>
            <prv_txn>%s</prv_txn>
            <result>0</result>
            <sum>%s</sum>
            <comment>Оплата успешно произведена.</comment>
            </response>
            """ % (reciept,reciept,amount,)
            return HttpResponse(response)
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()
            response=u"""<?xml version="1.0" encoding="utf-8"?>
            <response>
            <osmp_txn_id>%s</osmp_txn_id>
            <result>300</result>
            <comment>Ошибка создания платежа</comment>
            </response>
            """ % reciept
            return HttpResponse(response)
