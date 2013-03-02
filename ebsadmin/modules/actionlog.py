# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem
from object_log.forms import LogItemFilterForm
from django.contrib.contenttypes.models import ContentType
from ebsadmin.tables import ActionLogTable
from django.contrib import messages

log = LogItem.objects.log_action
from billservice.helpers import systemuser_required


@systemuser_required
@render_to('ebsadmin/actionlog_list.html')
def actionlog(request):
    if  not (request.user.account.has_perm('object_log.view_logitem')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    
    if request.GET:
        form = LogItemFilterForm(request.GET)
        if form.is_valid():
            id = form.cleaned_data.get("id")
            content_type = form.cleaned_data.get("ct")
            action = form.cleaned_data.get("action")
            user = form.cleaned_data.get("user")
            start_date = form.cleaned_data.get("start_date")
            end_date = form.cleaned_data.get("end_date")
            
            
            
            res = LogItem.objects.all()
            
            if id:
                res = res.filter(object_id1=id)
                
            if content_type:
                res = res.filter(object_type1=content_type)
                
            if action:
                res = res.filter(action__in=action)
            if user:
                res = res.filter(user__in=user)
                
            if start_date:
                res = res.filter(timestamp__gte=start_date)
            if end_date:
                res = res.filter(timestamp__lte=end_date)
                
            res = res.order_by('-id').select_related('user')
            table = ActionLogTable(res)
            table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else {"per_page": request.COOKIES.get("ebs_per_page")}).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
    else:
        table = None
        form = LogItemFilterForm()
        
    return {"table": table, 'form': form} 
    
