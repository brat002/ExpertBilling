# -*- coding: utf-8 -*-

import datetime

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from billservice.forms import TransactionModelForm
from billservice.utils import systemuser_required
from billservice.models import Account, AccountTarif, TransactionType
from ebscab.utils.decorators import ajax_request, render_to
from object_log.models import LogItem

from ebsadmin.constants import MODEL_BY_TABLE


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/transaction_edit.html')
def transaction(request):
    account = None
    account_id = request.GET.get("account_id")
    id = request.POST.get("id")
    promise_type = TransactionType.objects.get(internal_name='PROMISE_PAYMENT')
    if request.method == 'POST':
        form = TransactionModelForm(request.POST)
        if id:
            if not (request.user.account.has_perm(
                    'billservice.edit_transaction')):
                messages.error(request,
                               _(u'У вас нет прав на изменение платежей'),
                               extra_tags='alert-danger')
                return {}
        else:
            if not (request.user.account.has_perm(
                    'billservice.add_transaction')):
                messages.error(request,
                               _(u'У вас нет прав на создание платежей'),
                               extra_tags='alert-danger')
                return {}

        form.fields["type"].queryset = request.user.account.transactiontype_set
        if form.is_valid():
            model = form.save(commit=False)
            model.systemuser = request.user.account
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)

            messages.success(request,
                             _(u'Операция выполнена.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True,
                'transaction': model
            }
        else:
            messages.success(request,
                             _(u'Ошибка при выполнении операции.'),
                             extra_tags='alert-danger')
            return {
                'form': form,
                'status': False,
                'promise_type': promise_type
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_transaction')):
            messages.error(request,
                           _(u'У вас нет прав на просмотр проводок'),
                           extra_tags='alert-danger')
            return {}
        if id:

            accounttariff = AccountTarif.objects.get(id=id)
            form = TransactionModelForm(instance=accounttariff)
        elif account_id:
            account = Account.objects.get(id=account_id)
        now = datetime.datetime.now()
        form = TransactionModelForm(initial={
            'account': account.id,
            'created': now,
            'type': (TransactionType.objects
                     .get(internal_name='MANUAL_TRANSACTION'))
        })  # An unbound form
        form.fields["type"].queryset = request.user.account.transactiontype_set
    return {
        'form': form,
        'status': False,
        'account': account,
        'promise_type': promise_type
    }


@ajax_request
@systemuser_required
def totaltransaction_delete(request):
    if not (request.user.account.has_perm('billservice.delete_transaction')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление проводок')
        }
    transactions = request.POST.getlist('transactions')
    if transactions:
        try:
            for item in transactions:
                table, tr_id = item.split('__')
                model = MODEL_BY_TABLE.get(table)
                item = model.objects.get(id=tr_id)

                log('DELETE', request.user, item)

                item.delete()
        except Exception, e:
            return {
                'status': False,
                'message': _(u"Указанные проводки не найдены %s") % str(e)
            }

        return {
            'status': True
        }
    else:
        return {
            'status': False,
            'message': _(u'Transaction not found')
        }
