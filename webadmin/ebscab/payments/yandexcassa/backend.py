# -*- coding: utf-8 -*-

import datetime
from hashlib import md5

from django.utils.translation import ugettext_lazy as _
from lxml import etree
from lxml.builder import E

from billservice.models import Account
from getpaid.backends import PaymentProcessorBase
from getpaid.models import Payment

from payments.yandexcassa.forms import CheckForm, NoticeForm, PaymentFillForm


class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.yandexcassa'
    BACKEND_NAME = _(u'YandexCassa')
    BACKEND_ACCEPTED_CURRENCY = ('RUB',)

    GATEWAY_URL = 'https://money.yandex.ru/eshop.xml'

    def get_gateway_url(self, request, payment):
        form = PaymentFillForm(request.POST)
        if form.is_valid():
            data = {
                'shopId': PaymentProcessor.get_backend_setting(
                    'YANDEX_MONEY_SHOP_ID', ''),
                'sum': '%.2f' % form.cleaned_data['summ'],
                'scid': PaymentProcessor.get_backend_setting(
                    'YANDEX_MONEY_SCID', ''),
                'customerNumber': payment.account.username,
                'paymentType': form.cleaned_data['paymentType'],
                'orderNumber': payment.id,
                'cps_phone': form.cleaned_data.get('cps_phone'),
                'cps_email': form.cleaned_data.get('cps_email')
            }

            return PaymentProcessor.GATEWAY_URL, 'POST', data

    @staticmethod
    def get_check_xml(params):
        element = E.checkOrderResponse(**params)
        return etree.tostring(element,
                              pretty_print=True,
                              xml_declaration=True,
                              encoding='UTF-8')

    @staticmethod
    def get_pay_xml(params):
        element = E.paymentAvisoResponse(**params)
        return etree.tostring(element,
                              pretty_print=True,
                              xml_declaration=True,
                              encoding='UTF-8')

    @staticmethod
    def form():
        return PaymentFillForm

    @staticmethod
    def compute_sig(params):
        """
        action;orderSumAmount;orderSumCurrencyPaycash;orderSumBankPaycash;shopId;invoiceId;customerNumber;shopPassword
        """
        params = [
            params['action'],
            str(params['orderSumAmount']),
            str(params['orderSumCurrencyPaycash']),
            str(params['orderSumBankPaycash']),
            str(params['shopId']),
            str(params['invoiceId']),
            params['customerNumber'],
            PaymentProcessor.get_backend_setting(
                'YANDEX_MONEY_SHOP_PASSWORD', '')
        ]
        s = str(';'.join(params))
        return md5(s).hexdigest().upper()

    @staticmethod
    def check_sig(params):
        return PaymentProcessor.make_md5(params) == params['md5']

    @staticmethod
    def check(request):
        form = CheckForm(request.POST)

        if not form.is_valid():
            return PaymentProcessor.get_check_xml({
                'code': 200,
                'performedDatetime': form.cleaned_data['orderCreatedDatetime'],
                'invoiceId': form.cleaned_data.get('invoiceId'),
                'shopId': form.cleaned_data.get('shopId'),
                'message': _(u'Ошибка разбора параметров'),
                'techMessage': unicode(form.form.errors.items)
            })

        if not PaymentProcessor.check_sig(form.cleaned_data):
            return PaymentProcessor.get_check_xml({
                'code': 1,
                'performedDatetime': form.cleaned_data['orderCreatedDatetime'],
                'invoiceId': form.cleaned_data.get('invoiceId'),
                'shopId': form.cleaned_data.get('shopId'),
                'message': _(u'Ошибка авторизации'),
                'techMessage': unicode(form.form.errors.items)
            })

        try:
            Account.objects.get(
                username=form.cleaned_data['customerNumber'])
        except Account.DoesNotExist, ex:
            return PaymentProcessor.get_check_xml({
                'code': 100,
                'performedDatetime': form.cleaned_data['orderCreatedDatetime'],
                'invoiceId': form.cleaned_data.get('invoiceId'),
                'shopId': form.cleaned_data.get('shopId'),
                'message': _(u'Абонент с указанным username не найден'),
                'techMessage': unicode(form.form.errors.items)
            })

        try:
            Payment.objects.get(id=form.cleaned_data['orderNumber'])
        except Account.DoesNotExist, ex:
            return PaymentProcessor.get_check_xml({
                'code': 100,
                'performedDatetime': form.cleaned_data['orderCreatedDatetime'],
                'invoiceId': form.cleaned_data.get('invoiceId'),
                'shopId': form.cleaned_data.get('shopId'),
                'message': _(u'Указанный платёж не найден'),
                'techMessage': unicode(form.form.errors.items)
            })

        return PaymentProcessor.get_check_xml({
            'code': 0,
            'performedDatetime': datetime.datetime.now(),
            'invoiceId': form.cleaned_data.get('invoiceId'),
            'shopId': form.cleaned_data.get('shopId')
        })

    @staticmethod
    def postback(request):
        form = NoticeForm(request.POST)
        if not form.is_valid():
            return PaymentProcessor.get_pay_xml({
                'code': 200,
                'performedDatetime': form.cleaned_data['performedDatetime'],
                'invoiceId': form.cleaned_data.get('invoiceId'),
                'shopId': form.cleaned_data.get('shopId'),
                'message': _(u'Ошибка разбора параметров'),
                'techMessage': unicode(form.form.errors.items)
            })

        if not PaymentProcessor.check_sig(form.cleaned_data):
            return PaymentProcessor.get_pay_xml({
                'code': 1,
                'performedDatetime': form.cleaned_data['performedDatetime'],
                'invoiceId': form.cleaned_data.get('invoiceId'),
                'shopId': form.cleaned_data.get('shopId'),
                'message': _(u'Ошибка авторизации'),
                'techMessage': unicode(form.form.errors.items)
            })

        try:
            Account.objects.get(
                username=form.cleaned_data['customerNumber'])
        except Account.DoesNotExist, ex:
            return PaymentProcessor.get_pay_xml({
                'code': 200,
                'performedDatetime': form.cleaned_data['performedDatetime'],
                'invoiceId': form.cleaned_data.get('invoiceId'),
                'shopId': form.cleaned_data.get('shopId'),
                'message': _(u'Абонент с указанным username не найден'),
                'techMessage': unicode(form.form.errors.items)
            })

        try:
            payment = Payment.objects.get(id=form.cleaned_data['orderNumber'])
        except Account.DoesNotExist, ex:
            return PaymentProcessor.get_pay_xml({
                'code': 100,
                'performedDatetime': form.cleaned_data['performedDatetime'],
                'invoiceId': form.cleaned_data.get('invoiceId'),
                'shopId': form.cleaned_data.get('shopId'),
                'message': _(u'Указанный платёж не найден'),
                'techMessage': unicode(form.form.errors.items)
            })

        if payment.status != 'paid' and form.cleaned_data['action'] == 'paymentAviso':
            payment.paid_on = datetime.datetime.now()
            payment.on_success(amount=form.cleaned_data['orderSumAmount'])
            payment.save()
        elif form.cleaned_data['action'] != 'paymentAviso':
            payment.delete()

        return PaymentProcessor.get_pay_xml({
            'code': 0,
            'performedDatetime': form.cleaned_data['performedDatetime'],
            'invoiceId': form.cleaned_data.get('invoiceId'),
            'shopId': form.cleaned_data.get('shopId')
        })
