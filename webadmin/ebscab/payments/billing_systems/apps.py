# -*- coding: utf-8 -*-

from django.apps import AppConfig


class BillingSystemsConfig(AppConfig):
    name = 'payments.billing_systems'

    def ready(self):
        from payments.billing_systems import signals  # pragma
