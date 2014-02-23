# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import GroupTable

from billservice.forms import GroupForm
from billservice.models import Group
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required
from django.utils.translation import ugettext_lazy as _

@systemuser_required
@render_to('ebsadmin/group/list.html')
def group(request):

    if  not (request.user.account.has_perm('billservice.view_group')):
        messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    res = Group.objects.all()
    table = GroupTable(res)
    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {"table": table} 
    
@systemuser_required
@render_to('ebsadmin/group/edit.html')
def group_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 
        model = None
        if id:
            model = Group.objects.get(id=id)
            form = GroupForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_group')):
                messages.error(request, _(u'У вас нет прав на редактирование групп трафика'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        else:
            form = GroupForm(request.POST) 
        if  not (request.user.account.has_perm('billservice.add_group')):
                messages.error(request, _(u'У вас нет прав на создание групп трафика'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid():
 
            model = form.save(commit=False)
            
            model.save()
            form.save_m2m()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, _(u'Группа трафика успешно сохранена.'), extra_tags='alert-success')
            return HttpResponseRedirect(reverse("group"))
        else:
            messages.error(request, _(u'При сохранении группы трафика возникли ошибки.'), extra_tags='alert-danger')
            return {'form':form,  'status': False, 'item': model} 

    else:
        id = request.GET.get("id")
        if  not (request.user.account.has_perm('billservice.view_group')):
            messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:


            item = Group.objects.get(id=id)
            
            form = GroupForm(instance=item)
        else:
            form = GroupForm()

    return { 'form':form, 'status': False, 'item':item} 

@ajax_request
@systemuser_required
def group_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_group')):
        return {'status':False, 'message': _(u'У вас нет прав на удаление групп трафика')}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Group.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": _(u"Указанная группа трафика не найдена %s") % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, _(u'Группа трафика успешно удалёна.'), extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, _(u'При удалении группы трафика возникли ошибки.'), extra_tags='alert-danger')
        return {"status": False, "message": "Group not found"} 
    