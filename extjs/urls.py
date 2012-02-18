#-*-coding:utf-8-*-

#import os

from django.conf.urls.defaults import *




urlpatterns = patterns('extjs.views',
                       (r'^$', 'index'), # Ext Main page
                       (r'^transactions/$', 'ext_transactions') # Ext Main page
                      )

urlpatterns += patterns('extjs.ajax',
                       (r'^ajax$', 'ajax'),
                          # (r'^qqq/(?P<qqq_id>\d+)/$', 'callback'),
                      )

