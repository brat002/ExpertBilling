# -*- coding: utf-8 -*-

from django.conf.urls import url

from payments.yandexcassa.views import PayView, FailureView, CheckView


urlpatterns = [
    url(r'^yandexcassa/success/$',
        PayView.as_view(),
        name='yandexcassa-postback'),
    url(r'^yandexcassa/check/$',
        CheckView.as_view(),
        name='yandexcassa-check'),
    url(r'^yandexcassa/failure/$',
        FailureView.as_view(),
        name='yandexcassa-failure')
]
