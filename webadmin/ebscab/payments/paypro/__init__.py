#-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from getpaid.backends import PaymentProcessorBase
import hashlib
import datetime

from billservice.models import Account

     

class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.paypro'
    BACKEND_NAME = _('PayPro backend')
    BACKEND_ACCEPTED_CURRENCY = ('RUB', )

    

    
    @staticmethod
    def error(body, text):
        
        return  '%s' % text
    
    @staticmethod
    def compute_sig(body):
        return ''

    @staticmethod
    def pay(request, body):
        acc = body.get('account')
        orderid = body.get('pay_id')
        amount = body.get('pay_amount_all')
        check = body.get('check')
        date = body.get('date')
        
        try:
            account = Account.objects.get(contract = acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(body, u'-1')


        try:
            amount = float(amount)
        except:
            return PaymentProcessor.error(body, u'-5')
        
        try:
            date =datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        except:
            return PaymentProcessor.error(body, u'-5')
        
        if amount>0:
            from getpaid.models import Payment
    
            print "amount=", amount, orderid
            payment = Payment.create(account, None,   PaymentProcessor.BACKEND, amount = amount, external_id='%s-%s' % (orderid, check))
            dt = datetime.datetime.now()
            payment.paid_on = dt
            payment.amount_paid = payment.amount
            payment.save()
            payment.change_status('paid')
        return ''
    
    
import listeners
