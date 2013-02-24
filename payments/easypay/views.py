import logging
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from payments.easypay import PaymentProcessor
from getpaid.models import Payment

from BeautifulSoup import BeautifulSoup

from billservice.models import Account
logger = logging.getLogger('payments.easypay')

class EasyPayView(View):
    def post(self, request, *args, **kwargs):


        try:
            body = BeautifulSoup(request.body)      
            print request.body
            print body
            print "==="
            print body.request.find('check')
            print "==="
            if body.request.find('check'):

                

                
                status = PaymentProcessor.check(request, body)
            elif body.request.find('payment'):
                status = PaymentProcessor.pay(request, body)
            elif body.request.find('confirm'):
                status = PaymentProcessor.pay(request, body)
            elif body.request.find('cancel'):
                status = PaymentProcessor.pay(request, body)
                
        except KeyError:
            logger.warning('Got malformed POST request: %s' % str(request.POST))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)




