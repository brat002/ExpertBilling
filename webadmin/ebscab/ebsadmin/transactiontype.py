# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2.config import RequestConfig
from object_log.models import LogItem

from tables import TransactionTypeTable

from billservice.forms import TransactionTypeForm
from billservice.models import TransactionType

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/transactiontype_list.html')
def transactiontype(request):
    res = TransactionType.objects.all()
    table = TransactionTypeTable(res)
    RequestConfig(request, paginate = False).configure(table)
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/transactiontype_edit.html')
def transactiontype_edit(request):

    id = request.GET.get("id")
    item = None
    if request.method == 'POST': 
        if id:
            item = TransactionType.objects.get(id=id)
            form = TransactionTypeForm(request.POST, instance=item)
        else:
             form = TransactionTypeForm(request.POST)
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_transactiontype')):
                return {'status':False, 'message': u'У вас нет прав на редактирование типов проводок'}
            
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_transactiontype')):
            return {'status':False, 'message': u'У вас нет прав на добавление типов транзакций'}

        
        if form.is_valid():
 
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("transactiontype"))
        else:

            return {'form':form,  'item': item} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.transactiontype_view')):
                return {'status':True}

            item = TransactionType.objects.get(id=id)
            form = TransactionTypeForm(instance=item)
        else:
            form = TransactionTypeForm()
   
    return { 'form':form, 'item': item} 

@ajax_request
@login_required
def transactiontype_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_transactiontype')):
        return {'status':False, 'message': u'У вас нет прав на удаление типов проводок'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TransactionType.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный тип не найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TransactionType not found"} 
    