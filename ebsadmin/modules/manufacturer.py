# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import ManufacturerTable

from billservice.forms import ManufacturerForm
from billservice.models import Manufacturer
from django.contrib import messages
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required
from django.utils.translation import ugettext_lazy as _

@systemuser_required
@render_to('ebsadmin/manufacturer_list.html')
def manufacturer(request):
    if  not (request.user.account.has_perm('billservice.view_manufacturer')):
        messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    
    res = Manufacturer.objects.all()
    table = ManufacturerTable(res)
    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else {"per_page": request.COOKIES.get("ebs_per_page")}).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {"table": table} 
    
@systemuser_required
@render_to('ebsadmin/manufacturer_edit.html')
def manufacturer_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = Manufacturer.objects.get(id=id)
            form = ManufacturerForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_manufacturer')):
                messages.error(request, _(u'У вас нет прав на редактирование производителей оборудования'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = ManufacturerForm(request.POST) 
            if  not (request.user.account.has_perm('billservice.add_manufacturer')):
                messages.error(request, _(u'У вас нет прав на создание производителей оборудования'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)



        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, _(u'Производитель успешно сохранён.'), extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:
            messages.error(request, _(u'При сохранении производителя возникли ошибки.'), extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if  not (request.user.account.has_perm('billservice.view_manufacturers')):
            messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
            return {}
        if id:

            item = Manufacturer.objects.get(id=id)
            
            form = ManufacturerForm(instance=item)
        else:
            form = ManufacturerForm()

    return { 'form':form, 'status': False} 

@ajax_request
@systemuser_required
def manufacturer_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_manufacturer')):
        return {'status':False, 'message': _(u'У вас нет прав на удаление производителей оборудования')}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Manufacturer.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": _(u"Указанный производитель оборудования найден %s") % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, _(u'Производитель успешно удалён.'), extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, _(u'При удалении производителя возникли ошибки.'), extra_tags='alert-danger')
        return {"status": False, "message": "manufacturer not found"} 
    