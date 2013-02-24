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


ERROR_TEMPLATE="""<Response>
<StatusCode>%(STATUS)s</StatusCode>
<StatusDetail>%(STATUS_DETAIL)s</StatusDetail>
<DateTime>%(DATETIME)s</DateTime>
<Sign>%(SIGN)s</Sign>
</Response>"""    

SUCCESS_CHECK_TEMPLATE= """<Response>
<StatusCode>%(STATUS)s</StatusCode>
<StatusDetail>%(STATUS_DETAIL)s</StatusDetail>
<DateTime>%(DATETIME)s</DateTime>
<Sign>%(SIGN)s</Sign>
<AccountInfo>
<fullname>%(FULLNAME)s</fullname>
</AccountInfo>
</Response>
"""
class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.easypay'
    BACKEND_NAME = _('Easypay backend')
    BACKEND_ACCEPTED_CURRENCY = ('UAH', )

    GATEWAY_URL = 'http://easysoft.com.ua/ProviderProtocolTest'
    


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
    def check(request, body):
        acc = body.request.check.account.text
        print "acc==", acc
        try:
            account = Account.objects.get(contract = acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(body, u'Аккаунт не найден')
        
        ServiceId = body.request.check.serviceId
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
        acc = body.request.check.account.text
        print "acc==", acc
        try:
            account = Account.objects.get(contract = acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(body, u'Аккаунт не найден')
        
        ServiceId = body.request.check.serviceId
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
    
