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
def render_report(request):
    class AccountTransactionsSumm(TableReport):
        username = django_tables.Column()
        summ = django_tables.Column()
        class Meta:
            attrs = {'class': 'table table-striped table-bordered table-condensed"'}
            
    if request.GET and request.method=='GET':
        form = AccountBallanceForm(request.GET)
        if form.is_valid():
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            res = Account.objects.all().extra(
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
            return {'table': table}
            
    form = AccountBallanceForm()
    return {'form': form}

@systemuser_required
@render_to("reportsystem/generic.html")
def accountaddonservicereport(request):
    class AccountAddonServiceReport(TableReport):
        account = django_tables.Column()
        service = django_tables.Column()
        class Meta:
            attrs = {'class': 'table table-striped table-bordered table-condensed"'}
            
    if request.GET and request.method=='GET':
        form = AccountBallanceForm(request.GET)
        if form.is_valid():
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            res = AccountAddonService.objects.all()
            table = AccountAddonServiceReport(res)
            table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            #print res[0].SUMM
            return {'table': table}
            
    form = AccountBallanceForm()
    return {'form': form}

rep = {
       'blabla': render_report,
       'accountaddonservicereport': accountaddonservicereport,
       }

