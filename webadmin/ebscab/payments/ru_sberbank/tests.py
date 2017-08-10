# -*- coding: utf-8 -*-

import datetime

from BeautifulSoup import BeautifulSoup
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

from billservice.models import Account, Transaction, TransactionType


class SimpleTest(TestCase):

    def test_check(self):
        c = Client()
        acc = Account()
        acc.username = '010001'
        acc.password = '010001'
        acc.fullname = 'foouser'
        acc.created = datetime.datetime.now()
        acc.contract = '010001'
        acc.save()
        response = c.post(reverse('getpaid-rusberbank-pay'),
                          u"""\
<?xml version="1.0" encoding="utf-8"?>
<request>
<params>
<act>1</act>
<agent_date>2009-04-15T11:22:33</agent_date>
<account>010001</account>
<pay_amount>10000</pay_amount>
<client_name>Иванов Иван Иванович</client_name>
</params>
<sign>853ee7471ac2eb774e850c727998e0cd</sign>
</request>""",
                          content_type='text/xml')
        print response.content

    def test_check_bad_user(self):
        c = Client()
        response = c.post(reverse('getpaid-rusberbank-pay'),
                          u"""\
<?xml version="1.0" encoding="utf-8"?>
<request>
<params>
<act>1</act>
<agent_date>2009-04-15T11:22:33</agent_date>
<account>010011</account>
<pay_amount>10000</pay_amount>
<client_name>Иванов Иван Иванович</client_name>
</params>
<sign>853ee7471ac2eb774e850c727998e0cd</sign>
</request>""",
                          content_type='text/xml')
        print response.content

    def test_pay(self):
        c = Client()
        acc = Account()
        acc.username = '010001'
        acc.password = '010001'
        acc.fullname = 'foouser'
        acc.created = datetime.datetime.now()
        acc.contract = '010001'
        acc.save()
        TransactionType.objects.create(
            name=u'Сбербанк РФ', internal_name='payments.ru_sberbank')

        response = c.post(reverse('getpaid-rusberbank-pay'),
                          u"""\
<?xml version="1.0" encoding="utf-8"?>
<request>
<params>
<act>2</act>
<agent_date>2009-04-15T11:22:33</agent_date>
<pay_id>2345</pay_id>
<pay_date>2009-04-15T11:00:12</pay_date>
<account>010001</account>
<pay_amount>10000</pay_amount>
<client_name>Иванов</client_name>
<month>03.2009</month>
</params>
<sign>853ee7471ac2eb774e850c727998e0cd</sign>
</request>""",
                          content_type='text/xml')
        print response.content
        xml = BeautifulSoup(response.content)
        self.assertEqual(Transaction.objects
                         .filter(type__internal_name='payments.ru_sberbank',
                                 bill='2345')
                         .count(), 1)

    def test_pay_bad_user(self):
        c = Client()

        TransactionType.objects.create(
            name=u'Сбербанк РФ', internal_name='payments.ru_sberbank')
        response = c.post(reverse('getpaid-rusberbank-pay'),
                          u"""\
<?xml version="1.0" encoding="utf-8"?>
<request>
<params>
<act>2</act>
<agent_date>2009-04-15T11:22:33</agent_date>
<pay_id>2345</pay_id>
<pay_date>2009-04-15T11:00:12</pay_date>
<account>010001</account>
<pay_amount>10000</pay_amount>
<client_name>Иванов</client_name>
<month>03.2009</month>
</params>
<sign>827CCB0EEA8A706C4C34A16891F84E7B</sign>
</request>""",
                          content_type='text/xml')
        print response.content
