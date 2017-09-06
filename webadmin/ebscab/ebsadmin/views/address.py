# -*- coding: utf-8 -*-

import json

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import CityForm, StreetForm, HouseForm
from billservice.utils import systemuser_required
from billservice.models import Account, City, Street, House
from ebscab.lib.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebscab.utils import instance_dict


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/address_list.html')
def address(request):
    if not (request.user.account.has_perm('billservice.view_address')):
        messages.error(
            request,
            _(u'У вас нет прав на доступ в этот раздел.'),
            extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = []
    for city in City.objects.all():
        s = []
        for street in Street.objects.filter(city=city):
            d = []
            for house in House.objects.filter(street=street):
                d.append({
                    'title': house.name,
                    'key': 'HOUSE___%s' % house.id
                })
            s.append({
                "title": street.name,
                'key': 'STREET___%s' % street.id,
                'children': d,
                "isFolder": True
            })
        res.append({
            "title": city.name,
            'key': 'CITY___%s' % city.id,
            'children': s,
            "isFolder": True
        })

    ojax = json.dumps(res, ensure_ascii=False)
    return {
        "ojax": ojax
    }


@ajax_request
@systemuser_required
def city_edit(request):
    key = request.GET.get('key', '')
    value = request.GET.get('value')
    v = key.split("___")
    id = None
    if len(v) == 2:
        prefix, id = v
    if id:
        if not (request.user.account.has_perm('billservice.change_city')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на изменение городов')
            }
        item = City.objects.get(id=id)
        form = CityForm({"name": value}, instance=item)
    else:
        if not (request.user.account.has_perm('billservice.add_city')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на добавление городов')
            }
        form = CityForm({'name': value})

    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res = {
                "status": True,
                'id': model.id
            }
            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
        except Exception, e:
            res = {
                "status": False,
                "message": str(e)
            }
    else:
        res = {
            "status": False,
            "errors": form._errors
        }

    return res


@ajax_request
@systemuser_required
def street_edit(request):
    key = request.GET.get('key', '')
    parent = request.GET.get('parent', '')
    value = request.GET.get('value')
    v = key.split("___")
    id = None
    if len(v) == 2:
        prefix, id = v

    v = parent.split("___")
    if len(v) == 2:
        prefix, parent_id = v

    if id:
        if not (request.user.account.has_perm('billservice.change_street')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на изменение улиц')
            }
        item = Street.objects.get(id=id)
        form = StreetForm({"name": value, "city": item.city.id}, instance=item)
    else:
        if not (request.user.account.has_perm('billservice.add_street')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на добавление улиц')
            }
        form = StreetForm({'city': parent_id, 'name': value})

    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res = {
                "status": True,
                'id': model.id
            }

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
        except Exception, e:
            res = {
                "status": False,
                "message": str(e)
            }
    else:
        res = {
            "status": False,
            "errors": form._errors
        }

    return res


@ajax_request
@systemuser_required
def house_edit(request):
    key = request.GET.get('key', '')
    parent = request.GET.get('parent', '')
    value = request.GET.get('value')
    v = key.split("___")
    id = None
    if len(v) == 2:
        prefix, id = v

    v = parent.split("___")
    if len(v) == 2:
        prefix, parent_id = v

    if id:
        if not (request.user.account.has_perm('billservice.change_house')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на изменение домов')
            }
        item = House.objects.get(id=id)
        form = HouseForm({"name": value, 'street': item.street.id},
                         instance=item)
    else:
        if not (request.user.account.has_perm('billservice.add_house')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на добавление домов')
            }
        form = HouseForm({'street': parent_id, 'name': value})

    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res = {"status": True, 'id': model.id}

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
        except Exception, e:
            res = {
                "status": False,
                "message": str(e)
            }
    else:
        res = {
            "status": False,
            "errors": form._errors
        }

    return res


@ajax_request
@systemuser_required
def address_delete(request):
    key = request.GET.get('key', '')
    v = key.split("___")
    id = None
    if len(v) == 2:
        prefix, id = v
    if not id:
        return {
            "status": False,
            "message": "Object not found"
        }

    if prefix == 'CITY':
        if not (request.user.account.has_perm('billservice.delete_city')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на удаление городов')
            }

        model = City.objects.get(id=id)

        log('DELETE', request.user, model)

        model.delete()
        return {
            "status": True
        }

    if prefix == 'STREET':
        if not (request.user.account.has_perm('billservice.delete_street')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на удаление улиц')
            }

        model = Street.objects.get(id=id)

        log('DELETE', request.user, model)

        model.delete()
        return {
            "status": True
        }

    if prefix == 'HOUSE':
        if not (request.user.account.has_perm('billservice.delete_house')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на удаление домов')
            }

        model = House.objects.get(id=id)

        log('DELETE', request.user, model)

        model.delete()
        return {
            "status": True
        }


@ajax_request
@systemuser_required
def cities(request):
    if not (request.user.account.has_perm('billservice.view_city')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }
    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    if id and id != 'None':
        items = City.objects.filter(id=id)
        if not items:
            return {
                'status': False,
                'message': 'City item with id=%s not found' % id
            }
        if len(items) > 1:
            return {
                'status': False,
                'message': 'Returned >1 items with id=%s' % id
            }

    else:
        items = City.objects.all().order_by('name')

    res = []
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {
        "records": res,
        'status': True,
        'totalCount': len(res)
    }


@ajax_request
@systemuser_required
def streets(request):
    if not (request.user.account.has_perm('billservice.view_street')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    city_id = request.POST.get('city_id')
    term = request.POST.get('term')
    id = request.POST.get('id')
    items = []
    if city_id:
        if city_id and term:
            items = Street.objects.filter(
                city__id=city_id, name__istartswith=term)
        else:
            items = Street.objects.filter(city__id=city_id)
    elif id:
        items = [Street.objects.get(id=id)]
    else:
        if term:
            items = Street.objects.filter(name__istartswith=term)
        else:
            items = Street.objects.all()
    res = []
    if items.count() > 0:
        for item in items:
            res.append(instance_dict(item))
    else:
        items = Account.objects.filter(
            street__istartswith=term).values('street')
        for item in items:
            res.append({
                'id': None,
                'name': item.get('street')
            })

    return {
        "records": res,
        'status': True,
        'totalCount': len(items)
    }


@ajax_request
@systemuser_required
def houses(request):
    if not (request.user.account.has_perm('billservice.view_house')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    street_name = request.POST.get('street_name')
    city_id = request.POST.get('city_id')
    term = request.POST.get('term')
    id = request.POST.get('id')
    fields = request.POST.get('fields')
    if street_name:
        if term:
            items = (House.objects
                     .filter(street__name__icontains=street_name,
                             name__istartswith=term)
                     .distinct())
        else:
            items = (House.objects
                     .filter(street__name__icontains=street_name)
                     .distinct())
    elif id:
        items = [House.objects.get(id=id)]
    else:
        if term:
            items = House.objects.filter(name__istartswith=term).distinct()
        else:
            items = House.objects.all().distinct()

    res = []
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {
        "records": res,
        'status': True,
        'totalCount': len(res)
    }
