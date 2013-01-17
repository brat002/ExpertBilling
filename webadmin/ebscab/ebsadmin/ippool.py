# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from tables import IPPoolTable

from billservice.forms import IPPoolForm
from billservice.models import IPPool
from django.contrib import messages
log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/ippool_list.html')
def ippool(request):
    if  not (request.user.account.has_perm('billservice.view_ippool')):
        return {'status':False}
    res = IPPool.objects.all()
    table = IPPoolTable(res)
    table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/ippool_edit.html')
def ippool_edit(request):

    id = request.GET.get("id")
    item = None
    if request.method == 'POST': 
        if id:
            item = IPPool.objects.get(id=id)
            form = IPPoolForm(request.POST, instance=item)
        else:
            form = IPPoolForm(request.POST)
        if id:
            if  not (request.user.account.has_perm('billservice.change_ippool')):
                return {'status':False, 'message': u'У вас нет прав на редактирование IP пулов'}
            
        if  not (request.user.account.has_perm('billservice.add_ippool')):
            return {'status':False, 'message': u'У вас нет прав на добавление IP пулов'}

        
        if form.is_valid():
 
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, u'IP пул сохранён.', extra_tags='alert-success')
            return HttpResponseRedirect(reverse("ippool"))
        else:
            messages.error(request, u'Ошибка при сохранении IP пула.', extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.account.has_perm('billservice.view_ippool')):
                return {'status':True}

            item = IPPool.objects.get(id=id)
            form = IPPoolForm(instance=item)
        else:
            form = IPPoolForm()
   
    return { 'form':form, 'item': item} 

@ajax_request
@login_required
def ippool_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_ippool')):
        return {'status':False, 'message': u'У вас нет прав на удаление IP пулов'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = IPPool.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный пул не найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'IP пул успешно удалён.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'Ошибка при удалении IP пула.', extra_tags='alert-danger')
        return {"status": False, "message": "IPPool not found"} 
    