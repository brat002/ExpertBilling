#-*- coding: utf-8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse

from django.test.client import Client
from billservice.models import Account, Transaction, TransactionType
import datetime
from BeautifulSoup import BeautifulSoup

class SimpleTest(TestCase):
       

    def test_pay(self):
        c = Client()
        acc = Account()
        acc.username='010001'
        acc.password='010001'
        acc.fullname='foouser'
        acc.created = datetime.datetime.now()
        acc.contract = '010001'
        acc.save()
        TransactionType.objects.create(name=u'SimpleTerminal', internal_name = 'payments.paypro')
        response = c.get(reverse('getpaid-paypro-pay'), {'pay_id': '12345', 'check': '11111', 'account': '010001', 'date': '2013-08-13 10:55:45', 'pay_amount': '100', 'pay_amount_all': '101'})
        print 'pay'
        print response.content
        
 