# -*- coding: utf-8 -*-
# $Id: http.py 1395 2008-08-22 09:24:49Z dmitry $

import json
from datetime import datetime
from decimal import Decimal

import ipaddr
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template


class MyJSONEncoder(json.JSONEncoder):
    """JSON encoder which understands decimals."""

    def default(self, obj):
        '''Convert object to JSON encodable type.'''
        if isinstance(obj, Decimal):
            return float(obj if obj else 0)
        if isinstance(obj, datetime):
            return {
                '__type__': 'datetime',
                'year': obj.year,
                'month': obj.month,
                'day': obj.day,
                'hour': obj.hour,
                'minute': obj.minute,
                'second': obj.second,
                'microsecond': obj.microsecond
            }
        else:
            if type(obj) == ipaddr.IPv4Network or \
                    type(obj) == ipaddr.IPAddress:
                return str(obj)
            return json.JSONEncoder.default(self, obj)


def render_response(request, tmpl, output):
    return render(request, tmpl, output)


class JsonResponse(HttpResponse):
    """
    HttpResponse descendant, which return response with ``application/json`` mimetype.
    """

    def __init__(self, data):
        super(JsonResponse, self).__init__(
            content=json.dumps(data,
                               ensure_ascii=False,
                               cls=MyJSONEncoder),
            content_type='application/json')