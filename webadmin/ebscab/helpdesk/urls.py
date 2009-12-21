import os
from helpdesk import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('helpdesk.views',
                       (r'^$', 'index'),
                       (r'^login/$', '_login'),
                       (r'^manage/tickets/$', 'manage_tickets'),
                       (r'^tickets/$', 'index_tickets'),
                       (r'^ajax/update/owner/tickets/$', 'update_owner_ticket'),
                       (r'^ticket/add/$', 'ticket_add'),
                       (r'^ticket/edit/(?P<ticket_id>\d+)/$', 'ticket_add'),     
                       (r'^ajax/update/owner/tickets/$', 'ajax_update_owner_ticket'),
                       (r'^ajax/load/table/tickets/$', 'ajax_load_table_tickets'),
                      )
