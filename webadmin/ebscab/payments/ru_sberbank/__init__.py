#-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from getpaid.backends import PaymentProcessorBase
import hashlib
import datetime

from billservice.models import Account

     
class TransactionStatus:
    OK = 0
    ERROR = 1


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

CHECK_BODY_SUCCESS=u"""<err_code>%(ERR_CODE)s</err_code>   
<err_text>%(ERR_TEXT)s</err_text>
<account>%(ACCOUNT)s</account>
<client_name>%(CLIENT_NAME)s</client_name>
<balance>%(BALLANCE)s</balance>"""

CHECK_BODY_ERROR=u"""<err_code>%(ERR_CODE)s</err_code>   
<err_text>%(ERR_TEXT)s</err_text>
"""

PAYMENT_BODY=u"""<err_code>%(ERR_CODE)s</err_code>   
<err_text>%(ERR_TEXT)s</err_text>
<account>%(ACCOUNT)s</account>
<reg_id>%(REG_ID)s</reg_id>
<reg_date>%(REG_DATE)s</reg_date>"""

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
class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.ru_sberbank'
    BACKEND_NAME = _('Sberbank backend')
    BACKEND_ACCEPTED_CURRENCY = ('RUB', )

    
    
    _ALLOWED_IP = ('93.183.196.28', '93.183.196.26')
    
    @staticmethod
    def check_allowed_ip(ip, body):
        allowed_ip = PaymentProcessor.get_backend_setting('allowed_ip', PaymentProcessor._ALLOWED_IP)

        if len(allowed_ip) != 0 and ip not in allowed_ip:
            dt = datetime.datetime.now()
            return PaymentProcessor.error(body, u'Unknown IP')
        return 'OK'

    def get_gateway_url(self, request):
        return self.GATEWAY_URL, "GET", {}
    
    @staticmethod
    def error(body, text):
        dt = datetime.datetime.now()
        
        return  ERROR_TEMPLATE % {
                                  'STATUS': TransactionStatus.ERROR,
                                  'STATUS_DETAIL': text,
                                  'DATETIME': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                  'SIGN': PaymentProcessor.compute_sig(body),
                                  
                                  }
    
    @staticmethod
    def compute_sig(body):
        return ''
    
    @staticmethod    
    def check_service_id(body, service_id):
        if service_id!=int(PaymentProcessor.get_backend_setting('SERVICE_ID')):
            return PaymentProcessor.error(body, u'Неизвестный Service ID')
            
    
    @staticmethod
    def check(request, body):
        acc = body.request.params.account.text
        print "acc==", acc
        try:
            account = Account.objects.get(contract = acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(body, u'Аккаунт не найден')
        
        service_id = body.request.check.serviceId
        PaymentProcessor.check_service_id(body, service_id)
        dt = datetime.datetime.now()
        ret = SUCCESS_CHECK_TEMPLATE % {
                                         'STATUS': TransactionStatus.OK,
                                         'STATUS_DETAIL': u'Аккаунт найден',
                                         'DATETIME': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'FULLNAME': account.fullname,
                                         'SIGN': ''
                                         
                                         }
        SIGN = PaymentProcessor.compute_sig(ret)
        ret = SUCCESS_CHECK_TEMPLATE % {
                                         'STATUS': TransactionStatus.OK,
                                         'STATUS_DETAIL': u'Аккаунт найден',
                                         'DATETIME': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'FULLNAME': account.fullname,
                                         'SIGN': SIGN
                                         
                                         }
        return ret
        

    @staticmethod
    def pay(request, body):
        acc = body.request.payment.account.text
        amount = float(body.request.payment.amount.text)
        orderid = body.request.payment.orderid.text
        service_id = body.request.payment.serviceId
        PaymentProcessor.check_service_id(body, service_id)
        
        try:
            account = Account.objects.get(contract = acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(body, u'Аккаунт не найден')
        
        
        if amount>0:
            from getpaid.models import Payment
    
            print "amount=", amount
            payment = Payment.create(account.id, None,   PaymentProcessor.BACKEND, amount = amount, external_id=orderid)
        dt = datetime.datetime.now()
        ret = SUCCESS_PAY_TEMPLATE % {
                                         'STATUS': TransactionStatus.OK,
                                         'STATUS_DETAIL': u'Платёж создан. Требуется подтверждение',
                                         'DATETIME': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'PAYMENT_ID': payment.id,
                                         'SIGN': ''
                                         
                                         }
        SIGN = PaymentProcessor.compute_sig(ret)
        ret = SUCCESS_PAY_TEMPLATE % {
                                         'STATUS': TransactionStatus.OK,
                                         'STATUS_DETAIL': u'Платёж создан. Требуется подтверждение',
                                         'DATETIME': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'PAYMENT_ID': payment.id,
                                         'SIGN': SIGN
                                         
                                         }
        return ret
    
    @staticmethod
    def confirm(request, body):
        paymentid = body.request.confirm.paymentid.text
        serviceid = body.request.confirm.serviceid
        service_id = body.request.confirm.serviceId
        PaymentProcessor.check_service_id(body, service_id)
        from getpaid.models import Payment
        try:
            payment = Payment.objects.get(id = paymentid)
        except Payment.DoesNotExist, ex:
            return PaymentProcessor.error(body, u'Платёж не найден')
        
        dt = datetime.datetime.now()
        payment.paid_on = dt
        payment.amount_paid = payment.amount
        payment.save()
        payment.change_status('paid')
        
        ret = SUCCESS_CONFIRM_TEMPLATE % {
                                         'STATUS': TransactionStatus.OK,
                                         'STATUS_DETAIL': u'Платёж подтверждён',
                                         'DATETIME': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'ORDER_DATE': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'SIGN': ''
                                         
                                         }
        SIGN = PaymentProcessor.compute_sig(ret)
        ret = SUCCESS_CONFIRM_TEMPLATE % {
                                         'STATUS': TransactionStatus.OK,
                                         'STATUS_DETAIL': u'Платёж подтверждён',
                                         'DATETIME': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'ORDER_DATE': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'SIGN': SIGN
                                         
                                         }
        return ret
    
    @staticmethod
    def cancel(request, body):
        paymentid = body.request.cancel.paymentid.text
        service_id = body.request.cancel.serviceid
        
        PaymentProcessor.check_service_id(body, service_id)
        
        from getpaid.models import Payment
        try:
            payment = Payment.objects.get(id = paymentid)
        except Payment.DoesNotExist, ex:
            return PaymentProcessor.error(body, u'Платёж не найден')
        
        payment.change_status('canceled')
        
        payment.save()

        dt = datetime.datetime.now()
        ret = SUCCESS_CANCEL_TEMPLATE % {
                                         'STATUS': TransactionStatus.OK,
                                         'STATUS_DETAIL': u'Платёж отменён',
                                         'DATETIME': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'CANCEL_DATE': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'SIGN': ''
                                         
                                         }
        SIGN = PaymentProcessor.compute_sig(ret)
        ret = SUCCESS_CANCEL_TEMPLATE % {
                                         'STATUS': TransactionStatus.OK,
                                         'STATUS_DETAIL': u'Платёж отменён',
                                         'DATETIME': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'CANCEL_DATE': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                                         'SIGN': SIGN
                                         
                                         }
        return ret
    
import listeners
