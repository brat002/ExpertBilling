# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import SheduleLogSearchForm
from billservice.utils import systemuser_required
from billservice.models import SheduleLog
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to
from object_log.models import LogItem

from ebsadmin.tables import SheduleLogTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/shedulelog_list.html')
def shedulelog(request):
    if not (request.user.account.has_perm('billservice.view_shedulelog')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    if request.method == 'GET' and request.GET:
        data = request.GET
        form = SheduleLogSearchForm(data)
        if form.is_valid():
            account = form.cleaned_data.get('account')
            res = SheduleLog.objects.all()
            if account:
                res = res.filter(accounttarif__account__id__in=account)

            table = SheduleLogTable(res)
            table_to_report = RequestConfig(
                request,
                paginate=(False if request.GET.get('paginate') == 'False'
                          else True))
            table_to_report = table_to_report.configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {
                "table": table,
                'form': form,
                'resultTab': True
            }

        else:
            return {
                'status': False,
                'form': form
            }
    else:
        form = SheduleLogSearchForm()
        return {
            'form': form
        }
