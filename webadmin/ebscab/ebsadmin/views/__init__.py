# -*- coding: utf-8 -*-

from ebsadmin.views.access import accessparameters
from ebsadmin.views.account import (
    account_management_accounttariff,
    account_management_delete,
    account_management_restore,
    account_management_status,
    account_management_suspendedperiod,
    accountedit,
    accounttarif_edit
)
from ebsadmin.views.accountaddonservice import (
    accountaddonservice_deactivate,
    accountaddonservice_delete,
    accountaddonservice_edit
)
from ebsadmin.views.accountgroup import (
    accountgroup,
    accountgroup_delete,
    accountgroup_edit
)
from ebsadmin.views.accounthardware import (
    accounthardware,
    accounthardware2,
    accounthardware_delete
)
from ebsadmin.views.accountprepaysradiustraffic import (
    accountprepaysradiustraffic,
    accountprepaysradiustraffic_delete,
    accountprepaysradiustraffic_edit
)
from ebsadmin.views.accountprepaystime import (
    accountprepaystime,
    accountprepaystime_delete,
    accountprepaystime_edit
)
from ebsadmin.views.accountprepaystraffic import (
    accountprepaystraffic,
    accountprepaystraffic_delete,
    accountprepaystraffic_edit
)
from ebsadmin.views.accountsreport import accountsreport
from ebsadmin.views.accountsuppagreement import (
    accountsuppagreement_delete,
    accountsuppagreement_edit
)
from ebsadmin.views.accounttariff import accounttariff_delete
from ebsadmin.views.actionlog import actionlog
from ebsadmin.views.actions import actions_set
from ebsadmin.views.activesessionreport import activesessionreport
from ebsadmin.views.addonservice import (
    addonservice,
    addonservice_delete,
    addonservice_edit
)
from ebsadmin.views.addonservicetariff import (
    addonservicetariff,
    addonservicetariff_delete,
    addonservicetariff_edit
)
from ebsadmin.views.address import (
    address,
    address_delete,
    cities,
    city_edit,
    house_edit,
    houses,
    street_edit,
    streets
)
from ebsadmin.views.admin_dashboard import admin_dashboard
from ebsadmin.views.authlog import authlogreport
from ebsadmin.views.ballancehistoryreport import ballancehistoryreport
from ebsadmin.views.bonustransaction import bonus_transaction_edit
from ebsadmin.views.card import (
    card,
    card_delete,
    card_edit,
    card_generate,
    card_manage,
    card_update,
    salecard,
    salecard_edit
)
from ebsadmin.views.charts import charts
from ebsadmin.views.comment import comment_delete, comment_edit
from ebsadmin.views.contracttemplate import (
    contracttemplate,
    contracttemplate_delete,
    contracttemplate_edit
)
from ebsadmin.views.credentials import generate_credentials, testCredentials
from ebsadmin.views.dealer import (
    dealer,
    dealer_delete,
    dealer_edit,
    dealer_select
)
from ebsadmin.views.document import (
    cheque_render,
    document,
    document_save,
    documentrender
)
from ebsadmin.views.dynamicfields import (
    dynamicschemafield,
    dynamicschemafield_delete,
    dynamicschemafield_edit
)
from ebsadmin.views.getipfrompool import getipfrompool, getipfrompool2
from ebsadmin.views.getmacforip import get_mac_for_ip
from ebsadmin.views.globalstat import globalstat
from ebsadmin.views.group import group, group_delete, group_edit
from ebsadmin.views.groupstat import groupstat
from ebsadmin.views.hardware import hardware, hardware_delete, hardware_edit
from ebsadmin.views.hardwaretype import (
    hardwaretype,
    hardwaretype_delete,
    hardwaretype_edit
)
from ebsadmin.views.ipinusereport import ipinusereport
from ebsadmin.views.ippool import ippool, ippool_delete, ippool_edit
from ebsadmin.views.login import simple_login
from ebsadmin.views.logview import logview
from ebsadmin.views.manufacturer import (
    manufacturer,
    manufacturer_delete,
    manufacturer_edit
)
from ebsadmin.views.model import model, model_delete, model_edit
from ebsadmin.views.monitoring import index, radiusstat
from ebsadmin.views.nasses import nas, nas_delete, nas_edit, testCredentials
from ebsadmin.views.news import news, news_delete, news_edit
from ebsadmin.views.notificationssettings import (
    notificationssettings,
    notificationssettings_delete,
    notificationssettings_edit
)
from ebsadmin.views.onetimeservice import (
    onetimeservice,
    onetimeservice_delete,
    onetimeservice_edit
)
from ebsadmin.views.operator import operator_edit
from ebsadmin.views.payment import payment, payment_delete, payment_edit
from ebsadmin.views.periodicalservice import (
    periodicalservice,
    periodicalservice_delete,
    periodicalservice_edit
)
from ebsadmin.views.periodicalservicelog import (
    periodicalservicelog,
    periodicalservicelog_delete
)
from ebsadmin.views.permissiongroup import (
    permissiongroup,
    permissiongroup_delete,
    permissiongroup_edit
)
from ebsadmin.views.ping import tools_ping
from ebsadmin.views.prepaidtraffic import (
    prepaidtraffic_delete,
    prepaidtraffic_edit
)
from ebsadmin.views.radiusattr import (
    radiusattr,
    radiusattr_delete,
    radiusattr_edit
)
from ebsadmin.views.radiustraffic import (
    radiustraffic,
    radiustrafficnode_delete,
    radiustrafficnode_edit,
    radiustrafficservice_delete
)
from ebsadmin.views.registrationrequest import (
    registrationrequest,
    registrationrequest_delete
)
from ebsadmin.views.session import session_hardreset, session_reset
from ebsadmin.views.settlementperiod import (
    settlementperiod,
    settlementperiod_delete,
    settlementperiod_edit
)
from ebsadmin.views.shedulelog import shedulelog
from ebsadmin.views.sms import sendsms, sms, sms_delete
from ebsadmin.views.speedlimit import speedlimit_delete, speedlimit_edit
from ebsadmin.views.sql import sql
from ebsadmin.views.subaccount import subaccount_delete, subaccountedit
from ebsadmin.views.suppagreement import (
    suppagreement,
    suppagreement_delete,
    suppagreement_edit
)
from ebsadmin.views.suspendedperiod import (
    suspendedperiod,
    suspendedperiod_delete
)
from ebsadmin.views.switch import (
    get_ports_status,
    set_ports_status,
    switch,
    switch_delete,
    switch_edit,
    switch_port_status
)
from ebsadmin.views.systemuser import (
    systemuser,
    systemuser_delete,
    systemuser_edit
)
from ebsadmin.views.table import table_settings
from ebsadmin.views.tariff import (
    tariff,
    tariff_delete,
    tariff_edit,
    tariff_hide
)
from ebsadmin.views.template import (
    template,
    template_delete,
    template_edit,
    templaterender,
    templates,
    templates_save,
    templateselect
)
from ebsadmin.views.timeaccess import (
    timeaccessnode_delete,
    timeaccessnode_edit,
    timeaccessservice,
    timeaccessservice_delete
)
from ebsadmin.views.timeperiod import (
    timeperiod,
    timeperiod_delete,
    timeperiod_edit,
    timeperiodnode_edit
)
from ebsadmin.views.timespeed import timespeed_delete, timespeed_edit
from ebsadmin.views.tpchangerule import (
    tpchangerule,
    tpchangerule_delete,
    tpchangerule_edit
)
from ebsadmin.views.trafficclass import (
    trafficclass,
    trafficclass_delete,
    trafficclass_edit,
    trafficclass_upload,
    trafficclass_weight,
    trafficnode,
    trafficnode_delete,
    trafficnode_list
)
from ebsadmin.views.trafficlimit import (
    trafficlimit,
    trafficlimit_delete,
    trafficlimit_edit
)
from ebsadmin.views.traffictransmit import (
    traffictransmitnode_delete,
    traffictransmitnode_edit,
    traffictransmitservice,
    traffictransmitservice_delete
)
from ebsadmin.views.transaction import totaltransaction_delete, transaction
from ebsadmin.views.transactionreport import (
    transactionreport,
    transactionreport2
)
from ebsadmin.views.transactiontype import (
    transactiontype,
    transactiontype_delete,
    transactiontype_edit
)
