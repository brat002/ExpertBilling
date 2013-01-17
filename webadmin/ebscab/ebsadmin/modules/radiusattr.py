# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import RadiusAttrTable

from billservice.forms import IPPoolForm, RadiusAttrsForm
from billservice.models import RadiusAttrs, Tariff
from ebscab.nas.models import Nas 

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/radiusattr_list.html')
def radiusattr(request):
    if  not (request.user.account.has_perm('billservice.view_radiusattrs')):
        return {'status':False}
    
    nas_id = request.GET.get("nas")
    tarif_id = request.GET.get("tarif")
    item = None
    tariff = None
    nas = None
    if nas_id:
        nas = Nas.objects.get(id=nas_id)
        res = RadiusAttrs.objects.filter(nas__id=nas_id)
    elif tarif_id:
        tariff = Tariff.objects.get(id=tarif_id)
        res = RadiusAttrs.objects.filter(tarif__id=tarif_id)
    else:
        res = RadiusAttrs.objects.all()
    table = RadiusAttrTable(res)
    table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {"table": table, 'nas':nas, 'tariff':tariff,  'model_name': nas.__class__.__name__ if nas else tariff.__class__.__name__ if tariff else '' } 
    
@login_required
@render_to('ebsadmin/radiusattr_edit.html')
def radiusattr_edit(request):
    
    account = None
    nas_id = request.GET.get("nas")
    tarif_id = request.GET.get("tarif")
    id = request.POST.get("id")
    tariff = None
    nas = None
    if nas_id:
        nas= Nas.objects.get(id=nas_id)
    elif tarif_id:
        tariff= Tariff.objects.get(id=tarif_id)

    if request.method == 'POST': 

        if id:
            model = RadiusAttrs.objects.get(id=id)
            form = RadiusAttrsForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_radiusattrs')):
                return {'status':False, 'message': u'У вас нет прав на редактирование радиус атрибутов'}
        else:
            form = RadiusAttrsForm(request.POST) 
        if  not (request.user.account.has_perm('billservice.add_radiusattrs')):
            return {'status':False, 'message': u'У вас нет прав на добавление радиус атрибутов'}


        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False, 'nas':nas, 'tariff':tariff } 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.account.has_perm('billservice.view_radiusattrs')):
                return {'status':False}

            item = RadiusAttrs.objects.get(id=id)
            
            form = RadiusAttrsForm(instance=item)
        elif nas_id:
            form = RadiusAttrsForm(initial={'nas': nas})
        elif tarif_id:
            form = RadiusAttrsForm(initial={'tarif': tariff, })

    return { 'form':form, 'status': False, 'nas':nas, 'tariff':tariff } 


@ajax_request
@login_required
def radiusattr_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_radiusattrs')):
        return {'status':False, 'message': u'У вас нет прав на удаление радиус атрибутов'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = RadiusAttrs.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный атрибут найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "RadiusAttrs not found"} 
    