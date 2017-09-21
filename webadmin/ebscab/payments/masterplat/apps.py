# -*- coding: utf-8 -*-

from django.apps import AppConfig


class MasterplatConfig(AppConfig):
    name = 'payments.masterplat'

    def ready(self):
        from payments.masterplat import signals  # pragma
