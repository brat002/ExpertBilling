# -*- coding: utf-8 -*-

from django.apps import AppConfig


class EasypayConfig(AppConfig):
    name = 'payments.easypay'

    def ready(self):
        from payments.easypay import signals  # pragma
