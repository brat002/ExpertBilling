# -*- coding: utf-8 -*-

from django.apps import AppConfig


class HelpdeskConfig(AppConfig):
    name = 'helpdesk'

    def ready(self):
        from helpdesk import signals  # pragma
