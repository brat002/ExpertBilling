import os
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
#from helpdesk import admin as helpdesk_admin
from django.db import connection
connection.features.can_return_id_from_insert = False
from ajax_select import urls as ajax_select_urls


admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ebscab/', include('ebscab.foo.urls')),
    #(r'^$','ebscab.billing.views.index'),
    #url('^helpdesk/admin/(.*)', helpdesk_admin.site.urls, name='helpdesk_admin'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    # Uncomment this for admin:
    (r'^objectlog/', include('object_log.urls')),
    (r'^helpdesk/', include('helpdesk.urls')),
    (r'^webmoney/', include('paymentgateways.webmoney.urls')),
    (r'^ebsadmin/', include('ebsadmin.urls')),
    (r'^admin/lookups/', include(ajax_select_urls)),
    (r'^admin/', include(admin.site.urls)),
    (r'^admin_media/jsi18n', 'django.views.i18n.javascript_catalog'),
    

)

urlpatterns += patterns('billservice.views',
    # Uncomment this for admin:
     #(r'^$', 'index'),
     url(r'^$', 'index', name='billservice_index'),
     (r'^login/$', 'login'),
     
     (r'^simple_login/$', 'simple_login'),
     (r'^get_ballance/$', 'get_ballance'),
     (r'^prepaid/$', 'account_prepays_traffic'),
     url(r'^accounts/logout/$', 'login_out', name='account_logout'),
     (r'^promise/$', 'get_promise'),
     (r'^payment/$', 'make_payment'),
     (r'^qiwi_payment/$', 'qiwi_payment'),
     (r'^qiwi_payment/balance/$', 'qiwi_balance'),     
     (r'^transaction/$', 'transaction'),
     (r'^session/info/$', 'vpn_session'),
     (r'^password/change/$', 'change_password'),
     (r'^email/change/$', 'change_email'),     
     (r'^password/form/$', 'password_form'),
     (r'^tariff/change/$', 'change_tariff'),
     (r'^tariff/form/$', 'change_tariff_form'),
     (r'^card/activation/$', 'card_acvation'),
     (r'^card/form/$', 'card_form'),
     (r'^traffic/limit/$', 'traffic_limit'),
     (r'^statistics/$', 'statistics'),
     (r'^services/$', 'addon_service'),
     (r'^service/(?P<action>set|del)/(?P<id>\d+)/$', 'service_action'),
     (r'^services/info/$', 'services_info'),
     (r'^service/history/info/$', 'periodical_service_history'),
     (r'^addon/services/transaction/info/$', 'addon_service_transaction'),
     (r'^traffic/transaction/info/$', 'traffic_transaction'),
     (r'^traffic/volume/info/$', 'traffic_volume'),
     (r'^one/time/history/info/$', 'one_time_history'),
     (r'^news/delete/$', 'news_delete'),
     (r'^subaccount/password/form/(?P<subaccount_id>\d+)/$', 'subaccount_password_form'),
     (r'^subaccount/password/change/$', 'subaccount_change_password'),
     (r'^service/(?P<action>set|del)/(?P<id>\d+)/$', 'service_action'),     
     (r'^account/block/$', 'user_block'),
     (r'^account/block/action/$', 'userblock_action'),
)
urlpatterns = urlpatterns + patterns('helpdesk.views.account',
    url(r'^account/helpdesk/$', 'list_tickets', name='helpdesk_account_tickets'), # list user's tickets
    url(r'^account/helpdesk/add$', 'create_ticket', name='helpdesk_account_tickets_add'), # create new ticket
    url(r'^account/helpdesk/(?P<ticket_id>[\d]+)/$', 'view_ticket', name='helpdesk_account_tickets_view'), #change/post comment,
)


urlpatterns += patterns('statistics.views',
                        #(?P<id>\d+)
    (r'^statistics/account/$', 'account_stat'),
    (r'^statistics/subaccount/$', 'subaccounts_stat'),
    (r'^statistics/subaccount_filter/$', 'subaccounts_filter_stat'),
    (r'^statistics/nasses_filter/$', 'nasses_filter_stat'),
    (r'^statistics/subaccount_period_filter/$', 'subaccounts_period_stat'),
    (r'^statistics/overall/$', 'overall_stat'),
    (r'^statistics/nasses_stat/$', 'nasses_stat'),
    (r'^statistics/nasses_period_filter/$', 'nasses_period_stat'),
    (r'^statistics/nas_stat/$', 'nas_stat'),
)

urlpatterns += patterns('cassa.views',
                        #(?P<id>\d+)
    (r'^cassa/$', 'index'),
)

urlpatterns += patterns('paymentgateways.quickpay.views',
    (r'^quickpay/payment/$', 'payment'),
)

urlpatterns += patterns('paymentgateways.osmp_customproviders.views',
    (r'^osmp_custom/payment/$', 'payment'),
)

urlpatterns += patterns('paymentgateways.rapida.views',
    (r'^pg/rapida/payment/$', 'payment'),
)

urlpatterns += patterns('paymentgateways.sberbank.views',
    (r'^pg/sberbank/payment/$', 'payment'),
)

