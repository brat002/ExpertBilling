# -*- coding:utf-8 -*-
from django.contrib import admin

from billservice.models import SystemUser, SubAccount, Account , Transaction, TransactionType, City, Street, House, IPPool, IPInUse, SettlementPeriod, TimePeriod, AddonService
from billservice.models import SheduleLog, PeriodicalServiceLog


admin.site.register(SystemUser)
admin.site.register(SubAccount)
admin.site.register(Account)
admin.site.register(Transaction)

admin.site.register(City)
admin.site.register(Street)
admin.site.register(House)

admin.site.register(IPPool)
admin.site.register(IPInUse)

admin.site.register(TransactionType)

admin.site.register(SettlementPeriod)
admin.site.register(TimePeriod)
admin.site.register(AddonService)

admin.site.register(SheduleLog)
admin.site.register(PeriodicalServiceLog)


