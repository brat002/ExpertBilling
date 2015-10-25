#-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from getpaid.backends import PaymentProcessorBase
import hashlib
import datetime

from billservice.models import Account

     

class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.simpleterminal'
    BACKEND_NAME = _('SimpleTerminal backend')
    BACKEND_ACCEPTED_CURRENCY = ('RUB', )

    

    
    @staticmethod
    def error(body, text):
        
        return  '%s' % text
    
    @staticmethod
    def compute_sig(body):
        return ''

    @staticmethod
    def pay(request, body):
        acc = body.get('uid')
        orderid = body.get('trans')
        amount = body.get('sum')
        

        try:
            account = Account.objects.get(contract = acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(body, u'-1')


        try:
            amount = float(amount)
        except:
            return PaymentProcessor.error(body, u'-5')
        
        
        if amount>0:
            from getpaid.models import Payment
    
            print "amount=", amount, orderid
            payment = Payment.create(account, None,   PaymentProcessor.BACKEND, amount = amount, external_id=orderid)
            dt = datetime.datetime.now()
            payment.paid_on = dt
            payment.amount_paid = payment.amount
            payment.save()
            payment.change_status('paid')
        return '0'
    
    
import listeners
