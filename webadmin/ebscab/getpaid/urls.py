# -*- coding: utf-8 -*-

from django.conf.urls import include, url

from getpaid.utils import import_backend_modules
from getpaid.views import SelectPaymentView, FallbackView, NewPaymentView


includes_list = []
for backend_name, urls in import_backend_modules('urls').items():
    includes_list.append(url(r'^%s/' % backend_name, include(urls)))

urlpatterns = [
    url(r'^new/payment/$',
        SelectPaymentView.as_view(),
        name='getpaid-select-payment'),
    url(r'^new/fillform/$',
        NewPaymentView.as_view(),
        name='getpaid-new-payment'),
    url(r'^payment/success/(?P<pk>\d+)/$',
        FallbackView.as_view(success=True),
        name='getpaid-success-fallback'),
    url(r'^payment/failure/(?P<pk>\d+)$',
        FallbackView.as_view(success=False),
        name='getpaid-failure-fallback')
]

urlpatterns += includes_list
