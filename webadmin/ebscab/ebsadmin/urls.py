from django.conf.urls.defaults import *
import transactionreport

urlpatterns = patterns('ebsadmin.transactionreport',
                       url(r'^transactionreport/$', 'transactionreport'),
                       url(r'^transactionreport2/$', 'transactionreport2'),
                       url(r'^accountsreport/$', 'accountsreport', name='accounts_report'),
                       url(r'^activesessionreport/$', 'activesessionreport'),
                       )
urlpatterns += patterns('ebsadmin.charts',
                       url(r'^charts/$', 'charts'),
                       
                       )
urlpatterns += patterns('',
    url('account_detail/(\d+)/', transactionreport.accountedit, name='account_detail'),
    
    url('subaccount_details/(\d+)/', transactionreport.subaccountedit, name='subaccount_detail')
    
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
     url(r'^subaccount/delete/$', 'subaccount_delete'),
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
     url(r'^documentrender/$', 'documentrender'),
     
     
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
     url(r'^ipaddress/getfrompool/$', 'getipfrompool'),
     #url(r'^credentials/gen/$', 'generate_credentials'),
     url(r'^getmacforip/$', 'get_mac_for_ip'),
     #url(r'^contracttemplate/$', 'contracttemplate'),
     url(r'^contracttemplate/set/$', 'contracttemplates_set'),
     url(r'^contracttemplate/delete/$', 'contracttemplate_delete'),
     
     url(r'^contracttemplates/$', 'contracttemplates'),
     
     
     url(r'^sessions/$', 'sessions'),
     url(r'^sessions/reset/$', 'session_reset'),
     
     url(r'^cities/set/$', 'cities_set'),
     url(r'^cities/$', 'cities'),
     
     url(r'^cities/delete/$', 'cities_delete'),
     url(r'^streets/$', 'streets'),
     url(r'^streets/set/$', 'streets_set'),
     url(r'^streets/delete/$', 'streets_delete'),
     url(r'^houses/$', 'houses'),
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
