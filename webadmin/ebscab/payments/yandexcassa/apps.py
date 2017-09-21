# -*- coding: utf-8 -*-

from django.apps import AppConfig


class YandexCassaConfig(AppConfig):
    name = 'payments.yandexcassa'

    def ready(self):
        from payments.yandexcassa import signals  # pragma
