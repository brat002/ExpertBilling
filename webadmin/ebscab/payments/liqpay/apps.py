# -*- coding: utf-8 -*-

from django.apps import AppConfig


class LiqpayConfig(AppConfig):
    name = 'payments.liqpay'

    def ready(self):
        from payments.liqpay import signals  # pragma
