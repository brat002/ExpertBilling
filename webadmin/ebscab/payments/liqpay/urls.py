from django.conf.urls import patterns, url
from views import PayView

urlpatterns = patterns('',
                       url(r'^liqpay/payment/result/$', PayView.as_view(), name='getpaid-liqpay-pay'),
                       url(r'^liqpay/payment/$', PayView.as_view(), name='payment-result'),
    
)
