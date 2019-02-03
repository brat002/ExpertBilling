# -*- coding: utf-8 -*-

from django.conf.urls import url

from payments.simpleterminal.views import PayView


urlpatterns = [
    url(r'^simpleterminal/payment/$',
        PayView.as_view(),
        name='getpaid-simpleterminal-pay')
]
