# -*- coding: utf-8 -*-

from django.apps import AppConfig


class RobokassaConfig(AppConfig):
    name = 'payments.robokassa'

    def ready(self):
        from payments.robokassa import signals  # pragma
