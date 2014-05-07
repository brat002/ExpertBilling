import logging
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from payments.privat24 import PaymentProcessor
from getpaid.models import Payment
from django.conf import settings
from BeautifulSoup import BeautifulSoup

from billservice.models import Account
logger = logging.getLogger('payments.privat24')

class PayView(View):
    def post(self, request, *args, **kwargs):

        try:
            status = PaymentProcessor.online(request)
                
                
        except Exception, e:
            logger.exception('Exeption: %s' % str(e))
            logger.warning('Got malformed POST request: %s' % str(request.POST))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)




