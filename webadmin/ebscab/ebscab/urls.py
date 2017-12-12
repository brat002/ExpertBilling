# -*- coding: utf-8 -*-

from autocomplete_light import shortcuts as autocomplete_light
from django.conf.urls import include, url
from django.contrib import admin
from django.views.i18n import javascript_catalog

from ajax_select import urls as ajax_select_urls
from billservice import views as billservice_views
from cassa import views as cassa_views
from helpdesk.views import account as helpdesk_account_views
from statistics import views as statistics_views


autocomplete_light.autodiscover()

admin.autodiscover()

# NOTE: override django error handlers
handler400 = 'ebsweb.views.bad_request'
handler403 = 'ebsweb.views.permission_denied'
handler404 = 'ebsweb.views.page_not_found'
handler500 = 'ebsweb.views.server_error'

urlpatterns = [
    url(r'^objectlog/', include('object_log.urls')),
    url(r'^helpdesk/', include('helpdesk.urls')),
    url(r'^ebsadmin/', include('ebsadmin.urls')),
    url(r'^cassa/', include('ebsadmin.cashier.urls')),
    url(r'^reports/', include('ebsadmin.reportsystem.urls')),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_media/jsi18n',
        javascript_catalog),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'', include('getpaid.urls')),
    url(r'^webcab/pay/$',
        billservice_views.SelectPaymentView.as_view(),
        name='payment-view'),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^selectable/', include('selectable.urls')),
    url(r'^captcha/', include('captcha.urls'))
]

urlpatterns += [
    url(r'^$', billservice_views.index, name='billservice_index'),
    url(r'^login/$', billservice_views.login, name='login'),
    url(r'^register/$', billservice_views.register, name='register'),
    url(r'^simple_login/$', billservice_views.simple_login),
    url(r'^get_ballance/$', billservice_views.get_ballance),
    url(r'^prepaid/$', billservice_views.account_prepays_traffic),
    url(r'^accounts/logout/$',
        billservice_views.login_out,
        name='account_logout'),
    url(r'^promise/$', billservice_views.get_promise),
    url(r'^payment/$', billservice_views.make_payment),
    url(r'^transaction/$', billservice_views.transaction),
    url(r'^session/info/$', billservice_views.vpn_session),
    url(r'^password/change/$', billservice_views.change_password),
    url(r'^email/change/$', billservice_views.change_email),
    url(r'^password/form/$', billservice_views.password_form),
    url(r'^tariff/change/$', billservice_views.change_tariff),
    url(r'^tariff/form/$', billservice_views.change_tariff_form),
    url(r'^card/activation/$', billservice_views.card_acvation),
    url(r'^card/form/$', billservice_views.card_form),
    url(r'^traffic/limit/$', billservice_views.traffic_limit),
    url(r'^statistics/$', billservice_views.statistics),
    url(r'^services/$', billservice_views.addon_service),
    url(r'^service/(?P<action>set|del)/(?P<id>\d+)/$',
        billservice_views.service_action),
    url(r'^services/info/$', billservice_views.services_info),
    url(r'^service/history/info/$', billservice_views.periodical_service_history),
    url(r'^addon/services/transaction/info/$',
        billservice_views.addon_service_transaction),
    url(r'^traffic/transaction/info/$', billservice_views.traffic_transaction),
    url(r'^traffic/volume/info/$', billservice_views.traffic_volume),
    url(r'^one/time/history/info/$', billservice_views.one_time_history),
    url(r'^news/delete/$', billservice_views.news_delete),
    url(r'^subaccount/password/form/(?P<subaccount_id>\d+)/$',
        billservice_views.subaccount_password_form),
    url(r'^subaccount/password/change/$',
        billservice_views.subaccount_change_password),
    url(r'^account/block/$', billservice_views.user_block),
    url(r'^account/block/action/$', billservice_views.userblock_action)
]

urlpatterns = urlpatterns + [
    # list user's tickets
    url(r'^account/helpdesk/$',
        helpdesk_account_views.list_tickets,
        name='helpdesk_account_tickets'),
    # create new ticket
    url(r'^account/helpdesk/add$',
        helpdesk_account_views.create_ticket,
        name='helpdesk_account_tickets_add'),
    # change/post comment
    url(r'^account/helpdesk/(?P<ticket_id>[\d]+)/$',
        helpdesk_account_views.view_ticket,
        name='helpdesk_account_tickets_view')
]

urlpatterns += [
    url(r'^statistics/account/$', statistics_views.account_stat),
    url(r'^statistics/subaccount/$', statistics_views.subaccounts_stat),
    url(r'^statistics/subaccount_filter/$',
        statistics_views.subaccounts_filter_stat),
    url(r'^statistics/nasses_filter/$', statistics_views.nasses_filter_stat),
    url(r'^statistics/subaccount_period_filter/$',
        statistics_views.subaccounts_period_stat),
    url(r'^statistics/overall/$', statistics_views.overall_stat),
    url(r'^statistics/nasses_stat/$', statistics_views.nasses_stat),
    url(r'^statistics/nasses_period_filter/$',
        statistics_views.nasses_period_stat),
    url(r'^statistics/nas_stat/$', statistics_views.nas_stat)
]

urlpatterns += [
    url(r'^cassa/$', cassa_views.index)
]

urlpatterns += [
    # TODO: remove prefix '20/'
    url('^20/', include('ebsweb.urls'))
]
