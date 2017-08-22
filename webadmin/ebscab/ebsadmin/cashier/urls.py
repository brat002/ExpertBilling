# -*- coding: utf-8 -*-

from django.conf.urls import url

from ebsadmin.cashier import views


urlpatterns = [
    url(r'^$',
        views.index,
        name='cashier_index'),
    url(r'^transactionreport/$',
        views.transactionreport,
        name='cashier_transactionreport')
]
