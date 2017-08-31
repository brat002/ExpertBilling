# -*- coding: utf-8 -*-

from django.conf.urls import url

from views import PayView


urlpatterns = [
    url(r'^ru-sberbank/payment/$',
        PayView.as_view(),
        name='getpaid-rusberbank-pay')
]
