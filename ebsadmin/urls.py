from django.conf.urls.defaults import *
import wi

urlpatterns = patterns('ebsadmin.transactionreport',
                       url(r'^transactionreport/$', 'transactionreport'),
                       )
urlpatterns += patterns('ebsadmin.charts',
                       url(r'^charts/$', 'charts'),
                       
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
    url(r'^nas/edit/$', 'nas_edit', name='nas_edit'),
    url(r'^nas/$', 'nas', name='nas'),
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
    url(r'^trafficclass/edit/$', 'trafficclass_edit', name='trafficclass_edit'),
    url(r'^trafficclass/$', 'trafficclass', name='trafficclass'),
    url(r'^trafficnode_list/$', 'trafficnode_list', name='trafficnode_list'),
    #url(r'^ippool/delete/$', "ippool_delete", name="ippool_delete"),
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
