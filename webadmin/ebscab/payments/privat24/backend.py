# -*- coding: utf-8 -*-

import hashlib
import logging
import urllib

from django.contrib.sites.models import Site
from django.contrib.sites.requests import RequestSite
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.utils.translation import ugettext_lazy as _

from getpaid.backends import PaymentProcessorBase
from getpaid.models import Payment

from payments.privat24.forms import AdditionalFieldsForm


logger = logging.getLogger('payments.privat24')


class TransactionStatus:
    OK = 'success'
    ERROR = 'failure'


class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.privat24'
    BACKEND_NAME = _(u'Privat24')
    BACKEND_ACCEPTED_CURRENCY = ('UAH',)
    DEFAULT_CURRENCY = 'UAH'
    LANGUAGE = 'ru'
    GATEWAY_URL = 'https://api.privatbank.ua/p24api/ishop'
    BACKEND_LOGO_URL = 'img/privat24.png'

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
        res['amt'] = amount
        res['ccy'] = PaymentProcessor.get_backend_setting('DEFAULT_CURRENCY')
        res['merchant'] = PaymentProcessor.get_backend_setting('MERCHANT_ID')
        res['order'] = payment.id
        res['details'] = u'Пополнение счёта %s на %s %s' % (
            request.user.account.username,
            amount,
            PaymentProcessor.get_backend_setting('DEFAULT_CURRENCY'))
        res['ext_details'] = ''
        res['pay_way'] = 'privat24'
        res['return_url'] = "http://%s" % (site, )
        res['server_url'] = "http://%s%s" % (site,
                                             reverse('getpaid-privat24-pay'))

        return self.GATEWAY_URL, 'POST', res

    @staticmethod
    def error(body, text):
        return text

    @staticmethod
    def compute_sig(payment):
        return hashlib.sha1(
            hashlib.md5(
                payment.encode('utf-8') +
                PaymentProcessor.get_backend_setting('PASSWORD')
            )
            .hexdigest()
        ).hexdigest()

    @staticmethod
    def online(request):
        payment = request.POST.get('payment')
        signature = request.POST.get('signature')

        if str(PaymentProcessor.compute_sig(payment)) != str(signature).strip():
            return "SIGNATURE CHECK ERROR"

        try:
            data = QueryDict(urllib.quote(payment, '=&'))
        except KeyError:
            data = QueryDict(urllib.quote(payment.encode('utf-8'), '=&'))

        order_id = data['order']
        amount = data['amt']
        status = data['state']
        transaction_id = data['ref']

        try:
            payment = Payment.objects.get(id=order_id)
        except Payment.DoesNotExist, ex:
            return PaymentProcessor.error(
                'PAYMENT NOT KNOWN', u'UNKNOWN PAYMENT')
        if status == 'ok':
            payment.on_success(amount=amount)
            payment.external_id = transaction_id
            payment.save()
        elif status == 'test':
            logger.warning(
                'Payment accepted in test mode!\n Got payment object: %s' %
                data)

        return 'OK'
