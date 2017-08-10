# -*- coding: utf-8 -*-

import logging

from BeautifulSoup import BeautifulSoup
from django.http import HttpResponse
from django.views.generic.base import View

from payments.ru_sberbank import PaymentProcessor


logger = logging.getLogger('payments.ru_sberbank')


class PayView(View):

    def post(self, request, *args, **kwargs):
        try:
            body = BeautifulSoup(request.body)
            cs = PaymentProcessor.check_sig(body)

            if cs == False:
                status = 'INCORRECT SIGNATURE'
                return HttpResponse(status)

            status = 'FAIL'
            act = body.request.params.act.text

            if body.request.params.act.text == '1':
                status = PaymentProcessor.check(request, body)
            elif body.request.params.act.text == '2':
                status = PaymentProcessor.pay(request, body)

        except KeyError:
            logger.warning('Got malformed POST request: %s' %
                           str(request.POST))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)
