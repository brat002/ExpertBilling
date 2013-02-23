import logging
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from getpaid.backends.easypay import PaymentProcessor
from getpaid.models import Payment

from BeautifulSoup import BeautifulSoup

from billservice.models import Account

class EasyPayView(View):
    def post(self, request, *args, **kwargs):


        try:
            body = BeautifulSoup(request.body)
            dt = body.Request.DateTime
            sign =  body.Request.Sign
            
            
            if 'Check' in body.Request:

                

                
                payment_status = PaymentProcessor.check(request, body)
                
        except KeyError:
            logger.warning('Got malformed POST request: %s' % str(request.POST))
            return HttpResponse('MALFORMED')



        status = PaymentProcessor.online(params, ip=request.META['REMOTE_ADDR'])
        return HttpResponse(status)




