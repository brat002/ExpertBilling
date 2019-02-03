# -*- coding: utf-8 -*-

from django.conf.urls import url

from payments.easypay.views import EasyPayView


urlpatterns = [
    url(r'^easypay/payment/$',
        EasyPayView.as_view(),
        name='getpaid-easypay-pay')
]
