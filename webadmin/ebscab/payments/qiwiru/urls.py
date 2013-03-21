from django.conf.urls import patterns, url
from payments.qiwiru.views import PayView

urlpatterns = patterns('',
    url(r'^qiwiru/payment/$', PayView.as_view(), name='getpaid-qiwiru-pay'),
)
