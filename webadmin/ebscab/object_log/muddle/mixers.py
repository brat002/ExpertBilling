# -*- coding: utf-8 -*-

from muddle.shots import register, TemplateMixer


register('user-detail-tab',
         TemplateMixer('object_log/muddle/user_actions_tab.html'))
register('user-detail-tab',
         TemplateMixer('object_log/muddle/user_log_tab.html'))
register('group-detail-tab',
         TemplateMixer('object_log/muddle/group_log_tab.html'))
