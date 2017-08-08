# -*- coding: utf-8 -*-

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from billservice.forms import BonusTransactionModelForm
from billservice.helpers import systemuser_required
from billservice.models import Transaction, Account
from ebscab.lib.decorators import render_to
from object_log.models import LogItem


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/bonus_transaction_edit.html')
def bonus_transaction_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        if id:
            model = Transaction.objects.get(id=id)
            form = BonusTransactionModelForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_transaction')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование  проводок'),
                    extra_tags='alert-danger')
                return {}
        else:
            form = BonusTransactionModelForm(request.POST)
            if not (request.user.account.has_perm(
                    'billservice.add_transaction')):
                messages.error(request,
                               _(u'У вас нет прав на создание проводок'),
                               extra_tags='alert-danger')

                return {}

        if form.is_valid():
            model = form.save(commit=False)
            model.systemuser = request.user.account
            model.is_bonus = True
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
        account_id = request.GET.get('account_id')
        if account_id:
            account = Account.objects.get(id=account_id)
            form = BonusTransactionModelForm(initial={'account': account})
        else:
            form = BonusTransactionModelForm()

    return {
        'form': form,
        'status': False
    }
