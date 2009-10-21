 #-*- coding=UTF-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.conf import settings

from lib.http import JsonResponse, render_response

def render_to(tmpl):
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            return render_to_response(tmpl, output,
                   context_instance=RequestContext(request))
        return wrapper
    return renderer

def ajax_request(func):
    """
    Checks request.method is POST. Return error in JSON in other case.

    If view returned dict, returns JsonResponse with this dict as content.
    """
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST' or request.method == 'GET':
        #if request.method == 'POST':
            response = func(request, *args, **kwargs)
        else:
            response = {'error': {'type': 403, 'message': 'Accepts only POST request'}}
        if isinstance(response, dict):
            return JsonResponse(response)
        else:
            return response
    return wrapper

def login_required(func):
    def wrapper(request, *args, **kw):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_URL)
        else:
            return None 
    return wrapper
