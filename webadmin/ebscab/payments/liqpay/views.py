# -*- coding: utf-8 -*-

import logging

from django.http import HttpResponse
from django.views.generic.base import View

from payments.liqpay.backend import PaymentProcessor


logger = logging.getLogger('payments.liqpay')


class PayView(View):

    def post(self, request, *args, **kwargs):
        try:
            status = PaymentProcessor.online(request)
        except Exception, e:
            logger.warning('Got malformed POST request: %s' %
                           str(request.POST))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)
