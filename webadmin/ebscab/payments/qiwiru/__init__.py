#-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from getpaid.backends import PaymentProcessorBase
from django.forms import ValidationError

from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from django.utils.timezone import utc
from base64 import b64encode

from forms import AdditionalFieldsForm, PostBackForm
from collections import defaultdict
import binascii
import listeners
import datetime
import requests
from requests.auth import HTTPBasicAuth
from urlparse import urljoin

from xml_helper import xml2obj
import IPy
import time
import hashlib

class CheckAdditionalFieldsForm(AdditionalFieldsForm):
    def clean_summ(self):
        summ = self.cleaned_data['summ']
        if summ<PaymentProcessor.get_backend_setting('MIN_SUM', PaymentProcessor.MIN_SUM):
            raise ValidationError(u"Сумма должна быть не меньше %s" % PaymentProcessor.get_backend_setting('MIN_SUM', PaymentProcessor.MIN_SUM) )

        return summ
    


result_codes={'-1':u'Произошла ошибка. Проверьте номер телефона и пароль',
'-2':u'Произошла ошибка. Счёт не может быть подтверждён. Возможно у вас недостаточно средств или включено подтверждение действий по SMS',              
'0':u'Успех',
'13':u'Сервер занят, повторите запрос позже',
'150':u'Ошибка авторизации (неверный логин/пароль)',
'210':u'Счет не найден',
'215':u'Счет с таким txn-id уже существует',
'241':u'Сумма слишком мала',
'242':u'Превышена максимальная сумма платежа – 15 000р.',
'278':u'Превышение максимального интервала получения списка счетов',
'298':u'Агента не существует в системе',
'300':u'Неизвестная ошибка',
'330':u'Ошибка шифрования',
'339':u'Не пройден контроль IP-адреса',
'353':u'Включено SMS подтверждение действий. Невозможно проверить баланс.',
'370':u'Превышено максимальное кол-во одновременно выполняемых запросов',
'1000':u'Ошибка выполнения запроса.',
}

payment_codes={
'18':u'Undefined',
'50':u'Выставлен',
'52':u'Проводится',
'60':u'Оплачен',
'150':u'Отменен (ошибка на терминале)',
'151':u'Отменен (ошибка авторизации: недостаточно средств на балансе, отклонен абонентом при оплате с лицевого счета оператора сотовой связи и т.п.).',
'160':u'Отменен',
'161':u'Отменен (Истекло время)',
}



"""
API_ID
API_PASSWORD
TERMINAL_ID
"""



    
class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.qiwiru'
    BACKEND_NAME = _(u'QIWI Россия')
    BACKEND_ACCEPTED_CURRENCY = ('RUB', )
    GATEWAY_URL = "http://ishop.qiwi.ru/xml"
    API_URL = 'https://api.qiwi.com'
    MIN_SUM=0
    _ALLOWED_IPS = ('91.232.230.0/23', '79.142.16.0/20') 
    PAY_SOURCE = 'qw'
    
    
    
    @staticmethod
    def check_allowed_ip(ip, request):
        allowed_ips = PaymentProcessor.get_backend_setting('allowed_ip', PaymentProcessor._ALLOWED_IPS)

        for allowed_ip in allowed_ips:
            if len(allowed_ip) != 0 and IPy.IP(ip) in IPy.IP(allowed_ip):
    
                return  'OK'
        return 'Unknown IP'
    
    @staticmethod
    def form():
        return CheckAdditionalFieldsForm
    
    @staticmethod
    def make_request(url_path, params):
        url = urljoin(PaymentProcessor.API_URL, url_path)
        return requests.put(url, params, headers = {'Accept': 'text/json'}, 
                            auth = HTTPBasicAuth(PaymentProcessor.get_backend_setting('API_ID'),
                                    PaymentProcessor.get_backend_setting('API_PASSWORD')))

    @staticmethod
    def create_invoice(phone_number, payment, summ=0, comment='', *args, **kwargs):
        result = PaymentProcessor.make_request(
                   url_path = '/api/v2/prv/%s/bills/%s' % (PaymentProcessor.get_backend_setting('TERMINAL_ID'),
                                                             payment.id
                                                             ),
                   params = {
                    "user": 'tel:%s' % phone_number,
                    "amount": summ, 
                    
                    'comment': u"Оплата за интернет по договору %s" % payment.account.contract,
                    'lifetime': (payment.created_on+ \
                        datetime.timedelta(hours=PaymentProcessor.get_backend_setting('LIFETIME'))).isoformat(),
                    'ccy': PaymentProcessor.get_backend_setting('DEFAULT_CURRENCY'),
        })
        
        if result.status_code>400:
            return False

    def get_gateway_url(self, request, payment):
        
        form = AdditionalFieldsForm(request.POST)
        if form.is_valid():
            summ = form.cleaned_data['summ']
            phone = form.cleaned_data['phone']
        else:
            return self.GATEWAY_URL, "GET", {}
        

        
        PaymentProcessor.create_invoice(phone, payment, summ=summ)
        
        
        payment_url="https://qiwi.com/order/external/main.action?shop=%s&transaction=%s&pay_source=%s" % (PaymentProcessor.get_backend_setting('TERMINAL_ID'), 
                                                                                                          payment.id,
                                                                                                          PaymentProcessor.get_backend_setting('PAY_SOURCE', PaymentProcessor.PAY_SOURCE))
        
        return payment_url, "GET", {}
    
    @staticmethod
    def response(code=0):
        return  """<?xml version="1.0"?>
<result>
<result_code>%s</result_code>
</result>""" % code
    
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
            if param == 'WMI_SIGNATURE': continue
            if type(value) in [list, tuple]:
                for k in sorted(value):
                    p.append((param, k))
            else:
                p.append((param, value))
        params = p
        lists_by_keys = defaultdict(list)
        for key, value in params:
            lists_by_keys[key].append(unicode(value))
    
        str_buff = PaymentProcessor.get_backend_setting('NOTIFICATION_PASSWORD','')+'|'
        for key in sorted(lists_by_keys, key=icase_key):
            
            str_buff += '|'.join(sorted(lists_by_keys[key], key=icase_key))
                
                

        
        sha_1 = hashlib.sha1()
        sha_1.update(str_buff)
        sha1_string = sha_1.hexdigest()
        
        return binascii.b2a_base64(sha1_string)[:-1]
    

    @staticmethod
    def postback(request):
        from getpaid.models import Payment


            
            
        form = PostBackForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data

            try:
                payment = Payment.objects.get(id=data['bill_id'])
            except:
                return PaymentProcessor.response(210)
        else:

            return PaymentProcessor.response(5)
        
        payment.description = u'Оплачено с %s' % data['user']
        
        if payment.status!='paid' and data['command']=='bill' and data['status']=='paid':
                        
            payment.paid_on = datetime.datetime.now()
            payment.on_success()
            payment.save()
            return PaymentProcessor.response(0)
        else:
            return PaymentProcessor.response(5)


    