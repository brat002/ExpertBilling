# -*- coding: utf-8 -*-

from django.dispatch import Signal


webmoney_payment_accepted = Signal(providing_args=["payment"])
