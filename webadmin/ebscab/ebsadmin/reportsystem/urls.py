from django.conf.urls import *


urlpatterns = patterns('ebsadmin.reportsystem.views',
                       url(r'^(?P<slug>[\w-]+)/$', 'report', name='reports_report'),
                       )
