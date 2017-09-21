# -*- coding: utf-8 -*-

from django.apps import AppConfig


class PayproConfig(AppConfig):
    name = 'payments.paypro'

    def ready(self):
        from payments.paypro import signals  # pragma
