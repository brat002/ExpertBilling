# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem


from billservice.forms import BonusTransactionModelForm
from billservice.models import Transaction, Account
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required
from django.utils.translation import ugettext_lazy as _


    
@systemuser_required
@render_to('ebsadmin/bonus_transaction_edit.html')
def bonus_transaction_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = Transaction.objects.get(id=id)
            form = BonusTransactionModelForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_transaction')):
                messages.error(request, _(u'У вас нет прав на редактирование  проводок'), extra_tags='alert-danger')
                return {}
        else:
            form = BonusTransactionModelForm(request.POST) 
            if  not (request.user.account.has_perm('billservice.add_transaction')):
                messages.error(request, _(u'У вас нет прав на создание проводок'), extra_tags='alert-danger')
                return {}


        if form.is_valid():
            model = form.save(commit=False)
            model.systemuser = request.user.account
            model.is_bonus = True
            model.save()
            
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        account_id = request.GET.get('account_id')
        if account_id:
            account = Account.objects.get(id=account_id)
            form = BonusTransactionModelForm(initial = {'account': account})
        else:
            form = BonusTransactionModelForm()

    return { 'form':form, 'status': False} 


    