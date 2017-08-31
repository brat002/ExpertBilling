# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.i18n import javascript_catalog

from ebsadmin import (
    accountsuppagreement as accountsuppagreement_views,
    addonservice as addonservice_views,
    address as address_views,
    charts as charts_views,
    ippool as ippool_views,
    settlementperiod as settlementperiod_views,
    suppagreement as suppagreement_views,
    systemuser as systemuser_views,
    timeperiod as timeperiod_views,
    trafficclass as trafficclass_views,
    transactionreport as transactionreport_views,
    transactiontype as transactiontype_views,
    views as ebsadmin_views,
    wi as wi_views
)
from ebsadmin.modules import (
    account as account_views,
    accountgroup as accountgroup_views,
    accountprepaysradiustraffic as accountprepaysradiustraffic_views,
    accountprepaystime as accountprepaystime_views,
    accountprepaystraffic as accountprepaystraffic_views,
    actionlog as actionlog_views,
    admin_dashboard as admin_dashboard_views,
    bonustransaction as bonustransaction_views,
    card as card_views,
    comment as comment_views,
    contracttemplate as contracttemplate_views,
    dealer as dealer_views,
    dynamicfields as dynamicfields_views,
    globalstat as globalstat_views,
    group as group_views,
    groupstat as groupstat_views,
    hardware as hardware_views,
    hardwaretype as hardwaretype_views,
    logview as logview_views,
    manufacturer as manufacturer_views,
    model as model_views,
    monitoring as monitoring_views,
    nasses as nasses_views,
    news as news_views,
    notificationssettings as notificationssettings_views,
    operator as operator_views,
    payment as payment_views,
    periodicalservicelog as periodicalservicelog_views,
    permissiongroup as permissiongroup_views,
    radiusattr as radiusattr_views,
    registrationrequest as registrationrequest_views,
    shedulelog as shedulelog_views,
    sms as sms_views,
    switch as switch_views,
    tariff as tariff_views,
    tpchangerule as tpchangerule_views
)


urlpatterns = [
    url(r'^transactionreport/$',
        transactionreport_views.transactionreport)
]

urlpatterns += [
    url(r'^charts/$',
        charts_views.charts,
        name='charts')
]

urlpatterns += [
    url(r'^account_management_status/',
        account_views.account_management_status,
        name='account_management_status'),
    url(r'^sendsms/',
        account_views.sendsms,
        name='sendsms'),
    url(r'^account_management_accounttariff/',
        account_views.account_management_accounttariff,
        name='account_management_accounttariff'),
    url(r'^account_management_delete/',
        account_views.account_management_delete,
        name='account_management_delete'),
    url(r'^account_management_restore/',
        account_views.account_management_restore,
        name='account_management_restore'),
    url(r'^accounttariff/edit/',
        account_views.accounttarif_edit,
        name='accounttariff_edit'),
    url(r'^account_management_suspendedperiod/',
        account_views.account_management_suspendedperiod,
        name='account_management_suspendedperiod'),
    url(r'^tools/ping/',
        account_views.tools_ping,
        name='tools_ping')
]

urlpatterns += [
    url(r'^account/',
        wi_views.accountedit,
        name='account_edit'),
    url(r'^accounttariff/delete/',
        wi_views.accounttariff_delete,
        name='accounttariff_delete'),
    url(r'^transaction/edit/',
        wi_views.transaction,
        name='transaction_edit'),
    url(r'^totaltransaction/delete/',
        wi_views.totaltransaction_delete,
        name='totaltransaction_delete'),

    url(r'^accountaddonservice/delete/',
        wi_views.accountaddonservice_delete,
        name='accountaddonservice_delete'),
    url(r'^accountaddonservice/deactivate/',
        wi_views.accountaddonservice_deactivate,
        name='accountaddonservice_deactivate'),
    url(r'^accountaddonservice/',
        wi_views.accountaddonservice_edit,
        name='accountaddonservice'),

    url(r'^subaccount/delete/',
        wi_views.subaccount_delete,
        name='subaccount_delete'),
    url(r'^subaccount/',
        wi_views.subaccountedit,
        name='subaccount'),
    url(r'^accounthardware/delete/$',
        wi_views.accounthardware_delete,
        name="accounthardware_delete"),
    url(r'^accounthardware/',
        wi_views.accounthardware,
        name='accounthardware'),
    url(r'^transactionreport2/$',
        wi_views.transactionreport2,
        name='transactionreport2'),
    url(r'^accountsreport/$',
        wi_views.accountsreport,
        name='account_list'),
    url(r'^ipinusereport/$',
        wi_views.ipinusereport,
        name='ipinuse_list'),
    url(r'^authlogreport/$',
        wi_views.authlogreport,
        name='authlog_list'),
    url(r'^suspendedperiod/delete/$',
        wi_views.suspendedperiod_delete,
        name='suspendedperiod_delete'),
    url(r'^suspendedperiod/$',
        wi_views.suspendedperiod,
        name='suspendedperiod'),
    url(r'^activesessionreport/$',
        wi_views.activesessionreport,
        name='activesessionreport'),

    url(r'^ballancehistoryreport/$',
        wi_views.ballancehistoryreport,
        name='ballancehistoryreport'),
    url(r'^template/edit/$',
        wi_views.template_edit,
        name='template_edit'),
    url(r'^template/delete/$',
        wi_views.template_delete,
        name='template_delete'),
    url(r'^template/$', wi_views.template, name='template'),
    url(r'^template/select/$', wi_views.templateselect, name='templateselect')
]

urlpatterns += [
    url(r'^settlementperiod/edit/$',
        settlementperiod_views.settlementperiod_edit,
        name='settlementperiod_edit'),
    url(r'^settlementperiod/delete/$',
        settlementperiod_views.settlementperiod_delete,
        name='settlementperiod_delete'),
    url(r'^settlementperiod/$',
        settlementperiod_views.settlementperiod,
        name='settlementperiod')
]

urlpatterns += [
    url(r'^monitoring/$', monitoring_views.index, name='monitoring'),
    url(r'^radiusstat/$', monitoring_views.radiusstat, name='radiusstat')
]


urlpatterns += [
    url(r'^permissiongroup/edit/$',
        permissiongroup_views.permissiongroup_edit,
        name='permissiongroup_edit'),
    url(r'^permissiongroup/delete/$',
        permissiongroup_views.permissiongroup_delete,
        name='permissiongroup_delete'),
    url(r'^permissiongroup/$',
        permissiongroup_views.permissiongroup,
        name='permissiongroup')
]

urlpatterns += [
    url(r'^notificationssettings/edit/$',
        notificationssettings_views.notificationssettings_edit,
        name='notificationssettings_edit'),
    url(r'^notificationssettings/delete/$',
        notificationssettings_views.notificationssettings_delete,
        name='notificationssettings_delete'),
    url(r'^notificationssettings/$',
        notificationssettings_views.notificationssettings,
        name='notificationssettings')
]

urlpatterns += [
    url(r'^bonustransaction/edit/$',
        bonustransaction_views.bonus_transaction_edit,
        name='bonus_transaction_edit')
]

urlpatterns += [
    url(r'^transactiontype/edit/$',
        transactiontype_views.transactiontype_edit,
        name='transactiontype_edit'),
    url(r'^transactiontype/delete/$',
        transactiontype_views.transactiontype_delete,
        name='transactiontype_delete'),
    url(r'^transactiontype/$',
        transactiontype_views.transactiontype,
        name='transactiontype')
]

urlpatterns += [
    url(r'^comment/edit/$',
        comment_views.comment_edit,
        name='comment_edit'),
    url(r'^comment/delete/$',
        comment_views.comment_delete,
        name='comment_delete')
]

urlpatterns += [
    url(r'^systemuser/edit/$',
        systemuser_views.systemuser_edit,
        name='systemuser_edit'),
    url(r'^systemuser/delete/$',
        systemuser_views.systemuser_delete,
        name='systemuser_delete'),
    url(r'^systemuser/$',
        systemuser_views.systemuser,
        name='systemuser')
]

urlpatterns += [
    url(r'^nas/edit/$',
        nasses_views.nas_edit,
        name='nas_edit'),
    url(r'^nas/delete/$',
        nasses_views.nas_delete,
        name='nas_delete'),
    url(r'^nas/testcreds/$',
        nasses_views.testCredentials,
        name='nas_test_credentials'),
    url(r'^nas/$',
        nasses_views.nas,
        name='nas')
]

urlpatterns += [
    url(r'^city/edit/$',
        address_views.city_edit,
        name="city_edit"),
    url(r'^street/edit/$',
        address_views.street_edit,
        name="street_edit"),
    url(r'^house/edit/$',
        address_views.house_edit,
        name="house_edit"),
    url(r'^address/delete/$',
        address_views.address_delete,
        name="address_delete"),
    url(r'^address/$',
        address_views.address,
        name='address')
]

urlpatterns += [
    url(r'^addonservice/edit/$',
        addonservice_views.addonservice_edit,
        name='addonservice_edit'),
    url(r'^addonservice/delete/$',
        addonservice_views.addonservice_delete,
        name='addonservice_delete'),
    url(r'^addonservice/$',
        addonservice_views.addonservice,
        name='addonservice')
]

urlpatterns += [
    url(r'^ippool/edit/$',
        ippool_views.ippool_edit,
        name='ippool_edit'),
    url(r'^ippool/$',
        ippool_views.ippool,
        name='ippool'),
    url(r'^ippool/delete/$',
        ippool_views.ippool_delete,
        name="ippool_delete")
]

urlpatterns += [
    url(r'^suppagreement/edit/$',
        suppagreement_views.suppagreement_edit,
        name='suppagreement_edit'),
    url(r'^suppagreement/$',
        suppagreement_views.suppagreement,
        name='suppagreement'),
    url(r'^suppagreement/delete/$',
        suppagreement_views.suppagreement_delete,
        name="suppagreement_delete")
]

urlpatterns += [
    url(r'^accountsuppagreement/edit/$',
        accountsuppagreement_views.accountsuppagreement_edit,
        name='accountsuppagreement_edit'),
    url(r'^accountsuppagreement/delete/$',
        accountsuppagreement_views.accountsuppagreement_delete,
        name="accountsuppagreement_delete")
]

urlpatterns += [
    url(r'^timeperiod/edit/$',
        timeperiod_views.timeperiod_edit,
        name='timeperiod_edit'),
    url(r'^timeperiodnode/edit/$',
        timeperiod_views.timeperiodnode_edit,
        name='timeperiodnode_edit'),
    url(r'^timeperiod/$',
        timeperiod_views.timeperiod,
        name='timeperiod'),
    url(r'^timeperiod/delete/$',
        timeperiod_views.timeperiod_delete,
        name="timeperiod_delete")
]

urlpatterns += [
    url(r'^trafficclass/$',
        trafficclass_views.trafficclass,
        name='trafficclass'),
    url(r'^trafficclass/edit/$',
        trafficclass_views.trafficclass_edit,
        name='trafficclass_edit'),
    url(r'^trafficclass/weight/$',
        trafficclass_views.trafficclass_weight,
        name='trafficclass_weight'),
    url(r'^trafficclass/upload/$',
        trafficclass_views.trafficclass_upload,
        name='trafficclass_upload'),
    url(r'^trafficclass/delete/$',
        trafficclass_views.trafficclass_delete,
        name='trafficclass_delete'),
    url(r'^trafficnode_list/$',
        trafficclass_views.trafficnode_list,
        name='trafficnode_list'),
    url(r'^trafficnode/$',
        trafficclass_views.trafficnode,
        name='trafficnode'),
    url(r'^trafficnode/delete/$',
        trafficclass_views.trafficnode_delete,
        name='trafficnode_delete')
]

urlpatterns += [
    url(r'^radiusattr/edit/$',
        radiusattr_views.radiusattr_edit,
        name='radiusattr_edit'),
    url(r'^radiusattr/$',
        radiusattr_views.radiusattr,
        name='radiusattr'),
    url(r'^radiusattr/delete/$',
        radiusattr_views.radiusattr_delete,
        name="radiusattr_delete")
]

urlpatterns += [
    url(r'^news/edit/$',
        news_views.news_edit,
        name='news_edit'),
    url(r'^news/$',
        news_views.news,
        name='news'),
    url(r'^news/delete/$',
        news_views.news_delete,
        name="news_delete")
]

urlpatterns += [
    url(r'^tpchangerule/edit/$',
        tpchangerule_views.tpchangerule_edit,
        name='tpchangerule_edit'),
    url(r'^tpchangerule/$',
        tpchangerule_views.tpchangerule,
        name='tpchangerule'),
    url(r'^tpchangerule/delete/$',
        tpchangerule_views.tpchangerule_delete,
        name="tpchangerule_delete")
]

urlpatterns += [
    url(r'^operator/edit/$',
        operator_views.operator_edit,
        name='operator_edit')
]

urlpatterns += [
    url(r'^logview/$',
        logview_views.logview,
        name='logview')
]

urlpatterns += [
    url(r'^$',
        admin_dashboard_views.admin_dashboard,
        name='admin_dashboard')
]

urlpatterns += [
    url(r'^periodicalservicelog/delete/$',
        periodicalservicelog_views.periodicalservicelog_delete,
        name='periodicalservicelog_delete'),
    url(r'^periodicalservicelog/$',
        periodicalservicelog_views.periodicalservicelog,
        name='periodicalservicelog')
]

urlpatterns += [
    url(r'^shedulelog/$',
        shedulelog_views.shedulelog,
        name='shedulelog')
]

urlpatterns += [
    url(r'^accountprepaystraffic/edit/$',
        accountprepaystraffic_views.accountprepaystraffic_edit,
        name='accountprepaystraffic_edit'),
    url(r'^accountprepaystraffic/delete/$',
        accountprepaystraffic_views.accountprepaystraffic_delete,
        name='accountprepaystraffic_delete'),
    url(r'^accountprepaystraffic/$',
        accountprepaystraffic_views.accountprepaystraffic,
        name='accountprepaystraffic')
]

urlpatterns += [
    url(r'^accountprepaysradiustraffic/edit/$',
        accountprepaysradiustraffic_views.accountprepaysradiustraffic_edit,
        name='accountprepaysradiustraffic_edit'),
    url(r'^accountprepaysradiustraffic/delete/$',
        accountprepaysradiustraffic_views.accountprepaysradiustraffic_delete,
        name='accountprepaysradiustraffic_delete'),
    url(r'^accountprepaysradiustraffic/$',
        accountprepaysradiustraffic_views.accountprepaysradiustraffic,
        name='accountprepaysradiustraffic')
]

urlpatterns += [
    url(r'^accountprepaystime/edit/$',
        accountprepaystime_views.accountprepaystime_edit,
        name='accountprepaystime_edit'),
    url(r'^accountprepaystime/delete/$',
        accountprepaystime_views.accountprepaystime_delete,
        name='accountprepaystime_delete'),
    url(r'^accountprepaystime/$',
        accountprepaystime_views.accountprepaystime,
        name='accountprepaystime')
]

urlpatterns += [
    url(r'^groupstat/$',
        groupstat_views.groupstat,
        name='groupstat')
]

urlpatterns += [
    url(r'^payment/edit/$',
        payment_views.payment_edit,
        name='payment_edit'),
    url(r'^payment/delete/$',
        payment_views.payment_delete,
        name='payment_delete'),
    url(r'^payment/$',
        payment_views.payment,
        name='payment')
]

urlpatterns += [
    url(r'^globalstat/$',
        globalstat_views.globalstat,
        name='globalstat')
]

urlpatterns += [
    url(r'^sms/$',
        sms_views.sms,
        name='sms'),
    url(r'^sms/delete/$',
        sms_views.sms_delete,
        name='sms_delete')
]

urlpatterns += [
    url(r'^manufacturer/edit/$',
        manufacturer_views.manufacturer_edit,
        name='manufacturer_edit'),
    url(r'^manufacturer/$',
        manufacturer_views.manufacturer,
        name='manufacturer'),
    url(r'^manufacturer/delete/$',
        manufacturer_views.manufacturer_delete,
        name="manufacturer_delete")
]

urlpatterns += [
    url(r'^dynamicschemafield/edit/$',
        dynamicfields_views.dynamicschemafield_edit,
        name='dynamicschemafield_edit'),
    url(r'^dynamicschemafield/$',
        dynamicfields_views.dynamicschemafield,
        name='dynamicschemafield'),
    url(r'^dynamicschemafield/delete/$',
        dynamicfields_views.dynamicschemafield_delete,
        name="dynamicschemafield_delete")
]

urlpatterns += [
    url(r'^hardwaretype/edit/$',
        hardwaretype_views.hardwaretype_edit,
        name='hardwaretype_edit'),
    url(r'^hardwaretype/$',
        hardwaretype_views.hardwaretype,
        name='hardwaretype'),
    url(r'^hardwaretype/delete/$',
        hardwaretype_views.hardwaretype_delete,
        name="hardwaretype_delete")
]

urlpatterns += [
    url(r'^accountgroup/edit/$',
        accountgroup_views.accountgroup_edit,
        name='accountgroup_edit'),
    url(r'^accountgroup/$',
        accountgroup_views.accountgroup,
        name='accountgroup'),
    url(r'^accountgroup/delete/$',
        accountgroup_views.accountgroup_delete,
        name="accountgroup_delete")
]

urlpatterns += [
    url(r'^model/edit/$',
        model_views.model_edit,
        name='model_edit'),
    url(r'^model/$',
        model_views.model,
        name='model'),
    url(r'^model/delete/$',
        model_views.model_delete,
        name="model_delete")
]

urlpatterns += [
    url(r'^hardware/edit/$',
        hardware_views.hardware_edit,
        name='hardware_edit'),
    url(r'^hardware/$',
        hardware_views.hardware,
        name='hardware'),
    url(r'^hardware/delete/$',
        hardware_views.hardware_delete,
        name="hardware_delete")
]

urlpatterns += [
    url(r'^switch/edit/$',
        switch_views.switch_edit,
        name='switch_edit'),
    url(r'^switch/port/status/$',
        switch_views.switch_port_status,
        name='switch_port_status'),
    url(r'^switch/$',
        switch_views.switch,
        name='switch'),
    url(r'^switch/delete/$',
        switch_views.switch_delete,
        name="switch_delete")
]

urlpatterns += [
    url(r'^actionlog/$',
        actionlog_views.actionlog,
        name='actionlog')
]

urlpatterns += [
    url(r'^card/edit/$',
        card_views.card_edit,
        name='card_edit'),
    url(r'^card/generate/$',
        card_views.card_generate,
        name='card_generate'),
    url(r'^card/update/$',
        card_views.card_update,
        name='card_update'),
    url(r'^card/manage/$',
        card_views.card_manage,
        name='card_manage'),
    url(r'^card/$',
        card_views.card,
        name='card'),
    url(r'^card/delete/$',
        card_views.card_delete,
        name="card_delete"),
    url(r'^salecard/edit/$',
        card_views.salecard_edit,
        name="salecard_edit"),
    url(r'^salecard/$',
        card_views.salecard,
        name="salecard")
]

urlpatterns += [
    url(r'^tariff/edit/$',
        tariff_views.tariff_edit,
        name='tariff_edit'),
    url(r'^tariff/hide/$',
        tariff_views.tariff_hide,
        name='tariff_hide'),
    url(r'^tariff/periodicalservice/edit/$',
        tariff_views.tariff_periodicalservice_edit,
        name='tariff_periodicalservice_edit'),
    url(r'^tariff/prepaidtraffic/edit/$',
        tariff_views.tariff_prepaidtraffic_edit,
        name='tariff_prepaidtraffic_edit'),
    url(r'^tariff/prepaidtraffic/delete/$',
        tariff_views.prepaidtraffic_delete,
        name='prepaidtraffic_delete'),

    url(r'^tariff/accessparameters/$',
        tariff_views.tariff_accessparameters,
        name='tariff_accessparameters'),
    url(r'^tariff/timespeed/edit/$',
        tariff_views.tariff_timespeed_edit,
        name='tariff_timespeed_edit'),
    url(r'^tariff/timespeed/delete/$',
        tariff_views.tariff_timespeed_delete,
        name='tariff_timespeed_delete'),
    url(r'^tariff/periodicalservice/$',
        tariff_views.tariff_periodicalservice,
        name='tariff_periodicalservice'),
    url(r'^tariff/periodicalservice/delete/$',
        tariff_views.periodicalservice_delete,
        name='periodicalservice_delete'),
    url(r'^tariff/traffictransmitnode/edit/$',
        tariff_views.tariff_traffictransmitnode_edit,
        name='tariff_traffictransmitnode_edit'),
    url(r'^tariff/traffictransmitnode/delete/$',
        tariff_views.traffictransmitnode_delete,
        name='traffictransmitnode_delete'),

    url(r'^tariff/onetimeservice/$',
        tariff_views.tariff_onetimeservice,
        name='tariff_onetimeservice'),
    url(r'^tariff/onetimeservice/edit/$',
        tariff_views.onetimeservice_edit,
        name='onetimeservice_edit'),
    url(r'^tariff/onetimeservice/delete/$',
        tariff_views.tariff_onetimeservice_delete,
        name='onetimeservice_delete'),

    url(r'^tariff/traffictransmitservice/delete/$',
        tariff_views.tariff_traffictransmitservice_delete,
        name='traffictransmitservice_delete'),
    url(r'^tariff/traffictransmitservice/$',
        tariff_views.tariff_traffictransmitservice,
        name='tariff_traffictransmitservice'),

    url(r'^tariff/radiustrafficservice/$',
        tariff_views.tariff_radiustraffic,
        name='tariff_radiustraffic'),
    url(r'^tariff/radiustrafficservice/delete/$',
        tariff_views.tariff_radiustrafficservice_delete,
        name='radiustrafficservice_delete'),
    url(r'^tariff/radiustrafficnode/edit/$',
        tariff_views.tariff_radiustrafficnode_edit,
        name='tariff_radiustrafficnode_edit'),
    url(r'^tariff/radiustrafficnode/delete/$',
        tariff_views.radiustrafficnode_delete,
        name='radiustrafficnode_delete'),

    url(r'^tariff/trafficlimit/edit/$',
        tariff_views.tariff_trafficlimit_edit,
        name='tariff_trafficlimit_edit'),
    url(r'^tariff/trafficlimit/delete/$',
        tariff_views.trafficlimit_delete,
        name='trafficlimit_delete'),
    url(r'^tariff/trafficlimit/$',
        tariff_views.tariff_trafficlimit,
        name='tariff_trafficlimit'),
    url(r'^tariff/speedlimit/edit/$',
        tariff_views.tariff_speedlimit_edit,
        name='tariff_speedlimit_edit'),
    url(r'^tariff/speedlimit/delete/$',
        tariff_views.speedlimit_delete,
        name='speedlimit_delete'),

    url(r'^tariff/timeaccessservice/delete/$',
        tariff_views.tariff_timeaccessservice_delete,
        name='tariff_timeaccessservice_delete'),
    url(r'^tariff/timeaccessservice/$',
        tariff_views.tariff_timeaccessservice,
        name='tariff_timeaccessservice'),
    url(r'^tariff/timeaccesssnode/edit/$',
        tariff_views.tariff_timeaccessnode_edit,
        name='tariff_timeaccessnode_edit'),
    url(r'^tariff/timeaccesssnode/delete/$',
        tariff_views.timeaccessnode_delete,
        name='timeaccessnode_delete'),

    url(r'^tariff/addonservicetariff/$',
        tariff_views.tariff_addonservicetariff,
        name='tariff_addonservicetariff'),
    url(r'^tariff/addonservicetariff/edit/$',
        tariff_views.tariff_addonservicetariff_edit,
        name='tariff_addonservicetariff_edit'),
    url(r'^tariff/addonservicetariff/delete/$',
        tariff_views.addonservicetariff_delete,
        name='addonservicetariff_delete'),
    url(r'^tariff/$',
        tariff_views.tariff,
        name='tariff')
]

urlpatterns += [
    url(r'^dealer/edit/$',
        dealer_views.dealer_edit,
        name='dealer_edit'),
    url(r'^dealer/select/$',
        dealer_views.dealer_select,
        name='dealer_select'),
    url(r'^dealer/$',
        dealer_views.dealer,
        name='dealer')
]

urlpatterns += [
    url(r'^group/edit/$',
        group_views.group_edit,
        name='group_edit'),
    url(r'^group/$',
        group_views.group,
        name='group'),
    url(r'^group/delete/$',
        group_views.group_delete,
        name="group_delete")
]

urlpatterns += [
    url(r'^registrationrequest/$',
        registrationrequest_views.registrationrequest,
        name='registrationrequest'),
    url(r'^registrationrequest/delete/$',
        registrationrequest_views.registrationrequest_delete,
        name="registrationrequest_delete")
]

urlpatterns += [
    url(r'^contracttemplate/edit/$',
        contracttemplate_views.contracttemplate_edit,
        name='contracttemplate_edit'),
    url(r'^contracttemplate/$',
        contracttemplate_views.contracttemplate,
        name='contracttemplate'),
    url(r'^contracttemplate/delete/$',
        contracttemplate_views.contracttemplate_delete,
        name="contracttemplate_delete")
]

urlpatterns += [
    url(r'^simple_login/$',
        ebsadmin_views.simple_login),
    url(r'^table/settings/$',
        ebsadmin_views.table_settings,
        name="table_settings"),
    url(r'^setportsstatus/$',
        ebsadmin_views.set_ports_status),
    url(r'^getportsstatus/$',
        ebsadmin_views.get_ports_status),
    url(r'^templates/$',
        ebsadmin_views.templates),
    url(r'^documentrender/$',
        ebsadmin_views.documentrender,
        name="documentrender"),
    url(r'^templaterender/$',
        ebsadmin_views.templaterender,
        name="templaterender"),
    url(r'^ipaddress/getfrompool/$',
        ebsadmin_views.getipfrompool,
        name='getipfrompool'),
    url(r'^credentials/gen/$',
        ebsadmin_views.generate_credentials,
        name="generate_credentials"),
    url(r'^getmacforip/$',
        ebsadmin_views.get_mac_for_ip,
        name="get_mac_for_ip"),
    url(r'^sessions/reset/$',
        ebsadmin_views.session_reset,
        name="session_reset"),
    url(r'^sessions/hardreset/$',
        ebsadmin_views.session_hardreset,
        name="session_hardreset"),
    url(r'^cities/$',
        ebsadmin_views.cities),
    url(r'^streets/$',
        ebsadmin_views.streets,
        name="street"),
    url(r'^houses/$',
        ebsadmin_views.houses,
        name="house"),
    url(r'^test_credentials/$',
        nasses_views.testCredentials)
]

urlpatterns += [
    url(r'^jsi18n/(?P<packages>\S+?)/$',
        javascript_catalog)
]
