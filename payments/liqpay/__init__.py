#-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from getpaid.backends import PaymentProcessorBase
import hashlib
import datetime
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from billservice.models import Account
from base64 import b64encode, b64decode
from BeautifulSoup import BeautifulSoup
from forms import AdditionalFieldsForm
import listeners

class TransactionStatus:
    OK = 'success'
    ERROR = 'failure'



PAYMENT_TEMPLATE= u"""<request>      
<version>1.2</version>
<merchant_id>%(MERCHANT_ID)s</merchant_id>
<result_url>%(RESULT_URL)s</result_url>
<server_url>%(SERVER_URL)s</server_url>
<order_id>%(ORDER_ID)s</order_id>
<amount>%(AMOUNT)s</amount>
<currency>%(CURRENCY)s</currency>
<description>%(COMMENT)s</description>
<pay_way>%(PAY_WAY)s</pay_way>
<exp_time>%(EXP_TIME)s</exp_time>
</request>"""


class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.liqpay'
    BACKEND_NAME = _('Liqpay backend')
    BACKEND_ACCEPTED_CURRENCY = ('UAH', )
    PAY_WAY = ('card', 'liqpay', 'delayed')

    GATEWAY_URL = 'https://www.liqpay.com/?do=clickNbuy'
    
    _ALLOWED_IP = ('93.183.196.28', '93.183.196.26')
    EXPIRE_TIME = 240
    
    @staticmethod
    def form():
        return AdditionalFieldsForm
    
    def get_gateway_url(self, request, payment):

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
            
        
        amount = float(request.POST.get('summ'))
        

        
        xml = PAYMENT_TEMPLATE % {
               'MERCHANT_ID': PaymentProcessor.get_backend_setting('MERCHANT_ID'),
               'RESULT_URL': "http://%s%s" % (site, reverse('payment-result')),
               'SERVER_URL': "http://%s%s" % (site, reverse('getpaid-liqpay-pay')),
               'ORDER_ID': payment.id,
               'AMOUNT': amount,
               'CURRENCY': PaymentProcessor.get_backend_setting('DEFAULT_CURRENCY', PaymentProcessor.BACKEND_ACCEPTED_CURRENCY[0]),
               'COMMENT': u'Internet payment',
               'PAY_WAY': ','.join(PaymentProcessor.get_backend_setting('PAY_WAY', PaymentProcessor.PAY_WAY)),
               'EXP_TIME': PaymentProcessor.get_backend_setting('EXPIRE_TIME', PaymentProcessor.EXPIRE_TIME),
               }

        operation_xml = b64encode(xml)
        signature = b64encode(hashlib.sha1(PaymentProcessor.get_backend_setting('MERCHANT_SIGNATURE')+xml+PaymentProcessor.get_backend_setting('MERCHANT_SIGNATURE')).digest())

        return self.GATEWAY_URL, "POST", {'operation_xml': operation_xml, 'signature': signature}
    
    @staticmethod
    def error(body, text):
        return  text
    
    @staticmethod
    def compute_sig(operation_xml):
        return b64encode(hashlib.sha1(PaymentProcessor.get_backend_setting('MERCHANT_SIGNATURE')+operation_xml+PaymentProcessor.get_backend_setting('MERCHANT_SIGNATURE')).digest())
        
    

    @staticmethod    
    def check_merchant_id(body, merchant_id):
        if merchant_id!=int(PaymentProcessor.get_backend_setting('MERCHANT_ID')):
            return PaymentProcessor.error(body, u'Unknown merchant ID')

    @staticmethod
    def online(request):
        operation_xml = request.POST.get('operation_xml')
        signature = request.POST.get('signature')
        
        if PaymentProcessor.compute_sig(operation_xml)!=signature:
            return "SIGNATURE CHECK ERROR"
        
        xml = b64decode(operation_xml)
        
        xml = BeautifulSoup(xml)
        
        merchant_id = xml.response.merchant_id.text
        order_id = xml.response.order_id.text
        amount = float(xml.response.amount.text)
        currency = xml.response.currency.text
        description = xml.response.description.text
        status = xml.response.status.text
        code = xml.response.code.text
        transaction_id = xml.response.transaction_id.text
        pay_way = xml.response.pay_way.text
        sender_phone = xml.response.sender_phone.text
        
        
        PaymentProcessor.check_merchant_id(xml, merchant_id)
        from getpaid.models import Payment
        try:
            payment = Payment.objects.get(id = order_id)
        except Payment.DoesNotExist, ex:
            return PaymentProcessor.error(xml, u'UNKNOWN PAYMENT')
        
        dt = datetime.datetime.now()
        if TransactionStatus.OK=='success':
            payment.paid_on = dt
            payment.external_id = transaction_id
            payment.amount_paid = amount
            payment.save()
            payment.change_status('paid')
            return 'OK'
        elif TransactionStatus.ERROR == 'failure':
            payment.change_status('failed')
            return 'FAIL'
        

        return 'UNKNOWS'
    
 
    

