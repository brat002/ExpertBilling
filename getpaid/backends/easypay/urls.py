from django.conf.urls import patterns, url
from getpaid.backends.easypay.views import DummyAuthorizationView

urlpatterns = patterns('',
    url(r'^payment/authorization/(?P<pk>[0-9]+)/$', DummyAuthorizationView.as_view(), name='getpaid-dummy-authorization'),
)
