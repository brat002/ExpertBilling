# -*- coding: utf-8 -*-

from django.apps import AppConfig


class RuSberbankConfig(AppConfig):
    name = 'payments.ru_sberbank'

    def ready(self):
        from payments.ru_sberbank import signals  # pragma
