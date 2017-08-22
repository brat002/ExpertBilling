# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

from billservice.models import Account


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
        response = c.post(reverse('getpaid-platezhkaua-pay'),
                          """\
<?xml version="1.0" encoding="UTF-8"?>
<commandCall>
    <login>12345</login>
    <password>12345</password>
    <command>check</command>
    <transactionID>204</transactionID>
    <payElementID>1</payElementID>
    <account>010001</account>
</commandCall>""",
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
        response = c.post(reverse('getpaid-platezhkaua-pay'),
                          """\
<?xml version="1.0" encoding="UTF-8"?>
<commandCall>
    <login>12345</login>
    <password>12345</password>
    <command>check</command>
    <transactionID>204</transactionID>
    <payElementID>1</payElementID>
    <account>010001</account>
</commandCall>""",
                          content_type='text/xml')
        print response.content
