# -*- coding: utf-8 -*-

from django.conf.urls import url

from views import PayView


urlpatterns = [
    url(r'^billing-systems/payment/$',
        PayView.as_view(),
        name='getpaid-billing-systems-pay')
]
