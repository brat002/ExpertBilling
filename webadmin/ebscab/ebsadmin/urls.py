from django.conf.urls.defaults import *
import wi

urlpatterns = patterns('ebsadmin.transactionreport',
                       url(r'^transactionreport/$', 'transactionreport'),
                       )
urlpatterns += patterns('ebsadmin.charts',
                       url(r'^charts/$', 'charts', name='charts'),
                       
                       )
urlpatterns += patterns('ebsadmin.wi',
    url(r'^account/', wi.accountedit, name='account_edit'),
    url(r'^accounttariff/delete/', wi.accounttariff_delete, name='accounttariff_delete'),
    url(r'^accounttariff/edit/', wi.accounttarif_edit, name='accounttariff_edit'),
    url(r'^transaction/edit/', wi.transaction, name='transaction_edit'),
    url(r'^accountaddonservice/', wi.accountaddonservice_edit, name='accountaddonservice'),
    url(r'^subaccount/delete/', wi.subaccount_delete, name='subaccount_delete'),
    url(r'^subaccount/', wi.subaccountedit, name='subaccount'),
    url(r'^accounthardware/delete/$', wi.accounthardware_delete, name="accounthardware_delete"),
    url(r'^accounthardware/', wi.accounthardware, name='accounthardware'),
    url(r'^transactionreport2/$', 'transactionreport2', name='transactionreport2'),
    url(r'^accountsreport/$', 'accountsreport', name='account_list'),
    url(r'^ipinusereport/$', 'ipinusereport', name='ipinuse_list'),
    url(r'^authlogreport/$', 'authlogreport', name='authlog_list'),
    url(r'^suspendedperiod/delete/$', 'suspendedperiod_delete', name='suspendedperiod_delete'),
    url(r'^suspendedperiod/$', 'suspendedperiod', name='suspendedperiod'),
    url(r'^activesessionreport/$', 'activesessionreport', name='activesessionreport'),
    url(r'^ballancehistoryreport/$', 'ballancehistoryreport', name='ballancehistoryreport'),
    url(r'^template/edit/$', 'template_edit', name='template_edit'),
    url(r'^template/delete/$', 'template_delete', name='template_delete'),
    url(r'^template/$', 'template', name='template'),
    url(r'^template/select/$', 'templateselect', name='templateselect'),
    
)

urlpatterns += patterns('ebsadmin.settlementperiod',
    url(r'^settlementperiod/edit/$', 'settlementperiod_edit', name='settlementperiod_edit'),
    url(r'^settlementperiod/delete/$', 'settlementperiod_delete', name='settlementperiod_delete'),
    url(r'^settlementperiod/$', 'settlementperiod', name='settlementperiod'),
)

urlpatterns += patterns('ebsadmin.transactiontype',
    url(r'^transactiontype/edit/$', 'transactiontype_edit', name='transactiontype_edit'),
    url(r'^transactiontype/delete/$', 'transactiontype_delete', name='transactiontype_delete'),
    url(r'^transactiontype/$', 'transactiontype', name='transactiontype'),
)

urlpatterns += patterns('ebsadmin.systemuser',
    url(r'^systemuser/edit/$', 'systemuser_edit', name='systemuser_edit'),
    url(r'^systemuser/delete/$', 'systemuser_delete', name='systemuser_delete'),
    url(r'^systemuser/$', 'systemuser', name='systemuser'),
)

urlpatterns += patterns('ebsadmin.modules.nas',
    url(r'^nas/edit/$', 'nas_edit', name='nas_edit'),
    url(r'^nas/delete/$', 'nas_delete', name='nas_delete'),
    url(r'^nas/testcreds/$', 'testCredentials', name='nas_test_credentials'),
    
    url(r'^nas/$', 'nas', name='nas'),
)

urlpatterns += patterns('ebsadmin.address',
    #url(r'^systemuser/edit/$', 'systemuser_edit', name='systemuser_edit'),
    #url(r'^systemuser/delete/$', 'systemuser_delete', name='systemuser_delete'),
    url(r'^city/edit/$', 'city_edit', name="city_edit"),
    url(r'^street/edit/$', 'street_edit', name="street_edit"),
    url(r'^house/edit/$', 'house_edit', name="house_edit"),
    url(r'^address/delete/$', 'address_delete', name="address_delete"),
    url(r'^address/$', 'address', name='address'),
    

    
)

urlpatterns += patterns('ebsadmin.addonservice',
    url(r'^addonservice/edit/$', 'addonservice_edit', name='addonservice_edit'),
    url(r'^addonservice/delete/$', 'addonservice_delete', name='addonservice_delete'),
    url(r'^addonservice/$', 'addonservice', name='addonservice'),
)

urlpatterns += patterns('ebsadmin.ippool',
    url(r'^ippool/edit/$', 'ippool_edit', name='ippool_edit'),
    url(r'^ippool/$', 'ippool', name='ippool'),
    url(r'^ippool/delete/$', "ippool_delete", name="ippool_delete"),
)

urlpatterns += patterns('ebsadmin.timeperiod',
    url(r'^timeperiod/edit/$', 'timeperiod_edit', name='timeperiod_edit'),
    url(r'^timeperiodnode/edit/$', 'timeperiodnode_edit', name='timeperiodnode_edit'),
    url(r'^timeperiod/$', 'timeperiod', name='timeperiod'),
    url(r'^timeperiod/delete/$', "timeperiod_delete", name="timeperiod_delete"),
)

urlpatterns += patterns('ebsadmin.trafficclass',
    url(r'^trafficclass/$', 'trafficclass', name='trafficclass'),
    url(r'^trafficclass/edit/$', 'trafficclass_edit', name='trafficclass_edit'),
    url(r'^trafficclass/weight/$', 'trafficclass_weight', name='trafficclass_weight'),
    url(r'^trafficclass/upload/$', 'trafficclass_upload', name='trafficclass_upload'),
    url(r'^trafficclass/delete/$', 'trafficclass_delete', name='trafficclass_delete'),
    
    url(r'^trafficnode_list/$', 'trafficnode_list', name='trafficnode_list'),
    url(r'^trafficnode/$', 'trafficnode', name='trafficnode'),
    url(r'^trafficnode/delete/$', 'trafficnode_delete', name='trafficnode_delete'),
    
    #url(r'^ippool/delete/$', "ippool_delete", name="ippool_delete"),
)

urlpatterns += patterns('ebsadmin.modules.radiusattr',
    url(r'^radiusattr/edit/$', 'radiusattr_edit', name='radiusattr_edit'),
    url(r'^radiusattr/$', 'radiusattr', name='radiusattr'),
    url(r'^radiusattr/delete/$', "radiusattr_delete", name="radiusattr_delete"),
)

urlpatterns += patterns('ebsadmin.modules.news',
    url(r'^news/edit/$', 'news_edit', name='news_edit'),
    url(r'^news/$', 'news', name='news'),
    url(r'^news/delete/$', "news_delete", name="news_delete"),
)

urlpatterns += patterns('ebsadmin.modules.tpchangerule',
    url(r'^tpchangerule/edit/$', 'tpchangerule_edit', name='tpchangerule_edit'),
    url(r'^tpchangerule/$', 'tpchangerule', name='tpchangerule'),
    url(r'^tpchangerule/delete/$', "tpchangerule_delete", name="tpchangerule_delete"),
    )

urlpatterns += patterns('ebsadmin.modules.operator',
    url(r'^operator/edit/$', 'operator_edit', name='operator_edit'),
)
urlpatterns += patterns('ebsadmin.modules.logview',
    url(r'^logview/$', 'logview', name='logview'),
)
urlpatterns += patterns('ebsadmin.modules.periodicalservicelog',
    url(r'^periodicalservicelog/delete/$', 'periodicalservicelog_delete', name='periodicalservicelog_delete'),
    url(r'^periodicalservicelog/$', 'periodicalservicelog', name='periodicalservicelog'),
    
)

urlpatterns += patterns('ebsadmin.modules.shedulelog',
    url(r'^shedulelog/delete/$', 'shedulelog_delete', name='shedulelog_delete'),
    url(r'^shedulelog/$', 'shedulelog', name='shedulelog'),
    
)


urlpatterns += patterns('ebsadmin.modules.manufacturer',
    url(r'^manufacturer/edit/$', 'manufacturer_edit', name='manufacturer_edit'),
    url(r'^manufacturer/$', 'manufacturer', name='manufacturer'),
    url(r'^manufacturer/delete/$', "manufacturer_delete", name="manufacturer_delete"),
)

urlpatterns += patterns('ebsadmin.modules.hardwaretype',
    url(r'^hardwaretype/edit/$', 'hardwaretype_edit', name='hardwaretype_edit'),
    url(r'^hardwaretype/$', 'hardwaretype', name='hardwaretype'),
    url(r'^hardwaretype/delete/$', "hardwaretype_delete", name="hardwaretype_delete"),
)

urlpatterns += patterns('ebsadmin.modules.model',
    url(r'^model/edit/$', 'model_edit', name='model_edit'),
    url(r'^model/$', 'model', name='model'),
    url(r'^model/delete/$', "model_delete", name="model_delete"),
)

urlpatterns += patterns('ebsadmin.modules.hardware',
    url(r'^hardware/edit/$', 'hardware_edit', name='hardware_edit'),
    url(r'^hardware/$', 'hardware', name='hardware'),
    url(r'^hardware/delete/$', "hardware_delete", name="hardware_delete"),
)

urlpatterns += patterns('ebsadmin.modules.switch',
    url(r'^switch/edit/$', 'switch_edit', name='switch_edit'),
    url(r'^switch/$', 'switch', name='switch'),
    url(r'^switch/delete/$', "switch_delete", name="switch_delete"),
)

urlpatterns += patterns('ebsadmin.modules.card',
    url(r'^card/edit/$', 'card_edit', name='card_edit'),
    url(r'^card/generate/$', 'card_generate', name='card_generate'),
    url(r'^card/update/$', 'card_update', name='card_update'),
    url(r'^card/manage/$', 'card_manage', name='card_manage'),
    url(r'^card/$', 'card', name='card'),
    url(r'^card/delete/$', "card_delete", name="card_delete"),
    url(r'^salecard/edit/$', "salecard_edit", name="salecard_edit"),
    url(r'^salecard/$', "salecard", name="salecard"),
)

urlpatterns += patterns('ebsadmin.modules.tariff',
    url(r'^tariff/edit/$', 'tariff_edit', name='tariff_edit'),
    url(r'^tariff/periodicalservice/edit/$', 'tariff_periodicalservice_edit', name='tariff_periodicalservice_edit'),
    url(r'^tariff/prepaidtraffic/edit/$', 'tariff_prepaidtraffic_edit', name='tariff_prepaidtraffic_edit'),
    
    url(r'^tariff/accessparameters/$', 'tariff_accessparameters', name='tariff_accessparameters'),
    url(r'^tariff/timespeed/edit/$', 'tariff_timespeed_edit', name='tariff_timespeed_edit'),
    url(r'^tariff/timespeed/delete/$', 'tariff_timespeed_delete', name='tariff_timespeed_delete'),
    url(r'^tariff/periodicalservice/$', 'tariff_periodicalservice', name='tariff_periodicalservice'),
    url(r'^tariff/periodicalservice/delete/$', 'periodicalservice_delete', name='periodicalservice_delete'),
    url(r'^tariff/traffictransmitnode/edit/$', 'tariff_traffictransmitnode_edit', name='tariff_traffictransmitnode_edit'),
    url(r'^tariff/traffictransmitnode/delete/$', 'traffictransmitnode_delete', name='traffictransmitnode_delete'),
    
    url(r'^tariff/onetimeservice/$', 'tariff_onetimeservice', name='tariff_onetimeservice'),
    url(r'^tariff/onetimeservice/edit/$', 'onetimeservice_edit', name='onetimeservice_edit'),
    url(r'^tariff/onetimeservice/delete/$', 'tariff_onetimeservice_delete', name='onetimeservice_delete'),
    
    url(r'^tariff/traffictransmitservice/delete/$', 'tariff_traffictransmitservice_delete', name='traffictransmitservice_delete'),
    url(r'^tariff/traffictransmitservice/$', 'tariff_traffictransmitservice', name='tariff_traffictransmitservice'),
    
    url(r'^tariff/radiustrafficservice/$', 'tariff_radiustraffic', name='tariff_radiustraffic'),
    url(r'^tariff/radiustrafficservice/delete/$', 'tariff_radiustrafficservice_delete', name='radiustrafficservice_delete'),
    url(r'^tariff/radiustrafficnode/edit/$', 'tariff_radiustrafficnode_edit', name='tariff_radiustrafficnode_edit'),
    url(r'^tariff/radiustrafficnode/delete/$', 'radiustrafficnode_delete', name='radiustrafficnode_delete'),
    
    url(r'^tariff/trafficlimit/edit/$', 'tariff_trafficlimit_edit', name='tariff_trafficlimit_edit'),
    url(r'^tariff/trafficlimit/delete/$', 'trafficlimit_delete', name='trafficlimit_delete'),
    url(r'^tariff/trafficlimit/$', 'tariff_trafficlimit', name='tariff_trafficlimit'),
    url(r'^tariff/speedlimit/edit/$', 'tariff_speedlimit_edit', name='tariff_speedlimit_edit'),
    url(r'^tariff/speedlimit/delete/$', 'speedlimit_delete', name='speedlimit_delete'),
    
    url(r'^tariff/timeaccessservice/delete/$', 'tariff_timeaccessservice_delete', name='tariff_timeaccessservice_delete'),
    url(r'^tariff/timeaccessservice/$', 'tariff_timeaccessservice', name='tariff_timeaccessservice'),
    url(r'^tariff/timeaccesssnode/edit/$', 'tariff_timeaccessnode_edit', name='tariff_timeaccessnode_edit'),
    url(r'^tariff/timeaccesssnode/delete/$', 'timeaccessnode_delete', name='timeaccessnode_delete'),
    
    url(r'^tariff/addonservicetariff/$', 'tariff_addonservicetariff', name='tariff_addonservicetariff'),
    url(r'^tariff/addonservicetariff/edit/$', 'tariff_addonservicetariff_edit', name='tariff_addonservicetariff_edit'),
    url(r'^tariff/addonservicetariff/delete/$', 'addonservicetariff_delete', name='addonservicetariff_delete'),
    url(r'^tariff/$', 'tariff', name='tariff'),
)

urlpatterns += patterns('ebsadmin.modules.dealer',
    url(r'^dealer/edit/$', 'dealer_edit', name='dealer_edit'),
    url(r'^dealer/select/$', 'dealer_select', name='dealer_select'),
    url(r'^dealer/$', 'dealer', name='dealer'),
)

urlpatterns += patterns('ebsadmin.modules.group',
    url(r'^group/edit/$', 'group_edit', name='group_edit'),
    url(r'^group/$', 'group', name='group'),
    url(r'^group/delete/$', "group_delete", name="group_delete"),
)

urlpatterns += patterns('ebsadmin.views',
     #url(r'^accounts/$', 'jsonaccounts'),
     url(r'^simple_login/$', 'simple_login'),
     #url(r'^periodicalservice/$', 'periodicalservice'),
     #url(r'^addonservice/$', 'addonservice'),
     
     
     
     url(r'^gettariffs/$', 'get_tariffs'),
     url(r'^actionlogs/$', 'actionlogs'),
     
     url(r'^accountsfortariff/$', 'accounts_for_tarif'),
     url(r'^accountsforcashier/$', 'get_accounts_for_cashier'),
     url(r'^systemuser_groups/$', 'systemuser_groups'),
     
     url(r'^timeperiods/save/$', 'timeperiods_save'),
     url(r'^timeperiods/delete/$', 'timeperiods_delete'),
     url(r'^timeperiods/$', 'timeperiods'),
     url(r'^timeperiodnodes/save/$', 'timeperiodnodes_save'),
     url(r'^timeperiodnodes/delete/$', 'timeperiodnodes_delete'),
     url(r'^timeperiodnodes/m2m/save/$', 'timeperiodnodes_m2m_save'),
     url(r'^timeperiodnodes/m2m/delete/$', 'timeperiodnodes_m2m_delete'),
     url(r'^timeperiodnodes/$', 'timeperiodnodes'),
     url(r'^onetimeservices/$', 'onetimeservices'),
     url(r'^trafficlimites/$', 'trafficlimites'),
     url(r'^speedlimites/$', 'speedlimites'),
     url(r'^addonservicetariff/$', 'addonservicetariff'),
     url(r'^authgroups/$', 'authgroups'),
     url(r'^sql/$', 'sql'),
     url(r'^spinfo/$', 'sp_info'),
     url(r'^traffictransmitservices/$', 'traffictransmitservices'),
     url(r'^radiustrafficservices/$', 'radiustrafficservices'),
     url(r'^radiustrafficservices/nodes/$', 'radiustrafficservices_nodes'),
     url(r'^prepaidtraffic/$', 'prepaidtraffic'),
     
     url(r'^traffictransmit/nodes/$', 'traffictransmit_nodes'),
     url(r'^timespeeds/$', 'timespeeds'),
     url(r'^timeaccessservices/nodes/$', 'timeaccessservices_nodes'),
     
     url(r'^timeaccessservices/$', 'timeaccessservices'),
     url(r'^settlementperiods/$', 'settlementperiods'),
     url(r'^accessparameters/$', 'accessparameters'),
     
     
     url(r'^settlementperiods/delete/$', 'settlementperiod_delete'),
     url(r'^settlementperiods/save/$', 'settlementperiod_save'),
     
     url(r'^listlogfiles/$', 'list_logfiles'),
     url(r'^gettaillog/$', 'get_tail_log'),
     
     url(r'^nasses/$', 'nasses'),
     url(r'^groups/$', 'groups'),
     url(r'^groups_detail/$', 'groups_detail'),
     
     url(r'^groups/set/$', 'groups_save'),
     url(r'^groups/delete/$', 'groups_delete'),
     url(r'^periodicalservices/$', 'periodicalservices'),
     
     
     
     url(r'^trafficclasses/set/$', 'trafficclasses_set'),
     url(r'^trafficclasses/delete/$', 'trafficclasses_delete'),
     url(r'^trafficclasses/$', 'trafficclasses'),
     
     
     url(r'^hardware/set/$', 'hardware_set'),
     url(r'^hardware/delete/$', 'hardware_delete'),
     url(r'^hardware/$', 'hardware'),
     url(r'^manufacturers/set/$', 'manufacturers_set'),
     url(r'^manufacturers/delete/$', 'manufacturers_delete'),
     url(r'^manufacturers/$', 'manufacturers'),
     url(r'^hwmodels/set/$', 'models_set'),
     url(r'^hwmodels/delete/$', 'models_delete'),
     url(r'^hwmodels/$', 'models'),
     url(r'^hardwaretypes/set/$', 'hardwaretypes_set'),
     url(r'^hardwaretypes/delete/$', 'hardwaretypes_delete'),
     url(r'^hardwaretypes/$', 'hardwaretypes'),
     
     url(r'^news/set/$', 'news_set'),
     url(r'^news/delete/$', 'news_delete'),
     url(r'^news/$', 'news'),
     
     url(r'^accounthardware/set/$', 'accounthardware_set'),
     url(r'^accounthardware/delete/$', 'accounthardware_delete'),
     url(r'^accounthardware/$', 'accounthardware'),
     url(r'^trafficclassnodes/set/$', 'trafficclassnodes_set'),
     url(r'^trafficclassnodes/delete/$', 'trafficclassnodes_delete'),
     url(r'^trafficclassnodes/$', 'trafficclassnodes'),
     url(r'^classforgroup/$', 'classforgroup'),
     url(r'^accountsfilter/$', 'accountsfilter'),
    
     
     url(r'^nasses/save/$', 'nas_save'),
     url(r'^nasses/delete/$', 'nas_delete'),
     
     #url(r'^nasses1/$', 'nasses1'),
     #url(r'^nas/$', 'nas'),
     
     #url(r'^switch/$', 'switch'),
     
     url(r'^switches/set/$', 'switches_set'),
     url(r'^switches/delete/$', 'switches_delete'),
     url(r'^switches/$', 'switches'),
     url(r'^setportsstatus/$', 'set_ports_status'),
     url(r'^getportsstatus/$', 'get_ports_status'),
     
     url(r'^cards/set/$', 'cards_set'),
     url(r'^cards/delete/$', 'cards_delete'),
     url(r'^cards/$', 'cards'),
     
     url(r'^dealers/set/$', 'dealers_set'),
     url(r'^dealers/delete/$', 'dealers_delete'),
     url(r'^dealers/$', 'dealers'),
     url(r'^getnotsoldcards/$', 'getnotsoldcards'),
     
     
     url(r'^getcardsnominal/$', 'get_cards_nominal'),
     url(r'^getnextcardseries/$', 'get_next_cardseries'),
     
     url(r'^pools/getbyipinuse/$', 'get_pool_by_ipinuse'),
     #url(r'^ippool/$', 'ippool'),
     url(r'^operator/set/$', 'operator_set'),
     url(r'^operator/$', 'operator'),
     
     
     url(r'^radiusattrs/set/$', 'radiusattrs_set'),
     url(r'^radiusattrs/delete/$', 'radiusattrs_delete'),
     url(r'^radiusattrs/$', 'radiusattrs'),
     
     url(r'^api/getmodel/$', 'get_model'),
     url(r'^api/getmodels/$', 'get_models'),
     url(r'^cards/status/set/$', 'cardsstatus_set'),
     url(r'^returncards/$', 'returncards'),
     url(r'^dealerpays/$', 'dealerpays'),
     url(r'^dealerpays/set/$', 'dealerpay_set'),
     url(r'^salecards/set/$', 'salecards_set'),
     url(r'^salecards/delete/$', 'salecards_delete'),
     url(r'^salecards/$', 'salecards'),
     
     url(r'^ippools/set/$', 'ippools_set'),
     url(r'^ippools/delete/$', 'ippools_delete'),
     url(r'^ippools/$', 'ippools'),
     #url(r'^tpchange/$', 'tpchange'),
     url(r'^tpchange/set/$', 'tpchange_save'),
     url(r'^actions/set/$', 'actions_set'),
     url(r'^render/cheque/$', 'cheque_render'),
     
     url(r'^accountaddonservices/$', 'accountaddonservices'),
     #url(r'^accountaddonservices/get/$', 'accountaddonservices_get'),
     url(r'^accountaddonservices/set/$', 'accountaddonservices_set'),
     url(r'^suspendedperiods/$', 'suspendedperiods'),
     #url(r'^suspendedperiod/get/$', 'suspendedperiod_get'),
     url(r'^suspendedperiod/set/$', 'suspendedperiod_set'),
     url(r'^suspendedperiod/delete/$', 'suspendedperiod_delete'),
     url(r'^transaction/set/$', 'transaction_set'),
     url(r'^transactions/delete/$', 'transactions_delete'),
     url(r'^transaction/$', 'transactions'),
     url(r'^tariffforaccount/$', 'tariffforaccount'),
     
     #url(r'^document/$', 'document'),
     #url(r'^document/set/$', 'document_save'),
     #url(r'^document/get/$', 'document_get'),
     url(r'^templates/delete/$', 'templates_delete'),
     url(r'^templates/save/$', 'templates_save'),
     url(r'^templates/$', 'templates'),
     url(r'^templatetypes/$', 'templatetypes'),
     url(r'^documentrender/$', 'documentrender', name="documentrender"),
     url(r'^templaterender/$', 'templaterender', name="templaterender"),
     
     
     url(r'^accountprepaysradiustrafic/set/$', 'accountprepaysradiustrafic_set'),
     url(r'^accountprepaysradiustrafic/$', 'accountprepaysradiustrafic'),

     url(r'^accountprepaystrafic/set/$', 'accountprepaystrafic_set'),
     url(r'^accountprepaystrafic/$', 'accountprepaystrafic'),
     
     url(r'^accounttariffs/$', 'accounttariffs'),
     url(r'^accounttariffs/set/$', 'accounttariffs_set'),
     url(r'^accounttariffs/bathset/$', 'accounttariffs_bathset'),
     
     url(r'^accounttariffs/delete/$', 'accounttariffs_delete'),
     
     url(r'^account/ipnforvpn/$', 'ipnforvpn'),
     url(r'^account/save/$', 'account_save'),
     url(r'^account/delete/$', 'account_delete'),
     url(r'^account/exists/$', 'account_exists'),
     url(r'^account/$', 'account'),
     #url(r'^accounts/live/$', 'account_livesearch'),
     url(r'^subaccounts/$', 'subaccounts'),
     url(r'^addonservices/$', 'addonservices'),
     url(r'^addonservices/set/$', 'addonservices_set'),
     url(r'^addonservices/delete/$', 'addonservices_delete'),
     url(r'^organizations/$', 'organizations'),
     url(r'^banks/set/$', 'banks_set'),
     url(r'^banks/$', 'banks'),
     
     url(r'^tariffs/set/$', 'tariffs_set'),
     url(r'^tariffs/delete/$', 'tariffs_delete'),
     url(r'^tariffs/$', 'tariffs'),
     #url(r'^subaccounts/get/$', 'subaccount'),
     url(r'^subaccounts/set/$', 'subaccount_save'),
     url(r'^subaccounts/delete/$', 'subaccount_delete'),
     url(r'^ipaddress/getfrompool/$', 'getipfrompool', name='getipfrompool'),
     url(r'^credentials/gen/$', 'generate_credentials', name="generate_credentials"),
     url(r'^getmacforip/$', 'get_mac_for_ip', name="get_mac_for_ip"),
     #url(r'^contracttemplate/$', 'contracttemplate'),
     url(r'^contracttemplate/set/$', 'contracttemplates_set'),
     url(r'^contracttemplate/delete/$', 'contracttemplate_delete'),
     
     url(r'^contracttemplates/$', 'contracttemplates'),
     
     
     url(r'^sessions/$', 'sessions'),
     url(r'^sessions/reset/$', 'session_reset'),
     
     url(r'^cities/set/$', 'cities_set'),
     url(r'^cities/$', 'cities'),
     
     url(r'^cities/delete/$', 'cities_delete'),
     url(r'^streets/$', 'streets', name="street"),
     url(r'^streets/set/$', 'streets_set'),
     url(r'^streets/delete/$', 'streets_delete'),
     url(r'^houses/$', 'houses', name="house"),
     url(r'^houses/set/$', 'houses_set'),
     url(r'^houses/delete/$', 'houses_delete'),

     url(r'^systemusers/$', 'systemusers'),
     url(r'^tpchangerules/set/$', 'tpchangerules_set'),
     url(r'^tpchangerules/delete/$', 'tpchangerules_delete'),
     url(r'^tpchangerules/$', 'tpchangerules'),
     url(r'^systemusers/delete/$', 'systemusers_delete'),
     url(r'^systemusers/set/$', 'systemusers_set'),

     url(r'^transactiontypes/set/$', 'transactiontypes_set'),
     url(r'^transactiontypes/$', 'transactiontypes'),
     url(r'^test_credentials/$', 'testCredentials'),
)
