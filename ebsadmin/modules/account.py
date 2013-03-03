# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2.config import RequestConfig
from object_log.models import LogItem

from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response

import datetime
from billservice.forms import AccountManagementForm, AccountTariffForm, BatchAccountTariffForm, SuspendedPeriodBatchForm
from billservice.models import Account, AccountTarif, SuspendedPeriod

log = LogItem.objects.log_action
from django.contrib import messages
from billservice.helpers import systemuser_required
import subprocess


@ajax_request
@systemuser_required
def account_management_status(request):
    if  not (request.user.account.has_perm('billservice.change_account')):
        return {'status':False, 'message': u'У вас нет прав на изменение аккаунтов'}
    status = request.GET.get('status')
    if request.method == 'POST' and status: 
        form = AccountManagementForm(request.POST) 
        print request.POST
        if form.is_valid():
            accounts = form.cleaned_data.get('accounts')
            if accounts:
                accounts.update(status=status)
 
            messages.success(request, u'Статус успешно изменён.', extra_tags='alert-success')
            return { 'status': True} 

        messages.error(request, u'Ошибка при изменении статуса.', extra_tags='alert-danger')
        return { 'status': False} 
    return {}
    
    
@systemuser_required
@render_to('ebsadmin/accounttarif_edit.html')
def accounttarif_edit(request):

    account = None
    account_id = request.GET.get("account_id")
    id = request.POST.get("id")
    
    if request.method == 'POST': 

        form = AccountTariffForm(request.POST) 
        if id:
            if  not (request.user.account.has_perm('billservice.change_accounttarif')):
                messages.error(request, u'У вас нет прав на изменение тарифных планов у аккаунта', extra_tags='alert-danger')
                return {}
            
        else:
            if  not (request.user.account.has_perm('billservice.add_accounttarif')):
                messages.error(request, u'У вас нет прав на создание тарифных планов у аккаунта', extra_tags='alert-danger')
                return {}
        
        
        if form.is_valid(): 
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        if  not (request.user.account.has_perm('billservice.add_accounttarif')):
            messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
            return {}

        if id:
            
            accounttariff = AccountTarif.objects.get(id=id)
            form = AccountTariffForm(instance=accounttariff)
        elif account_id:
            
            account= Account.objects.get(id=account_id)
        form = AccountTariffForm(initial={'account': account.id, 'datetime': datetime.datetime.now()}) # An unbound form

    return { 'form':form, 'status': False, 'account':account} 


@systemuser_required
@render_to('ebsadmin/accounttarif_batch_edit.html')
def account_management_accounttariff(request):

    account = None
    account_id = request.GET.get("account_id")
    id = request.POST.get("id")

    if request.method == 'POST': 
        form = BatchAccountTariffForm(request.POST) 

        if  not (request.user.account.has_perm('billservice.add_accounttarif')):
            messages.error(request, u'У вас нет прав на создание тарифных планов у аккаунта', extra_tags='alert-danger')
            return {}

        if form.is_valid(): 
            tariff = form.cleaned_data.get('tariff')
            dt = form.cleaned_data.get('datetime')
            for acc in form.cleaned_data.get('accounts'):
                acct = AccountTarif()
                acct.account = acc
                acct.tarif = tariff
                acct.datetime = dt
                acct.save() 
                log('CREATE', request.user, acct)
            return {'form':form,  'status': True} 
        else:
            print form._errors
            return {'form':form,  'status': False} 
    else:

        if  not (request.user.account.has_perm('billservice.add_accounttarif')):
            messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
            return {}

        m_form = AccountManagementForm(request.GET) 
        form = None
        if m_form.is_valid():
            form = BatchAccountTariffForm(initial={'accounts': m_form.cleaned_data.get('accounts', []), 'datetime': datetime.datetime.now()}) # An unbound form

    return { 'form':form, 'status': False, 'account':account} 

@systemuser_required
@render_to('ebsadmin/suspendedperiod_batch_edit.html')
def account_management_suspendedperiod(request):
    

    if request.method == 'POST': 
        print request.POST
        form = SuspendedPeriodBatchForm(request.POST) 

        if  not (request.user.account.has_perm('billservice.add_suspendedperiod')):
            messages.error(request, u'У вас нет прав на создание периодов без списаний', extra_tags='alert-danger')
            return {}
        
        
        if form.is_valid(): 
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            for acc in form.cleaned_data.get('accounts'):
                print acc
                item = SuspendedPeriod()
                item.start_date = start_date
                item.end_date = end_date
                item.account = acc
                item.save() 
                log('CREATE', request.user, item)
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:

        if  not (request.user.account.has_perm('billservice.add_suspendedperiod')):
            messages.error(request, u'У вас нет прав на создание периодов без списаний', extra_tags='alert-danger')
            return {}

        m_form = AccountManagementForm(request.GET) 
        form = None
        if m_form.is_valid():
            form = SuspendedPeriodBatchForm(initial={'accounts': m_form.cleaned_data.get('accounts', [])}) # An unbound form


    return { 'form':form, 'status': False} 


@systemuser_required
@ajax_request
def account_management_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_account')):
        return {'status':False, 'message': u'У вас нет прав на удаление аккаунтов'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    m_form = AccountManagementForm(request.GET) 

    if m_form.is_valid():
        for acc in m_form.cleaned_data.get('accounts'):

            log('DELETE', request.user, acc)
            acc.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Account not found"} 
    
@systemuser_required
@ajax_request
def account_management_restore(request):
    if  not (request.user.account.has_perm('billservice.edit_account')):
        return {'status':False, 'message': u'У вас нет прав редактирование аккаунтов'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    m_form = AccountManagementForm(request.GET) 

    if m_form.is_valid():
        for acc in m_form.cleaned_data.get('accounts'):
            acc.deleted=None
            acc.save()
            log('EDIT', request.user, acc)
        return {"status": True}
    else:
        return {"status": False, "message": "Account not found"} 
    
@systemuser_required
@render_to('ebsadmin/ping_check.html')
def tools_ping(request):
    

    if request.GET: 

        if  not (request.user.account.has_perm('billservice.view_account')):
            messages.error(request, u'У вас нет прав на просмотр данных аккаунта', extra_tags='alert-danger')
            return {}
        
        ip = request.GET.get('ip')
        if ip:
            cmd = ['ping', '-c', '3', ip]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output = ''
            for line in p.stdout:
                output+= line
            p.wait()
            print p.returncode
            return {'output':output,  'status': True} 


    return {'status': False} 

    