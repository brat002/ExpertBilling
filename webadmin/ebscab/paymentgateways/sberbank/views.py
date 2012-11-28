#-*- coding=UTF-8 -*-
import os, sys

import datetime
from billservice.models import Account, Transaction
from django.conf import settings

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django import template
import decimal
import time
from BeautifulSoup import BeautifulSoup
from hashlib import md5

password=12345
"""
check

<?xml version="1.0" encoding="windows-1251"?>  
<request>
<params>
<act>1</act>
<agent_date>2009-04-15T11:22:33</agent_date>
<account>54321</account>
<pay_amount>10000</pay_amount>
<client_name>Иванов Иван Иванович</client_name>
</params>
<sign>827CCB0EEA8A706C4C34A16891F84E7B</sign>
</request>
"""
BODY=u"""<?xml version="1.0" encoding="utf-8"?>  
<request>
<params>
%s
</params>
<sign>%s</sign>
</request>"""

BODY_ERR=u"""<?xml version="1.0" encoding="utf-8"?>  
<request>
<params>
%s
</params>
</request>"""

CHECK_BODY_SUCCESS=u"""
<err_code>%(ERR_CODE)s</err_code>   
<err_text>%(ERR_TEXT)s</err_text>
<account>%(ACCOUNT)s</account>
<client_name>%(CLIENT_NAME)s</client_name>
<balance>%(BALLANCE)s</balance>"""

CHECK_BODY_ERROR=u"""
<err_code>%(ERR_CODE)s</err_code>   
<err_text>%(ERR_TEXT)s</err_text>
"""

PAYMENT_BODY=u"""
<err_code>%(ERR_CODE)s</err_code>   
<err_text>%(ERR_TEXT)s</err_text>
<account>%(ACCOUNT)s</account>
<reg_id>%(REG_ID)s</reg_id>
<reg_date>%(REG_DATE)s</reg_date>"""


CHECK='1'
PAYMENT='2'

ERRCODES={
"0": u"Успешное выполнение операции",
"1": u"Платеж уже был проведен",
"10": u"Запрос выполнен с неразрешенного адреса",
"11": u"Указаны не все необходимые параметры ",
"12": u"Неверный формат параметров",
"13": u"Неверная цифровая подпись",
"20": u"Указанный номер счета отсутствует",
"21": u"Запрещены платежи на указанный номер счета",
"22": u"Запрещены платежи для указанной услуги",
"23": u"Запрещены платежи для указанного агента",
"29": u"Неверные параметры платежа. В тэге err_text конкретное описание причины",
"30": u"Был другой платеж с указанным номером",
"90": u"Временная техническая ошибка",
"99": u"Прочие ошибки Оператора. В тэге err_text указывается описание причины",

            }
def genSign(body):
    s = body
    hash = md5("%s%s" % (s.encode("utf-8"), password)).hexdigest()
    return hash

def checkSign(body):
    s = body.request.params
    hash = md5("%s%s" % (unicode(s).encode("utf-8"), password)).hexdigest()
    return hash==body.request.sign.text


def payment(request):
    if request.META.get("REMOTE_ADDR") not in ['1.1.1.1']:
        response=u"""<?xml version="1.0" encoding="utf-8"?>
        <response>
        <code>1</code>
        <message>У вас нет доступа к этому сервису </message>
        </response>
        """
        return HttpResponse(response)
    
    source = request.POST.get("params", "")
    xml = BeautifulSoup(source)
    #action = request.GET.get('type')
    contract= xml.request.params.account.text
    amount = xml.request.params.pay_amount.text
    action = xml.request.params.act.text
    if xml.request.params.agent_date:
        date = xml.request.params.agent_date.text
    if xml.request.params.pay_id:
        reciept = xml.request.params.pay_id.text
    if xml.request.params.pay_date:
        pay_date = xml.request.params.pay_date.text
    sign = xml.request.sign.text
    
    if not sign:
        return HttpResponse(BODY_ERR % CHECK_BODY_ERROR % ({"ERR_CODE": 11, "ERR_TEXT": ERRCODES.get("11"),}))
    res = checkSign(xml)
    if not res:
        return HttpResponse(BODY_ERR % CHECK_BODY_ERROR % ({"ERR_CODE": 13, "ERR_TEXT": ERRCODES.get("13"),}))

        
            
    if not (contract or amount or action not in [CHECK,PAYMENT]):
        response = CHECK_BODY_ERROR % ({"ERR_CODE": 11, "ERR_TEXT": ERRCODES.get("11"),})

        return HttpResponse(BODY % (response, genSign(response)) )
    
    try:
        amount = decimal.Decimal(amount)
    except:
        response = CHECK_BODY_ERROR % ({"ERR_CODE": 12, "ERR_TEXT": ERRCODES.get("12"),})
        return HttpResponse(BODY % (response, genSign(response)) )
    
    if amount<=0:
        response = CHECK_BODY_ERROR % ({"ERR_CODE": 12, "ERR_TEXT": u"Сумма должна быть больше нуля",})
        return HttpResponse(BODY % (response, genSign(response)) )   
    
    #print contract
    try:
        account = Account.objects.get(username=contract)
    except Exception, e:
        response = CHECK_BODY_ERROR % ({"ERR_CODE": 20, "ERR_TEXT": ERRCODES.get("20"),})
        return HttpResponse(BODY % (response, genSign(response)) )
        
    if action==CHECK:
        response = CHECK_BODY_SUCCESS % ({"ERR_CODE": 0, "ERR_TEXT": ERRCODES.get("0"), "ACCOUNT": account.username, "CLIENT_NAME": account.fullname, "BALLANCE": account.ballance})
        return HttpResponse(BODY % (response, genSign(response)) )
    
    if action==PAYMENT:
        if not (pay_date and reciept):
            response = CHECK_BODY_ERROR % ({"ERR_CODE": 11, "ERR_TEXT": ERRCODES.get("11"),})
    
            return HttpResponse(BODY % (response, genSign(response)) )
    
        try:
            payment_date = datetime.datetime(*time.strptime(pay_date, "%Y-%m-%dT%H:%M:%S")[0:5])
        except Exception, e:
            response = CHECK_BODY_ERROR % ({"ERR_CODE": 11, "ERR_TEXT": u"Неверный формат даты %s" % e,})
    
            return HttpResponse(BODY % (response, genSign(response)) )
        
        try:    
            model=Transaction()
            model.summ=amount
            model.account=account
            model.approved=True
            #model.bill=u'kPay'
            model.created=payment_date
            model.promise=False
            model.bill=reciept
            model.type_id='SBERBANK_BILL'
            model.save()
            response = PAYMENT_BODY % ({"REG_ID": model.id, "REG_DATE": model.created.strftime("%Y-%m-%dT%H:%M:%S"), "ERR_CODE": 0, "ERR_TEXT": ERRCODES.get("0"), "ACCOUNT": account.username, })
            return HttpResponse(BODY % (response, genSign(response)) )
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()
            response = CHECK_BODY_ERROR % ({"ERR_CODE": 99, "ERR_TEXT": u"Ошибка проведения платежа %s" % e,})
    
            return HttpResponse(BODY % (response, genSign(response)) )
