import os
from helpdesk import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('helpdesk.views',
                       (r'^$', 'index'),
                       (r'^login/$', '_login'),
                       (r'^manage/tickets/$', 'manage_tickets'),
                       (r'^tickets/$', 'index_tickets'),
                       (r'^ajax/update/owner/tickets/$', 'ajax_update_owner_ticket'),
                       (r'^ajax/deleted/tickets/$', 'ajax_deleted_tickets'),
                       (r'^ajax/archived/tickets/$', 'ajax_archived_tickets'),
                       (r'^ticket/add/$', 'ticket_add'),
                       (r'^ticket/edit/(?P<ticket_id>\d+)/$', 'ticket_edit'),
                       (r'^tickets/new/$', 'tickets_new'),
                       (r'^tickets/attention/$', 'tickets_attention'),
                       (r'^comment/add/(?P<ticket_id>\d+)/$', 'comment_add'),     
                       (r'^ajax/update/owner/tickets/$', 'ajax_update_owner_ticket'),
                       (r'^ajax/load/table/tickets/$', 'ajax_load_table_tickets'),
                       (r'^users/$', 'get_users'),
                       (r'^logout/$', 'login_out'),
                       (r'^user/(?P<user_id>\d+)/$', 'user_info'),
                       (r'^password/change/(?P<user_id>\d+)/$', 'change_password'),
                       (r'^password/gen/$', 'gen_password'),
                       (r'^status/change/(?P<user_id>\d+)/$', 'change_status'),
                       (r'^tariff/change/(?P<user_id>\d+)/$', 'change_tariff'),
                       (r'^user/system/settings/(?P<system_user_id>\d+)/$', 'system_user_settings'),
                      )
