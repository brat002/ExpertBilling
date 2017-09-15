# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal

import ipaddr
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse as DjangoJsonResponse


class MyJSONEncoder(DjangoJSONEncoder):
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
            return super(MyJSONEncoder, self).default(obj)


class JsonResponse(DjangoJsonResponse):
    """
    HttpResponse descendant, which return response with ``application/json`` mimetype.
    """

    def __init__(self, data):
        super(JsonResponse, self).__init__(
            data,
            encoder=MyJSONEncoder,
            json_dumps_params={
                'ensure_ascii': False
            })
