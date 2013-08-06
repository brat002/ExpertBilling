# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from billservice.helpers import systemuser_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import AccountsCashierReportTable, CashierReportTable
from billservice.forms import CashierAccountForm
from billservice.models import Account, Transaction

log = LogItem.objects.log_action

from django.utils.translation import ugettext_lazy as _

@systemuser_required
@render_to('cassa/index.html')
def index(request):
        
    if  not request.user.account.has_perm('billservice.view_cashier'):
        return {'status':False}

    if request.method=='GET' and request.GET: 
        data = request.GET

        #pageitems = 100
        form = CashierAccountForm(request.GET)
        if form.is_valid():
            
            res = Account.objects.all()
            
            contract = form.cleaned_data.get('contract')
            username = form.cleaned_data.get('username')
            fullname = form.cleaned_data.get('fullname')
            city = form.cleaned_data.get('city')
            street = form.cleaned_data.get('street')
            house = form.cleaned_data.get('house')
            
            
            if contract:
                res = res.filter(contract__istartswith=contract)

            if username:
                res = res.filter(username__istartswith=username)

            if fullname:
                res = res.filter(fullname__istartswith=fullname)
    
            if city:
                res = res.filter(city=city)        
                
            if street:
                res = res.filter(street__istartswith=street)

            if house:
                res = res.filter(house__istartswith=house)
                

            
            table = AccountsCashierReportTable(res)
            table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            
            return {"table": table,  'form':form, 'resultTab':True}   
    
        else:
            return {'status':False, 'form':form}
    else:
        res = Account.objects.filter(status=1)
        table = AccountsCashierReportTable(res)
        table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
        if table_to_report:
            return create_report_http_response(table_to_report, request)        
        form = CashierAccountForm()
        return { 'form':form, 'table': table}   


@systemuser_required
@render_to('cassa/transactionreport.html')
def transactionreport(request):
        
    if  not (request.user.account.has_perm('billservice.view_transaction')):
        return {'status':False}

    res = Transaction.objects.filter(systemuser=request.user.account).order_by('-created')

            
    table = CashierReportTable(res)
    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    
    return {"table": table, }   
    
  

