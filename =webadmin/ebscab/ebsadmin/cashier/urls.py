from django.conf.urls.defaults import *




urlpatterns = patterns('ebsadmin.cashier.views',
    url(r'^$', 'index', name='cashier_index'),
    url(r'^transactionreport/$', 'transactionreport', name='cashier_transactionreport'),
)

