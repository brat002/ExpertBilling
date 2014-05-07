from django.conf.urls import patterns, url
from views import PayView

urlpatterns = patterns('',
                       url(r'^privat24/payment/result/$', PayView.as_view(), name='getpaid-privat24-pay'),
                       url(r'^privat24/payment/$', PayView.as_view(), name='payment-result'),
    
)
