# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem


from billservice.forms import OperatorForm
from billservice.models import Operator

log = LogItem.objects.log_action

    
@login_required
@render_to('ebsadmin/operator_edit.html')
def operator_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = Operator.objects.get(id=id)
            form = OperatorForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_operator')):
                return {'status':False, 'message': u'У вас нет прав на редактирование данных о провайдере'}
        else:
            form = OperatorForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_operator')):
            return {'status':False, 'message': u'У вас нет прав на добавление информации о провайдере'}

        if form.is_valid():
 
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("operator_edit"))
        else:
            print form._errors
            return {'form':form,  'status': False} 

    else:

        items = Operator.objects.all()
        if items:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.operator_view')):
                return {'status':True}

            item = items[0]
            
            form = OperatorForm(instance=item)
        else:
            form = OperatorForm()

    return { 'form':form, 'status': False} 

