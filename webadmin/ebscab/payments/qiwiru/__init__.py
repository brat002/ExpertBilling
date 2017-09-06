# -*- coding: utf-8 -*-

import binascii
import datetime
import hashlib
import urllib2
from base64 import b64encode
from collections import defaultdict
from copy import deepcopy

from django import forms
from django.contrib.sites.requests import RequestSite
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

import IPy
from billservice.models import Account
from getpaid.backends import PaymentProcessorBase
from getpaid.models import Payment

import listeners
from forms import AdditionalFieldsForm
from xml_helper import xml2obj
import time


class CheckAdditionalFieldsForm(AdditionalFieldsForm):

    def clean_summ(self):
        summ = self.cleaned_data['summ']
        if summ < PaymentProcessor.get_backend_setting(
                'MIN_SUM', PaymentProcessor.MIN_SUM):
            raise ValidationError(_(u"Сумма должна быть не меньше %s" %
                                    PaymentProcessor.get_backend_setting(
                                        'MIN_SUM', PaymentProcessor.MIN_SUM)))

        return summ

params = {
    'create_invoice': u"""\
<?xml version="1.0" encoding="utf-8"?>
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
</request>""",
    'get_invoices_status': u"""\
<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>33</request-type>
    <extra name="password">%(TERMINAL_PASSWORD)s</extra>
    <terminal-id>%(TERMINAL_ID)s</terminal-id>
    <bills-list>
    %(BILLS)s
    </bills-list>
</request>""",
    'get_invoices': u"""\
<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>28</request-type>
     <terminal-id>%s</terminal-id>
    <extra name="password">%s</extra>
    <extra name="dir">0</extra>
    <extra name="from">%s 00:00:00</extra>
    <extra name="to">%s 23:59:59</extra>
</request>""",

    'response': u"""\
<?xml version="1.0" encoding="UTF-8"?>
<response>
<osmp_txn_id>%(TXN_ID)s</osmp_txn_id>
<prv_txn>%(PRV_TXN)s</prv_txn>
<sum>%(SUM)s</sum>
<result>%(RESULT)s</result>
<comment>%(COMMENT)s</comment>
</response>""",

    'response_error': u"""\
<?xml version="1.0" encoding="UTF-8"?>
<response>
<osmp_txn_id>%(TXN_ID)s</osmp_txn_id>
<result>%(RESULT)s</result>
<comment>%(COMMENT)s</comment>
</response>"""
}

result_codes = {
    '-1': _(u'Произошла ошибка. Проверьте номер телефона и пароль'),
    '-2': _(u'Произошла ошибка. Счёт не может быть подтверждён. Возможно '
            u'у вас недостаточно средств или включено подтверждение действий '
            u'по SMS'),
    '0': _(u'Успех'),
    '13': _(u'Сервер занят, повторите запрос позже'),
    '150': _(u'Ошибка авторизации (неверный логин/пароль)'),
    '210': _(u'Счет не найден'),
    '215': _(u'Счет с таким txn-id уже существует'),
    '241': _(u'Сумма слишком мала'),
    '242': _(u'Превышена максимальная сумма платежа – 15 000р.'),
    '278': _(u'Превышение максимального интервала получения списка счетов'),
    '298': _(u'Агента не существует в системе'),
    '300': _(u'Неизвестная ошибка'),
    '330': _(u'Ошибка шифрования'),
    '339': _(u'Не пройден контроль IP-адреса'),
    '353': _(u'Включено SMS подтверждение действий. Невозможно '
             u'проверить баланс.'),
    '370': _(u'Превышено максимальное кол-во одновременно выполняемых запросов'),
    '1000': _(u'Ошибка выполнения запроса.')
}

payment_codes = {
    '18': _(u'Undefined'),
    '50': _(u'Выставлен'),
    '52': _(u'Проводится'),
    '60': _(u'Оплачен'),
    '150': _(u'Отменен (ошибка на терминале)'),
    '151': _(u'Отменен (ошибка авторизации: недостаточно средств на балансе, '
             u'отклонен абонентом при оплате с лицевого счета оператора '
             u'сотовой связи и т.п.).'),
    '160': _(u'Отменен'),
    '161': _(u'Отменен (Истекло время)')
}

term_codes = {
    0: _(u'ОК'),
    1: _(u'Временная ошибка. Повторите запрос позже'),
    4: _(u'Неверный формат идентификатора Клиента'),
    5: _(u'Идентификатор Клиента не найден (Ошиблись номером)'),
    7: _(u'Прием Платежа запрещен Поставщиком'),
    90: _(u'Проведение Платежа не окончено'),
    241: _(u'Сумма слишком мала'),
    242: _(u'Сумма слишком велика'),
    300: _(u'Другая ошибка Поставщика')
}


def status_code(obj):
    if obj.result_code.data == '0':
        return int(obj.result_code.data), result_codes[obj.result_code.data]
    return int(obj.result_code.data), result_codes[obj.result_code.data]


def payment_code(obj):
    if obj.status == '50':
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
    MIN_SUM = 0
    _ALLOWED_IP = '79.142.16.0/20',

    @staticmethod
    def check_allowed_ip(ip, request, body):
        allowed_ip = PaymentProcessor.get_backend_setting(
            'allowed_ip', PaymentProcessor._ALLOWED_IP)

        if len(allowed_ip) != 0 and IPy.IP(ip) not in IPy.IP(allowed_ip):
            return u'Unknown IP'
        return 'OK'

    @staticmethod
    def form():
        return CheckAdditionalFieldsForm

    @staticmethod
    def make_request(xml):
        request = urllib2.Request(
            PaymentProcessor.GATEWAY_URL, xml.encode('utf-8'))
        try:
            response = urllib2.urlopen(request)
            return response.read()
        except Exception, e:
            print e
        return """<response><result-code fatal="true">1000</result-code>"""

    @staticmethod
    def create_invoice(phone_number, payment, summ=0, comment=''):
        xml = PaymentProcessor.make_request(params['create_invoice'] % {
            "TERMINAL_PASSWORD": PaymentProcessor.get_backend_setting(
                'TERMINAL_PASSWORD'),
            "TERMINAL_ID": PaymentProcessor.get_backend_setting('TERMINAL_ID'),
            "PHONE": phone_number,
            "AMOUNT": summ,
            "PAYMENT_ID": payment.id,
            'ALARM_SMS': PaymentProcessor.get_backend_setting(
                'ALARM_SMS', PaymentProcessor.ALARM_SMS),
            'ACCEPT_CALL': PaymentProcessor.get_backend_setting(
                'ACCEPT_CALL', PaymentProcessor.ACCEPT_CALL),
            'LIFETIME': PaymentProcessor.get_backend_setting(
                'LIFETIME', PaymentProcessor.LIFETIME),
            'COMMENT': _(u"Оплата за интернет по договору %s" %
                         payment.account.contract)
        })

        if not xml:
            return None
        o = xml2obj(xml)
        status = status_code(o)
        return status

    def get_gateway_url(self, request, payment):
        form = AdditionalFieldsForm(request.POST)
        if form.is_valid():
            summ = form.cleaned_data['summ']
            phone = form.cleaned_data['phone']
        else:
            return self.GATEWAY_URL, "GET", {}

        status, message = PaymentProcessor.create_invoice(
            phone, payment, summ=summ)

        payment_url = ("https://w.qiwi.ru/externalorder.action"
                       "?shop=%s&transaction=%s") % (
            PaymentProcessor.get_backend_setting('TERMINAL_ID'), payment.id)

        return payment_url, "GET", {}

    @staticmethod
    def error(txn_id, code):
        dt = datetime.datetime.now()
        return params['response_error'] % {
            'TXN_ID': txn_id,
            'RESULT': code,
            'COMMENT': term_codes[code]
        }

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
        # FIXME: undefined variable
        md5_string = md5(str_buff.encode('1251')).digest()

        return binascii.b2a_base64(md5_string)[:-1]

    @staticmethod
    def postback(request):
        class PostBackForm(forms.Form):
            WMI_MERCHANT_ID = forms.CharField(
                initial=PaymentProcessor.get_backend_setting('MERCHANT_ID', ''))
            WMI_PAYMENT_AMOUNT = forms.CharField()
            WMI_CURRENCY_ID = forms.CharField(
                # FIXME: undefined variable
                initial=CURRENCIES.get(PaymentProcessor.get_backend_setting(
                    'DEFAULT_CURRENCY',
                    PaymentProcessor.get_backend_setting(
                        'BACKEND_ACCEPTED_CURRENCY',
                        ['RUB'])[0]
                ))
            )
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
            if PaymentProcessor.compute_sig(data) != data['WMI_SIGNATURE']:
                return (u'WMI_RESULT=RETRY&WMI_DESCRIPTION=' +
                        _(u'Неверная цифровая подпись'))
            try:
                payment = Payment.objects.get(id=data['WMI_PAYMENT_NO'])
            except:
                return (u'WMI_RESULT=RETRY&WMI_DESCRIPTION=' +
                        _(u'Платёж в ID %s не найден' % data['WMI_PAYMENT_NO']))
        else:
            print form._errors
            return (u'WMI_RESULT=RETRY&WMI_DESCRIPTION=' +
                    _(u'Не все поля заполнены или заполнены неверно'))
        payment.external_id = data['WMI_ORDER_ID']
        payment.description = _(u'Оплачено с %s' % data['WMI_TO_USER_ID'])

        if data['WMI_ORDER_STATE'] == 'Accepted' and \
                payment.on_success(amount=data['WMI_PAYMENT_AMOUNT']):
            payment.save()
            return 'WMI_RESULT=OK'
        else:
            return u'WMI_RESULT=RETRY&WMI_DESCRIPTION=' + _(u'Ошибка обработки платежа')

    @staticmethod
    def check(request):
        if not request.GET:
            # FIXME: using variable before assignment
            return PaymentProcessor.error(txn_id, 300)

        txn_id = request.GET.get('txn_id')
        amount = request.GET.get('sum')
        acc = request.GET.get('account')

        if not amount:
            return PaymentProcessor.error(txn_id, 300)
        else:
            amount = float(amount)

        if len(str(acc)) > 32:
            return PaymentProcessor.error(txn_id, 4)

        try:
            account = Account.objects.get(contract=acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(txn_id, 5)

        dt = datetime.datetime.now()
        if amount < PaymentProcessor.get_backend_setting(
                'MIN_SUM', PaymentProcessor.MIN_SUM):
            return PaymentProcessor.error(txn_id, 241)

        return params['response_error'] % {
            'TXN_ID': txn_id,
            'RESULT': 0,
            'COMMENT': term_codes[0],
        }

    @staticmethod
    def pay(request):
        if not request.GET:
            # FIXME: using variable before assignment
            return PaymentProcessor.error(txn_id, 300)
        txn_id = request.GET.get('txn_id')
        amount = request.GET.get('sum')
        txn_date = datetime.datetime(
            *time.strptime(request.GET.get('txn_date'), "%Y%m%d%H%M%S")[0:5])
        acc = request.GET.get('account')

        if not amount:
            return PaymentProcessor.error(txn_id, 300)
        else:
            amount = float(amount)

        if len(str(acc)) > 32:
            return PaymentProcessor.error(txn_id, 4)

        try:
            account = Account.objects.get(contract=acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(txn_id, 5)

        dt = datetime.datetime.now()
        if amount < PaymentProcessor.get_backend_setting(
                'MIN_SUM', PaymentProcessor.MIN_SUM):
            return PaymentProcessor.error(txn_id, 241)

        try:
            payment = Payment.objects.get(
                backend=PaymentProcessor.BACKEND, external_id=txn_id)
        except:
            payment = Payment.create(
                account,
                None,
                PaymentProcessor.BACKEND,
                amount=amount,
                external_id=txn_id)

        payment.on_success(amount=amount)
        payment.paid_on = txn_date
        payment.save()

        return params['response'] % {
            'TXN_ID': txn_id,
            'PRV_TXN': payment.id,
            'SUM': '%.2f' % payment.amount,
            'RESULT': 0,
            'COMMENT': term_codes[0],
        }
