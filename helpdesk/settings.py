# -*- coding=utf-8 -*-
"""
Default settings for helpdesk.
"""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# User area menu
# (view_name, verbose)
PERSONAL_AREA_MENU = [
    #('account_profile', _(u'Profile')),
    ('helpdesk_account_tickets', _(u'Support')),
    ('helpdesk_account_tickets_add', _(u'Add ticket')),
    ('billservice_index', _(u'View site')),
    #('account_logout', _(u'Logout')),
]
# check for django-tagging support
HAS_TAG_SUPPORT = 'tagging' in settings.INSTALLED_APPS


try:
        import tagging
except ImportError:
        HAS_TAG_SUPPORT = False
        

