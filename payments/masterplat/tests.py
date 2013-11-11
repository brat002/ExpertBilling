#-*- coding: utf-8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse

from django.test.client import Client
from billservice.models import Account, Transaction, TransactionType
import datetime
from BeautifulSoup import BeautifulSoup

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
        response = c.get(reverse('getpaid-masterplat-pay'), {'duser': 'test', 'dpass': 'test', 'cid': '010001', 'uact': 'get_info'})
        print response.content
        print 'check'
        

    def test_pay(self):
        c = Client()
        acc = Account()
        acc.username='010001'
        acc.password='010001'
        acc.fullname='foouser'
        acc.created = datetime.datetime.now()
        acc.contract = '010001'
        acc.save()
        TransactionType.objects.create(name=u'Materplat', internal_name = 'payments.masterplat')
        response = c.get(reverse('getpaid-masterplat-pay'), {'duser': 'test', 'dpass': 'test', 'cid': '010001', 'uact': 'payment', 'Term':1, 'trans': 'aabbcc', 'sum':100})
        print 'pay'
        print response.content
        
 