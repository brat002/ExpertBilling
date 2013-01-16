# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import PermissionGroupTable

from billservice.forms import PermissionGroupForm
from billservice.models import PermissionGroup


log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/permissiongroup_list.html')
def permissiongroup(request):
    if  not (request.user.account.has_perm('billservice.view_permissiongroup')):
        return {'status':False}

    items = PermissionGroup.objects.all()
    table = PermissionGroupTable(items)
    table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    
    return {"table": table}   


    
@login_required
@render_to('ebsadmin/permissiongroup_edit.html')
def permissiongroup_edit(request):
    

    id = request.POST.get("id")
    item = None
    if request.method == 'POST': 

        if id:
            model = PermissionGroup.objects.get(id=id)
            form = PermissionGroupForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_permissionrule')):
                return {'status':False, 'message': u'У вас нет прав на редактирование групп доступа'}
        else:
            form = PermissionGroupForm(request.POST) 
        if  not (request.user.has_perm('billservice.add_permissiongroup')):
            return {'status':False, 'message': u'У вас нет прав на добавление групп доступа'}


        if form.is_valid():

            model = form.save(commit=False)
            model.save()
            form.save_m2m()
            log('CREATE', request.user, model) 
                    
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("permissiongroup"))
        else:

            return {'form':form,  'status': False,  } 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.account.has_perm('billservice.view_permissiongroup')):
                return {'status':False}

            item = PermissionGroup.objects.get(id=id)
            
            form = PermissionGroupForm(instance=item)

        else:
            form = PermissionGroupForm()

    return { 'form':form, 'status': False, 'item': item} 


@ajax_request
@login_required
def permissiongroup_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_permissiongroup')):
        return {'status':False, 'message': u'У вас нет прав на удаление групп доступа'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = PermissionGroup.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная группа доступа не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "PermissionGroup not found"} 
    