# -*- coding: utf-8 -*-

from hashlib import md5

from django import forms
from django.utils.translation import ugettext_lazy as _

from getpaid.backends import PaymentProcessorBase
from getpaid.models import Payment


CURRENCIES = {
    'RUB': 643,
    'USD': 840,
    'EUR': 978,
    'UAH': 980
}


class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.robokassa'
    BACKEND_NAME = _(u'Robokassa')
    BACKEND_ACCEPTED_CURRENCY = ('RUB',)

    GATEWAY_URL = u'https://merchant.roboxchange.com/Index.aspx'

    def get_gateway_url(self, request, payment):
        amount = float(request.POST.get('summ'))
        data = {
            'MrchLogin': PaymentProcessor.get_backend_setting(
                'MERCHANT_LOGIN', ''),
            'OutSum': '%.2f' % amount,
            'Desc': _(u'Оплата за интернет'),
            'InvId': payment.id
        }
        data['SignatureValue'] = PaymentProcessor.compute_sig(data)

        if PaymentProcessor.get_backend_setting('TEST_MODE', True):
            GATEWAY_URL = u'http://test.robokassa.ru/Index.aspx'
        else:
            GATEWAY_URL = self.GATEWAY_URL

        return GATEWAY_URL, 'POST', data

    @staticmethod
    def compute_sig(params):
        return md5(
            ':'.join([
                params.get('MrchLogin'),
                str(params.get('OutSum')),
                str(params.get('InvId')),
                PaymentProcessor.get_backend_setting('PASSWORD1', '')
            ])
        ).hexdigest().upper()

    @staticmethod
    def check_sig(params):
        return md5(
            ':'.join([
                str(params.get('OutSum')),
                str(params.get('InvId')),
                PaymentProcessor.get_backend_setting('PASSWORD2', '')
            ])
        ).hexdigest().upper()

    @staticmethod
    def postback(request):
        class PostBackForm(forms.Form):
            OutSum = forms.CharField(max_length=15)
            InvId = forms.IntegerField(min_value=0)
            SignatureValue = forms.CharField(max_length=32)

            def clean(self):
                try:
                    signature = self.cleaned_data['SignatureValue'].upper()
                    if signature != PaymentProcessor.check_sig(self.cleaned_data):
                        raise forms.ValidationError(
                            _(u'Ошибка в контрольной сумме'))
                except KeyError:
                    raise forms.ValidationError(
                        _(u'Пришли не все необходимые параметры'))

                return self.cleaned_data

        form = PostBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                payment = Payment.objects.get(id=data['InvId'])
            except:
                return 'PAYMENT_NOT_FOUND'
        else:
            return 'SIGN_ERROR'

        payment.on_success(amount=data['OutSum'])
        payment.save()
        return 'OK%s' % data['InvId']
