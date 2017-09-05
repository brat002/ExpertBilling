# -*- coding: utf-8 -*-

import json
from itertools import chain
from operator import mul, __not__

import psycopg2
import psycopg2.extras
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models.fields import DateField, DecimalField
from django.db.models.fields.related import ForeignKey

from billservice.models import AddonService, PeriodicalService, TransactionType


LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 10
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 8
NUM_PAGES_OUTSIDE_RANGE = 5
ADJACENT_PAGES = 4


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


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


def digg_paginator(cnt, current):
    in_leading_range = in_trailing_range = False
    pages_outside_leading_range = pages_outside_trailing_range = range(0)

    if (cnt <= LEADING_PAGE_RANGE_DISPLAYED):
        in_leading_range = in_trailing_range = True
        page_numbers = [n for n in range(1, cnt + 1) if n > 0 and n <= cnt]
    elif (current <= LEADING_PAGE_RANGE):
        in_leading_range = True
        page_numbers = [n for n in range(
            1, LEADING_PAGE_RANGE_DISPLAYED + 1) if n > 0 and n <= cnt]
        pages_outside_leading_range = [
            n + cnt for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
    elif (current > cnt - TRAILING_PAGE_RANGE):
        in_trailing_range = True
        page_numbers = [
            n
            for n in range(cnt - TRAILING_PAGE_RANGE_DISPLAYED + 1, cnt + 1)
            if n > 0 and n <= cnt
        ]
        pages_outside_trailing_range = [
            n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
    else:
        page_numbers = [
            n
            for n in range(current - ADJACENT_PAGES,
                           current + ADJACENT_PAGES + 1)
            if n > 0 and n <= cnt
        ]
        pages_outside_leading_range = [
            n + cnt for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        pages_outside_trailing_range = [
            n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
    return {
        "page_numbers": page_numbers,
        "pages_outside_trailing_range": pages_outside_trailing_range,
        "pages_outside_leading_range": sorted(pages_outside_leading_range)
    }


def mul_it(it1, it2):
    '''
    Element-wise iterables multiplications.
    '''
    assert len(it1) == len(it2), \
        "Can not element-wise multiply iterables of different length."
    return map(mul, it1, it2)


def chain_sing(*iterables_or_items):
    '''
    As itertools.chain except that if an argument is not iterable then chain it
    as a singleton.
    '''
    for iter_or_item in iterables_or_items:
        if hasattr(iter_or_item, '__iter__'):
            for item in iter_or_item:
                yield item
        else:
            yield iter_or_item


def gettransactiontypes(current=[]):
    res = []
    for t in TransactionType.objects.all():
        d = []
        if t.internal_name == 'PS_AT_START':
            pstypes = PeriodicalService.objects.filter(cash_method='AT_START')
            d = []
            for pstype in pstypes:
                key = 'PS_AT_START___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })
        if t.internal_name == 'PS_AT_END':
            pstypes = PeriodicalService.objects.filter(cash_method='AT_END')
            d = []
            for pstype in pstypes:
                key = 'PS_AT_END___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })

        if t.internal_name == 'PS_GRADUAL':
            pstypes = PeriodicalService.objects.filter(cash_method='GRADUAL')
            d = []
            for pstype in pstypes:
                key = 'PS_GRADUAL___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })

        if t.internal_name == 'ADDONSERVICE_PERIODICAL_GRADUAL':
            pstypes = AddonService.objects.filter(sp_type='GRADUAL')
            d = []
            for pstype in pstypes:
                key = 'ADDONSERVICE_PERIODICAL_GRADUAL___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })

        if t.internal_name == 'ADDONSERVICE_PERIODICAL_AT_START':
            pstypes = AddonService.objects.filter(sp_type='AT_START')
            d = []
            for pstype in pstypes:
                key = 'ADDONSERVICE_PERIODICAL_AT_START___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })
        if t.internal_name == 'ADDONSERVICE_PERIODICAL_AT_END':
            pstypes = AddonService.objects.filter(sp_type='AT_END')
            d = []
            for pstype in pstypes:
                key = 'ADDONSERVICE_PERIODICAL_AT_END___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })
        if t.internal_name == 'ADDONSERVICE_ONETIME':
            pstypes = AddonService.objects.filter(service_type='onetime')
            d = []
            for pstype in pstypes:
                key = 'ADDONSERVICE_ONETIME___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })

        res.append({
            'title': t.name,
            'key': t.internal_name,
            'children': d,
            'isFolder': True if d else False,
            'select': True if t.internal_name in current else False
        })

    res = {
        'title': u'Все',
        'key': 'all',
        'children': res,
        'isFolder': True,
        'select': True
    }
    res = json.dumps(res, ensure_ascii=False)
    return res


class ExtDirectStore(object):
    """
    Implement the server-side needed to load an Ext.data.DirectStore
    """

    def __init__(self, model, extras=[], root='records', total='total',
                 start='start', limit='limit', sort='sort', dir='dir',
                 groupby='groupby', groupdir='groupdir'):
        self.model = model
        self.root = root
        self.total = total
        self.extras = extras

        # paramNames
        self.start = start
        self.limit = limit
        self.sort = sort
        self.dir = dir
        self.groupby = groupby
        self.groupdir = groupdir

    def query(self, qs=None, **kw):
        paginate = False
        total = None
        order = False
        groupby = None
        if kw.has_key(self.groupby):
            groupby = kw.pop(self.groupby)
            groupdir = kw.pop(self.groupdir)

        if kw.has_key(self.start) and kw.has_key(self.limit) and \
                kw.get(self.limit) != -1:
            start = kw.pop(self.start)
            limit = kw.pop(self.limit)
            paginate = True

        if kw.has_key(self.sort) and kw.has_key(self.dir):
            sort = kw.pop(self.sort)
            dir = kw.pop(self.dir)
            order = True

            if dir == 'DESC':
                sort = '-' + sort

        if qs is not None:
            # Don't use queryset = qs or self.model.objects
            # because qs could be empty list (evaluate to False)
            # but it's actually an empty queryset that must have precedence
            queryset = qs
        else:
            queryset = self.model.objects

        queryset = queryset.filter(**kw)

        if groupby:
            queryset = queryset.order_by(
                "-%s" % groupby if groupdir == 'asc' else groupby)
        if order:
            queryset = queryset.order_by(sort)

        if not paginate:
            objects = queryset
            total = queryset.count()
        else:
            paginator = Paginator(queryset, limit)
            total = paginator.count

            try:
                page = paginator.page(int(start / limit) + 1)
            except (EmptyPage, InvalidPage), e:
                print e
                # out of range, deliver last page of results.
                page = paginator.page(paginator.num_pages)

            objects = page.object_list

        return objects, total


class DBWrap:

    def __init__(self, dsn):
        self.connection = None
        self._cur = None
        self.dsn = dsn

    @property
    def cursor(self):
        if self.connection is None:
            self.connection = psycopg2.connect(self.dsn)
            # set autocommit transations
            self.connection.set_isolation_level(0)
            self._cur = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor)
        elif not self._cur:
            self._cur = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor)
        return self._cur
