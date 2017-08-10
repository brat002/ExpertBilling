# -*- coding: utf-8 -*-

import logging

from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.base import View

from . import PaymentProcessor


logger = logging.getLogger('payments.yandexcassa')


class PayView(View):

    def post(self, request, *args, **kwargs):
        try:
            status = PaymentProcessor.postback(request)
        except KeyError, e:
            logger.warning('Got malformed POST request: %s %s' %
                           (str(request.POST), e))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)


class CheckView(View):

    def post(self, request, *args, **kwargs):
        try:
            status = PaymentProcessor.check(request)
        except KeyError, e:
            logger.warning('Got malformed POST request: %s %s' %
                           (str(request.POST), e))
            return HttpResponse('MALFORMED')

        return HttpResponse(status)


class FailureView(TemplateView):
    template_name = "accounts/payment_failure.html"

    def get(self, request, **kwargs):
        return self.render_to_response({})

    def post(self, request, **kwargs):
        return self.render_to_response({})
