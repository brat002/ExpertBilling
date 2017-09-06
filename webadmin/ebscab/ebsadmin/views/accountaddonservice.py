# -*- coding: utf-8 -*-

import datetime

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from billservice.forms import AccountAddonServiceModelForm
from billservice.utils import systemuser_required
from billservice.models import Account, AccountAddonService, SubAccount
from ebscab.utils.decorators import ajax_request, render_to
from object_log.models import LogItem


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/accountaddonservice_edit.html')
def accountaddonservice_edit(request):
    account = None
    account_id = request.GET.get("account_id")
    subaccount_id = request.GET.get("subaccount_id")
    id = request.GET.get("id")
    accountaddonservice = None
    if request.method == 'POST':
        if id:
            model = AccountAddonService.objects.get(id=id)
            form = AccountAddonServiceModelForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_accountaddonservice')):
                messages.error(request,
                               _(u'У вас нет прав на редактирование привязок '
                                 u'подключаемых услуг'),
                               extra_tags='alert-danger')
                return {}

        else:
            form = AccountAddonServiceModelForm(request.POST)
            if not (request.user.account.has_perm(
                    'billservice.add_accountaddonservice')):
                messages.error(request,
                               _(u'У вас нет прав на создание привязок '
                                 u'подключаемых услуг'),
                               extra_tags='alert-danger')
                return {}

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)

            messages.success(request,
                             _(u'Услуга добавлена.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(request,
                           _(u'Услуга не добавлена.'),
                           extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm(
                'billservice.view_addonservice')):
            messages.error(request,
                           _(u'У вас нет прав на просмотр  подключаемых услуг'),
                           extra_tags='alert-danger')
            return {}
        if id:
            accountaddonservice = AccountAddonService.objects.get(id=id)
            form = AccountAddonServiceModelForm(instance=accountaddonservice)
        elif account_id:
            account = Account.objects.get(id=account_id)
            form = AccountAddonServiceModelForm(initial={
                'account': account,
                'activated': datetime.datetime.now()
            })  # An unbound form
        elif subaccount_id:
            subaccount = SubAccount.objects.get(id=subaccount_id)
            account = subaccount.account
            form = AccountAddonServiceModelForm(
                initial={
                    'account': account,
                    'subaccount': subaccount,
                    'activated': datetime.datetime.now()
                })  # An unbound form

    return {
        'form': form,
        'status': False,
        'account': account,
        'accountaddonservice': accountaddonservice
    }


@ajax_request
@systemuser_required
def accountaddonservice_deactivate(request):
    if not (request.user.account.has_perm(
            'billservice.change_accountaddonservice')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на изменение подключаемых услуг '
                         u'аккаунта')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        model = AccountAddonService.objects.get(id=id)

        log('DELETE', request.user, model)

        model.deactivated = datetime.datetime.now()
        model.save()
        return {
            'status': True
        }
    else:
        return {
            'status': False,
            'message': 'AccountAddonService not found'
        }


@ajax_request
@systemuser_required
def accountaddonservice_delete(request):
    if not (request.user.account.has_perm(
            'billservice.delete_accountaddonservice')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление подключаемых услуг '
                         u'аккаунта')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        model = AccountAddonService.objects.get(id=id)

        log('DELETE', request.user, model)

        model.delete()
        return {
            'status': True
        }
    else:
        return {
            'status': False,
            'message': "AccountAddonService not found"
        }
