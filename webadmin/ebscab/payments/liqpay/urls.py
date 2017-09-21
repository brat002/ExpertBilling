# -*- coding: utf-8 -*-

from django.conf.urls import url

from payments.liqpay.views import PayView


urlpatterns = [
    url(r'^liqpay/payment/result/$',
        PayView.as_view(),
        name='getpaid-liqpay-pay'),
    url(r'^liqpay/payment/$',
        PayView.as_view(),
        name='payment-result')
]
