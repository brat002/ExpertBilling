# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import SearchAuthLogForm
from billservice.utils import systemuser_required
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.utils.decorators import render_to
from radius.models import AuthLog

from ebsadmin.tables import AuthLogTable


@systemuser_required
@render_to('ebsadmin/authlog_list.html')
def authlogreport(request):
    if not (request.user.account.has_perm('radius.view_authlog')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    if request.method == 'GET' and request.GET:
        data = request.GET
        form = SearchAuthLogForm(data)
        if form.is_valid():
            account = form.cleaned_data.get('account')
            nas = form.cleaned_data.get('nas')
            start_date, end_date = (request.GET.get('start_date'),
                                    request.GET.get('end_date'))

            res = AuthLog.objects.all()
            if account:
                res = res.filter(account__in=account)

            if nas:
                res = res.filter(nas__in=nas)

            if start_date:
                res = res.filter(datetime__gte=start_date)
            if end_date:
                res = res.filter(datetime__lte=end_date)

            table = AuthLogTable(res)
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
        form = SearchAuthLogForm()
        return {
            'form': form
        }
