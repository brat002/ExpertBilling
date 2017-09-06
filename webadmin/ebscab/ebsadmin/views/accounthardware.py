# -*- coding: utf-8 -*-

import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import AccountHardwareForm
from billservice.utils import systemuser_required
from billservice.models import Account, AccountHardware
from ebscab.lib.decorators import ajax_request, render_to
from object_log.models import LogItem

from ebsadmin.lib import instance_dict


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/accounthardware_edit.html')
def accounthardware(request):
    account = None
    account_id = request.POST.get("account_id")
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            item = AccountHardware.objects.get(id=id)
            form = AccountHardwareForm(request.POST, instance=item)
        else:
            form = AccountHardwareForm(request.POST)

        if not (request.user.account.has_perm('billservice.change_account')):
            messages.error(request,
                           _(u'У вас нет прав на редактирование аккаунтов'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Оборудование успешно добавлено.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        account_id = request.GET.get("account_id")
        if not (request.user.account.has_perm(
                'billservice.view_accounthardware')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect(
                "%s?id=%s" % (reverse("account_edit"), account_id))

        if id:
            item = AccountHardware.objects.get(id=id)
            form = AccountHardwareForm(instance=item)
        elif account_id:
            account = Account.objects.get(id=account_id)
            form = AccountHardwareForm(initial={
                'account': account,
                'datetime': datetime.datetime.now()
            })  # An unbound form

    return {
        'form': form,
        'status': False,
        'account': account,
        'item': item
    }


@ajax_request
@systemuser_required
def accounthardware_delete(request):
    if not (request.user.account.has_perm(
            'billservice.delete_accounthardware')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление оборудования аккаунта')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        model = AccountHardware.objects.get(id=id)

        log('DELETE', request.user, model)

        model.delete()
        return {
            'status': True
        }
    else:
        return {
            'status': False,
            'message': 'AccountHardware not found'
        }


@ajax_request
@systemuser_required
def accounthardware2(request):
    if not (request.user.account.has_perm('billservice.view_accounthardware')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }
    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    account_id = request.POST.get('account_id', None)
    hardware_id = request.POST.get('hardware_id', None)
    if id and id != 'None':
        items = AccountHardware.objects.filter(id=id)
        if not items:
            return {
                'status': False,
                'message': 'AccountHardware item with id=%s not found' % id
            }
        if len(items) > 1:
            return {
                'status': False,
                'message': 'Returned >1 items with id=%s' % id
            }
    elif account_id:
        items = AccountHardware.objects.filter(account__id=account_id)
    elif hardware_id:
        items = AccountHardware.objects.filter(hardware__id=hardware_id)
    else:
        items = AccountHardware.objects.all()

    res = []
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {
        "records": res,
        'status': True,
        'totalCount': len(res)
    }
