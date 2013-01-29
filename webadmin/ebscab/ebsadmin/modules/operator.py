# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem


from billservice.forms import OperatorForm
from billservice.models import Operator
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required
    
@systemuser_required
@render_to('ebsadmin/operator_edit.html')
def operator_edit(request):

    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = Operator.objects.get(id=id)
            form = OperatorForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_operator')):
                messages.error(request, u'У вас нет прав на редактирование данных о провайдере', extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = OperatorForm(request.POST) 
            if  not (request.user.account.has_perm('billservice.add_operator')):
                messages.error(request, u'У вас нет прав на создание данных о провайдере', extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid():
 
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("operator_edit"))
        else:
            print form._errors
            return {'form':form,  'status': False} 

    else:
        if  not (request.user.account.has_perm('billservice.view_operator')):
            messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        
        items = Operator.objects.all()
        if items:


            item = items[0]
            
            form = OperatorForm(instance=item)
        else:
            form = OperatorForm()

    return { 'form':form, 'status': False, 'item': item} 

