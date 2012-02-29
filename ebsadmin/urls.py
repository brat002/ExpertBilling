from django.conf.urls.defaults import *

urlpatterns = patterns('ebsadmin.transactionreport',
                       url(r'^transactions/$', 'transactionreport'),
                       )

urlpatterns += patterns('ebsadmin.views',
     url(r'^accounts/$', 'jsonaccounts'),
     url(r'^simple_login/$', 'simple_login'),
     url(r'^periodicalservice/$', 'periodicalservice'),
     url(r'^addonservice/$', 'addonservice'),
     
     url(r'^gettariffs/$', 'get_tariffs'),
     url(r'^accountsfortariff/$', 'accounts_for_tarif'),
     
     
     url(r'^settlementperiods/$', 'settlementperiods'),
     url(r'^settlementperiods/delete/$', 'settlementperiod_delete'),
     url(r'^settlementperiods/save/$', 'settlementperiod_save'),
     
     url(r'^cities/$', 'cities'),
     
     url(r'^nasses/$', 'nasses'),
     url(r'^nasses/save/$', 'nas_save'),
     url(r'^nasses/delete/$', 'nas_delete'),
     #url(r'^nasses1/$', 'nasses1'),
     url(r'^nas/$', 'nas'),
     
     url(r'^switch/$', 'switch'),
     url(r'^ippool/$', 'ippool'),
     url(r'^tpchange/$', 'tpchange'),
     url(r'^tpchange/set/$', 'tpchange_save'),
     url(r'^actions/set/$', 'actions_set'),
     url(r'^render/cheque/$', 'cheque_render'),
     
     url(r'^accountaddonservices/$', 'accountaddonservices'),
     url(r'^accountaddonservices/get/$', 'accountaddonservices_get'),
     url(r'^accountaddonservices/set/$', 'accountaddonservices_set'),
     url(r'^suspendedperiods/$', 'suspendedperiods'),
     url(r'^suspendedperiod/get/$', 'suspendedperiod_get'),
     url(r'^suspendedperiod/set/$', 'suspendedperiod_set'),
     url(r'^transaction/set/$', 'transaction_set'),
     
     url(r'^document/$', 'document'),
     url(r'^document/set/$', 'document_save'),
     url(r'^document/get/$', 'document_get'),
     url(r'^template/$', 'template'),
     url(r'^documentrender/$', 'documentrender'),
     url(r'^accounthardware/$', 'accounthardware'),
     
     
     
     url(r'^accounttariffs/$', 'accounttariffs'),
     
     url(r'^account/ipnforvpn/$', 'ipnforvpn'),
     url(r'^account/save/$', 'account_save'),
     url(r'^account/exists/$', 'account_exists'),
     url(r'^account/$', 'account'),
     url(r'^accounts/live/$', 'account_livesearch'),
     url(r'^subaccounts/$', 'subaccounts'),
     url(r'^addonservices/$', 'addonservices'),
     url(r'^organizations/$', 'organizations'),
     url(r'^banks/$', 'banks'),
     
     url(r'^tariffs/$', 'tariffs'),
     url(r'^subaccounts/get/$', 'subaccount'),
     url(r'^subaccounts/set/$', 'subaccount_save'),
     url(r'^subaccounts/delete/$', 'subaccount_delete'),
     url(r'^ipaddress/getfrompool/$', 'getipfrompool'),
     url(r'^credentials/gen/$', 'generate_credentials'),
     url(r'^getmacforip/$', 'get_mac_for_ip'),
     url(r'^contracttemplate/$', 'contracttemplate'),
     url(r'^contracttemplates/$', 'contracttemplates'),
     url(r'^sessions/$', 'sessions'),
     
     #url(r'^simplelogin/$', 'simplelogin'),
     url(r'^grid/$', 'grid'),
     url(r'^city/$', 'city'),
     url(r'^streets/$', 'streets'),
     url(r'^houses/$', 'houses'),
     url(r'^systemuser/$', 'systemuser'),
     url(r'^systemusers/$', 'systemusers'),
     
     url(r'^accountstatus/$', 'accountstatus'),
     url(r'^transactiontypes/$', 'transactiontypes'),
     url(r'^test_credentials/$', 'testCredentials'),
)
