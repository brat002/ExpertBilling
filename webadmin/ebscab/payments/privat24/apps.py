# -*- coding: utf-8 -*-

from django.apps import AppConfig


class Privat24Config(AppConfig):
    name = 'payments.privat24'

    def ready(self):
        from payments.privat24 import signals  # pragma
