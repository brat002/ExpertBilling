# -*- coding: utf-8 -*-

import binascii
import datetime
import urllib
from base64 import b64encode
from collections import defaultdict
from copy import deepcopy
from hashlib import md5

from django import forms
from django.contrib.sites.requests import RequestSite, Site
from django.core.urlresolvers import reverse
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from billservice.models import Account
from getpaid.backends import PaymentProcessorBase
from getpaid.models import Payment

import listeners


CURRENCIES = {
    'RUB': 643,
    'USD': 840,
    'EUR': 978,
    'UAH': 980,
}


class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.w1ru'
    BACKEND_NAME = _(u'Единая касса')
    BACKEND_ACCEPTED_CURRENCY = ('RUB', 'USD', 'EUR', 'UAH')
    GATEWAY_URL = 'https://merchant.w1.ru/checkout/default.aspx'
    EXPIRE_DAYS = 31

    def get_gateway_url(self, request, payment):
        amount = float(request.POST.get('summ'))

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        account = request.user.account

        data = {
         'WMI_MERCHANT_ID': PaymentProcessor.get_backend_setting(
            'MERCHANT_ID', ''),
            'WMI_PAYMENT_AMOUNT': "%.2f" % amount,
            'WMI_CURRENCY_ID': CURRENCIES.get(
                PaymentProcessor.get_backend_setting(
                    'DEFAULT_CURRENCY',
                    PaymentProcessor.get_backend_setting(
                        'BACKEND_ACCEPTED_CURRENCY',
                        ['RUB'])[0]
                )
            ),
            'WMI_PAYMENT_NO': payment.id,
            'WMI_DESCRIPTION': "BASE64:%s" % b64encode(
                (u'Internet payment %s' %
                 payment.account.contract).encode('utf-8')),
            'WMI_SUCCESS_URL': ("http://%s%s" %
                                (site, reverse('getpaid-w1ru-success'))),
            'WMI_FAIL_URL': ("http://%s%s" %
                             (site, reverse('getpaid-w1ru-failure'))),
            'WMI_EXPIRED_DATE': (payment.created_on.replace(tzinfo=utc) +
                                 datetime.timedelta(days=PaymentProcessor.get_backend_setting(
                                     'EXPIRE_DAYS', PaymentProcessor.EXPIRE_DAYS
                                 ))
                                 ).strftime('%Y-%m-%dT%H:%M:%S')
        }

        if PaymentProcessor.get_backend_setting('PTENABLED', []):
            data.update({
                'WMI_PTENABLED': PaymentProcessor.get_backend_setting(
                    'PTENABLED', [])
            })

        if PaymentProcessor.get_backend_setting('PTDISABLED', []):
            data.update({
                'WMI_PTDISABLED': PaymentProcessor.get_backend_setting(
                    'PTDISABLED', [])
            })

        data['WMI_SIGNATURE'] = PaymentProcessor.compute_sig(data)

        print 'data=', data
        return self.GATEWAY_URL, "POST", data

    @staticmethod
    def compute_sig(params):
        """
        Base64(Byte(MD5(Windows1251(Sort(Params) + SecretKey))))
        params - list of tuples [('WMI_CURRENCY_ID', 643), ('WMI_PAYMENT_AMOUNT', 10)]
        exclude WMI_SIGNATURE
        """
        icase_key = lambda s: unicode(s).lower()

        p = []
        for param, value in params.items():
            if param == 'WMI_SIGNATURE':
                continue
            if type(value) in [list, tuple]:
                for k in sorted(value):
                    p.append((param, k))
            else:
                p.append((param, value))
        params = p
        lists_by_keys = defaultdict(list)
        for key, value in params:
            lists_by_keys[key].append(value)

        str_buff = ''
        for key in sorted(lists_by_keys, key=icase_key):
            for value in sorted(lists_by_keys[key], key=icase_key):
                str_buff += unicode(value)

        str_buff += PaymentProcessor.get_backend_setting(
            'MERCHANT_PASSWORD', '')
        md5_string = md5(str_buff.encode('1251')).digest()

        return binascii.b2a_base64(md5_string)[:-1]

    @staticmethod
    def postback(request):
        class PostBackForm(forms.Form):
            WMI_MERCHANT_ID = forms.CharField(
                initial=PaymentProcessor.get_backend_setting(
                    'MERCHANT_ID', '')
            )
            WMI_PAYMENT_AMOUNT = forms.CharField()
            WMI_CURRENCY_ID = forms.CharField(
                initial=CURRENCIES.get(PaymentProcessor.get_backend_setting(
                    'DEFAULT_CURRENCY',
                    PaymentProcessor.get_backend_setting(
                        'BACKEND_ACCEPTED_CURRENCY', ['RUB'])[0]
                ))
            )
            if 'WMI_TO_USER_ID' in request.POST:
                WMI_TO_USER_ID = forms.CharField()

            WMI_PAYMENT_NO = forms.CharField()
            WMI_ORDER_ID = forms.CharField()
            WMI_DESCRIPTION = forms.CharField()
            WMI_SUCCESS_URL = forms.CharField()
            WMI_FAIL_URL = forms.CharField()
            WMI_EXPIRED_DATE = forms.CharField()
            WMI_CREATE_DATE = forms.CharField()
            WMI_UPDATE_DATE = forms.CharField()
            WMI_ORDER_STATE = forms.CharField()
            WMI_SIGNATURE = forms.CharField()

        form = PostBackForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            if PaymentProcessor.compute_sig(request.POST) != \
                    data['WMI_SIGNATURE']:
                return u'WMI_RESULT=RETRY&WMI_DESCRIPTION=%s' % \
                    urllib.quote_plus(_(u'Неверная цифровая подпись'))
            try:
                payment = Payment.objects.get(id=data['WMI_PAYMENT_NO'])
            except:
                return ((u'WMI_RESULT=RETRY&WMI_DESCRIPTION=%s' %
                         urllib.quote_plus(_(u'Платёж c ID %s не найден' %
                                             data['WMI_PAYMENT_NO'])))
                        .encode('utf-8'))
        else:
            print form._errors
            return u'WMI_RESULT=RETRY&WMI_DESCRIPTION=%s' % \
                urllib.quote_plus(
                    _(u'Не все поля заполнены или заполнены неверно'))
        payment.external_id = data['WMI_ORDER_ID']

        if data['WMI_ORDER_STATE'] == 'Accepted':
            payment.on_success(amount=data['WMI_PAYMENT_AMOUNT'])
            payment.save()
            return 'WMI_RESULT=OK&WMI_DESCRIPTION=%s' % \
                urllib.quote_plus(_(u'Order successfully processed'))
        else:
            return u'WMI_RESULT=RETRY&WMI_DESCRIPTION=%s' % \
                urllib.quote_plus(_(u'Ошибка обработки платежа'))
