# -*- coding: utf-8 -*-

from django.conf.urls import url

from payments.qiwiru.views import PayView


urlpatterns = [
    url(r'^qiwiru/payment/$',
        PayView.as_view(),
        name='getpaid-qiwiru-pay')
]
