# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2.config import RequestConfig
from object_log.models import LogItem

from tables import SystemUserTable
from django.contrib.auth.models import User
from billservice.forms import SystemUserForm
from billservice.models import SystemUser

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/systemuser_list.html')
def systemuser(request):
    res = SystemUser.objects.all()
    table = SystemUserTable(res)
    RequestConfig(request, paginate = False).configure(table)
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/systemuser_edit.html')
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
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_systemuser')):
                return {'status':False, 'message': u'У вас нет прав на редактирование системных пользователей'}
            
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_systemuser')):
            return {'status':False, 'message': u'У вас нет прав на добавление системных пользователей'}

        
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
            u.is_superuser = form.cleaned_data.get("superuser")
            u.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("systemuser"))
        else:
            print form._errors
            return {'form':form,  'item': item} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.systemuser_view')):
                return {'status':True}
            item = SystemUser.objects.get(id=id)
            u = User.objects.filter(username=item.username)
            if not u:
                u = User.objects.create_user(item.username, item.email, item.text_password)
            else:
                u=u[0]
            
            form = SystemUserForm(initial={'authgroup': u.groups.all(), 'superuser': u.is_superuser}, instance=item)
        else:
            form = SystemUserForm()
   
    return { 'form':form, 'item': item} 


@ajax_request
@login_required
def systemuser_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_systemuser')):
        return {'status':False, 'message': u'У вас нет прав на удаление администраторов'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = SystemUser.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный администратор не найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "systemuser not found"} 