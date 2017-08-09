# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib import admin

from views import *


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(
        r'^success/$',
        success,
        name='wm_sample-success'),
    url(
        r'^fail/$',
        fail,
        name='wm_sample-fail'),
    url(
        r'^$',
        simple_payment,
        name='wm_sample-payment'),
    url(
        r'^result/$',
        result,
        name='webmoney-result')
)
