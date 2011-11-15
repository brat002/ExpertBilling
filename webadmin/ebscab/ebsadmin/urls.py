from django.conf.urls.defaults import *


urlpatterns = patterns('ebsadmin.views',
     url(r'^accounts/$', 'jsonaccounts'),
     url(r'^nasses/$', 'nasses'),
     url(r'^nas/$', 'nas'),
     url(r'^switch/$', 'switch'),
     url(r'^ippool/$', 'ippool'),
     url(r'^accountaddonservices/$', 'accountaddonservices'),
     
     url(r'^account/$', 'account'),
     url(r'^subaccounts/$', 'subaccounts'),
     url(r'^subaccounts/get/$', 'subaccount'),
     url(r'^subaccounts/set/$', 'subaccount_save'),
     #url(r'^simplelogin/$', 'simplelogin'),
     url(r'^grid/$', 'grid'),
     url(r'^city/$', 'city'),
     url(r'^street/$', 'street'),
     url(r'^house/$', 'house'),
     url(r'^systemuser/$', 'systemuser'),
     url(r'^account/save/$', 'account_save'),
     url(r'^accountstatus/$', 'accountstatus'),
     url(r'^transactiontypes/$', 'transactiontypes'),
)
