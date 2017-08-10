# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.generic.base import View

from payments.qiwiru import PaymentProcessor


logger = logging.getLogger('payments.qiwiru')


class PayView(View):

    def post(self, request, *args, **kwargs):
        status = ''
        try:
            ip = request.META['REMOTE_ADDR']
            if settings.DEBUG == False:
                status = PaymentProcessor.check_allowed_ip(ip, request)
                if status != 'OK':
                    return HttpResponse(status)

            status = PaymentProcessor.postback(request)
        except KeyError, e:
            print e
            logger.warning('Got malformed GET request: %s' % str(e))
            return HttpResponse('MALFORMED')

        return HttpResponse(status, content_type="text/xml")

    def get(self, request, *args, **kwargs):
        status = PaymentProcessor.error(0, 300)
        try:
            ip = request.META['REMOTE_ADDR']
            if settings.DEBUG == False:
                status = PaymentProcessor.check_allowed_ip(ip, request)
                if status != 'OK':
                    return HttpResponse(status)
            request_type = request.GET.get('command')
            if request_type == 'check':
                status = PaymentProcessor.check(request)
            elif request_type == 'pay':
                status = PaymentProcessor.pay(request)
            else:
                status = PaymentProcessor.error(0, 300)

        except KeyError, e:
            print e
            logger.warning('Got malformed GET request: %s' % str(request.POST))
            return HttpResponse(status)

        return HttpResponse(status)
