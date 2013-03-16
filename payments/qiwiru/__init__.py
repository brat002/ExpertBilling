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

from forms import AdditionalFieldsForm
from collections import defaultdict
import binascii

from copy import deepcopy
import urllib2
from xml_helper import xml2obj

params={
'create_invoice':u"""<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>30</request-type>
    <extra name="password">%(TERMINAL_PASSWORD)s</extra>
    <terminal-id>%(TERMINAL_ID)s</terminal-id>
    <extra name="to-account">%(PHONE)s</extra>
    <extra name="amount">%(AMOUNT)s</extra>
    <extra name="txn-id">%(PAYMENT_ID)s</extra>
    <extra name="ALARM_SMS">%(ALARM_SMS)s</extra>
    <extra name="ACCEPT_CALL">%(ACCEPT_CALL)s</extra>
    <extra name="ltime">%(LIFETIME)s</extra>
    <extra name="comment">%(COMMENT)s</extra>
    <extra name="create-agt">1</extra>
</request>
""",
'get_invoices_status':u"""<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>33</request-type>
    <extra name="password">%(TERMINAL_PASSWORD)s</extra>
    <terminal-id>%(TERMINAL_ID)s</terminal-id>
    <bills-list>
    %(BILLS)s
    </bills-list>
</request>
""",
'get_invoices':u"""<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>28</request-type>
     <terminal-id>%s</terminal-id>
    <extra name="password">%s</extra>
    <extra name="dir">0</extra>
    <extra name="from">%s 00:00:00</extra>
    <extra name="to">%s 23:59:59</extra>
</request>
"""
}

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

        
def status_code(obj):
    if obj.result_code.data=='0':
        return int(obj.result_code.data), result_codes[obj.result_code.data]
    return int(obj.result_code.data), result_codes[obj.result_code.data]

def payment_code(obj):
    if obj.status=='50':
        return int(obj.status), payment_codes[obj.status]
    return int(obj.status), payment_codes[obj.status]





    
class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.qiwiru'
    BACKEND_NAME = _(u'QIWI Россия')
    BACKEND_ACCEPTED_CURRENCY = ('RUB', )
    GATEWAY_URL = "http://ishop.qiwi.ru/xml"
    LIFETIME = 48
    ALARM_SMS = 0
    ACCEPT_CALL = 0

    
    
    @staticmethod
    def form():
        return AdditionalFieldsForm
    
    @staticmethod
    def make_request(xml):
    
        request = urllib2.Request(PaymentProcessor.GATEWAY_URL, xml.encode('utf-8'))
        try:
            response = urllib2.urlopen(request)
            return response.read()
        except Exception, e:
            print e
        return """<response><result-code fatal="true">1000</result-code>"""

    @staticmethod
    def create_invoice(phone_number, payment, summ=0, comment=''):
        xml = PaymentProcessor.make_request(params['create_invoice'] % {
                                                                        "TERMINAL_PASSWORD": PaymentProcessor.get_backend_setting('TERMINAL_PASSWORD'),
                                                                        "TERMINAL_ID":  PaymentProcessor.get_backend_setting('TERMINAL_ID'),
                                                                        "PHONE": phone_number,
                                                                        "AMOUNT": summ, 
                                                                        "PAYMENT_ID": payment.id,
                                                                        'ALARM_SMS': PaymentProcessor.get_backend_setting('ALARM_SMS', PaymentProcessor.ALARM_SMS), 
                                                                        'ACCEPT_CALL': PaymentProcessor.get_backend_setting('ACCEPT_CALL', PaymentProcessor.ACCEPT_CALL),
                                                                        'LIFETIME': PaymentProcessor.get_backend_setting('LIFETIME', PaymentProcessor.LIFETIME),
                                                                        'COMMENT': u"Оплата за интернет по договору %s" % payment.account.contract,
                                                                        })
        
        if not xml: return None
        o=xml2obj(xml)
        status = status_code(o)
        return status

    def get_gateway_url(self, request, payment):
        
        form = AdditionalFieldsForm(request.POST)
        if form.is_valid():
            summ = form.cleaned_data['summ']
            phone = form.cleaned_data['phone']
        else:
            return self.GATEWAY_URL, "GET", {}
        
        status, message = PaymentProcessor.create_invoice(phone, payment, summ=summ)
        
        
        payment_url="https://w.qiwi.ru/externalorder.action?shop=%s&transaction=%s" % (PaymentProcessor.get_backend_setting('TERMINAL_ID'), payment.id)
        
        return payment_url, "GET", {}
    
        
    
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
            lists_by_keys[key].append(value)
    
        str_buff = ''
        for key in sorted(lists_by_keys, key=icase_key):
            
            for value in sorted(lists_by_keys[key], key=icase_key):
                
                str_buff += unicode(value)

        str_buff += PaymentProcessor.get_backend_setting('MERCHANT_PASSWORD','')
        md5_string = md5(str_buff.encode('1251')).digest()
        
        return binascii.b2a_base64(md5_string)[:-1]
    

    @staticmethod
    def postback(request):
        from getpaid.models import Payment
        class PostBackForm(forms.Form):
            WMI_MERCHANT_ID = forms.CharField(initial = PaymentProcessor.get_backend_setting('MERCHANT_ID',''))
            WMI_PAYMENT_AMOUNT = forms.CharField()
            WMI_CURRENCY_ID = forms.CharField(initial=CURRENCIES.get(PaymentProcessor.get_backend_setting('DEFAULT_CURRENCY', PaymentProcessor.get_backend_setting('BACKEND_ACCEPTED_CURRENCY', ['RUB'])[0])))
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
            if PaymentProcessor.compute_sig(data)!=data['WMI_SIGNATURE']:
                return u'WMI_RESULT=RETRY&WMI_DESCRIPTION=Неверная цифровая подпись'
            try:
                payment = Payment.objects.get(id=data['WMI_PAYMENT_NO'])
            except:
                return u'WMI_RESULT=RETRY&WMI_DESCRIPTION=Платёж в ID %s не найден' % data['WMI_PAYMENT_NO']
        else:
            print form._errors
            return u'WMI_RESULT=RETRY&WMI_DESCRIPTION=Не все поля заполнены или заполнены неверно'
        payment.external_id = data['WMI_ORDER_ID']
        payment.description = u'Оплачено с %s' % data['WMI_TO_USER_ID']
        
        if data['WMI_ORDER_STATE']=='Accepted' and  payment.on_success(amount=data['WMI_PAYMENT_AMOUNT']):
            payment.save()
            return 'WMI_RESULT=OK'
        else:
            return u'WMI_RESULT=RETRY&WMI_DESCRIPTION=Ошибка обработки платежа'
    

    

