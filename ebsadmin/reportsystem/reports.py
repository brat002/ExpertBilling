#-*- coding: utf-8 -*-


from ebsadmin.reportsystem.forms import AccountBallanceForm

from ebscab.lib.decorators import render_to, ajax_request
from billservice.helpers import systemuser_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from billservice.models import Account

#from ebsadmin.tables import AccountsCashierReportTable, CashierReportTable

@systemuser_required
@render_to("reportsystem/generic.html")
def render_report(request):
    
    if request.GET and request.method=='GET':
        form = AccountBallanceForm(request.GET)
        if form.is_valid():
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            res = Account.objects.all().extra(
                select={
                    'SUMM': "SELECT sum(summ) FROM billservice_transaction WHERE account_id=billservice_account.id and created between '%s' and '%s' " % (date_start, date_end)
                },
            )
            print res[0].SUMM
            return {'table': res}
            
    form = AccountBallanceForm()
    return {'form': form}

rep = {
       'blabla': render_report
       }