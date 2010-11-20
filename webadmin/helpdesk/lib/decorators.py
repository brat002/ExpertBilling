 #-*- coding=UTF-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.conf import settings

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


def login_required(func):
    def wrapper(request, *args, **kw):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_URL)
        else:
            return None 
    return wrapper
