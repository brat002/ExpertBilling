# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem
from django.template.loader import render_to_string



from billservice.forms import TimePeriodForm, TimePeriodNodeForm
from billservice.models import TimePeriod, TimePeriodNode
import datetime
import simplejson as json
from django.contrib import messages
log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/timeperiod_list.html')
def timeperiod(request):
    if  not (request.user.account.has_perm('billservice.view_timeperiod')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = []
    for tp in  TimePeriod.objects.all():
        s=[]

        for node in TimePeriodNode.objects.filter(time_period=tp):
            d=[]
            s.append({"title": node.name, 'key': 'NODE___%s' % node.id,})
        res.append({"title": tp.name, 'key': 'TP___%s' % tp.id, 'children':s, "isFolder":True})
            
    ojax = json.dumps(res, ensure_ascii=False)
    form = TimePeriodNodeForm
    return {"ojax": ojax, 'form':form} 
    
@ajax_request
@login_required
def timeperiod_edit(request):
    
    key = request.GET.get('key','')
    value = request.GET.get('value')
    v = key.split("___")
    id = None
    if len(v)==2:
        prefix, id = v
    if id:
        if  not (request.user.account.has_perm('billservice.change_timeperiod')):
            return {'status':False, 'message':u'У вас нет прав на изменение периодов'}
        item = TimePeriod.objects.get(id=id)
        form = TimePeriodForm({"name":value}, instance=item)
    else:
        if  not (request.user.account.has_perm('billservice.add_timeperiod')):
            return {'status':False, 'message':u'У вас нет прав на добавление периодов'}
        form = TimePeriodForm({'name': value})
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id': model.id}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@login_required
@ajax_request
def timeperiodnode_edit(request):

    key = request.GET.get('key','')
    v = key.split("___")
    id = None
    prefix=''
    if len(v)==2:
        prefix, id = v
        
    item = None
    if prefix=='TP':
        return {"status":True,"form":render_to_string('ebsadmin/timeperiodnode_edit.html', {'form': TimePeriodNodeForm(initial={'time_period': id})})}
    
    if request.method == 'POST': 
        id = request.POST.get('id','')

        if id:
            item = TimePeriodNode.objects.get(id=id)
            form = TimePeriodNodeForm(request.POST, instance=item)
        else:
            form = TimePeriodNodeForm(request.POST)
        if id:
            if  not (request.user.account.has_perm('billservice.change_timeperiodnode')):
                return {'status':False, 'message': u'У вас нет прав на редактирование подпериодов'}
        else:
            if  not (request.user.account.has_perm('billservice.add_timeperiodnode')):
                return {'status':False, 'message': u'У вас нет прав на добавление подпериодов'}

        if form.is_valid():
 
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 

            return {"status":True, "name": model.name, "id":model.id, "form":render_to_string('ebsadmin/timeperiodnode_edit.html', {'form': TimePeriodNodeForm()})}
        else:

            return {"status":False,"form":render_to_string('ebsadmin/timeperiodnode_edit.html', {'form': form})} 
    else:
        if  not (request.user.account.has_perm('billservice.view_timeperiodnode')):
            return {'status':True}
        key = request.GET.get('key','')
        v = key.split("___")
        id = None
        if len(v)==2:
            prefix, id = v

        if id:


            item = TimePeriodNode.objects.get(id=id)
            form = TimePeriodNodeForm(initial={"time_end": item.time_start+datetime.timedelta(seconds=item.length)},instance=item)
        else:
            form = TimePeriodNodeForm()
   
    return {"status":True,"form":render_to_string('ebsadmin/timeperiodnode_edit.html', {'form': form})}


@ajax_request
@login_required
def timeperiod_delete(request):

    key = request.GET.get('key','')
    v = key.split("___")
    id = None
    if len(v)==2:
        prefix, id = v
    if not id:
        return {"status": False, "message": "Object not found"}
    
    if prefix=='TP':
        if  not (request.user.account.has_perm('billservice.delete_timeperiod')):
            return {'status':False, 'message':u'У вас нет прав на удаление периодов'}
    
        model = TimePeriod.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}

    if prefix=='NODE':
        if  not (request.user.account.has_perm('billservice.delete_timeperiodnode')):
            return {'status':False, 'message':u'У вас нет прав на удаление подпериодов'}
    
        model = TimePeriodNode.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}

    
    
    