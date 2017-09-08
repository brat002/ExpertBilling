# -*- coding: utf-8 -*-

import datetime

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from billservice.forms import SuspendedPeriodModelForm
from billservice.utils import systemuser_required
from billservice.models import Account, SuspendedPeriod
from ebscab.utils.decorators import ajax_request, render_to
from object_log.models import LogItem


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/suspendedperiod/edit.html')
def suspendedperiod(request):
    account = None
    account_id = request.GET.get("account_id")
    id = request.POST.get("id")

    if request.method == 'POST':
        form = SuspendedPeriodModelForm(request.POST)
        if id:
            if not (request.user.account.has_perm(
                    'billservice.change_suspendedperiod')):
                messages.error(request,
                               _(u'У вас нет прав на редактирование периодов '
                                 u'без списаний'),
                               extra_tags='alert-danger')
                return {}
        else:
            if not (request.user.account.has_perm(
                    'billservice.add_suspendedperiod')):
                messages.error(request,
                               _(u'У вас нет прав на создание периодов без списаний'),
                               extra_tags='alert-danger')
                return {}

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
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
        if not (request.user.account.has_perm(
                'billservice.view_accounthardware')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел'),
                           extra_tags='alert-danger')
            return {}
        if id:

            accounttariff = SuspendedPeriod.objects.get(id=id)
            form = SuspendedPeriodModelForm(instance=accounttariff)
        elif account_id:

            account = Account.objects.get(id=account_id)
            form = SuspendedPeriodModelForm(initial={
                'account': account.id,
                'datetime': datetime.datetime.now()
            })  # An unbound form

    return {
        'form': form,
        'status': False,
        'account': account
    }


@ajax_request
@systemuser_required
def suspendedperiod_delete(request):
    if not (request.user.account.has_perm(
            'billservice.delete_suspendedperiod')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление периода простоя')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = SuspendedPeriod.objects.get(id=id)
        except Exception, e:
            return {
                'status': False,
                'message': _(u"Указанный период не найден %s") % str(e)
            }

        log('DELETE', request.user, item)

        item.delete()
        return {
            'status': True
        }
    else:
        return {
            'status': False,
            'message': 'SuspendedPeriod not found'
        }
