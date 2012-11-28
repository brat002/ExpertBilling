# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import DealerTable

from ebscab.billservice.forms import DealerForm, BankDataForm, DealerSelectForm
from ebscab.billservice.models import Dealer

log = LogItem.objects.log_action

@login_required
@render_to('ebsadmin/dealer_list.html')
def dealer(request):
    res = Dealer.objects.all()
    table = DealerTable(res)
    table_to_report = RequestConfig(request, paginate= False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/dealer_edit.html')
def dealer_edit(request):

    id = request.POST.get("id")

    item = None
    if request.method == 'POST': 
        id = request.POST.get("dealer-id")
        
        if id:
            item = Dealer.objects.get(id=id)
            form = DealerForm(request.POST, instance=item, prefix='dealer')
            bank_form = BankDataForm(request.POST, instance=item.bank, prefix='bank')
        else:
            form = DealerForm(request.POST, prefix='dealer')
            bank_form = BankDataForm(request.POST, prefix='bank')

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_dealer')):
                return {'status':False, 'message': u'У вас нет прав на редактирование дилеров'}
            
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_dealer')):
            return {'status':False, 'message': u'У вас нет прав на добавление дилеров'}

        
        if form.is_valid() and bank_form.is_valid():
 
            model = form.save(commit=False)
            bank_model = bank_form.save(commit=False)
            bank_model.save()
            model.bank=bank_model
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("dealer"))
        else:
            print form._errors
            return {'form':form,  'status': False,  'item': item, 'bank_form': bank_form} 
    else:
        id = request.GET.get("id")
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.dealer_view')):
                return {'status':True}

            item = Dealer.objects.get(id=id)
            form = DealerForm(instance=item, prefix='dealer')
            bank_form = BankDataForm(instance=item.bank, prefix='bank')
        else:
            form = DealerForm(preffix='dealer')
            bank_form = BankDataForm(prefix='bank')
   
    return { 'form':form, 'bank_form': bank_form,  'item': item} 

@login_required
@render_to('ebsadmin/dealerselect_window.html')
def dealer_select(request):
    
    form = DealerSelectForm()

    return { 'form':form} 

@ajax_request
@login_required
def dealer_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('nas.delete_nas')):
        return {'status':False, 'message': u'У вас нет прав на удаление серверов доступа'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Nas.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный сервер доступа найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Nas not found"} 
    
