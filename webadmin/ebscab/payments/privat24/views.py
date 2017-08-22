# -*- coding: utf-8 -*-

import logging

from django.http import HttpResponse
from django.views.generic.base import View

from payments.privat24 import PaymentProcessor


logger = logging.getLogger('payments.privat24')


class PayView(View):

    def post(self, request, *args, **kwargs):
        try:
            status = PaymentProcessor.online(request)
        except Exception, e:
            logger.exception('Exeption: %s' % str(e))
            logger.warning('Got malformed POST request: %s' %
                           str(request.POST))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)
