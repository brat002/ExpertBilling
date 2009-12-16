from django.conf.urls.defaults import *
from django.contrib import admin

try:
    from settings import MEDIA_ROOT
    from settings import DEVELOPMENT_MODE
except:
    DEVELOPMENT_MODE = False
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^helpdesk/', include('helpdesk.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
)

if DEVELOPMENT_MODE:
    urlpatterns += patterns('',
      url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    )

urlpatterns += patterns('account.views',
                            
     url(r'^login/$', 'login', name="login"),
)

urlpatterns += patterns('ticket.views',
                            
     url(r'^manage/tickets/$', 'manage_tickets', name="manage_tickets"),
     url(r'^tickets/$', 'index_tickets', name="index_tickets"),
     url(r'^test/$', 'test', name='test'),
     url(r'^ajax/update/owner/tickets/$', 'update_owner_ticket', name="update_owner_ticket")
)