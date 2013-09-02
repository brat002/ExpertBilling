import logging
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from payments.paypro import PaymentProcessor
from getpaid.models import Payment
from django.conf import settings

from billservice.models import Account
logger = logging.getLogger('payments.paypro')

class PayView(View):
    def get(self, request, *args, **kwargs):


        try:

            status = PaymentProcessor.pay(request, request.GET)
                
        except KeyError:
            logger.warning('Got malformed POST request: %s' % str(request.GET))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)




