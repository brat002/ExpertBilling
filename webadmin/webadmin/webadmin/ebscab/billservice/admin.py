# -*- coding:utf-8 -*-
from django.contrib import admin

from billservice.models import SystemUser, SystemGroup 


admin.site.register(SystemUser)
admin.site.register(SystemGroup)