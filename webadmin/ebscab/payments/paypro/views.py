# -*- coding: utf-8 -*-

import logging

from django.http import HttpResponse
from django.views.generic.base import View

from payments.paypro import PaymentProcessor


logger = logging.getLogger('payments.paypro')


class PayView(View):

    def get(self, request, *args, **kwargs):
        try:
            status = PaymentProcessor.pay(request, request.GET)
        except KeyError:
            logger.warning('Got malformed POST request: %s' % str(request.GET))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)
