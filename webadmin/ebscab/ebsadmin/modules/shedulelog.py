# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import SheduleLogTable
from billservice.forms import SheduleLogSearchForm
from billservice.models import SheduleLog

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/shedulelog_list.html')
def shedulelog(request):
        


    if request.method=='GET' and request.GET: 
        data = request.GET

        #pageitems = 100
        form = SheduleLogSearchForm(data)
        if form.is_valid():
            
            account = form.cleaned_data.get('account')


            
            
            
            res = SheduleLog.objects.all()
            if account:
                res = res.filter(accounttarif__account__id__in=account)

  

            
            table = SheduleLogTable(res)
            table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            
            return {"table": table,  'form':form, 'resultTab':True}   
    
        else:
            return {'status':False, 'form':form}
    else:
        form = SheduleLogSearchForm()
        return { 'form':form}   

@ajax_request
@login_required
def shedulelog_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_periodicalservicelog')):
        return {'status':False, 'message': u'У вас нет прав на удаление истории списаний по период. услугам'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = PeriodicalServiceLog.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное списание не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "PeriodicalServiceLog not found"} 
    