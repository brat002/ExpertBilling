# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from billservice.helpers import systemuser_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from tables import SystemUserTable
from django.contrib.auth.models import User
from billservice.forms import SystemUserForm
from billservice.models import SystemUser
from django.contrib import messages
log = LogItem.objects.log_action
from django.utils.translation import ugettext_lazy as _


@systemuser_required
@render_to('ebsadmin/systemuser/list.html')
def systemuser(request):
    if  not (request.user.account.has_perm('billservice.view_systemuser')):
        messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    
    res = SystemUser.objects.all()
    table = SystemUserTable(res)
    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {"table": table} 
    
@systemuser_required
@render_to('ebsadmin/systemuser/edit.html')
def systemuser_edit(request):

    id = request.GET.get("id")
    item = None
    if request.method == 'POST': 

        if id:
            item = SystemUser.objects.get(id=id)
            form = SystemUserForm(request.POST, instance=item)
        else:
            form = SystemUserForm(request.POST)
             
        if id:
            if  not (request.user.account.has_perm('billservice.change_systemuser')):
                messages.error(request, _(u'У вас нет прав на редактирование системных пользователей'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            if  not (request.user.account.has_perm('billservice.add_systemuser')):
                messages.error(request, _(u'У вас нет прав на создание системных пользователей'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)


        
        if form.is_valid():
            authgroups = form.cleaned_data.get('authgroup')
            model = form.save(commit=False)
            model.save()    

            u = User.objects.filter(username=model.username)
            if not u:
                u = User.objects.create_user(model.username, model.email, model.text_password)
            else:
                u=u[0]
            for item in authgroups:
                if item not in u.groups.all():
                    u.groups.add(item)
            for item in u.groups.all():
                if item not in u.groups.all():
                    u.groups.remove(item)
                
            u.is_staff = True
            u.is_active = model.status
            u.is_superuser = form.cleaned_data.get("is_superuser")
            u.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, _(u'Администратор успешно сохранён.'), extra_tags='alert-success')
            return HttpResponseRedirect(reverse("systemuser"))
        else:
            messages.success(request, _(u'Ошибка при сохранении администратора.'), extra_tags='alert-success')
            return {'form':form,  'item': item} 
    else:
        if  not (request.user.account.has_perm('billservice.view_systemuser')):
            messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        id = request.GET.get("id")

        if id:

            item = SystemUser.objects.get(id=id)
            u = User.objects.filter(username=item.username)
            if not u:
                u = User.objects.create_user(item.username, item.email, item.text_password)
            else:
                u=u[0]
            print item.is_superuser
            form = SystemUserForm(initial={'authgroup': u.groups.all(), 'superuser': u.is_superuser}, instance=item)
        else:
            form = SystemUserForm()
   
    return { 'form':form, 'item': item} 


@ajax_request
@systemuser_required
def systemuser_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_systemuser')):
        return {'status':False, 'message': _(u'У вас нет прав на удаление администраторов')}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = SystemUser.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": _(u"Указанный администратор не найден %s") % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, _(u'Администратор успешно удалён.'), extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, _(u'Ошибка при удалении администратора.'), extra_tags='alert-danger')
        return {"status": False, "message": "systemuser not found"} 
    