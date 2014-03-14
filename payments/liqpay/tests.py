#-*- coding: utf-8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse

from django.test.client import Client
from billservice.models import Account, Transaction, TransactionType
import datetime
from Beautifulsoup import Beautifulsoup

class SimpleTest(TestCase):
    def test_check(self):
        c = Client()
        acc = Account()
        acc.username='010001'
        acc.password='010001'
        acc.fullname='foouser'
        acc.created = datetime.datetime.now()
        acc.contract = '010001'
        acc.save()
        response = c.post(reverse('getpaid-easypay-pay'), "")
        print response.content
        

    def test_pay(self):
        c = Client()
        acc = Account()
        acc.username='010001'
        acc.password='010001'
        acc.fullname='foouser'
        acc.created = datetime.datetime.now()
        acc.contract = '010001'
        acc.save()
        response = c.post(reverse('getpaid-easypay-pay'), "")
        print response.content
        
    def test_confirm(self):
        c = Client()
        acc = Account()
        acc.username='010001'
        acc.password='010001'
        acc.fullname='foouser'
        acc.created = datetime.datetime.now()
        acc.contract = '010001'
        acc.save()
        TransactionType.objects.create(name='EasyPay', internal_name = 'payments.easypay')
        
        response = c.post(reverse('getpaid-easypay-pay'), """<Request>
<DateTime>yyyy-MM-ddTHH:mm:ss</DateTime>
<Sign></Sign>
<Payment>
<ServiceId>1</ServiceId>
<OrderId>1</OrderId>
<Account>010001</Account>
<Amount>10.11</Amount>
</Payment>
</Request>""", content_type='text/xml')
        print response.content
        bs = Beautifulsoup(response.content)
        response = c.post(reverse('getpaid-easypay-pay'), """<Request>
<DateTime>yyyy-MM-ddTHH:mm:ss</DateTime>
<Sign></Sign>
<Confirm>
<ServiceId>1</ServiceId>
<PaymentId>%s</PaymentId>
</Confirm>
</Request>""" % bs.response.paymentid, content_type='text/xml')
        
        print 'TRANSACTION=', Transaction.objects.get(type__internal_name='payments.easypay', bill='1')
        
        print response.content
        
    def test_cancel(self):
        c = Client()
        acc = Account()
        acc.username='010001'
        acc.password='010001'
        acc.fullname='foouser'
        acc.created = datetime.datetime.now()
        acc.contract = '010001'
        acc.save()
        TransactionType.objects.create(name='EasyPay', internal_name = 'payments.easypay')
        
        response = c.post(reverse('getpaid-easypay-pay'), """<Request>
<DateTime>yyyy-MM-ddTHH:mm:ss</DateTime>
<Sign></Sign>
<Payment>
<ServiceId>1</ServiceId>
<OrderId>1</OrderId>
<Account>010001</Account>
<Amount>10.11</Amount>
</Payment>
</Request>""", content_type='text/xml')
        print response.content
        bs = Beautifulsoup(response.content)
        response = c.post(reverse('getpaid-easypay-pay'), """<Request>
<DateTime>yyyy-MM-ddTHH:mm:ss</DateTime>
<Sign></Sign>
<Confirm>
<ServiceId>1</ServiceId>
<PaymentId>%s</PaymentId>
</Confirm>
</Request>"""  % bs.response.paymentid, content_type='text/xml')
        
        response = c.post(reverse('getpaid-easypay-pay'), """<Request>
<DateTime>yyyy-MM-ddTHH:mm:ss</DateTime>
<Sign></Sign>
<Cancel>
<ServiceId>1</ServiceId>
<PaymentId>%s</PaymentId>
</Cancel>
</Request>""" % bs.response.paymentid, content_type='text/xml')
        self.assertEqual(Transaction.objects.filter(type__internal_name='payments.easypay', bill='1').count(), 0)
        
        print response.content