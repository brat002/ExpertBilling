# -*- coding: utf-8 -*-

from django.contrib import admin


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'currency', 'status',
                    'created_on', 'paid_on', 'amount_paid')
    list_filter = ('status', 'created_on', 'paid_on')
    search_fields = ('id',)
    raw_id_fields = ('order',)
