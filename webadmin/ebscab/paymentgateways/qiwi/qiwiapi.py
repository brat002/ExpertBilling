#-*-coding: utf-8 -*-

import urllib, urllib2
from decimal import Decimal
from xml_helper import xml2obj
import datetime
import os
import sys


HOST="http://ishop.qiwi.ru/xml"
term_id=11468
term_password='df[vehrf2007'
lifetime = 48
ALARM_SMS = 0
ALARM_CALL = 0
proxy_host='10.129.112.2'
proxy_port=8080
proxy_username='akuzmitski'
proxy_password='12qwaszx++'

params=u"""<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>33</request-type>
    <extra name="password">%s</extra>
    <terminal-id>%s</terminal-id>
    <bills-list>
    <bill txn-id="123"/>
    </bills-list>
</request>
""" % (term_password, term_id)

params=u"""<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>30</request-type>
    <extra name="password">df[vehrf2007</extra>
    <terminal-id>11468</terminal-id>
    <extra name="comment"></extra>
    <extra name="to-account">1234567890</extra>
    <extra name="amount">100.00</extra>
    <extra name="txn-id">123</extra>
    <extra name="ALARM_SMS">0</extra>
    <extra name="ACCEPT_CALL">0</extra>
    <extra name="ltime">60</extra>
</request>
"""
params={'get_balance':u"""<?xml version="1.0" encoding="utf-8"?>
<request>
<protocol-version>4.00</protocol-version>
<request-type>3</request-type>
<extra name="password">%s</extra>
<terminal-id>%s</terminal-id>
</request>
""",
'create_invoice':u"""<?xml version="1.0" encoding="utf-8"?>
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
</request>
""" % (term_password, term_id, ALARM_SMS, ALARM_CALL,),
'get_invoices_status':u"""<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>33</request-type>
    <extra name="password">%s</extra>
    <terminal-id>%s</terminal-id>
    <bills-list>
    %%s
    </bills-list>
</request>
""" % (term_password, term_id),
'get_invoices':u"""<request>
    <protocol-version>4.00</protocol-version>
    <request-type>28</request-type>
     <terminal-id>%s</terminal-id>
    <extra name="password">%s</extra>
    <extra name="dir">0</extra>
    <extra name="from">%s 00:00:00</extra>
    <extra name="to">%s 23:59:59</extra>
</request>
""",
'accept_payment':u"""<request>
    <protocol-version>4.00</protocol-version>
    <request-type>29</request-type>
    <terminal-id>%s</terminal-id>
    <extra name="password">%s</extra>
    <extra name="status">accept</extra>
    <extra name="bill-id">%s</extra>
    <extra name="trm-txn-id"></extra>
</request>
"""
}

result_codes={'-1':u'Произошла ошибка. Проверьте номер телефона и пароль',
'0':'Успех',
'13':'Сервер занят, повторите запрос позже',
'150':'Ошибка авторизации (неверный логин/пароль)',
'210':'Счет не найден',
'215':'Счет с таким txn-id уже существует',
'241':'Сумма слишком мала',
'242':'Превышена максимальная сумма платежа – 15 000р.',
'278':'Превышение максимального интервала получения списка счетов',
'298':'Агента не существует в системе',
'300':'Неизвестная ошибка',
'330':'Ошибка шифрования',
'339':'Не пройден контроль IP-адреса',
'370':'Превышено максимальное кол-во одновременно выполняемых запросов'}

def make_request(xml):
    print xml
    proxy = urllib2.ProxyHandler({'http': 'http://%s:%s@%s:%s' % (proxy_username, proxy_password, proxy_host, proxy_port, )})
    auth = urllib2.HTTPBasicAuthHandler()
    opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
    urllib2.install_opener(opener)    
    request = urllib2.Request(HOST,xml.encode('utf-8'))
    response = urllib2.urlopen(request)
    try:
        return response.read()
    except Exception, e:
        print e
    return
        
def status_code(obj):
    if obj.result_code.data=='0':
        return int(obj.result_code.data), result_codes[obj.result_code.data]
    return int(obj.result_code.data), result_codes[obj.result_code.data]
        
def get_balance(phone=None, password=None):
    if not (phone and password):
        xml = make_request(params['get_balance']  % (term_password, term_id))
    if phone and password:
        xml = make_request(params['get_balance']  % (password, phone))
    if not xml: return None
    o=xml2obj(xml)
    status = status_code(o)
    print o.__dict__
    if status[0]==0:
        if o.extra[0]['name']=='BALANCE':
            return o.extra[0].data, status[1]
    else:
        return 0, status[1]

def create_invoice(phone_number,transaction_id, summ=0, comment='', lifetime=48):
    xml = make_request(params['create_invoice'] % (phone_number, summ, transaction_id, lifetime, comment,))
    if not xml: return None
    print xml
    o=xml2obj(xml)
    print o.__dict__
    status = status_code(o)
    print status
    return status
    #    if o.extra[0]['name']=='BALANCE':
    #       return o.extra[0].data

def get_invoice_id(phone, password, transaction_id, date):
    date_start = (date - datetime.timedelta(hours=1)).strftime("%d.%m.%Y")
    date_end = (date + datetime.timedelta(hours=1)).strftime("%d.%m.%Y")
    xml = make_request(params['get_invoices'] % (phone, password, date_start, date_end))
    if not xml: return None
    o=xml2obj(xml)
    if not o.account_list: return -1
    for a in o.account_list.account:
        if a['from'].prv=='%s' % term_id and a.term_ransaction=="%s" % transaction_id:
            return a.id
    return -1

def accept_invoice_id(phone, password, transaction_id, date):
    txn_id=get_invoice_id(phone=phone, password=password, transaction_id=transaction_id, date=datetime.datetime.now())
    if txn_id!=-1:
        xml = make_request(params['accept_payment'] % (phone, password, txn_id))
        if not xml: return None
        o=xml2obj(xml)
        return status_code(o)
    return -1, result_codes['-1']
    
def process_invoices():
    sys.path.append('/opt/ebs/web/')
    sys.path.append('/opt/ebs/web/ebscab/')
    sys.path.append('../../../')
    sys.path.append('../../')
    sys.path.append('.')
    
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ebscab.settings'
   
    from paymentgateways.qiwi.models import Invoice
    a = Invoice.objects.filter(autoaccept=False, accepted=False)
    pattern='<bill txn-id="%s"/>'
    p=''
    for x in a:
        p+=pattern % x.id
        
    xml=make_request(params['get_invoices_status'] % p)
    print xml
    o=xml2obj(xml)
    print o.__dict__
    
process_invoices()