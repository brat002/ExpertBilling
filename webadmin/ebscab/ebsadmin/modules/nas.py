# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2.config import RequestConfig
from object_log.models import LogItem

from ebsadmin.tables import NasTable

from ebscab.nas.forms import NasForm
from ebscab.nas.models import Nas

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/nas_list.html')
def nas(request):
    res = Nas.objects.all()
    table = NasTable(res)
    RequestConfig(request, paginate = False).configure(table)
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/nas_edit.html')
def nas_edit(request):

    id = request.POST.get("id")
    item = None
    if request.method == 'POST': 
        if id:
            item = Nas.objects.get(id=id)
            form = NasForm(request.POST, instance=item)
        else:
             form = NasForm(request.POST)
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('nas.change_nas')):
                return {'status':False, 'message': u'У вас нет прав на редактирование серверов доступа'}
            
        if  not (request.user.is_staff==True and request.user.has_perm('nas.add_nas')):
            return {'status':False, 'message': u'У вас нет прав на добавление Серверов доступа'}

        
        if form.is_valid():
 
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("nas"))
        else:
            print form._errors
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('nas.nas_view')):
                return {'status':True}

            item = Nas.objects.get(id=id)
            form = NasForm(instance=item)
        else:
            form = NasForm()
   
    return { 'form':form, 'item': item} 

@ajax_request
@login_required
def nas_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('nas.delete_nas')):
        return {'status':False, 'message': u'У вас нет прав на удаление серверов доступа'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Nas.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный сервер доступа найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Nas not found"} 
    