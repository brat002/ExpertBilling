# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import BallanceHistoryForm
from billservice.helpers import systemuser_required
from billservice.models import BalanceHistory
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to

from ebsadmin.tables import BallanceHistoryTable


@systemuser_required
@render_to('ebsadmin/ballancehistory_list.html')
def ballancehistoryreport(request):
    if not (request.user.account.has_perm('billservice.view_balancehistory')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    if request.method == 'GET' and request.GET:
        form = BallanceHistoryForm(request.GET)
        if form.is_valid():
            account = form.cleaned_data.get('account')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            res = BalanceHistory.objects.all()

            if account:
                res = res.filter(account__in=account)
            if start_date:
                res = res.filter(datetime__gte=start_date)
            if end_date:
                res = res.filter(datetime__lte=end_date)

            res = res.values('id',
                             'account',
                             'account__username',
                             'balance',
                             'summ',
                             'datetime')
            table = BallanceHistoryTable(res)
            table_to_report = RequestConfig(
                request,
                paginate=(False if request.GET.get('paginate') == 'False'
                          else True))
            table_to_report = table_to_report.configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {
                'table': table,
                'form': form,
                'resultTab': True
            }

        else:
            return {
                'status': False,
                'form': form
            }
    else:
        form = BallanceHistoryForm()
        return {
            'form': form
        }
