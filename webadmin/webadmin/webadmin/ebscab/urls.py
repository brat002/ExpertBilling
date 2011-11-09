import os
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ebscab/', include('ebscab.foo.urls')),
    #(r'^$','ebscab.billing.views.index'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    # Uncomment this for admin:
    ('^admin/(.*)', admin.site.root),
     #(r'^accounts/profile/$', 'ebscab.billing.views.profile'),
     #(r'^accounts/logout/$', 'ebscab.billing.views.logout_view'),
     (r'^helpdesk/', include('helpdesk.urls')),
    (r'^ext/', include('extjs.urls')),
    (r'^ebsadmin/', include('ebsadmin.urls')),
)

urlpatterns += patterns('billservice.views',
    # Uncomment this for admin:
     #(r'^$', 'index'),
     #(r'^$', 'index'),
     (r'^login/$', 'login'),
     (r'^prepaid/$', 'account_prepays_traffic'),
     (r'^accounts/logout/$', 'login_out'),
     (r'^traffic/info/$', 'netflowstream_info'),
     (r'^promise/$', 'get_promise'),
     (r'^transaction/$', 'transaction'),
     (r'^session/info/$', 'vpn_session'),
     (r'^password/change/$', 'change_password'),
     (r'^password/form/$', 'password_form'),
     (r'^tariff/change/$', 'change_tariff'),
     (r'^tariff/form/$', 'change_tariff_form'),
     (r'^card/activation/$', 'card_acvation'),
     (r'^card/form/$', 'card_form'),
     (r'^client/$', 'client'),
     (r'^traffic/limit/$', 'traffic_limit'),
     (r'^statistics/$', 'statistics'),
     (r'^services/$', 'addon_service'),
     (r'^service/(?P<action>set|del)/(?P<id>\d+)/$', 'service_action'), 
     (r'^services/info/$', 'services_info'),
     (r'^service/history/info/$', 'periodical_service_history'),
     (r'^addon/services/transaction/info/$', 'addon_service_transaction'),
     (r'^traffic/transaction/info/$', 'traffic_transaction'),
     (r'^one/time/history/info/$', 'one_time_history'),
     (r'^news/delete/$', 'news_delete'),
)



urlpatterns += patterns('service_monitor.views',
                        #(?P<id>\d+)
    (r'^service_data/$', 'service_data'),
)


from extjs import direct


urlpatterns += patterns('extjs.views',
                       (r'^$', 'index') # Ext Main page
                      )

urlpatterns += patterns('extjs.ajax',
                       (r'^ajax$', 'ajax'),
                          # (r'^qqq/(?P<qqq_id>\d+)/$', 'callback'),
                      )

# ExtJs backend connectivity
urlpatterns += patterns('',
                        (r'^extjs/remoting/router/$', direct.remote_provider.router),
                        (r'^extjs/remoting/provider_js$', direct.remote_provider.script),
                        (r'^extjs/remoting/api/$', direct.remote_provider.api),
                        (r'^extjs/polling/router/$', direct.polling_provider.router),
                        (r'^extjs/polling/provider_js$', direct.polling_provider.script)
                    )

