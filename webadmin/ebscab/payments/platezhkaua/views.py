# -*- coding: utf-8 -*-

import logging

from BeautifulSoup import BeautifulSoup
from django.http import HttpResponse
from django.views.generic.base import View
from django.conf import settings

from payments.platezhkaua import PaymentProcessor


logger = logging.getLogger('payments.platezhkaua')


class PayView(View):

    def post(self, request, *args, **kwargs):
        try:
            body = BeautifulSoup(request.body)
            ip = request.META['REMOTE_ADDR']
            if settings.DEBUG == False:
                status = PaymentProcessor.check_allowed_ip(ip, request, body)
                if status != 'OK':
                    return HttpResponse(status)

            status = PaymentProcessor.check_credentials(request, body)
            if status != 'OK':
                return HttpResponse(status)

            if body.commandcall.command.text == 'check':
                status = PaymentProcessor.check(request, body)
            elif body.commandcall.command.text == 'pay':
                status = PaymentProcessor.pay(request, body)

        except KeyError:
            logger.warning('Got malformed POST request: %s' %
                           str(request.POST))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)
