from django.conf.urls import patterns, url
from views import PayView, FailureView, CheckView

urlpatterns = patterns('',
    url(r'^yandexcassa/success/$', PayView.as_view(), name='yandexcassa-postback'),
    url(r'^yandexcassa/check/$', CheckView.as_view(), name='yandexcassa-check'),
    url(r'^yandexcassa/failure/$', FailureView.as_view(), name='yandexcassa-failure'),
)
