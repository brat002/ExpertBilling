# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from models import Account, SystemUser


ADMIN_URLS = (
    '/helpdesk/',
    '/media/',
    '/admin/',
    '/static/',
    '/admin_media',
    'admin-media',
    '/accounts/logout',
    '/ext/',
    '/ext/transactions/',
    '/ebsadmin/'
)


class UrlFilter(object):

    def process_request(self, request):
        try:
            account_obj = request.user.account
            if isinstance(account_obj, SystemUser):
                # we need to test user against a number of URLs
                if not any([request.META['PATH_INFO'].startswith(a)
                            for a in ADMIN_URLS]):
                    return HttpResponseRedirect(reverse("helpdesk_dashboard"))
        except AttributeError, e:
            # assumed that user is Anonimous
            pass
