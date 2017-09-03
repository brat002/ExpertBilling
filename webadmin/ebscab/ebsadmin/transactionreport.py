# -*- coding: utf-8 -*-

import json

import psycopg2
import psycopg2.extras
from django.conf import settings

import billservice.models as bsmodels
from billservice.forms import TransactionReportForm
from billservice.helpers import systemuser_required
from billservice.models import (
    TotalTransactionReport as TransactionReport,
    TransactionType
)
from ebscab.lib.decorators import ajax_request

from ebsadmin.constants import TRANSACTION_MODELS


class DBWrap:

    def __init__(self, dsn):
        self.connection = None
        self._cur = None
        self.dsn = dsn

    @property
    def cursor(self):
        if self.connection is None:
            self.connection = psycopg2.connect(self.dsn)
            # set autocmmit transations
            self.connection.set_isolation_level(0)
            self._cur = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor)
        elif not self._cur:
            self._cur = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor)
        return self._cur


dsn = 'host=%s port=%s dbname=%s user=%s password=%s' % (
    settings.DATABASES.get('default').get('HOST'),
    settings.DATABASES.get('default').get('PORT'),
    settings.DATABASES.get('default').get('NAME'),
    settings.DATABASES.get('default').get('USER'),
    settings.DATABASES.get('default').get('PASSWORD')
)

db = DBWrap(dsn)


@ajax_request
@systemuser_required
def transactionreport(request):
    if not (request.user.account.has_perm(
            'billservice.view_transactionreport')):
        return {
            'status': False
        }

    data = json.loads(request.POST.get('data', '{}'))
    form = TransactionReportForm(data)
    if form.is_valid():
        account = form.cleaned_data.get('account')
        daterange = form.cleaned_data.get('daterange') or []
        date_start, date_end = None, None
        if len(daterange) == 2:
            date_start, date_end = daterange

        systemusers = form.cleaned_data.get('systemuser')
        account_group = form.cleaned_data.get('account_group')
        tariffs = form.cleaned_data.get('tarif')
        extra = {}
        if data.get('limit', 100) == 'all':
            l = -1
        else:
            l = int(data.get('limit', 100))
            extra = {
                'start': int(data.get('start', 0)),
                'limit': l
            }

        if data.get('sort', ''):
            extra['sort'] = data.get('sort', '')
            extra['dir'] = data.get('dir', 'asc')
        if data.get('groupBy', ''):
            extra['groupby'] = data.get('groupBy', '')
            extra['groupdir'] = data.get('groupDir', 'asc')

        res = []
        resitems = []
        TYPES = {}
        TRTYPES = {}
        LTYPES = []
        for x in form.cleaned_data.get('transactiontype', ''):
            key = TRANSACTION_MODELS.get(x)
            model = bsmodels.__dict__.get(key)
            if key not in TYPES:
                TYPES[key] = []
            if key not in TRTYPES:
                TRTYPES[key] = []
            TYPES[key].append(model)
            TRTYPES[key].append(TransactionType.objects.get(internal_name=x))
            LTYPES.append(x)

        items = (TransactionReport.objects
                 .filter(created__gte=date_start, created__lte=date_end)
                 .order_by('-created'))
        if account:
            items = items.filter(account=account)

        if systemusers:
            items = items.filter(systemuser__in=systemusers)
        if account_group:
            items = items.filter(account__account_group__in=account_group)

        if tariffs:
            items = items.filter(tariff__in=tariffs)

        if form.cleaned_data.get('transactiontype'):
            items = items.filter(type__in=LTYPES)

        if form.cleaned_data.get('addonservice'):
            items = items.filter(
                service_id__in=[x.id for x in
                                form.cleaned_data.get('addonservice')],
                type__in=[
                    'ADDONSERVICE_WYTE_PAY',
                    'ADDONSERVICE_PERIODICAL_GRADUAL',
                    'ADDONSERVICE_PERIODICAL_AT_START',
                    'ADDONSERVICE_PERIODICAL_AT_END',
                    'ADDONSERVICE_ONETIME'
                ]
            )

        if form.cleaned_data.get('periodicalservice'):
            items = items.filter(
                service_id__in=[x.id for x in
                                form.cleaned_data.get('periodicalservice')],
                type__in=['PS_GRADUAL', 'PS_AT_END', 'PS_AT_START']
            )

        ds = ExtDirectStore(TransactionReport)
        items, totalcount = ds.query(items, **extra)
        res = tuple(items.values(
            'id',
            'service_name',
            'table',
            'created',
            'tariff__name',
            'summ',
            'account__username',
            'account__fullname',
            'type',
            'systemuser_id',
            'bill',
            'description',
            'end_promise',
            'promise_expired'
        ))
        t = [
            {'name': 'id', 'sortable': True, 'type': 'integer'},
            {'name': 'service_name', 'sortable': True, 'type': 'string'},
            {'name': 'created', 'sortable': True, 'type': 'date'},
            {'name': 'tariff__name', 'sortable': True, 'type': 'string'},
            {'name': 'summ', 'sortable': True, 'type': 'float'},
            {'name': 'account', 'sortable': True, 'type': 'string'},
            {'name': 'type', 'sortable': True, 'type': 'string'},
            {'name': 'type__name', 'sortable': True, 'type': 'string'},
            {'name': 'systemuser', 'sortable': True, 'type': 'string'},
            {'name': 'bill', 'sortable': True, 'type': 'string'},
            {'name': 'descrition', 'sortable': True, 'type': 'string'},
            {'name': 'end_promise', 'sortable': True, 'type': 'date'},
            {'name': 'promise_expired', 'sortable': True, 'type': 'boolean'}
        ]

        return {
            "records": res,
            'status': True,
            'totalCount': len(res),
            'metaData': {
                'root': 'records',
                'totalProperty': 'total',
                'fields': t
            },
            "sortInfo": {
                "field": "created",
                "direction": "ASC"
            }
        }
    else:
        return {
            'status': False,
            'errors': form._errors
        }
