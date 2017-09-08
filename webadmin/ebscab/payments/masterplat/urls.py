# -*- coding: utf-8 -*-

from django.conf.urls import url

from payments.masterplat.views import PayView


urlpatterns = [
    url(r'^masterplat/payment/$',
        PayView.as_view(),
        name='getpaid-masterplat-pay')
]
