from django.conf.urls import patterns, url
from views import PayView

urlpatterns = patterns('',
    url(r'^payment/$', PayView.as_view(), name='getpaid-liqpay-pay'),
)
