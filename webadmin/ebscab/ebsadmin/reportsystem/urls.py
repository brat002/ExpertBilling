# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'ebsadmin.reportsystem.views',
    url(r'^(?P<slug>[\w-]+)/$',
        'report',
        name='reports_report'),
)
