# -*- coding: utf-8 -*-

from django.apps import AppConfig


class EBSAdminConfig(AppConfig):
    name = 'ebsadmin'

    def ready(self):
        from ebsadmin import signals  # pragma
