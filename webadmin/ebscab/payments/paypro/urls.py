# -*- coding: utf-8 -*-

from django.conf.urls import url

from views import PayView


urlpatterns = [
    url(r'^paypro/payment/$',
        PayView.as_view(),
        name='getpaid-paypro-pay')
]
