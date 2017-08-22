# -*- coding: utf-8 -*-

from django.conf.urls import url

from views import PayView, SuccessView, FailureView


urlpatterns = [
    url(r'^robokassa/postback/$',
        PayView.as_view(),
        name='robokassa-w1ru-postback'),
    url(r'^robokassa/success/$',
        SuccessView.as_view(),
        name='robokassa-w1ru-success'),
    url(r'^robokassa/failure/$',
        FailureView.as_view(),
        name='robokassa-w1ru-failure')
]
