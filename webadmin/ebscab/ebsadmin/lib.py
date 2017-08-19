# -*- coding: utf-8 -*-

from itertools import chain, dropwhile
from operator import mul, attrgetter, __not__

from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models.fields import DateField, DecimalField
from django.db.models.fields.related import ForeignKey
from django.db.models.query import REPR_OUTPUT_SIZE, EmptyQuerySet


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

        # return self.serialize(objects, total)
        return objects, total


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


class IableSequence(object):
    '''
    Wrapper for sequence of iterable and indexable by non-negative integers
    objects. That is a sequence of objects which implement __iter__, __len__ and
    __getitem__ for slices, ints and longs.

    Note: not a Django-specific class.
    '''

    def __init__(self, *args, **kwargs):
        self.iables = args  # wrapped sequence
        self._len = None  # length cache
        self._collapsed = []  # collapsed elements cache

    def __len__(self):
        if not self._len:
            self._len = sum(len(iable) for iable in self.iables)
        return self._len

    def __iter__(self):
        return chain(*self.iables)

    def __nonzero__(self):
        try:
            iter(self).next()
        except StopIteration:
            return False
        return True

    def _collect(self, start=0, stop=None, step=1):
        if not stop:
            stop = len(self)
        sub_iables = []
        # collect sub sets
        it = self.iables.__iter__()
        try:
            while stop > start:
                i = it.next()
                i_len = len(i)
                if i_len > start:
                    # no problem with 'stop' being too big
                    sub_iables.append(i[start:stop:step])
                start = max(0, start - i_len)
                stop -= i_len
        except StopIteration:
            pass
        return sub_iables

    def __getitem__(self, key):
        '''
        Preserves wrapped indexable sequences.
        Does not support negative indices.
        '''
        # params validation
        if not isinstance(key, (slice, int, long)):
            raise TypeError
        assert ((not isinstance(key, slice) and (key >= 0)) or
                (isinstance(key, slice) and
                 (key.start is None or key.start >= 0) and
                 (key.stop is None or key.stop >= 0))), \
            "Negative indexing is not supported."
        # initialization
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            ret_item = False
        else:  # isinstance(key, (int,long))
            start, stop, step = key, key + 1, 1
            ret_item = True
        # collect sub sets
        ret_iables = self._collect(start, stop, step)
        # return the simplest possible answer
        if not len(ret_iables):
            if ret_item:
                raise IndexError("'%s' index out of range" %
                                 self.__class__.__name__)
            return ()
        if ret_item:
            # we have exactly one query set with exactly one item
            assert len(ret_iables) == 1 and len(ret_iables[0]) == 1
            return ret_iables[0][0]
        # otherwise we have more then one item in at least one query set
        if len(ret_iables) == 1:
            return ret_iables[0]
        # Note: this can't be self.__class__ instead of IableSequence; exemplary
        # cause is that indexing over query sets returns lists so we can not
        # return QuerySetSequence by default. Some type checking enhancement can
        # be implemented in subclasses.
        return IableSequence(*ret_iables)

    def collapse(self, stop=None):
        '''
        Collapses sequence into a list.

        Try to do it effectively with caching.
        '''
        if not stop:
            stop = len(self)
        # if we already calculated sufficient collapse then return it
        if len(self._collapsed) >= stop:
            return self._collapsed[:stop]
        # otherwise collapse only the missing part
        items = self._collapsed
        sub_iables = self._collect(len(self._collapsed), stop)
        for sub_iable in sub_iables:
            items += sub_iable
        # cache new collapsed items
        self._collapsed = items
        return self._collapsed

    def __repr__(self):
        # get +1 element for the truncation msg if applicable
        items = self.collapse(stop=REPR_OUTPUT_SIZE + 1)
        if len(items) > REPR_OUTPUT_SIZE:
            items[-1] = "...(remaining elements truncated)..."
        return repr(items)


class QuerySetSequence(IableSequence):
    '''
    Wrapper for the query sets sequence without the restriction on the identity
    of the base models.
    '''

    def count(self):
        print[type(qs) for qs in self.iables]
        if not self._len:
            self._len = sum(qs.count() for qs in self.iables)
        return self._len

    def __len__(self):
        # override: use DB effective count's instead of len()
        return self.count()

    def order_by(self, *field_names):
        '''
        Returns a list of the QuerySetSequence items with the ordering changed.
        '''
        # construct a comparator function based on the field names prefixes
        reverses = [1] * len(field_names)
        field_names = list(field_names)
        for i in range(len(field_names)):
            field_name = field_names[i]
            if field_name[0] == '-':
                reverses[i] = -1
                field_names[i] = field_name[1:]
        # wanna iterable and attrgetter returns single item if 1 arg supplied
        fields_getter = lambda i: chain_sing(attrgetter(*field_names)(i))
        # comparator gets the first non-zero value of the field comparison
        # results taking into account reverse order for fields prefixed with
        # '-'
        comparator = lambda i1, i2:\
            dropwhile(__not__,
                      mul_it(map(cmp,
                                 fields_getter(i1),
                                 fields_getter(i2)),
                             reverses)
                      ).next()
        # return new sorted list
        return sorted(self.collapse(), cmp=comparator)

    def filter(self, *args, **kwargs):
        """
        Returns a new QuerySetSequence or instance with the args ANDed to the
        existing set.

        QuerySetSequence is simplified thus result actually can be one of:
        QuerySetSequence, QuerySet, EmptyQuerySet.
        """
        return self._filter_or_exclude(False, *args, **kwargs)

    def exclude(self, *args, **kwargs):
        """
        Returns a new QuerySetSequence instance with NOT (args) ANDed to the
        existing set.

        QuerySetSequence is simplified thus result actually can be one of:
        QuerySetSequence, QuerySet, EmptyQuerySet.
        """
        return self._filter_or_exclude(True, *args, **kwargs)

    def _simplify(self, qss=None):
        '''
        Returns QuerySetSequence, QuerySet or EmptyQuerySet depending on the
        contents of items, i.e. at least two non empty QuerySets, exactly one
        non empty QuerySet and all empty QuerySets respectively.

        Does not modify original QuerySetSequence.
        '''
        not_empty_qss = filter(None, qss if qss else self.iables)
        if not len(not_empty_qss):
            return EmptyQuerySet()
        if len(not_empty_qss) == 1:
            return not_empty_qss[0]
        return QuerySetSequence(*not_empty_qss)

    def _filter_or_exclude(self, negate, *args, **kwargs):
        '''
        Maps _filter_or_exclude over QuerySet items and simplifies the result.
        '''
        # each Query set is cloned separately
        return self._simplify(
            *map(lambda qs: qs._filter_or_exclude(negate, *args, **kwargs),
                 self.iables))

    def exists(self):
        for qs in self.iables:
            if qs.exists():
                return True
        return False
