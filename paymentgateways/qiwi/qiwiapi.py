#-*-coding: utf-8 -*-

import urllib, urllib2
from decimal import Decimal
from xml_helper import xml2obj
HOST="http://ishop.qiwi.ru/xml"
term_id=11468
term_password='df[vehrf2007'
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
""" % (term_password, term_id),
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
    <bill txn-id="123"/>
    </bills-list>
</request>
""" % (term_password, term_id)
}

result_codes={'0':'Успех',
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
        
def get_balance():
    xml = make_request(params['get_balance'])
    if not xml: return None
    o=xml2obj(xml)
    status = status_code(o)
    if status[0]:
        if o.extra[0]['name']=='BALANCE':
           return o.extra[0].data, status[1]

def create_invoice(phone_number,transaction_id, summ=0, comment='', lifetime=48):
    xml = make_request(params['create_invoice'] % (phone_number, summ, transaction_id, lifetime, comment,))
    if not xml: return None
    print xml
    o=xml2obj(xml)
    status = status_code(o)
    return status[1]
    #    if o.extra[0]['name']=='BALANCE':
    #       return o.extra[0].data

    
#print Decimal(get_balance())
print create_invoice('9992945489', 12345, 20, 'test')

#element = ET.XML(a)

#for subelement in element:
#    print subelement.text
#    print subelement.findAll()
#print element.findAll('response/result-code')

"""
<request-type>3</request-type>

<?xml version="1.0" encoding="utf-8"?>
<request>
<protocol-version>4.00</protocol-version>
<request-type>3</request-type>
<extra name="password">df[vehrf2007</extra>
<terminal-id>11468</terminal-id>
<extra name="serial">123</extra>
</request>
"""
