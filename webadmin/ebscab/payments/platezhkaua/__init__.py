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


ERROR_TEMPLATE="""<?xml version="1.0" encoding="UTF-8"?>
<commandResponse>
<extTransactionID>%(TRANSACTION_ID)s</extTransactionID>
<account>%(ACCOUNT)s</account>
<result>%(RESULT)s</result>
<comment>%(COMMENT)s</comment>
</commandResponse>"""

SUCCESS_CHECK_TEMPLATE= """<?xml version="1.0" encoding="UTF-8"?>
<commandResponse>
<extTransactionID>%(TRANSACTION_ID)s</extTransactionID>
<account>%(ACCOUNT)s</account>
<result>%(RESULT)s</result>
<comment>%(COMMENT)s</comment>
</commandResponse>"""



class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.platezhkaua'
    BACKEND_NAME = _('Platezhka UA backend')
    BACKEND_ACCEPTED_CURRENCY = ('UAH', )

    GATEWAY_URL = ''
    
    _ALLOWED_IP = ('62.149.15.210',)
    
    @staticmethod
    def check_allowed_ip(ip, request, body):
        allowed_ip = PaymentProcessor.get_backend_setting('allowed_ip', PaymentProcessor._ALLOWED_IP)

        if len(allowed_ip) != 0 and ip not in allowed_ip:
            dt = datetime.datetime.now()
            return PaymentProcessor.error(body, u'Unknown IP')
        return 'OK'
    
    @staticmethod
    def check_credentials(ip, request, body):
        login = PaymentProcessor.get_backend_setting('login')
        password = PaymentProcessor.get_backend_setting('password')

        if login!=body.commandCall.login.text or password!=body.commandCall.password.text:
            dt = datetime.datetime.now()
            return PaymentProcessor.error(body, 300, 'Incorrect credentials')
        return 'OK'

    def get_gateway_url(self, request, payment):
        return self.GATEWAY_URL, "GET", {}
    
    @staticmethod
    def error(body, text, comment=''):
        
        return  ERROR_TEMPLATE % ERROR_TEMPLATE % {
                                  'TRANSACTION_ID': body.commandCall.transactionID.text,
                                  'RESULT': text,
                                  'ACCOUNT': body.commandCall.account.text,
                                  'COMMENT': comment,
                                  
                                  }

    
    @staticmethod
    def check(request, body):
        acc = body.commandCall.account.text

        try:
            account = Account.objects.get(contract = acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(body, 5, u'Аккаунт не найден')
        
        ret = ERROR_TEMPLATE % {
                                  'TRANSACTION_ID': body.commandCall.transactionID.text,
                                  'RESULT': 0,
                                  'ACCOUNT': body.commandCall.account.text,
                                  'COMMENT': 'OK',
                                  
                                  }

        return ret
        

    @staticmethod
    def pay(request, body):
        acc = body.commandCall.account.text
        amount = float(body.commandCall.amount.text)
        orderid = body.commandCall.payID.text
        timestamp = body.commandCall.payTimestamp.text


        
        try:
            account = Account.objects.get(contract = acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(body, 5, u'Аккаунт не найден')
        
        
        if amount>0:
            from getpaid.models import Payment
    

            payment = Payment.create(account, None,   PaymentProcessor.BACKEND, amount = amount, external_id=orderid)
            payment.paid_on = datetime.datetime.strptime(timestamp, '%Y%m%d%H%M%S')
            payment.amount_paid = payment.amount
            payment.save()
            payment.change_status('paid')
            ret = SUCCESS_CHECK_TEMPLATE % {
                                      'TRANSACTION_ID': body.commandCall.transactionID.text,
                                      'RESULT': 0,
                                      'ACCOUNT': body.commandCall.account.text,
                                      'COMMENT': 'OK',
                                      }

            return ret

    
import listeners
