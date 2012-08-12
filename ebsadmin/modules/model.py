# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2.config import RequestConfig
from object_log.models import LogItem

from ebsadmin.tables import ModelTable

from billservice.forms import ModelHardwareForm as ModelForm
from billservice.models import Model

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/model_list.html')
def model(request):
    res = Model.objects.all()
    table = ModelTable(res)
    RequestConfig(request, paginate = False).configure(table)
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/model_edit.html')
def model_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = Model.objects.get(id=id)
            form = ModelForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_model')):
                return {'status':False, 'message': u'У вас нет прав на редактирование моделей оборудования'}
        else:
            form = ModelForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_model')):
            return {'status':False, 'message': u'У вас нет прав на добавление моделей оборудования'}


        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.model_view')):
                return {'status':True}

            item = Model.objects.get(id=id)
            
            form = ModelForm(instance=item)
        else:
            form = ModelForm()

    return { 'form':form, 'status': False} 

@ajax_request
@login_required
def model_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_model')):
        return {'status':False, 'message': u'У вас нет прав на удаление моделей оборудования'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Model.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная модель оборудования не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Model not found"} 
    