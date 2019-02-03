# -*- coding: utf-8 -*-

from django.conf.urls import url

from payments.privat24.views import PayView


urlpatterns = [
    url(r'^privat24/payment/result/$',
        PayView.as_view(),
        name='getpaid-privat24-pay'),
    url(r'^privat24/payment/$',
        PayView.as_view(),
        name='payment-result')
]
