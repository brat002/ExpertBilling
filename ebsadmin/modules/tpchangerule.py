# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import TPChangeRuleTable

from billservice.forms import TPChangeRuleForm, TPChangeMultipleRuleForm
from billservice.models import TPChangeRule


log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/tpchangerule_list.html')
def tpchangerule(request):


    items = TPChangeRule.objects.all()
    table = TPChangeRuleTable(items)
    table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    
    return {"table": table}   


    
@login_required
@render_to('ebsadmin/tpchangerule_edit.html')
def tpchangerule_edit(request):
    

    id = request.POST.get("id")
    item = None
    if request.method == 'POST': 

        if id:
            model = TPChangeRule.objects.get(id=id)
            form = TPChangeRuleForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_tpchangerule')):
                return {'status':False, 'message': u'У вас нет прав на редактирование правил смены тарифных планов'}
        else:
            form = TPChangeMultipleRuleForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_tpchangerule')):
            return {'status':False, 'message': u'У вас нет прав на добавление правил смены тарифных планов'}


        if form.is_valid():
            if id:
                model = form.save(commit=False)
                model.save()
            else:
                from_tariff = form.cleaned_data.get("from_tariff")
                cost = form.cleaned_data.get("cost")
                disabled = form.cleaned_data.get("disabled")
                on_next_sp = form.cleaned_data.get("on_next_sp")
                settlement_period = form.cleaned_data.get("settlement_period")
                ballance_min = form.cleaned_data.get("ballance_min")
                mirror = form.cleaned_data.get("mirror")
                
                for tariff in form.cleaned_data.get("to_tariffs"):
                    tp = TPChangeRule.objects.filter(from_tariff=from_tariff, to_tariff=tariff)
                    if not tp:
                        model=TPChangeRule(from_tariff=from_tariff, to_tariff=tariff, cost=cost, disabled=disabled, on_next_sp=on_next_sp, settlement_period=settlement_period, ballance_min=ballance_min)
                        model.save()
                    else:
                        tp.update(cost=cost, disabled=disabled, on_next_sp=on_next_sp, settlement_period=settlement_period, ballance_min=ballance_min)
                    log('CREATE', request.user, model) 
                    tp = TPChangeRule.objects.filter(from_tariff=tariff, to_tariff=from_tariff)
                    if not tp:
                        model=TPChangeRule(from_tariff=tariff, to_tariff=from_tariff, cost=cost, disabled=disabled, on_next_sp=on_next_sp, settlement_period=settlement_period, ballance_min=ballance_min)
                        model.save()
                    else:
                        tp.update(cost=cost, disabled=disabled, on_next_sp=on_next_sp, settlement_period=settlement_period, ballance_min=ballance_min)
                    log('CREATE', request.user, model) 
                    
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("tpchangerule"))
        else:
            print form._errors
            return {'form':form,  'status': False,  } 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tpchangerule_view')):
                return {'status':True}

            item = TPChangeRule.objects.get(id=id)
            
            form = TPChangeRuleForm(instance=item)

        else:
            form = TPChangeMultipleRuleForm()

    return { 'form':form, 'status': False, 'item': item} 


@ajax_request
@login_required
def tpchangerule_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_tpchangerule')):
        return {'status':False, 'message': u'У вас нет прав на удаление правил смены тарифных планов'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TPChangeRule.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TPChangeRule not found"} 
    