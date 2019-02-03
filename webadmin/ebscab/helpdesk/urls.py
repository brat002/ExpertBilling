# -*- coding: utf-8 -*-

"""
Jutda Helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

urls.py - Mapping of URL's to our various views. Note we always used NAMED
          views for simplicity in linking later on.
"""

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed as django_feed

from helpdesk.views import api as api_views
from helpdesk.views import kb as kb_views
from helpdesk.views import public as public_views
from helpdesk.views import staff as staff_views
from helpdesk.views.feeds import feed_setup


admin.autodiscover()


urlpatterns = [
    url(r'^dashboard/$',
        staff_views.dashboard,
        name='helpdesk_dashboard'),

    url(r'^ticket/info/$',
        staff_views.ticket_info,
        name='ticket_info'),
    url(r'^ticket/followup/$',
        staff_views.followup_edit,
        name='followup_edit'),
    url(r'^ticket/assign/$',
        staff_views.ticket_assign,
        name='ticket_assign'),

    url(r'^tickets/$',
        staff_views.tickets,
        name='helpdesk_list'),

    url(r'^tickets/update/$',
        staff_views.mass_update,
        name='helpdesk_mass_update'),

    url(r'^tickets/submit/$',
        staff_views.create_ticket,
        name='helpdesk_submit'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/$',
        staff_views.view_ticket,
        name='helpdesk_view'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/edit/$',
        staff_views.edit_ticket,
        name='helpdesk_edit'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/update/$',
        staff_views.update_ticket,
        name='helpdesk_update'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/delete/$',
        staff_views.delete_ticket,
        name='helpdesk_delete'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/hold/$',
        staff_views.hold_ticket,
        name='helpdesk_hold'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/unhold/$',
        staff_views.unhold_ticket,
        name='helpdesk_unhold'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/cc/$',
        staff_views.ticket_cc,
        name='helpdesk_ticket_cc'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/cc/add/$',
        staff_views.ticket_cc_add,
        name='helpdesk_ticket_cc_add'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/cc/delete/(?P<cc_id>[0-9]+)/$',
        staff_views.ticket_cc_del,
        name='helpdesk_ticket_cc_del'),

    url(r'^raw/(?P<type>\w+)/$',
        staff_views.raw_details,
        name='helpdesk_raw'),

    url(r'^rss/$',
        staff_views.rss_list,
        name='helpdesk_rss_index'),

    url(r'^reports/$',
        staff_views.report_index,
        name='helpdesk_report_index'),

    url(r'^reports/(?P<report>\w+)/$',
        staff_views.run_report,
        name='helpdesk_run_report'),

    url(r'^save_query/$',
        staff_views.save_query,
        name='helpdesk_savequery'),

    url(r'^delete_query/(?P<id>[0-9]+)/$',
        staff_views.delete_saved_query,
        name='helpdesk_delete_query'),

    url(r'^settings/$',
        staff_views.user_settings,
        name='helpdesk_user_settings'),

    url(r'^ignore/$',
        staff_views.email_ignore,
        name='helpdesk_email_ignore'),

    url(r'^ignore/add/$',
        staff_views.email_ignore_add,
        name='helpdesk_email_ignore_add'),

    url(r'^ignore/delete/(?P<id>[0-9]+)/$',
        staff_views.email_ignore_del,
        name='helpdesk_email_ignore_del'),
    url(r'^queue/select/$',
        staff_views.queueselect,
        name='queueselect')
]

urlpatterns += [
    url(r'^$',
        public_views.view_tickets,
        name='helpdesk_home'),

    url(r'^view/$',
        public_views.view_ticket,
        name='helpdesk_public_view'),

    url(r'^add/$',
        public_views.add_ticket,
        name='helpdesk_public_add'),
    url(r'^publicticket/(?P<ticket_id>[0-9]+)/update/$',
        public_views.update_ticket,
        name='helpdesk_updatepublicticket')
]

urlpatterns += [
    url(r'^rss/(?P<url>.*)/$',
        login_required(django_feed),
        {'feed_dict': feed_setup},
        name='helpdesk_rss'),

    url(r'^api/(?P<method>[a-z_-]+)/$',
        api_views.api,
        name='helpdesk_api'),

    url(r'^login/$',
        auth_views.login,
        name='login'),

    url(r'^logout/$',
        auth_views.logout,
        {'next_page': '../'},
        name='logout')
]

urlpatterns += [
    url(r'^kb/$',
        kb_views.index,
        name='helpdesk_kb_index'),

    url(r'^kb/(?P<slug>[A-Za-z_-]+)/$',
        kb_views.category,
        name='helpdesk_kb_category'),

    url(r'^kb/(?P<item>[0-9]+)/$',
        kb_views.item,
        name='helpdesk_kb_item'),

    url(r'^kb/(?P<item>[0-9]+)/vote/$',
        kb_views.vote,
        name='helpdesk_kb_vote')
]
