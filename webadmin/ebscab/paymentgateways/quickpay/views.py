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
у нас платеж состоит из двух частей первая часть 
?type=1&id=123456
нужно получить
или
<response>
<code>0</code>
<comment>Договор действителен</comment>
</response>
или
<response>
<code>1</code>
<comment>Договор не найден</comment>
</response>

если получаем ответ с кодом 0 то
?type=2&id=123456&sum=10.00&SessionID=123

id - это кого искать
SessionID - код транзакции

type=1 - проверка
type=2 - проведение

<code>0</code> - ок
<code>1</code> - ошибка

<?xml version="1.0" encoding="windows-1251" ?> 
<response>
<code>0</code> 
<message>000001 (Нифонтов Павел Витальевич)</message> 
</response>

"""


def payment(request):
    if request.META.get("REMOTE_ADDR") not in ['1.1.1.1']:
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <code>1</code>
        <message>У вас нет доступа к этому сервису </message>
        </response>
        """
        return HttpResponse(response)
    
    #action = request.GET.get('type')
    contract= request.GET.get('number')
    amount = request.GET.get('amount')
    action = request.GET.get('action')
    date = request.GET.get("date")
    reciept = request.GET.get("receipt")
    
    if not (contract or amount or action not in ['check','payment']):
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <code>1</code>
        <message>Ошибка передачи параметров, тип action </message>
        </response>
        """
        return HttpResponse(response)
    
    try:
        amount = decimal.Decimal(amount)
    except:
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <code>1</code>
        <message>Введённая сумма не является числом</message>
        </response>
        """
        return HttpResponse(response)
    if amount<=0:
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <code>1</code>
        <message>Введённая сумма слишком мала</message>
        </response>
        """
        return HttpResponse(response)      
    
    #print contract
    try:
        account = Account.objects.get(username=contract)
    except Exception, e:
        print e
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <code>1</code>
        <message>Договор не найден</message>
        </response>
        """
        return HttpResponse(response)
        
    if action=='check':
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <code>0</code>
        <message>Договор найден</message>
        </response>
        """
        return HttpResponse(response)
    
    if action=='payment':
        if not (date and reciept):
            response=u"""<?xml version="1.0" encoding="utf-8"?>
            <response>
            <code>1</code>
            <message>Ошибка передачи параметров. смотри reciept or date.</message>
            </response>
            """
            return HttpResponse(response)
        try:
            payment_date = datetime.datetime(*time.strptime(date, "%Y-%m-%dT%H:%M:%S")[0:5])
        except Exception, e:
            print e
            import traceback
            response=u"""<?xml version="1.0" encoding="utf-8"?>
            <response>
            <code>1</code>
            <message>Ошибка передачи параметров. смотри дату.</message>
            </response>
            """
            return HttpResponse(response)
        
        try:    
            model=Transaction()
            model.summ=amount
            model.account=account
            model.approved=True
            #model.bill=u'kPay'
            model.created=payment_date
            model.promise=False
            model.bill=reciept
            model.description=u"Автоматический платёж через систему QuickPay %s" % reciept

            model.type_id='QUICKPAY_BILL'
            model.save()
            response=u"""<?xml version="1.0" encoding="utf-8"?>
            <response>
            <code>0</code>
            <message>Оплата успешно произведена.</message>
            </response>
            """
            return HttpResponse(response)
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()
            response=u"""<?xml version="1.0" encoding="utf-8"?>
            <response>
            <code>1</code>
            <message>Ошибка создания платежа</message>
            </response>
            """
            return HttpResponse(response)
