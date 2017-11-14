# -*- coding: utf-8 -*-

from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import (
    bad_request as default_bad_request,
    page_not_found as default_page_not_found,
    permission_denied as default_permission_denied,
    server_error as default_server_error
)

from billservice.models import Account


def _custom_hadler_factory(name, default_handler, template_name):
    @requires_csrf_token
    def handler(request, *args, **kwargs):
        if isinstance(request.user.account, Account):
            kwargs['template_name'] = template_name
        return default_handler(request, *args, **kwargs)
    handler.__name__ = name
    return handler


bad_request = _custom_hadler_factory(
    'bad_request', default_bad_request, 'ebsweb/400.html')

permission_denied = _custom_hadler_factory(
    'permission_denied', default_permission_denied, 'ebsweb/403.html')

page_not_found = _custom_hadler_factory(
    'page_not_found', default_page_not_found, 'ebsweb/404.html')

server_error = _custom_hadler_factory(
    'server_error', default_server_error, 'ebsweb/500.html')
