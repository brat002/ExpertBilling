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
        TransactionType.objects.create(name=u'SimpleTerminal', internal_name = 'payments.simpleterminal')
        response = c.get(reverse('getpaid-simpleterminal-pay'), {'uid': '010001', 'sum': '100', 'trans':1})
        print 'pay'
        print response.content
        
 