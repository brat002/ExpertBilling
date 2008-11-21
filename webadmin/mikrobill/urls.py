import os
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    # Example:
    # (r'^mikrobill/', include('mikrobill.foo.urls')),
    #(r'^$','mikrobill.billing.views.index'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
     #(r'^accounts/profile/$', 'mikrobill.billing.views.profile'),
     #(r'^accounts/logout/$', 'mikrobill.billing.views.logout_view'),
)

urlpatterns += patterns('billservice.views',
    # Uncomment this for admin:
     (r'^$', 'index'),
     (r'^index/$', 'index'),
     (r'^account/login/$', 'login'),
     (r'^prepaid/$', 'account_prepays_traffic'),
     (r'^accounts/logout/$', 'login_out'),
     (r'^traffic/info/$', 'netflowstream_info'),
     (r'^transaction/$', 'transaction'),
     (r'^session/info/$', 'vpn_session'),
     (r'^password/change/$', 'change_password'),
     (r'^card/activation/$', 'card_acvation'),
)