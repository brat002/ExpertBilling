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
            body = BeautifulSoup(request.POST.get('params'))
            cs = PaymentProcessor.check_sig(body)
            if cs == False:
                return HttpResponse(PaymentProcessor.error(body, 13))

            status = 'FAIL'
            act = body.request.params.act.text

            if body.request.params.act.text == '1':
                status = PaymentProcessor.check(request, body)
            elif body.request.params.act.text == '2':
                status = PaymentProcessor.pay(request, body)

        except Exception, e:
            logger.warning('Got malformed POST request: %s' %
                           str(request.POST))
            return HttpResponse(PaymentProcessor.error(body, 99, e))

        return HttpResponse(status)
