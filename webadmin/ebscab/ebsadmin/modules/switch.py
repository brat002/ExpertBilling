# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import SwitchTable

from billservice.forms import SwitchForm
from billservice.models import Switch

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/switch_list.html')
def switch(request):
    res = Switch.objects.all()
    table = SwitchTable(res)
    table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/switch_edit.html')
def switch_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = Switch.objects.get(id=id)
            form = SwitchForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_switch')):
                return {'status':False, 'message': u'У вас нет прав на редактирование коммутатора'}
        else:
            form = SwitchForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_switch')):
            return {'status':False, 'message': u'У вас нет прав на добавление коммутатора'}


        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("switch")) 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.switch_view')):
                return {'status':True}

            item = Switch.objects.get(id=id)
            
            form = SwitchForm(instance=item)
        else:
            form = SwitchForm()

    return { 'form':form, 'status': False} 

@ajax_request
@login_required
def switch_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_switch')):
        return {'status':False, 'message': u'У вас нет прав на удаление коммутатора'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Switch.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный коммутатор не найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Switch not found"} 
    