# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2.config import RequestConfig
from object_log.models import LogItem

from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response

from ebsadmin.tables import AccountGroupTable

from billservice.forms import AccountGroupForm
from billservice.models import AccountGroup

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/accountgroup_list.html')
def accountgroup(request):
    res = AccountGroup.objects.all()
    table = AccountGroupTable(res)
    table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/accountgroup_edit.html')
def accountgroup_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = AccountGroup.objects.get(id=id)
            form = AccountGroupForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_accountgroup')):
                return {'status':False, 'message': u'У вас нет прав на редактирование типов оборудования'}
        else:
            form = AccountGroupForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_accountgroup')):
            return {'status':False, 'message': u'У вас нет прав на добавление типов оборудования'}


        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False, 'item': model} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.accountgroup_view')):
                return {'status':True}

            item = AccountGroup.objects.get(id=id)
            
            form = AccountGroupForm(instance=item)
        else:
            form = AccountGroupForm()

    return { 'form':form, 'status': False, 'item': item} 

@ajax_request
@login_required
def accountgroup_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_accountgroup')):
        return {'status':False, 'message': u'У вас нет прав на удаление групп пользователей'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = AccountGroup.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная группа не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "AccountGroup not found"} 
    