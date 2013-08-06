# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import PeriodicalServiceLogTable
from billservice.forms import PeriodicalServiceLogSearchForm
from billservice.models import PeriodicalServiceLog
from django.contrib import messages

log = LogItem.objects.log_action
from billservice.helpers import systemuser_required
from django.utils.translation import ugettext_lazy as _


@systemuser_required
@render_to('ebsadmin/periodicalservicelog_list.html')
def periodicalservicelog(request):
        
    if  not (request.user.account.has_perm('billservice.view_periodicalservicelog')):
        messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    if request.method=='GET' and request.GET: 
        data = request.GET

        #pageitems = 100
        form = PeriodicalServiceLogSearchForm(data)
        if form.is_valid():
            
            account = form.cleaned_data.get('account')
            tariff = form.cleaned_data.get('tariff')
            periodicalservice = form.cleaned_data.get('periodicalservice')

            
            
            
            res = PeriodicalServiceLog.objects.all()
            if account:
                res = res.filter(accounttarif__account__id__in=account)

            if tariff:
                res = res.filter(service__tarif=tariff)

            
            if periodicalservice:
                res = res.filter(service=periodicalservice)

            
            table = PeriodicalServiceLogTable(res)
            table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            
            
            
            return {"table": table,  'form':form, 'resultTab':True}   
    
        else:
            return {'status':False, 'form':form}
    else:
        form = PeriodicalServiceLogSearchForm()
        return { 'form':form}   

@ajax_request
@systemuser_required
def periodicalservicelog_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_periodicalservicelog')):
        return {'status':False, 'message': _(u'У вас нет прав на удаление истории списаний по период. услугам')}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = PeriodicalServiceLog.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": _(u"Указанное списание не найдено %s") % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "PeriodicalServiceLog not found"} 
    