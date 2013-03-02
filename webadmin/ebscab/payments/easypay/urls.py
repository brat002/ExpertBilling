from django.conf.urls import patterns, url
from payments.easypay.views import EasyPayView

urlpatterns = patterns('',
    url(r'^easypay/payment/$', EasyPayView.as_view(), name='getpaid-easypay-pay'),
)
