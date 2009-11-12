# -*- coding: utf-8 -*-
# $Id: http.py 1395 2008-08-22 09:24:49Z dmitry $

from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext


def render_response(request, tmpl, output):
    return render_to_response(tmpl, output, context_instance=RequestContext(request))

class JsonResponse(HttpResponse):
    """
    HttpResponse descendant, which return response with ``application/json`` mimetype.
    """
    def __init__(self, data):
        super(JsonResponse, self).__init__(content=simplejson.dumps(data,ensure_ascii=False), mimetype='application/json')
