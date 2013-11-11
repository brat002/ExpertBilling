#-*- coding=UTF-8 -*-
import os, sys

import datetime
from billservice.models import Account, Transaction
from django.conf import settings

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django import template
import decimal
import time

response_check=u"""<?xml version="1.0" encoding="utf-8"?>
<response>
<rapida_txn_id>%s</rapida_txn_id>
<result>%s</result>
<comment>%s</comment>
</response>
"""

response_pay=u"""<?xml version="1.0" encoding="utf-8"?>
<response>
<rapida_txn_id>%s</rapida_txn_id>
<prv_txn>%s</prv_txn>
<result>%s</result>
<comment>%s</comment>
</response>
"""


def payment(request):
    #if request.META.get("REMOTE_ADDR") not in ['1.1.1.1']:
    #    response=u"""<?xml version="1.0" encoding="utf-8"?>
    #    <response>
    #    <code>1</code>
    #    <message>У вас нет доступа к этому сервису </message>
    #    </response>
    #    """
    #    return HttpResponse(response)
    
    #action = request.GET.get('type')
    txn_id = request.GET.get("txn_id")
    contract= request.GET.get('account')
    amount = float(request.GET.get('sum', 0))
    action = request.GET.get('command')
    date = request.GET.get("txn_date")
    #reciept = request.GET.get("receipt")
    
    if not (contract or amount or action not in ['check','pay']):
        response=response_check % (txn_id, 300, u"Ошибка передачи параметров")
        return HttpResponse(response)
    
    try:
        amount = decimal.Decimal(amount)
    except:
        response = response_check % (txn_id, 300, u"Введённая сумма не является числом")
        return HttpResponse(response)

    if amount<=0:
        response = response_check % (txn_id, 241, u"Введённая сумма слишком мала")

        return HttpResponse(response)      
    
    #print contract
    try:
        account = Account.objects.get(contract=contract)
    except Exception, e:
        #print e
        response = response_check % (txn_id, 5, u"Договор не найден")
        return HttpResponse(response)
        
    if action=='check':
        response = response_check % (txn_id, 0, u"Договор найден")
        return HttpResponse(response)
    
    if action=='pay':
        if not date:
            response = response_check % (txn_id, 300, u"Дата не указана")        
            return HttpResponse(response)        
        try:
            payment_date = datetime.datetime(*time.strptime(date, "%Y%m%d%H%M%S")[0:5])
        except Exception, e:
            #print e
            #import traceback
            response = response_check % (txn_id, 300, u"Неверный формат даты")        
            return HttpResponse(response)
        
        try:    
            model=Transaction()
            model.summ=amount*(-1)
            model.account=account
            model.approved=True
            #model.bill=u'kPay'
            model.created=payment_date
            model.promise=False
            model.bill=reciept
            #model.description=u"Автоматический платёж через систему  %s" % reciept

            model.type_id='RAPIDA_PAYMENT'
            model.save()
            response = response_pay % (txn_id, model.id, 0, u"Оплата произведена успешно.")
            return HttpResponse(response)
        except Exception, e:
            #print e
            #import traceback
            #traceback.print_exc()
            response = response_check % (txn_id, 300, u"Ошибка выполнения платежа")
            return HttpResponse(response)
