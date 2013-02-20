from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from getpaid.backends import PaymentProcessorBase

class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'getpaid.backends.easypay'
    BACKEND_NAME = _('Easypay backend')
    BACKEND_ACCEPTED_CURRENCY = ('UAH', )

    GATEWAY_URL = 'http://easysoft.com.ua/ProviderProtocolTest'
    
    def get_gateway_url(self, request):
        return self.GATEWAY_URL, "GET", {}