# -*- coding: utf-8 -*-

from django.conf.urls import url

from ebsadmin.reportsystem import views as reportsystem_views


urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/$',
        reportsystem_views.report,
        name='reports_report')
]
