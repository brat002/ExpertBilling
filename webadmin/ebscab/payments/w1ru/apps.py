# -*- coding: utf-8 -*-

from django.apps import AppConfig


class W1ruConfig(AppConfig):
    name = 'payments.w1ru'

    def ready(self):
        from payments.w1ru import signals  # pragma
