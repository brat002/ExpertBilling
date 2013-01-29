# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem
from django.db.models import Sum
from ebsadmin.tables import GroupStatTable
from billservice.forms import GroupStatSearchForm
from billservice.models import GroupStat
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required


@systemuser_required
@render_to('ebsadmin/groupstat_list.html')
def groupstat(request):
        
    if  not (request.user.account.has_perm('billservice.view_groupstat')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')


    if request.GET: 
        data = request.GET

        #pageitems = 100
        form = GroupStatSearchForm(data)
        if form.is_valid():
            
            accounts = form.cleaned_data.get('accounts')
            groups = form.cleaned_data.get('groups')
            daterange = form.cleaned_data.get('daterange') or []

            start_date, end_date =None, None
            if len(daterange)==2:
                start_date, end_date = daterange


            
            
            
            res = GroupStat.objects.all().select_related().values('account__username', 'group__name').annotate(summ_bytes=Sum('bytes'))
            if accounts:
                res = res.filter(account__in=accounts)
            if groups:
                res = res.filter(group__in=groups)
  
            if start_date:
                res = res.filter(datetime__gte=start_date)

            if end_date:
                res = res.filter(datetime__lte=end_date)
                
            table = GroupStatTable(res)
            table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            
            return {"table": table,  'form':form, 'resultTab':True}   
    
        else:
            return {'status':False, 'form':form}
    else:
        form = GroupStatSearchForm()
        return { 'form':form}   


    