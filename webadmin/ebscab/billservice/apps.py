# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.db import models


class BillServiceConfig(AppConfig):
    name = 'billservice'

    def ready(self):
        import django.contrib.auth.models as m

        m.Permission.name = models.CharField(max_length=128)
