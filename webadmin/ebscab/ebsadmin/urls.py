# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.i18n import javascript_catalog

from ebsadmin import views


urlpatterns = [
    url(r'^transactionreport/$',
        views.transactionreport)
]

urlpatterns += [
    url(r'^charts/$',
        views.charts,
        name='charts')
]

urlpatterns += [
    url(r'^account_management_status/',
        views.account_management_status,
        name='account_management_status'),
    url(r'^sendsms/',
        views.sendsms,
        name='sendsms'),
    url(r'^account_management_accounttariff/',
        views.account_management_accounttariff,
        name='account_management_accounttariff'),
    url(r'^account_management_delete/',
        views.account_management_delete,
        name='account_management_delete'),
    url(r'^account_management_restore/',
        views.account_management_restore,
        name='account_management_restore'),
    url(r'^accounttariff/edit/',
        views.accounttarif_edit,
        name='accounttariff_edit'),
    url(r'^account_management_suspendedperiod/',
        views.account_management_suspendedperiod,
        name='account_management_suspendedperiod'),
    url(r'^tools/ping/',
        views.tools_ping,
        name='tools_ping')
]

urlpatterns += [
    url(r'^account/',
        views.accountedit,
        name='account_edit'),
    url(r'^accounttariff/delete/',
        views.accounttariff_delete,
        name='accounttariff_delete'),
    url(r'^transaction/edit/',
        views.transaction,
        name='transaction_edit'),
    url(r'^totaltransaction/delete/',
        views.totaltransaction_delete,
        name='totaltransaction_delete'),

    url(r'^accountaddonservice/delete/',
        views.accountaddonservice_delete,
        name='accountaddonservice_delete'),
    url(r'^accountaddonservice/deactivate/',
        views.accountaddonservice_deactivate,
        name='accountaddonservice_deactivate'),
    url(r'^accountaddonservice/',
        views.accountaddonservice_edit,
        name='accountaddonservice'),

    url(r'^subaccount/delete/',
        views.subaccount_delete,
        name='subaccount_delete'),
    url(r'^subaccount/',
        views.subaccountedit,
        name='subaccount'),
    url(r'^accounthardware/delete/$',
        views.accounthardware_delete,
        name="accounthardware_delete"),
    url(r'^accounthardware/',
        views.accounthardware,
        name='accounthardware'),
    url(r'^transactionreport2/$',
        views.transactionreport2,
        name='transactionreport2'),
    url(r'^accountsreport/$',
        views.accountsreport,
        name='account_list'),
    url(r'^ipinusereport/$',
        views.ipinusereport,
        name='ipinuse_list'),
    url(r'^authlogreport/$',
        views.authlogreport,
        name='authlog_list'),
    url(r'^suspendedperiod/delete/$',
        views.suspendedperiod_delete,
        name='suspendedperiod_delete'),
    url(r'^suspendedperiod/$',
        views.suspendedperiod,
        name='suspendedperiod'),
    url(r'^activesessionreport/$',
        views.activesessionreport,
        name='activesessionreport'),

    url(r'^ballancehistoryreport/$',
        views.ballancehistoryreport,
        name='ballancehistoryreport'),
    url(r'^template/edit/$',
        views.template_edit,
        name='template_edit'),
    url(r'^template/delete/$',
        views.template_delete,
        name='template_delete'),
    url(r'^template/$', views.template, name='template'),
    url(r'^template/select/$', views.templateselect, name='templateselect')
]

urlpatterns += [
    url(r'^settlementperiod/edit/$',
        views.settlementperiod_edit,
        name='settlementperiod_edit'),
    url(r'^settlementperiod/delete/$',
        views.settlementperiod_delete,
        name='settlementperiod_delete'),
    url(r'^settlementperiod/$',
        views.settlementperiod,
        name='settlementperiod')
]

urlpatterns += [
    url(r'^monitoring/$', views.index, name='monitoring'),
    url(r'^radiusstat/$', views.radiusstat, name='radiusstat')
]


urlpatterns += [
    url(r'^permissiongroup/edit/$',
        views.permissiongroup_edit,
        name='permissiongroup_edit'),
    url(r'^permissiongroup/delete/$',
        views.permissiongroup_delete,
        name='permissiongroup_delete'),
    url(r'^permissiongroup/$',
        views.permissiongroup,
        name='permissiongroup')
]

urlpatterns += [
    url(r'^notificationssettings/edit/$',
        views.notificationssettings_edit,
        name='notificationssettings_edit'),
    url(r'^notificationssettings/delete/$',
        views.notificationssettings_delete,
        name='notificationssettings_delete'),
    url(r'^notificationssettings/$',
        views.notificationssettings,
        name='notificationssettings')
]

urlpatterns += [
    url(r'^bonustransaction/edit/$',
        views.bonus_transaction_edit,
        name='bonus_transaction_edit')
]

urlpatterns += [
    url(r'^transactiontype/edit/$',
        views.transactiontype_edit,
        name='transactiontype_edit'),
    url(r'^transactiontype/delete/$',
        views.transactiontype_delete,
        name='transactiontype_delete'),
    url(r'^transactiontype/$',
        views.transactiontype,
        name='transactiontype')
]

urlpatterns += [
    url(r'^comment/edit/$',
        views.comment_edit,
        name='comment_edit'),
    url(r'^comment/delete/$',
        views.comment_delete,
        name='comment_delete')
]

urlpatterns += [
    url(r'^systemuser/edit/$',
        views.systemuser_edit,
        name='systemuser_edit'),
    url(r'^systemuser/delete/$',
        views.systemuser_delete,
        name='systemuser_delete'),
    url(r'^systemuser/$',
        views.systemuser,
        name='systemuser')
]

urlpatterns += [
    url(r'^nas/edit/$',
        views.nas_edit,
        name='nas_edit'),
    url(r'^nas/delete/$',
        views.nas_delete,
        name='nas_delete'),
    url(r'^nas/testcreds/$',
        views.testCredentials,
        name='nas_test_credentials'),
    url(r'^nas/$',
        views.nas,
        name='nas')
]

urlpatterns += [
    url(r'^city/edit/$',
        views.city_edit,
        name="city_edit"),
    url(r'^street/edit/$',
        views.street_edit,
        name="street_edit"),
    url(r'^house/edit/$',
        views.house_edit,
        name="house_edit"),
    url(r'^address/delete/$',
        views.address_delete,
        name="address_delete"),
    url(r'^address/$',
        views.address,
        name='address')
]

urlpatterns += [
    url(r'^addonservice/edit/$',
        views.addonservice_edit,
        name='addonservice_edit'),
    url(r'^addonservice/delete/$',
        views.addonservice_delete,
        name='addonservice_delete'),
    url(r'^addonservice/$',
        views.addonservice,
        name='addonservice')
]

urlpatterns += [
    url(r'^ippool/edit/$',
        views.ippool_edit,
        name='ippool_edit'),
    url(r'^ippool/$',
        views.ippool,
        name='ippool'),
    url(r'^ippool/delete/$',
        views.ippool_delete,
        name="ippool_delete")
]

urlpatterns += [
    url(r'^suppagreement/edit/$',
        views.suppagreement_edit,
        name='suppagreement_edit'),
    url(r'^suppagreement/$',
        views.suppagreement,
        name='suppagreement'),
    url(r'^suppagreement/delete/$',
        views.suppagreement_delete,
        name="suppagreement_delete")
]

urlpatterns += [
    url(r'^accountsuppagreement/edit/$',
        views.accountsuppagreement_edit,
        name='accountsuppagreement_edit'),
    url(r'^accountsuppagreement/delete/$',
        views.accountsuppagreement_delete,
        name="accountsuppagreement_delete")
]

urlpatterns += [
    url(r'^timeperiod/edit/$',
        views.timeperiod_edit,
        name='timeperiod_edit'),
    url(r'^timeperiodnode/edit/$',
        views.timeperiodnode_edit,
        name='timeperiodnode_edit'),
    url(r'^timeperiod/$',
        views.timeperiod,
        name='timeperiod'),
    url(r'^timeperiod/delete/$',
        views.timeperiod_delete,
        name="timeperiod_delete")
]

urlpatterns += [
    url(r'^trafficclass/$',
        views.trafficclass,
        name='trafficclass'),
    url(r'^trafficclass/edit/$',
        views.trafficclass_edit,
        name='trafficclass_edit'),
    url(r'^trafficclass/weight/$',
        views.trafficclass_weight,
        name='trafficclass_weight'),
    url(r'^trafficclass/upload/$',
        views.trafficclass_upload,
        name='trafficclass_upload'),
    url(r'^trafficclass/delete/$',
        views.trafficclass_delete,
        name='trafficclass_delete'),
    url(r'^trafficnode_list/$',
        views.trafficnode_list,
        name='trafficnode_list'),
    url(r'^trafficnode/$',
        views.trafficnode,
        name='trafficnode'),
    url(r'^trafficnode/delete/$',
        views.trafficnode_delete,
        name='trafficnode_delete')
]

urlpatterns += [
    url(r'^radiusattr/edit/$',
        views.radiusattr_edit,
        name='radiusattr_edit'),
    url(r'^radiusattr/$',
        views.radiusattr,
        name='radiusattr'),
    url(r'^radiusattr/delete/$',
        views.radiusattr_delete,
        name="radiusattr_delete")
]

urlpatterns += [
    url(r'^news/edit/$',
        views.news_edit,
        name='news_edit'),
    url(r'^news/$',
        views.news,
        name='news'),
    url(r'^news/delete/$',
        views.news_delete,
        name="news_delete")
]

urlpatterns += [
    url(r'^tpchangerule/edit/$',
        views.tpchangerule_edit,
        name='tpchangerule_edit'),
    url(r'^tpchangerule/$',
        views.tpchangerule,
        name='tpchangerule'),
    url(r'^tpchangerule/delete/$',
        views.tpchangerule_delete,
        name="tpchangerule_delete")
]

urlpatterns += [
    url(r'^operator/edit/$',
        views.operator_edit,
        name='operator_edit')
]

urlpatterns += [
    url(r'^logview/$',
        views.logview,
        name='logview')
]

urlpatterns += [
    url(r'^$',
        views.admin_dashboard,
        name='admin_dashboard')
]

urlpatterns += [
    url(r'^periodicalservicelog/delete/$',
        views.periodicalservicelog_delete,
        name='periodicalservicelog_delete'),
    url(r'^periodicalservicelog/$',
        views.periodicalservicelog,
        name='periodicalservicelog')
]

urlpatterns += [
    url(r'^shedulelog/$',
        views.shedulelog,
        name='shedulelog')
]

urlpatterns += [
    url(r'^accountprepaystraffic/edit/$',
        views.accountprepaystraffic_edit,
        name='accountprepaystraffic_edit'),
    url(r'^accountprepaystraffic/delete/$',
        views.accountprepaystraffic_delete,
        name='accountprepaystraffic_delete'),
    url(r'^accountprepaystraffic/$',
        views.accountprepaystraffic,
        name='accountprepaystraffic')
]

urlpatterns += [
    url(r'^accountprepaysradiustraffic/edit/$',
        views.accountprepaysradiustraffic_edit,
        name='accountprepaysradiustraffic_edit'),
    url(r'^accountprepaysradiustraffic/delete/$',
        views.accountprepaysradiustraffic_delete,
        name='accountprepaysradiustraffic_delete'),
    url(r'^accountprepaysradiustraffic/$',
        views.accountprepaysradiustraffic,
        name='accountprepaysradiustraffic')
]

urlpatterns += [
    url(r'^accountprepaystime/edit/$',
        views.accountprepaystime_edit,
        name='accountprepaystime_edit'),
    url(r'^accountprepaystime/delete/$',
        views.accountprepaystime_delete,
        name='accountprepaystime_delete'),
    url(r'^accountprepaystime/$',
        views.accountprepaystime,
        name='accountprepaystime')
]

urlpatterns += [
    url(r'^groupstat/$',
        views.groupstat,
        name='groupstat')
]

urlpatterns += [
    url(r'^payment/edit/$',
        views.payment_edit,
        name='payment_edit'),
    url(r'^payment/delete/$',
        views.payment_delete,
        name='payment_delete'),
    url(r'^payment/$',
        views.payment,
        name='payment')
]

urlpatterns += [
    url(r'^globalstat/$',
        views.globalstat,
        name='globalstat')
]

urlpatterns += [
    url(r'^sms/$',
        views.sms,
        name='sms'),
    url(r'^sms/delete/$',
        views.sms_delete,
        name='sms_delete')
]

urlpatterns += [
    url(r'^manufacturer/edit/$',
        views.manufacturer_edit,
        name='manufacturer_edit'),
    url(r'^manufacturer/$',
        views.manufacturer,
        name='manufacturer'),
    url(r'^manufacturer/delete/$',
        views.manufacturer_delete,
        name="manufacturer_delete")
]

urlpatterns += [
    url(r'^dynamicschemafield/edit/$',
        views.dynamicschemafield_edit,
        name='dynamicschemafield_edit'),
    url(r'^dynamicschemafield/$',
        views.dynamicschemafield,
        name='dynamicschemafield'),
    url(r'^dynamicschemafield/delete/$',
        views.dynamicschemafield_delete,
        name="dynamicschemafield_delete")
]

urlpatterns += [
    url(r'^hardwaretype/edit/$',
        views.hardwaretype_edit,
        name='hardwaretype_edit'),
    url(r'^hardwaretype/$',
        views.hardwaretype,
        name='hardwaretype'),
    url(r'^hardwaretype/delete/$',
        views.hardwaretype_delete,
        name="hardwaretype_delete")
]

urlpatterns += [
    url(r'^accountgroup/edit/$',
        views.accountgroup_edit,
        name='accountgroup_edit'),
    url(r'^accountgroup/$',
        views.accountgroup,
        name='accountgroup'),
    url(r'^accountgroup/delete/$',
        views.accountgroup_delete,
        name="accountgroup_delete")
]

urlpatterns += [
    url(r'^model/edit/$',
        views.model_edit,
        name='model_edit'),
    url(r'^model/$',
        views.model,
        name='model'),
    url(r'^model/delete/$',
        views.model_delete,
        name="model_delete")
]

urlpatterns += [
    url(r'^hardware/edit/$',
        views.hardware_edit,
        name='hardware_edit'),
    url(r'^hardware/$',
        views.hardware,
        name='hardware'),
    url(r'^hardware/delete/$',
        views.hardware_delete,
        name="hardware_delete")
]

urlpatterns += [
    url(r'^switch/edit/$',
        views.switch_edit,
        name='switch_edit'),
    url(r'^switch/port/status/$',
        views.switch_port_status,
        name='switch_port_status'),
    url(r'^switch/$',
        views.switch,
        name='switch'),
    url(r'^switch/delete/$',
        views.switch_delete,
        name="switch_delete")
]

urlpatterns += [
    url(r'^actionlog/$',
        views.actionlog,
        name='actionlog')
]

urlpatterns += [
    url(r'^card/edit/$',
        views.card_edit,
        name='card_edit'),
    url(r'^card/generate/$',
        views.card_generate,
        name='card_generate'),
    url(r'^card/update/$',
        views.card_update,
        name='card_update'),
    url(r'^card/manage/$',
        views.card_manage,
        name='card_manage'),
    url(r'^card/$',
        views.card,
        name='card'),
    url(r'^card/delete/$',
        views.card_delete,
        name="card_delete"),
    url(r'^salecard/edit/$',
        views.salecard_edit,
        name="salecard_edit"),
    url(r'^salecard/$',
        views.salecard,
        name="salecard")
]

urlpatterns += [
    url(r'^tariff/$',
        views.tariff,
        name='tariff'),
    url(r'^tariff/edit/$',
        views.tariff_edit,
        name='tariff_edit'),
    url(r'^tariff/hide/$',
        views.tariff_hide,
        name='tariff_hide'),

    url(r'^tariff/periodicalservice/edit/$',
        views.periodicalservice_edit,
        name='tariff_periodicalservice_edit'),
    url(r'^tariff/prepaidtraffic/edit/$',
        views.prepaidtraffic_edit,
        name='tariff_prepaidtraffic_edit'),
    url(r'^tariff/prepaidtraffic/delete/$',
        views.prepaidtraffic_delete,
        name='prepaidtraffic_delete'),

    url(r'^tariff/accessparameters/$',
        views.accessparameters,
        name='tariff_accessparameters'),
    url(r'^tariff/timespeed/edit/$',
        views.timespeed_edit,
        name='tariff_timespeed_edit'),
    url(r'^tariff/timespeed/delete/$',
        views.timespeed_delete,
        name='tariff_timespeed_delete'),
    url(r'^tariff/periodicalservice/$',
        views.periodicalservice,
        name='periodicalservice'),
    url(r'^tariff/periodicalservice/delete/$',
        views.periodicalservice_delete,
        name='periodicalservice_delete'),
    url(r'^tariff/traffictransmitnode/edit/$',
        views.traffictransmitnode_edit,
        name='tariff_traffictransmitnode_edit'),
    url(r'^tariff/traffictransmitnode/delete/$',
        views.traffictransmitnode_delete,
        name='traffictransmitnode_delete'),

    url(r'^tariff/onetimeservice/$',
        views.onetimeservice,
        name='tariff_onetimeservice'),
    url(r'^tariff/onetimeservice/edit/$',
        views.onetimeservice_edit,
        name='onetimeservice_edit'),
    url(r'^tariff/onetimeservice/delete/$',
        views.onetimeservice_delete,
        name='onetimeservice_delete'),

    url(r'^tariff/traffictransmitservice/delete/$',
        views.traffictransmitservice_delete,
        name='traffictransmitservice_delete'),
    url(r'^tariff/traffictransmitservice/$',
        views.traffictransmitservice,
        name='tariff_traffictransmitservice'),

    url(r'^tariff/radiustrafficservice/$',
        views.radiustraffic,
        name='tariff_radiustraffic'),
    url(r'^tariff/radiustrafficservice/delete/$',
        views.radiustrafficservice_delete,
        name='radiustrafficservice_delete'),
    url(r'^tariff/radiustrafficnode/edit/$',
        views.radiustrafficnode_edit,
        name='tariff_radiustrafficnode_edit'),
    url(r'^tariff/radiustrafficnode/delete/$',
        views.radiustrafficnode_delete,
        name='radiustrafficnode_delete'),

    url(r'^tariff/trafficlimit/edit/$',
        views.trafficlimit_edit,
        name='tariff_trafficlimit_edit'),
    url(r'^tariff/trafficlimit/delete/$',
        views.trafficlimit_delete,
        name='trafficlimit_delete'),
    url(r'^tariff/trafficlimit/$',
        views.trafficlimit,
        name='tariff_trafficlimit'),
    url(r'^tariff/speedlimit/edit/$',
        views.speedlimit_edit,
        name='tariff_speedlimit_edit'),
    url(r'^tariff/speedlimit/delete/$',
        views.speedlimit_delete,
        name='speedlimit_delete'),

    url(r'^tariff/timeaccessservice/delete/$',
        views.timeaccessservice_delete,
        name='tariff_timeaccessservice_delete'),
    url(r'^tariff/timeaccessservice/$',
        views.timeaccessservice,
        name='tariff_timeaccessservice'),
    url(r'^tariff/timeaccesssnode/edit/$',
        views.timeaccessnode_edit,
        name='tariff_timeaccessnode_edit'),
    url(r'^tariff/timeaccesssnode/delete/$',
        views.timeaccessnode_delete,
        name='timeaccessnode_delete'),

    url(r'^tariff/addonservicetariff/$',
        views.addonservicetariff,
        name='tariff_addonservicetariff'),
    url(r'^tariff/addonservicetariff/edit/$',
        views.addonservicetariff_edit,
        name='tariff_addonservicetariff_edit'),
    url(r'^tariff/addonservicetariff/delete/$',
        views.addonservicetariff_delete,
        name='addonservicetariff_delete')
]

urlpatterns += [
    url(r'^dealer/edit/$',
        views.dealer_edit,
        name='dealer_edit'),
    url(r'^dealer/select/$',
        views.dealer_select,
        name='dealer_select'),
    url(r'^dealer/$',
        views.dealer,
        name='dealer')
]

urlpatterns += [
    url(r'^group/edit/$',
        views.group_edit,
        name='group_edit'),
    url(r'^group/$',
        views.group,
        name='group'),
    url(r'^group/delete/$',
        views.group_delete,
        name="group_delete")
]

urlpatterns += [
    url(r'^registrationrequest/$',
        views.registrationrequest,
        name='registrationrequest'),
    url(r'^registrationrequest/delete/$',
        views.registrationrequest_delete,
        name="registrationrequest_delete")
]

urlpatterns += [
    url(r'^contracttemplate/edit/$',
        views.contracttemplate_edit,
        name='contracttemplate_edit'),
    url(r'^contracttemplate/$',
        views.contracttemplate,
        name='contracttemplate'),
    url(r'^contracttemplate/delete/$',
        views.contracttemplate_delete,
        name="contracttemplate_delete")
]

urlpatterns += [
    url(r'^simple_login/$',
        views.simple_login),
    url(r'^table/settings/$',
        views.table_settings,
        name="table_settings"),
    url(r'^setportsstatus/$',
        views.set_ports_status),
    url(r'^getportsstatus/$',
        views.get_ports_status),
    url(r'^templates/$',
        views.templates),
    url(r'^documentrender/$',
        views.documentrender,
        name="documentrender"),
    url(r'^templaterender/$',
        views.templaterender,
        name="templaterender"),
    url(r'^ipaddress/getfrompool/$',
        views.getipfrompool,
        name='getipfrompool'),
    url(r'^credentials/gen/$',
        views.generate_credentials,
        name="generate_credentials"),
    url(r'^getmacforip/$',
        views.get_mac_for_ip,
        name="get_mac_for_ip"),
    url(r'^sessions/reset/$',
        views.session_reset,
        name="session_reset"),
    url(r'^sessions/hardreset/$',
        views.session_hardreset,
        name="session_hardreset"),
    url(r'^cities/$',
        views.cities),
    url(r'^streets/$',
        views.streets,
        name="street"),
    url(r'^houses/$',
        views.houses,
        name="house"),
    url(r'^test_credentials/$',
        views.testCredentials)
]

urlpatterns += [
    url(r'^jsi18n/(?P<packages>\S+?)/$',
        javascript_catalog)
]
