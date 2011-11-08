#-*-coding:utf-8-*-

#import os

from django.conf.urls.defaults import *

from extjs import direct


urlpatterns = patterns('extjs.views',
                       (r'^$', 'index') # Ext Main page
                      )

urlpatterns += patterns('extjs.ajax',
                       (r'^ajax$', 'ajax'),
                          # (r'^qqq/(?P<qqq_id>\d+)/$', 'callback'),
                      )

# ExtJs backend connectivity
urlpatterns += patterns('',
                        (r'^remoting/router/$', direct.remote_provider.router),
                        (r'^remoting/provider_js$', direct.remote_provider.script),
                        (r'^remoting/api/$', direct.remote_provider.api),
                        (r'^polling/router/$', direct.polling_provider.router),
                        (r'^polling/provider_js$', direct.polling_provider.script)
                    )

