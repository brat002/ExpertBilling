# -*- coding: utf-8 -*-


import datetime
import urllib2

from django.utils.translation import ugettext_lazy as _

from paymentgateways.qiwi.models import Invoice
from paymentgateways.qiwi.utils import xml2obj


HOST = 'http://ishop.qiwi.ru/xml'
TERM_ID = 0
TERM_PASSWORD = ''
LIFETIME = 48  # в часах
ALARM_SMS = 0
ALARM_CALL = 0
PROXY_HOST = ''
PROXY_PORT = 8080
PROXY_USERNAME = ''
PROXY_PASSWORD = ''

GET_BALANCE_TEMPLATE = u'''\
<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>3</request-type>
    <extra name="password">%s</extra>
    <terminal-id>%s</terminal-id>
</request>
'''

CREATE_INVOICE_TEMPLATE = u'''\
<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>30</request-type>
    <extra name="password">%s</extra>
    <terminal-id>%s</terminal-id>
    <extra name="to-account">%%s</extra>
    <extra name="amount">%%s</extra>
    <extra name="txn-id">%%s</extra>
    <extra name="ALARM_SMS">%s</extra>
    <extra name="ACCEPT_CALL">%s</extra>
    <extra name="ltime">%%s</extra>
    <extra name="comment">%%s</extra>
    <extra name="create-agt">1</extra>
</request>
''' % (TERM_PASSWORD, TERM_ID, ALARM_SMS, ALARM_CALL)

GET_INVOICE_STATUS_TEMPLATE = u'''\
<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>33</request-type>
    <extra name="password">%s</extra>
    <terminal-id>%s</terminal-id>
    <bills-list>
        %%s
    </bills-list>
</request>
''' % (TERM_PASSWORD, TERM_ID)

GET_INVOICES_TEMPLATE = u'''\
<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>28</request-type>
     <terminal-id>%s</terminal-id>
    <extra name="password">%s</extra>
    <extra name="dir">0</extra>
    <extra name="from">%s 00:00:00</extra>
    <extra name="to">%s 23:59:59</extra>
</request>
'''

ACCEPT_PAYMENT_TEMPLATE = u'''\
<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>29</request-type>
    <terminal-id>%s</terminal-id>
    <extra name="password">%s</extra>
    <extra name="status">accept</extra>
    <extra name="bill-id">%s</extra>
    <extra name="trm-txn-id"></extra>
</request>
'''

RESULT_CODES = {
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

PAYMENT_CODES = {
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


def make_request(xml):
    if PROXY_HOST:
        if PROXY_USERNAME:
            proxy = urllib2.ProxyHandler({
                'http': 'http://%s:%s@%s:%s' % (PROXY_USERNAME,
                                                PROXY_PASSWORD,
                                                PROXY_HOST,
                                                PROXY_PORT)
            })
        else:
            proxy = urllib2.ProxyHandler({
                'http': 'http://%s:%s' % (PROXY_HOST,
                                          PROXY_PORT)
            })
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
    request = urllib2.Request(HOST, xml.encode('utf-8'))
    try:
        response = urllib2.urlopen(request)
        return response.read()
    except Exception, e:
        print e
    return '<response><result-code fatal="true">1000</result-code>'


def status_code(obj):
    if obj.result_code.data == '0':
        return int(obj.result_code.data), RESULT_CODES[obj.result_code.data]
    return int(obj.result_code.data), RESULT_CODES[obj.result_code.data]


def payment_code(obj):
    if obj.status == '50':
        return int(obj.status), PAYMENT_CODES[obj.status]
    return int(obj.status), PAYMENT_CODES[obj.status]


def get_balance(phone=None, password=None):
    if not (phone and password):
        xml = make_request(GET_BALANCE_TEMPLATE % (TERM_PASSWORD, TERM_ID))
    if phone and password:
        xml = make_request(GET_BALANCE_TEMPLATE % (password, phone))
    if not xml:
        return None
    o = xml2obj(xml)
    status = status_code(o)
    if status[0] == 0:
        if o.extra[0]['name'] == 'BALANCE':
            return o.extra[0].data, status[1]
    else:
        return 0, status[1]


def create_invoice(phone_number, transaction_id, summ=0, comment='',
                   lifetime=LIFETIME):
    xml = make_request(CREATE_INVOICE_TEMPLATE % (
        phone_number, summ, transaction_id, lifetime, comment))
    if not xml:
        return None
    o = xml2obj(xml)
    status = status_code(o)
    return status


def get_invoice_id(phone, password, transaction_id, date):
    date_start = (date - datetime.timedelta(hours=24)).strftime('%d.%m.%Y')
    date_end = (date + datetime.timedelta(hours=24)).strftime('%d.%m.%Y')
    xml = make_request(GET_INVOICES_TEMPLATE % (
        phone, password, date_start, date_end))
    if not xml:
        return None

    o = xml2obj(xml)
    if not o.account_list:
        return -1
    for a in o.account_list.account:
        if a['from'].prv == '%s' % TERM_ID and \
                a.term_ransaction == '%s' % transaction_id:
            return a.id
    return -1


def accept_invoice_id(phone, password, transaction_id, date):
    txn_id = get_invoice_id(phone=phone,
                            password=password,
                            transaction_id=transaction_id,
                            date=datetime.datetime.now())
    if txn_id != -1:
        xml = make_request(ACCEPT_PAYMENT_TEMPLATE % (
            phone, password, txn_id))
        if not xml:
            return None
        o = xml2obj(xml)
        return status_code(o)
    return -1, RESULT_CODES['-1']


def process_invoices():
    a = Invoice.objects.filter(autoaccept=False, accepted=False, deleted=False)
    pattern = '<bill txn-id="%s"/>'
    p = ''
    for x in a:
        p += pattern % x.id

    xml = make_request(GET_INVOICE_STATUS_TEMPLATE % p)
    o = xml2obj(xml)
    if status_code(o)[0] != 0:
        return
    for x in a:
        if not o.bills_list:
            continue
        for item in o.bills_list.bill:
            p_code, _ = payment_code(item)
            if p_code == 60 and int(item.id) == x.id:
                x.accepted = True
                x.date_accepted = datetime.datetime.now()
                x.save()
                continue
        if p_code > 100:
            x.deleted = True
            x.save()


if __name__ == '__main__':
    process_invoices()
