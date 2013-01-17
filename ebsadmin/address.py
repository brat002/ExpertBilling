# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from object_log.models import LogItem



from billservice.forms import IPPoolForm, CityForm, StreetForm, HouseForm
from billservice.models import City, Street, House
import simplejson as json

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/address_list.html')
def address(request):
    if  not (request.user.account.has_perm('billservice.view_address')):
        return {'status':False}
    res = []
    for city in  City.objects.all():
        s=[]
        for street in Street.objects.filter(city=city):
            d=[]
            for house in House.objects.filter(street=street):
                d.append({'title': house.name, 'key': 'HOUSE___%s' % house.id})
            s.append({"title": street.name, 'key': 'STREET___%s' % street.id, 'children':d, "isFolder":True})
        res.append({"title": city.name, 'key': 'CITY___%s' % city.id, 'children':s, "isFolder":True})
            
    ojax = json.dumps(res, ensure_ascii=False)
    return {"ojax": ojax} 
    
@ajax_request
@login_required
def city_edit(request):
    
    key = request.GET.get('key','')
    value = request.GET.get('value')
    v = key.split("___")
    id = None
    if len(v)==2:
        prefix, id = v
    if id:
        if  not (request.user.account.has_perm('billservice.change_city')):
            return {'status':False, 'message':u'У вас нет прав на изменение городов'}
        item = City.objects.get(id=id)
        form = CityForm({"name":value}, instance=item)
    else:
        if  not (request.user.account.has_perm('billservice.add_city')):
            return {'status':False, 'message':u'У вас нет прав на добавление городов'}
        form = CityForm({'name': value})
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id': model.id}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def street_edit(request):
    
    key = request.GET.get('key','')
    parent = request.GET.get('parent','')
    value = request.GET.get('value')
    v = key.split("___")
    id = None
    if len(v)==2:
        prefix, id = v
        
    v = parent.split("___")
    if len(v)==2:
        prefix, parent_id = v
        
    if id:
        if  not (request.user.account.has_perm('billservice.change_street')):
            return {'status':False, 'message':u'У вас нет прав на изменение улиц'}
        item = Street.objects.get(id=id)
        form = StreetForm({"name":value, "city": item.city.id}, instance=item)
    else:
        if  not (request.user.account.has_perm('billservice.add_street')):
            return {'status':False, 'message':u'У вас нет прав на добавление улиц'}
        form = StreetForm({'city':parent_id, 'name': value})
    
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id': model.id}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

    
@ajax_request
@login_required
def house_edit(request):
    
    key = request.GET.get('key','')
    parent = request.GET.get('parent','')
    value = request.GET.get('value')
    v = key.split("___")
    id = None
    if len(v)==2:
        prefix, id = v
        
    v = parent.split("___")
    if len(v)==2:
        prefix, parent_id = v
        
    if id:
        if  not (request.user.account.has_perm('billservice.change_house')):
            return {'status':False, 'message':u'У вас нет прав на изменение Домов'}
        item = House.objects.get(id=id)
        form = HouseForm({"name":value, 'street':item.street.id}, instance=item)
    else:
        if  not (request.user.account.has_perm('billservice.add_house')):
            return {'status':False, 'message':u'У вас нет прав на добавление Домов'}
        form = HouseForm({'street':parent_id, 'name': value})
    
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id': model.id}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def address_delete(request):

    key = request.GET.get('key','')
    v = key.split("___")
    id = None
    if len(v)==2:
        prefix, id = v
    if not id:
        return {"status": False, "message": "Object not found"}
    
    if prefix=='CITY':
        if  not (request.user.account.has_perm('billservice.delete_city')):
            return {'status':False, 'message':u'У вас нет прав на удаление городов'}
    
        model = City.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}

    if prefix=='STREET':
        if  not (request.user.account.has_perm('billservice.delete_street')):
            return {'status':False, 'message':u'У вас нет прав на удаление улиц'}
    
        model = Street.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}

    if prefix=='HOUSE':
        if  not (request.user.account.has_perm('billservice.delete_house')):
            return {'status':False, 'message':u'У вас нет прав на удаление домов'}
    
        model = House.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}

    