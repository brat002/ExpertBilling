from django.conf.urls import patterns, url
from views import PayView

urlpatterns = patterns('',
    url(r'^simpleterminal/payment/$', PayView.as_view(), name='getpaid-simpleterminal-pay'),
)
