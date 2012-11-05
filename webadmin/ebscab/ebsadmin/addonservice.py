# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from tables import AddonServiceTable

from billservice.forms import AddonServiceForm
from billservice.models import AddonService

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/addonservice_list.html')
def addonservice(request):
    res = AddonService.objects.all()
    table = AddonServiceTable(res)
    table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/addonservice_edit.html')
def addonservice_edit(request):
    
    account = None
    id = request.GET.get("id")
    item = None
    if request.method == 'POST': 
        if id:
            item = AddonService.objects.get(id=id)
            form = AddonServiceForm(request.POST, instance=item)
        else:
             form = AddonServiceForm(request.POST)
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_addonservice')):
                return {'status':False, 'message': u'У вас нет прав на редактирование подключаемых услуг'}
            
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_addonservice')):
            return {'status':False, 'message': u'У вас нет прав на добавление подключаемых услуг'}

        
        if form.is_valid():
 
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("addonservice"))
        else:
            print form._errors
            return {'form':form,  'item': item} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.addonservice_view')):
                return {'status':True}

            item = AddonService.objects.get(id=id)
            form = AddonServiceForm(instance=item)
        else:
            form = AddonServiceForm() # An unbound form
    return { 'form':form, 'item': item} 

@ajax_request
@login_required
def addonservice_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_addonservice')):
        return {'status':False, 'message': u'У вас нет прав на удаление подключаемых услуг'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = AddonService.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        
        return {"status": True}
    else:
        return {"status": False, "message": "TransactionType not found"} 
    
