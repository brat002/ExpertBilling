# -*- coding: utf-8 -*-

from django.conf.urls import url

from payments.platezhkaua.views import PayView


urlpatterns = [
    url(r'^platezhkaua/payment/$',
        PayView.as_view(),
        name='getpaid-platezhkaua-pay')
]
