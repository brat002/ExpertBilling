# -*- coding: utf-8 -*-


from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.helpers import systemuser_required
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to
from radius.forms import SessionFilterForm
from radius.models import ActiveSession

from ebsadmin.tables import ActiveSessionTable


@systemuser_required
@render_to('ebsadmin/activesession_list.html')
def activesessionreport(request):
    if not (request.user.account.has_perm('radius.view_activesession')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    if request.GET:
        form = SessionFilterForm(request.GET)
        if form.is_valid():
            account_text = request.GET.get('account_text')
            res = ActiveSession.objects.prefetch_related()
            if form.cleaned_data.get("account"):
                res = res.filter(account__in=form.cleaned_data.get("account"))

            if form.cleaned_data.get("date_start"):
                res = res.filter(
                    date_start__gte=form.cleaned_data.get("date_start"))

            if form.cleaned_data.get("date_end"):
                res = res.filter(
                    date_end__lte=form.cleaned_data.get("date_end"))

            if form.cleaned_data.get("city"):
                res = res.filter(account__city=form.cleaned_data.get("city"))

            if form.cleaned_data.get("street"):
                res = res.filter(
                    account__street=form.cleaned_data.get("street"))

            if form.cleaned_data.get("house"):
                res = res.filter(account__house=form.cleaned_data.get("house"))

            if form.cleaned_data.get("only_active"):
                res = res.filter(session_status='ACTIVE')
            if account_text:
                res = (res
                       .filter(Q(account__username__startswith=account_text) |
                               Q(account__contract__startswith=account_text)))

            if form.cleaned_data.get("nas"):
                res = res.filter(nas_int__in=form.cleaned_data.get("nas"))

            res = res.values('id',
                             'subaccount__username',
                             'subaccount',
                             'framed_ip_address',
                             'interrim_update',
                             'framed_protocol',
                             'bytes_in',
                             'bytes_out',
                             'date_start',
                             'date_end',
                             'session_status',
                             'caller_id',
                             'nas_int__name',
                             'session_time',
                             'account__street',
                             'account__house',
                             'account__room')
            table = ActiveSessionTable(res)
            table_to_report = RequestConfig(
                request,
                paginate=(False if request.GET.get('paginate') == 'False'
                          else True))
            table_to_report = table_to_report.configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {
                'table': table,
                'form': form
            }

        else:
            return {
                'form': form
            }
    else:
        table = None
        res = (ActiveSession.objects
               .filter(session_status='ACTIVE')
               .prefetch_related())
        res = res.values('id',
                         'subaccount__username',
                         'subaccount',
                         'framed_ip_address',
                         'interrim_update',
                         'framed_protocol',
                         'bytes_in',
                         'bytes_out',
                         'date_start',
                         'date_end',
                         'session_status',
                         'caller_id',
                         'nas_int__name',
                         'session_time',
                         'account__street',
                         'account__house',
                         'account__room')
        table = ActiveSessionTable(res)
        table_to_report = RequestConfig(
            request,
            paginate=(False if request.GET.get('paginate') == 'False'
                      else True))
        table_to_report = table_to_report.configure(table)
        if table_to_report:
            return create_report_http_response(table_to_report, request)

        form = SessionFilterForm(initial={'only_active': True})
        return {
            'table': table,
            'form': form
        }
