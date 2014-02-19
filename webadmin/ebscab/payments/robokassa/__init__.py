#-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from getpaid.backends import PaymentProcessorBase
from django import forms
import hashlib
import datetime
import listeners
from billservice.models import Account
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from django.utils.timezone import utc
from base64 import b64encode

import urllib

CURRENCIES = {
'RUB': 643,
'USD': 840,
'EUR': 978,
'UAH': 980,
}
from collections import defaultdict
import binascii
from hashlib import md5
from copy import deepcopy


    
class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.robokassa'
    BACKEND_NAME = _(u'Robokassa')
    BACKEND_ACCEPTED_CURRENCY = ('RUB', )
    

    GATEWAY_URL = u'https://merchant.roboxchange.com/Index.aspx'

    




    def get_gateway_url(self, request, payment):
        amount = float(request.POST.get('summ'))
        
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
            
        account = request.user.account

        data = {
         'MrchLogin': PaymentProcessor.get_backend_setting('MERCHANT_LOGIN',''),
        'OutSum': "%.2f" % amount,
        'Desc': u'Оплата за интернет'.encode('1251'),
        'InvId': payment.id,
        }
        

 
        data['SignatureValue'] = PaymentProcessor.compute_sig(data)
        

        if PaymentProcessor.get_backend_setting('TEST_MODE', True):
            GATEWAY_URL = u'http://test.robokassa.ru/Index.aspx'
        else:
            GATEWAY_URL = self.GATEWAY_URL

        
        return GATEWAY_URL, "POST", data
    
        
    
    @staticmethod
    def compute_sig(params):
        return md5(':'.join([params.get('MrchLogin'), str(params.get('OutSum')), str(params.get('InvId')), PaymentProcessor.get_backend_setting('PASSWORD1', '')])).hexdigest().upper()
    
    @staticmethod
    def check_sig(params):
        return md5(':'.join([str(params.get('OutSum')), str(params.get('InvId')), PaymentProcessor.get_backend_setting('PASSWORD2', '')])).hexdigest().upper()
    

    @staticmethod
    def postback(request):
        from getpaid.models import Payment
        class PostBackForm(forms.Form):

            OutSum = forms.CharField(max_length=15)
            InvId = forms.IntegerField(min_value=0)
            SignatureValue = forms.CharField(max_length=32)
        
            def clean(self):
                try:
                    signature = self.cleaned_data['SignatureValue'].upper()
                    if signature != PaymentProcessor.check_sig(self.cleaned_data):
                        raise forms.ValidationError(u'Ошибка в контрольной сумме')
                except KeyError:
                    raise forms.ValidationError(u'Пришли не все необходимые параметры')
        
                return self.cleaned_data
        

            
        form = PostBackForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            try:
                payment = Payment.objects.get(id=data['InvId'])
            except:
                #return u'Платёж не найден'
                return 'PAYMENT_NOT_FOUND'
        else:
            return 'SIGN_ERROR'


        payment.on_success(amount=data['OutSum'])
        payment.save()
        return 'OK%s' % data['InvId']

            
    

    

