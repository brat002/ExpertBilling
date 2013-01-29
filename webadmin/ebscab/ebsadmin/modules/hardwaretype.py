# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import HardwareTypeTable

from billservice.forms import HardwareTypeForm
from billservice.models import HardwareType
from django.contrib import messages
log = LogItem.objects.log_action
from billservice/helpers import systemuser_required


@systemuser_required
@render_to('ebsadmin/hardwaretype_list.html')
def hardwaretype(request):
    if  not (request.user.account.has_perm('billservice.view_hardwaretype')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    
    res = HardwareType.objects.all()
    table = HardwareTypeTable(res)
    table_to_report = RequestConfig(request, paginate=False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {"table": table} 
    
@systemuser_required
@render_to('ebsadmin/hardwaretype_edit.html')
def hardwaretype_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = HardwareType.objects.get(id=id)
            form = HardwareTypeForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_hardwaretype')):
                messages.error(request, u'У вас нет прав на редактирование типов оборудования', extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = HardwareTypeForm(request.POST) 
            if  not (request.user.account.has_perm('billservice.add_hardwaretype')):
                messages.error(request, u'У вас нет прав на создание типов оборудования', extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)


        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        if  not (request.user.account.has_perm('billservice.view_hardwaretype')):
            messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
            return {}
        if id:


            item = HardwareType.objects.get(id=id)
            
            form = HardwareTypeForm(instance=item)
        else:
            form = HardwareTypeForm()

    return { 'form':form, 'status': False} 

@ajax_request
@systemuser_required
def hardwaretype_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_hardwaretype')):
        return {'status':False, 'message': u'У вас нет прав на удаление типов оборудования пулов'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = HardwareType.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный тип оборудования не найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "HardwareType not found"} 
    