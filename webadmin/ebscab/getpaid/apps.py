# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.contrib import admin
from django.db import models

from getpaid.admin import PaymentAdmin


class GetpaidConfig(AppConfig):
    name = 'getpaid'

    def ready(self):
        from billservice.models import Transaction

        from getpaid.models import register_to_payment

        # NOTE: register models: Payment, Order into getpaid.models
        register_to_payment(Transaction,
                            unique=False,
                            blank=True,
                            null=True,
                            related_name='payments',
                            on_delete=models.CASCADE)

        from getpaid.models import Payment  # after register

        admin.site.register(Payment, PaymentAdmin)
