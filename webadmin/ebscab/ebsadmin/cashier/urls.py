# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'ebsadmin.cashier.views',
    url(r'^$',
        'index',
        name='cashier_index'),
    url(r'^transactionreport/$',
        'transactionreport',
        name='cashier_transactionreport'),
)
