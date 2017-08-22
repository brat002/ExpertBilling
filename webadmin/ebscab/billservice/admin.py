# -*- coding: utf-8 -*-

from django.contrib import admin

from billservice.models import (
    Account,
    AddonService,
    City,
    House,
    IPInUse,
    IPPool,
    PeriodicalServiceLog,
    SettlementPeriod,
    SheduleLog,
    Street,
    SubAccount,
    SystemUser,
    TimePeriod,
    Transaction,
    TransactionType
)


admin.site.register(Account)
admin.site.register(AddonService)
admin.site.register(City)
admin.site.register(House)
admin.site.register(IPInUse)
admin.site.register(IPPool)
admin.site.register(PeriodicalServiceLog)
admin.site.register(SettlementPeriod)
admin.site.register(SheduleLog)
admin.site.register(Street)
admin.site.register(SubAccount)
admin.site.register(SystemUser)
admin.site.register(TimePeriod)
admin.site.register(Transaction)
admin.site.register(TransactionType)
