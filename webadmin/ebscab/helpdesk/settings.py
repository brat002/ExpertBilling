# -*- coding: utf-8 -*-

"""
Default settings for helpdesk.
"""


# User area menu
# (view_name, verbose)
PERSONAL_AREA_MENU = [
    ('helpdesk_account_tickets', u'Список запросов'),
    ('helpdesk_account_tickets_add', u'Добавить запрос'),
    ('billservice_index', u'В кабинет'),
    ('admin_dashboard', u'Интерфейс администратора'),
]

# check for django-tagging support
HAS_TAG_SUPPORT = False  # 'tagging' in settings.INSTALLED_APPS
try:
    import tagging
except ImportError:
    HAS_TAG_SUPPORT = False


MAX_EMAIL_ATTACHMENT_SIZE = 10000000
