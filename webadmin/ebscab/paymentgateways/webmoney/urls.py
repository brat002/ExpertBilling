# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin

from . import views


admin.autodiscover()


urlpatterns = [
    url(r'^success/$',
        views.success,
        name='wm_sample-success'),
    url(r'^fail/$',
        views.fail,
        name='wm_sample-fail'),
    url(r'^$',
        views.simple_payment,
        name='wm_sample-payment'),
    url(r'^result/$',
        views.result,
        name='webmoney-result')
]
