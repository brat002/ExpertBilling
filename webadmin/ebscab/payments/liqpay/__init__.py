# -*- coding: utf-8 -*-

import hashlib
import datetime
import urllib
from base64 import b64encode, b64decode

from BeautifulSoup import BeautifulSoup
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from getpaid.backends import PaymentProcessorBase

from billservice.models import Account
from getpaid.models import Payment

import listeners
from forms import AdditionalFieldsForm


class TransactionStatus:
    OK = 'success'
    ERROR = 'failure'


class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.liqpay'
    BACKEND_NAME = _(u'Liqpay Украина')
    PAY_WAY = ('card', 'liqpay', 'delayed')
    BACKEND_ACCEPTED_CURRENCY = ('UAH', 'RUB')
    DEFAULT_CURRENCY = 'UAH'
    LANGUAGE = 'ru'
    GATEWAY_URL = 'https://www.liqpay.com/api/pay'

    _ALLOWED_IP = ('93.183.196.28', '93.183.196.26')
    EXPIRE_TIME = 240

    @staticmethod
    def form():
        return AdditionalFieldsForm

    def get_gateway_url(self, request, payment):

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        amount = float(request.POST.get('summ'))

        res = {}
        res['public_key'] = PaymentProcessor.get_backend_setting('PUBLIC_KEY')
        res['amount'] = amount
        res['currency'] = \
            PaymentProcessor.get_backend_setting('DEFAULT_CURRENCY')
        res['description'] = u'Internet payment'
        res['order_id'] = payment.id
        res['result_url'] = "http://%s" % (site, )
        res['server_url'] = "http://%s%s" % (site,
                                             reverse('getpaid-liqpay-pay'))
        res['type'] = 'buy'
        res['language'] = PaymentProcessor.get_backend_setting('LANGUAGE')

        res['signature'] = b64encode(hashlib.sha1(
            PaymentProcessor.get_backend_setting('PRIVATE_KEY') +
            str(res['amount']) +
            res['currency'] +
            res['public_key'] +
            str(res['order_id']) +
            res['type'] +
            res['description'] +
            res['result_url'] +
            res['server_url'])
            .digest())

        return self.GATEWAY_URL, "POST", res

    @staticmethod
    def error(body, text):
        return text

    @staticmethod
    def compute_sig(data):
        return b64encode(hashlib.sha1(
            PaymentProcessor.get_backend_setting('PRIVATE_KEY') +
            data.get('amount') +
            data.get('currency') +
            data.get('public_key') +
            data.get('order_id') +
            data.get('type') +
            data.get('description') +
            data.get('status') +
            data.get('transaction_id') +
            data.get('sender_phone'))
            .digest())

    @staticmethod
    def online(request):
        signature = request.POST.get('signature')
        if str(PaymentProcessor.compute_sig(request.POST)) != \
                str(signature).strip():
            return "SIGNATURE CHECK ERROR"

        data = request.POST
        order_id = data['order_id']
        amount = data['amount']
        currency = data['currency']
        description = data['description']
        type = data['type']
        status = data['status']
        transaction_id = data['transaction_id']
        sender_phone = data['sender_phone']

        try:
            payment = Payment.objects.get(id=order_id)
        except Payment.DoesNotExist, ex:
            return PaymentProcessor.error(
                'PAYMENT NOT KNOWN', u'UNKNOWN PAYMENT')
        if status == 'success':
            payment.on_success(amount=amount)
            payment.external_id = transaction_id
            payment.save()

        return 'OK'
