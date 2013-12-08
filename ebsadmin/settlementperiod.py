# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from billservice.helpers import systemuser_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from tables import SettlementPeriodTable

from billservice.forms import SettlementPeriodForm
from billservice.models import SettlementPeriod
import datetime
from django.contrib import messages
log = LogItem.objects.log_action
from django.utils.translation import ugettext_lazy as _


@systemuser_required
@render_to('ebsadmin/settlement_period/list.html')
def settlementperiod(request):
    if  not (request.user.account.has_perm('billservice.view_settlementperiod')):
        messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    
    res = SettlementPeriod.objects.all()
    table = SettlementPeriodTable(res)
    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {"table": table} 
    
@systemuser_required
@render_to('ebsadmin/settlement_period/edit.html')
def settlementperiod_edit(request):

    id = request.GET.get("id")
    item = None
    if request.method == 'POST': 
        if id:
            item = SettlementPeriod.objects.get(id=id)
            form = SettlementPeriodForm(request.POST, instance=item)
        else:
            form = SettlementPeriodForm(request.POST)
        if id:
            if  not (request.user.account.has_perm('billservice.change_settlementperiod')):
                messages.error(request, _(u'У вас нет прав на редактирование расчётных периодов'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
            
        else:
            if  not (request.user.account.has_perm('billservice.add_settlementperiod')):
                messages.error(request, _(u'У вас нет прав на создание расчётных периодов'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)


        
        if form.is_valid():
 
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, _(u'Расчётный период удачно создан.'), extra_tags='alert-success')
            return HttpResponseRedirect(reverse("settlementperiod"))
        else:
            messages.warning(request, _(u'Ошибка.'), extra_tags='alert-danger')
            return {'form':form,  'status': False, 'item':item} 
    else:
        if  not (request.user.account.has_perm('billservice.view_settlementperiod')):
            messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        id = request.GET.get("id")

        if id:


            item = SettlementPeriod.objects.get(id=id)
            form = SettlementPeriodForm(instance=item)
        else:
            form = SettlementPeriodForm(initial={'time_start':datetime.datetime(2010,1,1,0,0,0)})
            
   
    return { 'form':form, 'item': item} 

@ajax_request
@systemuser_required
def settlementperiod_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_settlementperiod')):
        return {'status':False, 'message': _(u'У вас нет прав на удаление расчётных периодов')}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = SettlementPeriod.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": _(u"Указанный расчётный период не найден %s") % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SettlementPeriod not found"} 
    
    