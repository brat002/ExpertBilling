# -*- coding: utf-8 -*-

from django.apps import AppConfig


class QiwiruConfig(AppConfig):
    name = 'payments.qiwiru'

    def ready(self):
        from payments.qiwiru import signals  # pragma
