# -*- coding: utf-8 -*-

import datetime
import json

from django.conf import settings
from django.contrib import messages
from django.db import connection
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

import billservice.models as bsmodels
from billservice.forms import TransactionReportForm
from billservice.utils import systemuser_required
from billservice.models import (
    AddonServiceTransaction,
    PeriodicalServiceHistory,
    TotalTransactionReport,
    TrafficTransaction,
    Transaction,
    TransactionType
)
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import ajax_request, render_to

from ebsadmin.constants import TRANSACTION_MODELS
from ebsadmin.lib import DBWrap, ExtDirectStore, gettransactiontypes
from ebsadmin.tables import (
    AddonServiceTransactionReportTable,
    PeriodicalServiceTransactionReportTable,
    TotalTransactionReportTable,
    TrafficTransactionReportTable,
    TransactionReportTable
)


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

        items = (TotalTransactionReport.objects
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

        ds = ExtDirectStore(TotalTransactionReport)
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


@systemuser_required
@render_to('ebsadmin/transactionreport_list.html')
def transactionreport2(request):
    if not (request.user.account.has_perm('billservice.view_transaction')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    if request.GET:
        data = request.GET
        form = TransactionReportForm(request.GET)
        only_payments = request.GET.get("only_payments")
        only_credits = request.GET.get("only_credits")
        if form.is_valid():
            page = int(request.GET.get("page", 1))

            if "all" in request.GET:
                per_page = 10000000000000000
            else:
                per_page = int(request.GET.get("per_page", 25))

            pageitems = per_page
            sort = request.GET.get(
                '''\
sortpaginate=True if not request.GET.get('paginate') == 'False' else False''',
                '-created')
            account = form.cleaned_data.get('account')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            systemusers = form.cleaned_data.get('systemuser')
            promise = form.cleaned_data.get('promise')
            account_group = form.cleaned_data.get('account_group')

            cur = connection.cursor()
            trtypes = data.getlist('tree')

            with_id = []
            by_groups = {}
            tr_types = []
            for tr in trtypes:
                l = tr.split("___")
                tr_type = l[0]
                tr_types.append(tr_type)
                id = None

                if len(l) == 2:
                    tr_type, id = l

                parent_tr_type = TRANSACTION_MODELS.get(tr_type, 'Transaction')
                if parent_tr_type not in by_groups:
                    by_groups[parent_tr_type] = []

                if id:
                    by_groups[parent_tr_type].append(id)
                elif parent_tr_type == 'Transaction':
                    by_groups[parent_tr_type].append(tr_type)

            res = []
            total_summ = 0
            for key in by_groups:
                continue
                if key == 'PeriodicalServiceHistory':
                    items = PeriodicalServiceHistory.objects.filter(
                        service__id__in=by_groups[key])
                    if only_credits:
                        items = items.filter(summ__lte=0)
                    if account:
                        items = items.filter(account__id__in=account)
                    if start_date:
                        items = items.filter(created__gte=start_date)
                    if end_date:
                        items = items.filter(created__lte=end_date)
                    total_summ += float(items.aggregate(Sum("summ"))
                                        ['summ__sum'] or 0)
                    res += items.values(
                        'id',
                        'account',
                        'account__username',
                        'account__city__name',
                        'account__street',
                        'account__house',
                        'account__room',
                        'account__fullname',
                        'summ',
                        'created',
                        'type__name',
                        'service__name'
                    )

                if key == 'AddonServiceTransaction':
                    items = AddonServiceTransaction.objects.filter(
                        service__id__in=by_groups[key])
                    if only_credits:
                        items = items.filter(summ__lte=0)
                    if account:
                        items = items.filter(account__id__in=account)
                    if start_date:
                        items = items.filter(created__gte=start_date)
                    if end_date:
                        items = items.filter(created__lte=end_date)
                    total_summ += float(
                        items.aggregate(Sum("summ"))['summ__sum'] or 0)
                    res += items.values(
                        'id',
                        'account',
                        'account__username',
                        'account__city__name',
                        'account__street',
                        'account__house',
                        'account__room',
                        'account__fullname',
                        'summ',
                        'created',
                        'type__name',
                        'service__name'
                    )

                if key == 'TrafficTransaction':
                    items = TrafficTransaction.objects.all()
                    if only_credits:
                        items = items.filter(summ__lte=0)
                    if account:
                        items = items.filter(account__id__in=account)
                    if start_date:
                        items = items.filter(created__gte=start_date)
                    if end_date:
                        items = items.filter(created__lte=end_date)
                    total_summ += float(
                        items.aggregate(Sum("summ"))['summ__sum'] or 0)
                    res += items.values(
                        'id',
                        'account',
                        'account__username',
                        'account__city__name',
                        'account__street',
                        'account__house',
                        'account__room',
                        'account__fullname',
                        'summ',
                        'created'
                    )

                if key == 'Transaction':
                    items = Transaction.objects.filter(
                        type__internal_name__in=by_groups[key])
                    if only_credits:
                        items = items.filter(summ__lte=0)
                    if only_payments:
                        items = items.filter(summ__gte=0)
                    if account:
                        items = items.filter(account__id__in=account)
                    if start_date:
                        items = items.filter(created__gte=start_date)
                    if end_date:
                        items = items.filter(created__lte=end_date)
                    if systemusers:
                        items = items.filter(systemuser__in=systemusers)
                    total_summ += float(
                        items.aggregate(Sum("summ"))['summ__sum'] or 0)
                    res += items.values(
                        'id',
                        'account',
                        'account__username',
                        'account__city__name',
                        'account__street',
                        'account__house',
                        'account__room',
                        'account_fullname',
                        'summ',
                        'created',
                        'type__name',
                        'bill',
                        'description'
                    )

            summOnThePage = 1500
            summ = total_summ
            total = False
            tf = TransactionReportForm(request.GET)

            if len(by_groups) == 1 and 'TrafficTransaction' in by_groups:
                res = TrafficTransaction.objects.all()
                table = TrafficTransactionReportTable
            elif len(by_groups) == 1 and by_groups.get('Transaction'):
                res = Transaction.objects.all()
                table = TransactionReportTable
            elif len(by_groups) == 1 and 'AddonServiceTransaction' in by_groups:
                res = AddonServiceTransaction.objects.all()
                table = AddonServiceTransactionReportTable
            elif len(by_groups) == 1 and 'PeriodicalServiceHistory' in by_groups:
                res = PeriodicalServiceHistory.objects.all()
                table = PeriodicalServiceTransactionReportTable
            else:
                res = TotalTransactionReport.objects.all()
                table = TotalTransactionReportTable
                total = True

            if account:
                res = res.filter(account__in=account)
            if account_group:
                res = res.filter(account__account_group__in=account_group)

            if start_date:
                res = res.filter(created__gte=start_date)
            if end_date:
                res = res.filter(created__lte=end_date)
            if tr_types and table not in \
                    (TrafficTransactionReportTable,
                     PeriodicalServiceTransactionReportTable):
                res = res.filter(type__internal_name__in=tr_types)

            if table in (AddonServiceTransactionReportTable, ):
                res = res.filter(
                    service__id__in=(by_groups
                                     .get('AddonServiceTransaction', [])))

            if table in (PeriodicalServiceTransactionReportTable, ):
                res = res.filter(
                    service__id__in=(by_groups
                                     .get('PeriodicalServiceHistory', [])))

            if table == TransactionReportTable and systemusers:
                res = res.filter(systemuser__in=systemusers)

            if only_credits:
                res = res.filter(summ__lte=0)
            if only_payments:
                res = res.filter(summ__gte=0)

            total_summ = "%.2f" % (res
                                   .aggregate(total_summ=Sum('summ'))
                                   .get('total_summ') or 0)
            if table == TotalTransactionReportTable:
                table = table(res
                              .prefetch_related('tariff__name', 'type__name')
                              .values('id',
                                      'account__username',
                                      'account__city__name',
                                      'account__street',
                                      'account__house',
                                      'account__room',
                                      'account__fullname',
                                      'account',
                                      'summ',
                                      'created',
                                      'tariff__name',
                                      'bill',
                                      'description',
                                      'end_promise',
                                      'promise_expired',
                                      'type__name',
                                      'service_id',
                                      'table',
                                      'prev_balance',
                                      'is_bonus'))
            elif table == TrafficTransactionReportTable:
                table = table(res
                              .prefetch_related('account__username')
                              .values('id',
                                      'account__username',
                                      'account__city__name',
                                      'account__street',
                                      'account__house',
                                      'account__room',
                                      'account__fullname',
                                      'account',
                                      'summ',
                                      'created'))

            elif table == TransactionReportTable:
                table = table(res
                              .prefetch_related('type__name',
                                                'account__username',
                                                'systemuser__username')
                              .values('id',
                                      'account__username',
                                      'account__city__name',
                                      'account__street',
                                      'account__house',
                                      'account__room',
                                      'account__fullname',
                                      'account',
                                      'summ',
                                      'description',
                                      'bill',
                                      'created',
                                      'type__name',
                                      'end_promise',
                                      'promise_expired',
                                      'systemuser__username',
                                      'prev_balance',
                                      'is_bonus'))
            elif table in (PeriodicalServiceTransactionReportTable,):
                table = table(res
                              .prefetch_related('type__name',
                                                'account__username',
                                                'service__name')
                              .values('id',
                                      'account__username',
                                      'account',
                                      'account__city__name',
                                      'account__street',
                                      'account__house',
                                      'account__room',
                                      'account__fullname',
                                      'summ',
                                      'created',
                                      'service__name',
                                      'type__name',
                                      'prev_balance',
                                      'real_created'))
            elif table in (AddonServiceTransactionReportTable,):
                table = table(res
                              .prefetch_related('type__name',
                                                'account__username',
                                                'service__name')
                              .values('id',
                                      'account__username',
                                      'account',
                                      'account__city__name',
                                      'account__street',
                                      'account__house',
                                      'account__room',
                                      'account__fullname',
                                      'summ',
                                      'created',
                                      'service__name',
                                      'type__name',
                                      'prev_balance'))

            else:
                table = table(res)

            table_to_report = RequestConfig(
                request,
                paginate=(False if request.GET.get('paginate') == 'False'
                          else True))
            table_to_report = table_to_report.configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            r = gettransactiontypes(current=trtypes)
            return {
                "table": table,
                'form': tf,
                'ojax': r,
                'total_summ': total_summ,
                'total': total
            }

        else:
            res = gettransactiontypes(current=data.getlist('tree'))
            return {
                'status': False,
                'form': form,
                'ojax': res
            }
    else:
        res = gettransactiontypes(current=request.GET.getlist('tree'))
        form = TransactionReportForm(
            request.GET,
            initial={
                'start_date': (datetime.datetime.now() -
                               datetime.timedelta(days=36500))
            })
        return {
            'form': form,
            'ojax': res
        }
