from django.conf.urls.defaults import *
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^EBS/', include('EBS.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
     (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
)

urlpatterns += patterns('',
        (r'^download/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'D:/EBS/'}),
    )

urlpatterns += patterns('account.views',
    (r'^login/$', '_login'),
    (r'^logout/$', '_logout'),
)

urlpatterns += patterns('files.views',
    (r'^files/category/$', 'file_categories'),
)