import logging
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from payments.ru_sberbank import PaymentProcessor
from getpaid.models import Payment
from django.conf import settings
from BeautifulSoup import BeautifulSoup

from billservice.models import Account
logger = logging.getLogger('payments.ru_sberbank')

class PayView(View):
    def post(self, request, *args, **kwargs):


        try:
            
            
            body = BeautifulSoup(request.body)      
            cs = PaymentProcessor.check_sig(body)
            
            if cs==False:
                status='INCORRECT SIGNATURE'
                return HttpResponse(status)
            #print body.request.params.account.text
            status = 'FAIL'
            #print '==', body.request.params.act.text,'==', type(body.request.params.act.text)
            act = body.request.params.act.text
            
            print "action", act, act=='1', act=='2'
            if body.request.params.act.text=='1':
                status = PaymentProcessor.check(request, body)
            elif body.request.params.act.text=='2':
                status = PaymentProcessor.pay(request, body)
                
        except KeyError:
            logger.warning('Got malformed POST request: %s' % str(request.POST))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)




