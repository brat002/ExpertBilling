#-*- coding: utf-8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse

from django.test.client import Client
from billservice.models import Account
import datetime

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
        response = c.post(reverse('getpaid-easypay-pay'), """<Request>
<DateTime>yyyy-MM-ddTHH:mm:ss</DateTime>
<Sign></Sign>
<Check>
<ServiceId>int</ServiceId>
<Account>010001</Account>
</Check>
</Request>""", content_type='text/xml')
        self.assertEqual(response.content, u"""<Response>
<StatusCode>0</StatusCode>
<StatusDetail>Аккаунт найден</StatusDetail>
<DateTime>2013-02-24T13:55:08</DateTime>
<Sign></Sign>
<AccountInfo>
<fullname>foouser</fullname>
</AccountInfo>
</Response>""")
