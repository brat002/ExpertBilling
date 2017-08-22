# -*- coding: utf-8 -*-

import logging

from django.http import HttpResponse
from django.views.generic.base import View

from payments.simpleterminal import PaymentProcessor


logger = logging.getLogger('payments.simpleterminal')


class PayView(View):

    def get(self, request, *args, **kwargs):
        if PaymentProcessor.get_backend_setting('SECRET') not in ['', None]:
            if request.GET.get('secret') != \
                    PaymentProcessor.get_backend_setting('SECRET'):
                return HttpResponse('-100')

        try:
            status = PaymentProcessor.pay(request, request.GET)
        except KeyError:
            logger.warning('Got malformed POST request: %s' % str(request.GET))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)
