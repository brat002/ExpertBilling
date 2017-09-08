# -*- coding: utf-8 -*-

from django.apps import AppConfig


class SimpleterminalConfig(AppConfig):
    name = 'payments.simpleterminal'

    def ready(self):
        from payments.simpleterminal import signals  # pragma
