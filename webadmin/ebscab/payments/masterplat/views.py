# -*- coding: utf-8 -*-

import logging

from django.http import HttpResponse
from django.views.generic.base import View

from payments.masterplat.backend import PaymentProcessor


logger = logging.getLogger('payments.easypay')


class PayView(View):

    def get(self, request, *args, **kwargs):
        try:
            action = request.GET.get('uact')
            if action == 'get_info':
                status = PaymentProcessor.check(request, request.GET)
            elif action == 'payment':
                status = PaymentProcessor.pay(request, request.GET)
        except KeyError:
            logger.warning('Got malformed POST request: %s' %
                           str(request.POST))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)
