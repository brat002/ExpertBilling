import logging
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from payments.w1ru import PaymentProcessor
from getpaid.models import Payment
from django.conf import settings
from BeautifulSoup import BeautifulSoup

from billservice.models import Account
logger = logging.getLogger('payments.w1ru')
from django.views.generic.base import TemplateView


class PayView(View):
    def post(self, request, *args, **kwargs):


        try:
                status = PaymentProcessor.postback(request)

                
        except KeyError:
            logger.warning('Got malformed POST request: %s' % str(request.POST))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)




class SuccessView(TemplateView):

    template_name = "accounts/payment_success.html"

    def get_context_data(self, **kwargs):
        return {}

    def get(self, request, **kwargs):
        return self.render_to_response({})

    def post(self, request, **kwargs):
        return self.render_to_response({})

        
    
class FailureView(TemplateView):

    template_name = "accounts/payment_failure.html"

    def get(self, request, **kwargs):
        return self.render_to_response({})

    def post(self, request, **kwargs):
        return self.render_to_response({})
    
