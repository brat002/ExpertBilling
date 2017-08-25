# -*- coding: utf-8 -*-

import django.contrib.auth.models as m
from django.db import models


default_app_config = 'billservice.apps.BillServiceConfig'


m.Permission.name = models.CharField(max_length=128)
