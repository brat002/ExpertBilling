# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import F, Max
from django.http import HttpResponseRedirect
from django_tables2.config import RequestConfig
from object_log.models import LogItem
from lib import instance_dict
from tables import TrafficClassTable, TrafficNodeTable

from nas.forms import TrafficClassForm, TrafficNodeForm
from nas.models import TrafficClass, TrafficNode

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/trafficclass_list.html')
def trafficclass(request):
    res = TrafficClass.objects.all()
    table = TrafficClassTable(res)
    RequestConfig(request, paginate = False).configure(table)
    return {"table": table} 
    
    

@login_required
@render_to('ebsadmin/trafficclass_upload.html')
def trafficclass_upload(request):

    return {} 
    
@ajax_request
@login_required
def trafficclass_weight(request):
    if  not (request.user.is_staff==True and request.user.has_perm('nas.change_trafficclass')):
        return {'status':False, 'message': u'У вас нет прав на измегегте классов'}
    ids = request.POST.getlist("id")
    k=1
    if ids:
        TrafficClass.objects.all().update(weight=F('weight')+1000)
    for i in ids:
        item = TrafficClass.objects.get(id=i)
        item.weight=k
        item.save()
        log('EDIT', request.user, item) if id else log('CREATE', request.user, item) 
        k+=1
    return {'status':True}
    
@login_required
@render_to('ebsadmin/trafficnode_list.html')
def trafficnode_list(request):
    id = request.GET.get("id")
    res = TrafficNode.objects.filter(traffic_class__id=id)
    table = TrafficNodeTable(res)
    RequestConfig(request, paginate = False).configure(table)
    return {"table": table, 'item':TrafficClass.objects.get(id=id)} 
    


@login_required
@render_to('ebsadmin/trafficclass_edit.html')
def trafficclass_edit(request):
    id = request.GET.get("id")
    item = None
    model = None
    if request.method == 'POST': 
        if id:
            model = TrafficClass.objects.get(id=id)
            form = TrafficClassForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_trafficclass')):
                return {'status':False, 'message': u'У вас нет прав на редактирование классов трафика'}
        else:
            form = TrafficClassForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_trafficclass')):
            return {'status':False, 'message': u'У вас нет прав на добавление классов трафика'}

        if form.is_valid():
            print 11
            model = form.save(commit=False)
            print 22
            if  not model.weight:
                print 33
                maxw = TrafficClass.objects.all().aggregate(Max('weight'))
                maxw = maxw.get("weight__max", 1)+1
                model.weight = maxw
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('nas.trafficclass_view')):
                return {'status':True}

            item = TrafficClass.objects.get(id=id)
            
            form = TrafficClassForm(instance=item)
        else:
            form = TrafficClassForm()
   
    return { 'form':form, 'status': False, 'item': item} 


@login_required
@render_to('ebsadmin/trafficnode_edit.html')
def trafficnode(request):

    traffic_class = request.GET.get("traffic_class")
    id = request.GET.get("id")
    accountaddonservice = None
    item = None
    if request.method == 'POST': 
        print 1
        print request.POST
        print request.GET
        if id:
            print 11
            model = TrafficNode.objects.get(id=id)
            form = TrafficNodeForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_accountaddonservice')):
                return {'status':False, 'message': u'У вас нет прав на редактирование привязок подключаемых услуг'}
        else:
            print 22
            form = TrafficNodeForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_accountaddonservice')):
            return {'status':False, 'message': u'У вас нет прав на добавление привязок подключаемых услуг'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        traffic_class_id = request.GET.get("traffic_class")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('nas.trafficnode_view')):
                return {'status':True}

            item = TrafficNode.objects.get(id=id)
            
            form = TrafficNodeForm(instance=item)
        elif traffic_class_id:
            form = TrafficNodeForm(initial={'traffic_class': TrafficClass.objects.get(id=traffic_class_id)})
   
    return { 'form':form, 'status': False, 'item': item} 


@ajax_request
@login_required
def trafficnode_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('nas.delete_trafficnode')):
        return {'status':False, 'message': u'У вас нет прав на удаление направлений'}
    id = request.GET.getlist('d')
    if id:
        try:
            items = TrafficNode.objects.filter(id__in=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное направление не найдено %s" % str(e)}
        for item in items:
            log('DELETE', request.user, item)
            item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TrafficNode not found"} 
    
@ajax_request
@login_required
def trafficclass_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_trafficclass')):
        return {'status':False, 'message': u'У вас нет прав на удаление классов трафика'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TrafficClass.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный класс не найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TrafficClass not found"} 
    