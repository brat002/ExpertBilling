from django.conf.urls.defaults import *
from django.contrib import admin

from views import *


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^webmoney/success/$', success,        name='wm_sample-success'),
    url(r'^webmoney/fail/$',    fail,           name='wm_sample-fail'),
    url(r'^webmoney/$',         simple_payment, name='wm_sample-payment'),
)
