# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem
from django.db.models import Sum
from ebsadmin.tables import PaymentTable
from billservice.forms import PaymentSearchForm, PaymentForm
from getpaid.models import Payment
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required
from django.utils.translation import ugettext_lazy as _


@systemuser_required
@render_to('ebsadmin/payment_list.html')
def payment(request):
        
    if  not (request.user.account.has_perm('billservice.view_transaction')):
        messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')


    if request.GET: 
        data = request.GET

        #pageitems = 100
        form = PaymentSearchForm(data)
        if form.is_valid():
            
            accounts = form.cleaned_data.get('accounts')
            payment = form.cleaned_data.get('payment')
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            paid_start = form.cleaned_data.get('paid_start')
            paid_end = form.cleaned_data.get('paid_end')
            status = form.cleaned_data.get('status')
            
            res = Payment.objects.all()
            
            if payment:
                res = res.filter(id=payment)
                
            if accounts:
                res = res.filter(account_id__in=accounts)

            if date_start:
                res = res.filter(created_on__gte=date_start)

            if date_end:
                res = res.filter(created_on__lte=date_end)
                

            if paid_start:
                res = res.filter(paid_on__gte=paid_start)

            if paid_end:
                res = res.filter(paid_on__lte=paid_end)
                
            if status:
                res = res.filter(status=status)
                
            table = PaymentTable(res)
            table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            
            return {"table": table,  'form':form, 'resultTab':True}   
    
        else:
            return {'status':False, 'form':form}
    else:
        form = PaymentSearchForm()
        return { 'form':form}   


@systemuser_required
@render_to('ebsadmin/payment_edit.html')
def payment_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = Payment.objects.get(id=id)
            form = PaymentForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_transaction')):
                messages.error(request, _(u'У вас нет прав на редактирование платежей'), extra_tags='alert-danger')
                return {}
        else:
            form = PaymentForm(request.POST) 
            if  not (request.user.account.has_perm('billservice.add_transaction')):
                messages.error(request, _(u'У вас нет прав на создание платежей'), extra_tags='alert-danger')
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
        if  not (request.user.account.has_perm('billservice.view_transaction')):
            messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
            return {}
        if id:

            item = Payment.objects.get(id=id)
            
            form = PaymentForm(instance=item)
        else:
            form = PaymentForm()

    return { 'form':form, 'status': False} 

@ajax_request
@systemuser_required
def payment_delete(request):
    if  not ( request.user.account.has_perm('billservice.delete_transaction')):
        return {'status':False, 'message': _(u'У вас нет прав на удаление платежей')}
    
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Payment.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": _(u"Указанный платёж не найден %s") % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Payment not found"} 
    