#-*- coding: utf-8 -*-


from ebsadmin.reportsystem.forms import AccountBallanceForm

from ebscab.lib.decorators import render_to, ajax_request
from billservice.helpers import systemuser_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from billservice.models import Account, AccountAddonService
from django_tables2_reports.tables import TableReport
import django_tables2 as django_tables
#from ebsadmin.tables import AccountsCashierReportTable, CashierReportTable

@systemuser_required
@render_to("reportsystem/generic.html")
def render_report(request, slug):
    class AccountTransactionsSumm(TableReport):
        username = django_tables.Column()
        summ = django_tables.Column()
        class Meta:
            attrs = {'class': 'table table-striped table-bordered table-condensed"'}
    name = rep.get(slug)[1]
    if request.GET and request.method=='GET':
        form = AccountBallanceForm(request.GET)
        if form.is_valid():
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            accounts = form.cleaned_data.get('accounts')
            res = Account.objects.all()
            if accounts:
                res = res.filter(id__in=[a.id for a in accounts])
            res =res.extra(
                select={
                    'summ': "SELECT sum(summ) FROM billservice_transaction WHERE account_id=billservice_account.id and created between '%s' and '%s' " % (date_start, date_end)
                },
                where=["(SELECT sum(summ) FROM billservice_transaction WHERE account_id=billservice_account.id and created between '%s' and '%s' )<>0" % (date_start, date_end)]
            )
            table = AccountTransactionsSumm(res)
            table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            #print res[0].SUMM
            return {'table': table, 'name': name, 'slug': slug}
            
    form = AccountBallanceForm()
    return {'form': form, 'name': name, 'slug': slug}

@systemuser_required
@render_to("reportsystem/generic.html")
def accountaddonservicereport(request, slug):
    class AccountAddonServiceReport(TableReport):
        class Meta:
            model = AccountAddonService
            attrs = {'class': 'table table-striped table-bordered table-condensed"'}
            
    name = rep.get(slug)[1]
    if request.GET and request.method=='GET':
        form = AccountBallanceForm(request.GET)
        if form.is_valid():
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            accounts = form.cleaned_data.get('accounts')
            
            res = AccountAddonService.objects.filter(activated__gte=date_start, deactivated__lte=date_end)
            if accounts:
                res = res.filter(account__in=accounts)
            table = AccountAddonServiceReport(res)
            table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            #print res[0].SUMM
            return {'table': table, 'name': name, 'slug': slug}
        else:
            return {'form': form, 'name': name, 'slug': slug}
    form = AccountBallanceForm()
    return {'form': form, 'name': name, 'slug': slug}

rep = {
       'blabla': (render_report, u'Отчёт по сумме платежей за период'),
       'accountaddonservicereport': (accountaddonservicereport, u'Отчёт по подключенным подключаемым услугам'),
       }

