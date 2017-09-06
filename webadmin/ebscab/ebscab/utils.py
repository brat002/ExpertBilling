# -*- coding: utf-8 -*-

from itertools import chain

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.fields import DateField, DecimalField
from django.db.models.fields.related import ForeignKey


def instance_dict(instance, key_format=None, normal_fields=False, fields=[]):
    """
    Returns a dictionary containing field names and values for the given
    instance
    """
    if key_format:
        assert '%s' in key_format, 'key_format must contain a %s'

    key = lambda key: key_format and key_format % key or key
    pk = instance._get_pk_val()
    d = {}

    for field in chain(instance._meta.fields, instance._meta.virtual_fields):
        print field
        attr = field.name
        if fields and attr not in fields:
            continue

        try:
            value = getattr(instance, attr)
        except:
            value = None

        if isinstance(field, ForeignKey):
            if value is not None:
                try:
                    d["%s_id" % key(attr)] = value.id
                    if normal_fields == False:
                        value = value._get_pk_val()
                    else:
                        value = unicode(value)
                except Exception, e:
                    print e
            else:
                d["%s_id" % key(attr)] = None
                value = None

        elif isinstance(field, DateField):
            value = value.strftime('%Y-%m-%d %H:%M:%S') if value else None
        elif isinstance(field, GenericForeignKey):
            value = unicode(value)
        elif isinstance(field, DecimalField):
            value = float(value) if value else 0

        d[key(attr)] = value
    for field in instance._meta.many_to_many:
        if pk:
            d[key(field.name)] = [
                obj._get_pk_val()
                for obj in getattr(instance, field.attname).all()
            ]
        else:
            d[key(field.name)] = []
    return d
