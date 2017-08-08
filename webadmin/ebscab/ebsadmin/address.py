# -*- coding: utf-8 -*-

import simplejson as json
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import CityForm, StreetForm, HouseForm
from billservice.helpers import systemuser_required
from billservice.models import City, Street, House
from ebscab.lib.decorators import render_to, ajax_request
from object_log.models import LogItem


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
