# -*- coding:utf-8 -*-
from django.contrib import admin

from billservice.models import SystemUser, SystemGroup, Account , Transaction


admin.site.register(SystemUser)
admin.site.register(SystemGroup)
admin.site.register(Account)
admin.site.register(Transaction)