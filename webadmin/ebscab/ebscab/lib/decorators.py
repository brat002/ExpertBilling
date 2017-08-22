# -*- coding: utf-8 -*-

from functools import wraps, WRAPPER_ASSIGNMENTS

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.template.loader import get_template

from ebscab.lib.http import JsonResponse


def available_attrs(fn):
    return tuple(a for a in WRAPPER_ASSIGNMENTS if hasattr(fn, a))


def render_to(tmpl):
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            return get_template(tmpl).render(output, request)
        return wrapper
    return renderer


def ajax_request(func):
    """
    Checks request.method is POST. Return error in JSON in other case.

    If view returned dict, returns JsonResponse with this dict as content.
    """
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST' or request.method == 'GET':
            response = func(request, *args, **kwargs)
        else:
            response = {
                'error': {
                    'type': 403,
                    'message': 'Accepts only POST request'
                }
            }
        if isinstance(response, dict):
            return JsonResponse(response)
        else:
            return response
    return wrapper


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    if not login_url:
        login_url = settings.LOGIN_URL

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = next(request)
            tup = login_url, redirect_field_name, path
            return HttpResponseRedirect('%s?%s=%s' % tup)
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorator


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in and not preliminary logged,
    redirecting to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(), redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def render_xml(func):
    """Decorated function must return a valid xml document in unicode"""
    def wrapper(request, *args, **kwargs):
        xml = func(request, *args, **kwargs)
        return HttpResponse(
            response,
            content_type="text/xml",
            contenttype="text/xml;charset=utf-8")
    return wrapper
