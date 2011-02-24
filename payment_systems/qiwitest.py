import urllib, urllib2
from decimal import Decimal
from xml_helper import xml2obj
HOST="http://ishop.qiwi.ru/xml"
from_terminal='11468'
from_password = 'df[vehrf2007'
term_id=9514444003
term_password='jft5fba'
ALARM_SMS = 0
ALARM_CALL = 0
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
    <bill txn-id="10"/>
    </bills-list>
</request>
""" % (term_password, term_id),
'get_invoices':u"""<request>
	<protocol-version>4.00</protocol-version>
	<request-type>28</request-type>
 	<terminal-id>%s</terminal-id>
	<extra name="password">%s</extra>
	<extra name="dir">0</extra>
    <extra name="from">23.02.2011 00:00:00</extra>
    <extra name="to">24.02.2011 23:59:59</extra>
</request>
""" % (term_id,term_password,),
}

def make_request(xml):
    request = urllib2.Request(HOST,xml)
    response = urllib2.urlopen(request)
    try:
        return response.read()
    except Exception, e:
        print e
    return
        
def status_code(obj):
    if obj.result_code['fatal']!='true':
        if obj.result_code.data=='0':
            return True
    return False
        
def get_balance():
    xml = make_request(params['get_balance'])
    if not xml: return None
    #print xml
    o=xml2obj(xml)
    if status_code(o):
        if o.extra[0]['name']=='BALANCE':
           return o.extra[0].data

def create_invoice(phone_number,transaction_id, summ=0, comment='', lifetime=48):
    xml = make_request(params['create_invoice'] % (phone_number, summ, transaction_id, lifetime, comment,))
    if not xml: return None
    print xml
    o=xml2obj(xml)
    if status_code(o):
        print True
    #    if o.extra[0]['name']=='BALANCE':
    #       return o.extra[0].data

def get_invoices():
    xml = make_request(params['get_invoices'])
    if not xml: return None
    o=xml2obj(xml)
    #print o.__dict__
    
    for a in o.account_list.account:
        if a['from'].prv=='11468':
            print a.id
        print a.__dict__
        #print 
print get_invoices()
#print get_balance()

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
