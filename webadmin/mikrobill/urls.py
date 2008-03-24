from django.conf.urls.defaults import *

urlpatterns = patterns('',
(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'c:/Python25/Scripts/mikrobill/media'}),

    # Example:
    # (r'^mikrobill/', include('mikrobill.foo.urls')),
    #(r'^$','mikrobill.billing.views.index'),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
     (r'^$', 'django.contrib.auth.views.login'),
     (r'^accounts/profile/$', 'mikrobill.billing.views.profile'),
     (r'^accounts/logout/$', 'mikrobill.billing.views.logout_view'),
     
     
)

