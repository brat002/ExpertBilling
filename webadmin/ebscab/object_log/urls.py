# -*- coding: utf-8 -*-

from django.conf.urls import url

from object_log import views


urlpatterns = [
    url(r'^user/(?P<pk>\d+)/actions/?$',
        views.list_user_actions,
        name="user-object_log-actions"),
    url(r'^user/(?P<pk>\d+)/object_log/?$',
        views.list_for_user,
        name="user-object_log"),
    url(r'^group/(?P<pk>\d+)/object_log/?$',
        views.list_for_group,
        name="group-object_log"),
    url(r'object/(?P<content_type_id>\d+)/(?P<pk>\d+)/?$',
        views.object_detail,
        name='object-detail')
]
