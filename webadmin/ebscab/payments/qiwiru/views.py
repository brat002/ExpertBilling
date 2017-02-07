import logging
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from payments.qiwiru import PaymentProcessor
from getpaid.models import Payment
from django.conf import settings
from BeautifulSoup import BeautifulSoup


logger = logging.getLogger('payments.qiwiru')

class PayView(View):
    def post(self, request, *args, **kwargs):

        status=''
        try:
            
            ip=request.META['REMOTE_ADDR']
            if settings.DEBUG==False:
                status = PaymentProcessor.check_allowed_ip(ip, request)
                if status!='OK':
                    return HttpResponse(status)

            status = PaymentProcessor.postback(request)

                
        except KeyError, e:
            print e
            logger.warning('Got malformed GET request: %s' % str(e))
            return HttpResponse('MALFORMED')

        return HttpResponse(status,  content_type="text/xml")




