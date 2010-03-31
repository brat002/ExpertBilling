# -*- coding=utf-8 -*-

import unittest
import jsonpickle
from django.test import Client
from django.core.management.commands import test
#from django.test.simple import DjangoTestSuiteRunner
from django.contrib.auth.models import User

from testcases.models import create_user

from ebscab.nas.models import Nas, TrafficClass

from billservice.models import Account, AccountTarif, NetFlowStream, Transaction, Card, TransactionType, TrafficLimit, Tariff, TPChangeRule, AddonService, AddonServiceTarif, AccountAddonService, PeriodicalServiceHistory, AddonServiceTransaction, OneTimeServiceHistory, TrafficTransaction, AccountPrepaysTrafic, PrepaidTraffic, News, AccountViewedNews

  

class ObtainignBallanceTestCase(unittest.TestCase):
    
    def setUp(self):        
        self.client = Client()
    
    def test_user_authenticate(self):
        
        user = Account.objects.get(username='mir')
                
        self.assertEqual(user.username, 'mir')
        self.assertEqual(user.password, 'mir')
       
        response = self.client.post('/login/',{'username':'mir', 'password':'mir'},follow=False)
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
                
    def test_user_balance(self):
        
        user = Account.objects.get(username='mir')
        
        response = self.client.post('/login/',{'username':'mir', 'password':'mir'},follow=False)        
        response = self.client.get('/service_data/', {'id':'1009'})
        
        self.assertEqual(response.status_code, 200)
                        
        data = jsonpickle.decode(response.content.replace('&quot;','\"'))
        
        if data['status_code'] == '1010':
            self.assertEqual(data['value'], "%.2f" % (user.ballance))
        else:
            self.assertNotEqual(data['status_code'], '1008')
            self.aseertEqual(data['status_code'], '1007')
        
    def test_user_news(self):
        pass