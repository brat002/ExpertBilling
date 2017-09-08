# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .models import PAYMENT_TYPE


def get_backend_param(param, default=None):
    return (settings.GETPAID_BACKENDS_SETTINGS['payments.yandexcassa']
            .get(param, default))


class PaymentFillForm(forms.Form):
    paymentType = forms.CharField(
        label=_(u'Способ оплаты'),
        widget=forms.Select(
            choices=PAYMENT_TYPE.CHOICES),
        min_length=2, max_length=2,
        initial=PAYMENT_TYPE.PC
    )
    summ = forms.FloatField(label=_(u'Сумма'))

    cps_email = forms.EmailField(label=_(u'Email'), required=False)
    cps_phone = forms.CharField(
        label=_(u'Телефон'),
        max_length=15,
        required=False
    )
    order = forms.IntegerField(
        widget=forms.widgets.HiddenInput, required=False)

    backend = forms.CharField(
        initial='payments.yandexcassa', widget=forms.widgets.HiddenInput)


class BasePaymentForm(forms.Form):
    """
        shopArticleId               <no use>
        scid                        scid
        sum                         amount
        customerNumber              user
        orderNumber                 id
        shopSuccessURL                success_url
        shopFailURL                    fail_url
        cps_provider                payment_type
        cps_email                   cps_email
        cps_phone                   cps_phone
        paymentType                    payment_type
        shopId                      shop_id
        invoiceId                   invoice_id
        orderCreatedDatetime        <no use>
        orderSumAmount                order_amount
        orderSumCurrencyPaycash        order_currency
        orderSumBankPaycash            <no use>
        shopSumAmount               shop_amount
        shopSumCurrencyPaycash      shop_currency
        shopSumBankPaycash          <no use>
        paymentPayerCode            payer_code
        paymentDatetime             <no use>
    """

    class ERROR_MESSAGE_CODES:
        BAD_SCID = 0
        BAD_SHOP_ID = 1

    error_messages = {
        ERROR_MESSAGE_CODES.BAD_SCID: _(u'scid не совпадает с YANDEX_MONEY_SCID'),
        ERROR_MESSAGE_CODES.BAD_SHOP_ID: _(u'scid не совпадает с YANDEX_MONEY_SHOP_ID')
    }

    class ACTION:
        CHECK = 'checkOrder'
        CPAYMENT = 'paymentAviso'

        CHOICES = (
            (CHECK, _(u'Проверка заказа')),
            (CPAYMENT, _(u'Уведомления о переводе'))
        )

    shopId = forms.IntegerField(
        initial=get_backend_param('YANDEX_MONEY_SHOP_ID'))
    scid = forms.IntegerField(initial=get_backend_param('YANDEX_MONEY_SCID'))
    customerNumber = forms.CharField(min_length=1, max_length=64)
    paymentType = forms.CharField(
        label=_(u'Способ оплаты'),
        widget=forms.Select(
            choices=PAYMENT_TYPE.CHOICES),
        min_length=2, max_length=2,
        initial=PAYMENT_TYPE.PC
    )
    orderSumBankPaycash = forms.IntegerField()

    md5 = forms.CharField(min_length=32, max_length=32)
    action = forms.CharField(max_length=16)
    backend = forms.CharField(
        initial='payments.yandexcassa', widget=forms.widgets.HiddenInput)

    def clean_scid(self):
        scid = self.cleaned_data['scid']
        if scid != get_backend_param('YANDEX_MONEY_SCID'):
            raise forms.ValidationError(
                self.error_messages[self.ERROR_MESSAGE_CODES.BAD_SCID])
        return scid

    def clean_shopId(self):
        shop_id = self.cleaned_data['shopId']
        if shop_id != get_backend_param('YANDEX_MONEY_SHOP_ID'):
            raise forms.ValidationError(
                self.error_messages[self.ERROR_MESSAGE_CODES.BAD_SHOP_ID])
        return shop_id


class PaymentForm(BasePaymentForm):

    def get_display_field_names(self):
        return ['paymentType', 'cps_email', 'cps_phone', 'sum']

    sum = forms.FloatField(label=_(u'Сумма'))

    cps_email = forms.EmailField(label=_(u'Email'), required=False)
    cps_phone = forms.CharField(
        label=_(u'Телефон'), max_length=15, required=False)

    def __init__(self, *args, **kwargs):

        super(PaymentForm, self).__init__(*args, **kwargs)

        self.fields.pop('md5')
        self.fields.pop('action')
        self.fields.pop('orderSumBankPaycash')

        if not get_backend_param('YANDEX_MONEY_DEBUG', False):
            for name in self.fields:
                if name not in self.get_display_field_names():
                    self.fields[name].widget = forms.HiddenInput()


class CheckForm(BasePaymentForm):
    invoiceId = forms.IntegerField()
    orderSumAmount = forms.DecimalField(min_value=0, decimal_places=2)
    orderSumCurrencyPaycash = forms.IntegerField()
    shopSumAmount = forms.DecimalField(min_value=0, decimal_places=2)
    shopSumCurrencyPaycash = forms.IntegerField()
    paymentPayerCode = forms.IntegerField(min_value=1)


class NoticeForm(BasePaymentForm):
    invoiceId = forms.IntegerField(min_value=1)
    orderSumAmount = forms.DecimalField(min_value=0, decimal_places=2)
    orderSumCurrencyPaycash = forms.IntegerField()
    shopSumAmount = forms.DecimalField(min_value=0, decimal_places=2)
    shopSumCurrencyPaycash = forms.IntegerField()
    paymentPayerCode = forms.IntegerField(min_value=1)
    cps_email = forms.EmailField(required=False)
    cps_phone = forms.CharField(max_length=15, required=False)
