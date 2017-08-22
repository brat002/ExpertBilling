# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from views import PayView


urlpatterns = patterns(
    '',
    url(r'^paypro/payment/$',
        PayView.as_view(),
        name='getpaid-paypro-pay')
)
