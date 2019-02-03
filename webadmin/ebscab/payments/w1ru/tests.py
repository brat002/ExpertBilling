# -*- coding: utf-8 -*-

import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from billservice.models import Account, TransactionType
from getpaid.models import Payment

from payments.w1ru import PaymentProcessor


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
        c.login(username='010001', password='010001')
        TransactionType.objects.create(
            name=u'Единая касса', internal_name='payments.w1ru')
        response = c.post(reverse('getpaid-new-payment'), {
            "summ": "10.00",
            "backend": "payments.w1ru"
        })

        payment = Payment.objects.filter().order_by('-id')[0]
        print response.content

        d = {
            "WMI_MERCHANT_ID": PaymentProcessor.get_backend_setting(
                'MERCHANT_ID', ''),
            "WMI_PAYMENT_AMOUNT": '10.00',
            "WMI_CURRENCY_ID": '643',
            "WMI_TO_USER_ID": '123456789012',
            "WMI_PAYMENT_NO": payment.id,
            "WMI_ORDER_ID": '12345',
            "WMI_DESCRIPTION": 'descr',
            "WMI_SUCCESS_URL": 'http://ya.ru',
            "WMI_FAIL_URL": 'http://ya.ru',
            "WMI_EXPIRED_DATE": '2012-01-01T00:00:00',
            "WMI_CREATE_DATE": '2012-01-01T00:00:00',
            "WMI_UPDATE_DATE": '2012-01-01T00:00:00',
            "WMI_ORDER_STATE": 'Accepted'
        }
        d['WMI_SIGNATURE'] = PaymentProcessor.compute_sig(d)
        response = c.post(reverse('getpaid-w1ru-postback'), d)
        print response.content
