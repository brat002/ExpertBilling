# -*- coding: utf-8 -*-

from django.apps import AppConfig


class PlatezhkauaConfig(AppConfig):
    name = 'payments.platezhkaua'

    def ready(self):
        from payments.platezhkaua import signals  # pragma
