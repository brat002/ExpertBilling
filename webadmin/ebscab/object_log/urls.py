# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns


urlpatterns = patterns(
    'object_log.views',
    url(r'^user/(?P<pk>\d+)/actions/?$',
        'list_user_actions',
        name="user-object_log-actions"),
    url(r'^user/(?P<pk>\d+)/object_log/?$',
        'list_for_user',
        name="user-object_log"),
    url(r'^group/(?P<pk>\d+)/object_log/?$',
        'list_for_group',
        name="group-object_log"),
    url(r'object/(?P<content_type_id>\d+)/(?P<pk>\d+)/?$',
        'object_detail',
        name='object-detail')
)
