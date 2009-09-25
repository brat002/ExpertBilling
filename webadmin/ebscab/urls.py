import os
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

#admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ebscab/', include('ebscab.foo.urls')),
    #(r'^$','ebscab.billing.views.index'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    # Uncomment this for admin:
    #('^admin/(.*)', admin.site.root),
     #(r'^accounts/profile/$', 'ebscab.billing.views.profile'),
     #(r'^accounts/logout/$', 'ebscab.billing.views.logout_view'),
)

urlpatterns += patterns('billservice.views',
    # Uncomment this for admin:
     #(r'^$', 'index'),
     (r'^$', 'index'),
     (r'^login/$', 'login'),
     (r'^prepaid/$', 'account_prepays_traffic'),
     (r'^accounts/logout/$', 'login_out'),
     (r'^traffic/info/$', 'netflowstream_info'),
     (r'^promise/$', 'get_promise'),
     (r'^transaction/$', 'transaction'),
     (r'^session/info/$', 'vpn_session'),
     (r'^password/change/$', 'change_password'),
     (r'^password/form/$', 'card_form'),
     (r'^tariff/change/$', 'change_tariff'),
     (r'^tariff/form/$', 'change_tariff_form'),
     (r'^card/activation/$', 'card_acvation'),
     (r'^client/$', 'client'),
     (r'^traffic/limit/$', 'traffic_limit'),
     (r'^statistics/$', 'statistics'),
     (r'^services/$', 'addon_service'),
     (r'^service/(?P<action>set|del)/(?P<id>\d+)/$', 'service_action'), 
     (r'^services/info/$', 'services_info'),
)