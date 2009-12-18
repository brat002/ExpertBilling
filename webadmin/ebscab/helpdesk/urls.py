import os
from helpdesk import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('helpdesk.views',
                       (r'^$', 'index'),
                       (r'^login/$', '_login'),
                       (r'^manage/tickets/$', 'manage_tickets'),
                       (r'^tickets/$', 'index_tickets'),
                       (r'^ajax/update/owner/tickets/$', 'update_owner_ticket')    
                      )
