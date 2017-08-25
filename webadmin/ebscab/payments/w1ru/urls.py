# -*- coding: utf-8 -*-

from django.conf.urls import url

from views import PayView, SuccessView, FailureView


urlpatterns = [
    url(r'^w1ru/postback/$',
        PayView.as_view(),
        name='getpaid-w1ru-postback'),
    url(r'^w1ru/success/$',
        SuccessView.as_view(),
        name='getpaid-w1ru-success'),
    url(r'^w1ru/failure/$',
        FailureView.as_view(),
        name='getpaid-w1ru-failure')
]
