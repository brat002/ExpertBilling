# -*- coding=utf-8 -*-
# $Id$

import unittest
import jsonpickle
from django.test import Client
from django.core.management.commands import test
from django.contrib.auth.models import User
from testcases.models import create_user
from ebscab.nas.models import Nas, TrafficClass
from billservice.models import Account, AccountTarif, NetFlowStream, Transaction, Card, TransactionType, TrafficLimit, Tariff, TPChangeRule, AddonService, AddonServiceTarif, AccountAddonService, PeriodicalServiceHistory, AddonServiceTransaction, OneTimeServiceHistory, TrafficTransaction, AccountPrepaysTrafic, PrepaidTraffic, News, AccountViewedNews


class CheckAccountTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.response_mime = 'text/xml'
    
    def test_auth_by_ip(self):
        response_body = \
        u"""<?xml version="1.0" encoding="UTF-8"?>
        <response>
          <result>0</result>
          <name>Абонент И.О</name>
          <balance>10.55</balance>
        </response>"""
        # test existing account
        
    
    
    def test_auth_by