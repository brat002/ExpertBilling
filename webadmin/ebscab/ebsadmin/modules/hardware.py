# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import HardwareTable

from billservice.forms import HardwareForm
from billservice.models import Hardware

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/hardware_list.html')
def hardware(request):
    res = Hardware.objects.all()
    table = HardwareTable(res)
    table_to_report = RequestConfig(request, paginate=False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/hardware_edit.html')
def hardware_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = Hardware.objects.get(id=id)
            form = HardwareForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_hardware')):
                return {'status':False, 'message': u'У вас нет прав на редактирование оборудования'}
        else:
            form = HardwareForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_hardware')):
            return {'status':False, 'message': u'У вас нет прав на добавление оборудования'}


        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("hardware")) 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.hardware_view')):
                return {'status':True}

            item = Hardware.objects.get(id=id)
            
            form = HardwareForm(instance=item)
        else:
            form = HardwareForm()

    return { 'form':form, 'status': False, 'item':item} 

@ajax_request
@login_required
def hardware_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_hardware')):
        return {'status':False, 'message': u'У вас нет прав на удаление оборудования'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Hardware.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное оборудование не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Hardware not found"} 
    