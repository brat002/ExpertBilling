# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import TariffTable, PeriodicalServiceTable, TrafficTransmitNodesTable, PrepaidTrafficTable,TimeSpeedTable, OneTimeServiceTable, RadiusTrafficNodeTable, TrafficLimitTable,  TimeAccessNodeTable, AddonServiceTarifTable

from ebscab.billservice.forms import TariffForm, PeriodicalServiceForm, TrafficTransmitServiceForm, PrepaidTrafficForm, TrafficTransmitNodeForm, AccessParametersForm, TimeSpeedForm, OneTimeServiceForm, RadiusTrafficForm, RadiusTrafficNodeForm, TrafficLimitForm, SpeedLimitForm, TimeAccessServiceForm, TimeAccessNodeForm, AddonServiceTarifForm
from ebscab.billservice.models import Tariff, PeriodicalService, TrafficTransmitService, TrafficTransmitNodes, PrepaidTraffic, AccessParameters, TimeSpeed, OneTimeService, RadiusTraffic, RadiusTrafficNode, TrafficLimit, SpeedLimit, TimeAccessService, TimeAccessNode, AddonServiceTarif
from django.contrib import messages
from django.contrib import messages

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/tariff_list.html')
def tariff(request):
    if  not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    
    res = Tariff.objects.all()
    table = TariffTable(res)
    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else {"per_page": request.COOKIES.get("ebs_per_page")}).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/tariff_edit_general.html')
def tariff_edit(request):
    item = None
    tariff = None
    if request.method == 'POST': 
        id = request.POST.get("id")
        if id:
            tariff = Tariff.objects.get(id=id)
            form = TariffForm(request.POST, instance=tariff)
            accessparameters_form = AccessParametersForm(request.POST, instance=tariff.access_parameters, prefix="ap")
        else:
            form = TariffForm(request.POST)
            accessparameters_form = AccessParametersForm(request.POST, prefix="ap")

        if id:
            if  not (request.user.account.has_perm('billservice.change_tariff')):
                messages.error(request, u'У вас нет прав на редактирование тарифных планов', extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

            
        else:
            if  not (request.user.account.has_perm('billservice.add_tariff')):
                messages.error(request, u'У вас нет прав на создание тарифных планов', extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)


        
        if form.is_valid() and accessparameters_form.is_valid():
            ap = accessparameters_form.save(commit=False)
            ap.save()
            model = form.save(commit=False)
            model.access_parameters = ap
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, u'Тарифный план сохранён.', extra_tags='alert-success')
            return HttpResponseRedirect("%s?id=%s" % (reverse("tariff_edit"), model.id))
        else:
            messages.error(request, u'Во время сохранения тарифного плана возникли ошибки.', extra_tags='alert-danger')
            return {'form':form, "access_parameters": accessparameters_form, 'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.account.has_perm('billservice.view_tariff')):
                return {'status':True}

            tariff = Tariff.objects.get(id=id)
            form = TariffForm( instance=tariff)
            accessparameters_form = AccessParametersForm(instance=tariff.access_parameters, prefix="ap")
        else:
            form = TariffForm()
            accessparameters_form = AccessParametersForm( prefix="ap")
   
    return { 'form':form, 'tariff': tariff,  "access_parameters": accessparameters_form, 'active': 'general'} 

@login_required
@render_to('ebsadmin/tariff_periodicalservice.html')
def tariff_periodicalservice(request):

    
    if  not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
        
    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    items = PeriodicalService.objects.filter(tarif__id=tariff_id)
    tariff = Tariff.objects.get(id=tariff_id)
    if items:


        #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
        
        #formset = PeriodicalServiceFormSet(queryset=items)
        table = PeriodicalServiceTable(items)
        RequestConfig(request, paginate = False).configure(table)
    else:
        form = PeriodicalServiceForm(initial={'tarif':tariff_id})
        table = PeriodicalServiceTable({})
   
    return { 'formset':None, 'table':table, 'tariff':tariff, 'active': 'ps'} 

@login_required
@render_to('ebsadmin/tariff_addonservice.html')
def tariff_addonservicetariff(request):
    if  not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    items = AddonServiceTarif.objects.filter(tarif__id=tariff_id)
    tariff = Tariff.objects.get(id=tariff_id)
    if items:
        #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
        
        #formset = PeriodicalServiceFormSet(queryset=items)
        table = AddonServiceTarifTable(items)
        RequestConfig(request, paginate = False).configure(table)
    else:
        form = AddonServiceTarifForm(initial={'tarif':tariff_id})
        table = AddonServiceTarifTable({})
   
    return { 'table':table, 'tariff':tariff, 'active': 'addst'} 

@login_required
@render_to('ebsadmin/tariff_addonservicetariff_edit.html')
def tariff_addonservicetariff_edit(request):

    
    item = None
    if request.method == 'POST': 
        if  not (request.user.account.has_perm('billservice.change_tariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'}
        id = request.POST.get("id")
        if id:
            model = AddonServiceTarif.objects.get(id=id)
            form = AddonServiceTarifForm(request.POST, instance=model) 
        else:

            form = AddonServiceTarifForm(request.POST) 

        if form.is_valid():

            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, u'Подключаемая услуга успешно добавлена в тарифный план.', extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:
            messages.error(request, u'Ошибка при сохранении.', extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        
        if id:
            if  not (request.user.account.has_perm('billservice.view_tariff')):
                messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
                return {}

            item = AddonServiceTarif.objects.get(id=id)
            form = AddonServiceTarifForm(instance=item)
        else:
            form = AddonServiceTarifForm(initial={'tarif':tariff_id})
   
    return { 'item':item, 'form':form} 

@login_required
@render_to('ebsadmin/tariff_trafficlimit.html')
def tariff_trafficlimit(request):

    if  not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    items = TrafficLimit.objects.filter(tarif__id=tariff_id)
    tariff = Tariff.objects.get(id=tariff_id)
    if items:


        table = TrafficLimitTable(items)
        RequestConfig(request, paginate = False).configure(table)
    else:
        table =TrafficLimitTable({})
   
    return { 'formset':None, 'table':table, 'tariff':tariff, 'active': 'trafficlimit'} 

@login_required
@render_to('ebsadmin/trafficlimit_edit.html')
def tariff_trafficlimit_edit(request):

    

    item = None
    if request.method == 'POST': 
        if  not (request.user.account.has_perm('billservice.change_tariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'}
        id = request.POST.get("id")
        if id:
            
            model = TrafficLimit.objects.get(id=id)
            form = TrafficLimitForm(request.POST, instance=model) 
        else:
            
            form = TrafficLimitForm(request.POST) 


        
        if form.is_valid():
            
            model = form.save(commit=False)
            model.save()
            
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, u'Лимит трафика успешно сохранён.', extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:
            messages.error(request, u'При сохранении лимита трафика возникли ошибки.', extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        
        if id:
            if  not (request.user.account.has_perm('billservice.view_tariff')):
                messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
                return {}

            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
            item = TrafficLimit.objects.get(id=id)
            form = TrafficLimitForm(instance=item)
        else:
            form = TrafficLimitForm(initial={'tarif':tariff_id})
   
    return { 'formset':None, 'form':form} 

@login_required
@render_to('ebsadmin/tariff_onetimeservice.html')
def tariff_onetimeservice(request):

    if  not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
        
    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    if tariff_id:


        #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
        items = OneTimeService.objects.filter(tarif__id=tariff_id)
        #formset = PeriodicalServiceFormSet(queryset=items)
        table = OneTimeServiceTable(items)
        RequestConfig(request, paginate = False).configure(table)
    else:
        form = OneTimeServiceForm(initial={'tarif':tariff_id})
   
    return { 'formset':None, 'table':table, 'tariff':tariff, 'active': 'ots'} 

@login_required
@render_to('ebsadmin/tariff_traffictransmitservice.html')
def tariff_traffictransmitservice(request):

    
    if  not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    
    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    prepaidtable = None
    
    if tariff_id:

        if request.method == 'POST': 
            if  not (request.user.account.has_perm('billservice.change_tariff')):
                return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'}
            id = request.POST.get("id")
            if id:
                print 11
                model = TrafficTransmitService.objects.get(id=id)
                form = TrafficTransmitServiceForm(request.POST, instance=model) 
            else:
                print 22
                form = TrafficTransmitServiceForm(request.POST) 

    
            print 2
            if form.is_valid():
                print 3
                model = form.save(commit=False)
                model.save()
                item = model
                tariff.traffic_transmit_service=model
                tariff.save()
                log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
                messages.success(request, u'Услуга тарификации трафика успешно сохранена.', extra_tags='alert-success')
                return HttpResponseRedirect("%s?tariff_id=%s" % (reverse("tariff_traffictransmitservice"), tariff.id))
            else:
                messages.error(request, u'При сохранении услуги тарификации трафика произошла ошибка.', extra_tags='alert-danger')
        else:
            
            item = tariff.traffic_transmit_service
            
        #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
        
        form = TrafficTransmitServiceForm(instance=item)
        #formset = PeriodicalServiceFormSet(queryset=items)
        items =TrafficTransmitNodes.objects.filter(traffic_transmit_service=item)
        table = TrafficTransmitNodesTable(items)
        RequestConfig(request, paginate = False).configure(table)
        prepaidtable = PrepaidTrafficTable(PrepaidTraffic.objects.filter(traffic_transmit_service=item)) 
        RequestConfig(request, paginate = False).configure(prepaidtable)
    else:
        form = TrafficTransmitServiceForm()
   
    return { 'formset':None, 'table':table, 'tariff': tariff,  'item':item, 'form':form, 'prepaidtraffic_table':prepaidtable, 'active': 'tts'} 

@login_required
@render_to('ebsadmin/tariff_radiustraffic.html')
def tariff_radiustraffic(request):

    if  not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    prepaidtable = None
    

    if tariff_id:

        if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
            return {'status':True}

        if request.method == 'POST':
            if  not (request.user.account.has_perm('billservice.change_tariff')):
                return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'}
            id = request.POST.get("id")
            if id:

                
                model = RadiusTraffic.objects.get(id=id)
                form = RadiusTrafficForm(request.POST, instance=model) 

            else:

                form = RadiusTrafficForm(request.POST) 

    

            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                item = model
                log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
                tariff.radius_traffic_transmit_service = item
                tariff.save()
                messages.success(request, u'Услуга RADIUS тарификации трафика успешно сохранена.', extra_tags='alert-success')
            else:
                item = model
                messages.error(request, u'При сохранении услуги RADIUS тарификации трафика произошла ошибка.', extra_tags='alert-danger')
        else:
            item = tariff.radius_traffic_transmit_service
            form = RadiusTrafficForm(instance=item)
            
        #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
        
        #formset = PeriodicalServiceFormSet(queryset=items)
        items =RadiusTrafficNode.objects.filter(radiustraffic=item)
        form = RadiusTrafficForm(instance=item)
        table = RadiusTrafficNodeTable(items)
        RequestConfig(request, paginate = False).configure(table)

    else:
        form = RadiusTrafficForm()
   
    return { 'formset':None, 'table':table, 'tariff': tariff,  'item':item, 'form':form,  'active': 'rts'} 

@login_required
@render_to('ebsadmin/tariff_timeaccessservice.html')
def tariff_timeaccessservice(request):

    if  not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    

    if tariff_id:


        if request.method == 'POST':
            if  not (request.user.account.has_perm('billservice.change_tariff')):
                return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
            id = request.POST.get("id")
            if id:

                
                model = TimeAccessService.objects.get(id=id)
                form = TimeAccessServiceForm(request.POST, instance=model) 

            else:

                form = TimeAccessServiceForm(request.POST) 

    

            if form.is_valid():

                model = form.save(commit=False)
                model.save()
                item = model
                log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
                tariff.time_access_service = item
                tariff.save()
                messages.success(request, u'Услуга RADIUS тарификации времени успешно сохранена.', extra_tags='alert-success')
            else:
                item = model
                messages.error(request, u'При сохранении услуги RADIUS тарификации времени произошла ошибка.', extra_tags='alert-danger')
        else:

            item = tariff.time_access_service
            form = TimeAccessServiceForm(instance=item)
            

        items =TimeAccessNode.objects.filter(time_access_service=item)
        #form = TimeAccessServiceForm(instance=item)
        table = TimeAccessNodeTable(items)
        RequestConfig(request, paginate = False).configure(table)

    else:
        form = RadiusTrafficForm()
   
    return { 'table':table, 'tariff': tariff,  'item':item, 'form':form,  'active': 'timeaccess'} 

@login_required
@render_to('ebsadmin/tariff_timeaccessnode_edit.html')
def tariff_timeaccessnode_edit(request):



    item = None
    if request.method == 'POST': 
        id = request.POST.get("id")
        if  not (request.user.account.has_perm('billservice.change_tariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
        
        if id:
            model = TimeAccessNode.objects.get(id=id)
            form = TimeAccessNodeForm(request.POST, instance=model) 
        else:
            form = TimeAccessNodeForm(request.POST) 


        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            item = model
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, u'Правило тарификации времени успешно сохранено.', extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:
            messages.error(request, u'При сохранении правила тарификации времени произошла ошибка.', extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        if  not (request.user.account.has_perm('billservice.view_tariff')):
            messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
            return {}
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        time_access_service_id = request.GET.get("time_access_service_id")
        tts = None
        if time_access_service_id:
            tas = TimeAccessService.objects.get(id=time_access_service_id)
        if id:


            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
            item = TimeAccessNode.objects.get(id=id)
            form = TimeAccessNodeForm(instance=item)
        elif tts:
            form = TimeAccessNodeForm(initial={"time_access_service": tas})
            
        else:
            form = TimeAccessNodeForm(initial={"time_access_service": tas})

    return { 'item':item, 'form':form} 

@login_required
@render_to('ebsadmin/tariff_accessparameters.html')
def tariff_accessparameters(request):



    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")

    tariff = Tariff.objects.get(id=tariff_id)
    prepaidtable = None
    
    if tariff:

        if request.method == 'POST': 
            id = request.POST.get("id")
            if tariff.access_parameters:
                model = tariff.access_parameters
                form = AccessParametersForm(request.POST, instance=model) 

            else:
                form = AccessParametersForm(request.POST) 

    
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                
                item = model
                log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
                messages.success(request, u'Параметры доступа успешно сохранены.', extra_tags='alert-success')
                return HttpResponseRedirect("%s?tariff_id=%s" % (reverse("tariff_accessparameters"), tariff.id))
            else:
                messages.error(request, u'При сохранении параметров доступа произошла ошибка.', extra_tags='alert-danger')
        else:
            item = tariff.access_parameters

        if  not (request.user.account.has_perm('billservice.view_tariff')):
            messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
        
        form = AccessParametersForm(instance=item)
        #formset = PeriodicalServiceFormSet(queryset=items)
        items =TimeSpeed.objects.filter(access_parameters=item)
        table = TimeSpeedTable(items)
        RequestConfig(request, paginate = False).configure(table)

    else:
        if  not (request.user.account.has_perm('billservice.view_tariff')):
            messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if  not (request.user.account.has_perm('billservice.change_tariff')):
            messages.error(request, u'У вас нет прав на редактирование тарифного плана', extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')

        form = AccessParametersForm()
   
    return { 'formset':None, 'table':table, 'tariff': tariff,  'item':item, 'form':form, 'active': 'accessparameters'} 


@login_required
@render_to('ebsadmin/tariff_timespeed_edit.html')
def tariff_timespeed_edit(request):

    

    item = None
    if request.method == 'POST': 

        if  not (request.user.account.has_perm('billservice.change_tariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
        id = request.POST.get("id")
        if id:

            model = TimeSpeed.objects.get(id=id)
            form = TimeSpeedForm(request.POST, instance=model) 

        else:

            form = TimeSpeedForm(request.POST) 



        if form.is_valid():

            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, u'Настройки скорости успешно сохранены.', extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:   
            messages.error(request, u'При сохранении параметров скорости произошла ошибка.', extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        if  not (request.user.account.has_perm('billservice.view_tariff')):
            return {'status':False}
        id = request.GET.get("id")
        access_parameters = request.GET.get("access_parameters")
        ap = AccessParameters.objects.get(id=access_parameters)
        if id:
            item = TimeSpeed.objects.get(id=id)
            form = TimeSpeedForm(instance=item)
        else:
            form = TimeSpeedForm({"access_parameters":ap})
   
    return { 'formset':None, 'form':form} 

@login_required
@render_to('ebsadmin/tariff_prepaidtraffic_edit.html')
def tariff_prepaidtraffic_edit(request):

    

    item = None
    if request.method == 'POST': 
        if  not (request.user.account.has_perm('billservice.change_tariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
        id = request.POST.get("id")
        if id:
            model = PrepaidTraffic.objects.get(id=id)
            form = PrepaidTrafficForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_prepaidtraffic')):
                return {'status':False, 'message': u'У вас нет прав на редактирование правил начисления предоплаченного трафика'}
        else:
            form = PrepaidTrafficForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_prepaidtraffic')):
            return {'status':False, 'message': u'У вас нет прав на добавление правил начисления предоплаченного трафика'}


        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model)
            messages.success(request, u'Настройки предоплаченного трафика успешно сохранены.', extra_tags='alert-success') 
            return {'form':form,  'status': True} 
        else:
            messages.error(request, u'При сохранении настроек предоплаченного трафика произошла ошибка.', extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        if  not (request.user.account.has_perm('billservice.view_tariff')):
            return {'status':False}
        
        if id:
            item = PrepaidTraffic.objects.get(id=id)
            form = PrepaidTrafficForm(instance=item)
        else:
            tariff_id = request.GET.get("tariff_id")
            tariff = Tariff.objects.get(id=tariff_id)
            form = PrepaidTrafficForm(initial={'traffic_transmit_service': tariff.traffic_transmit_service})
   
    return { 'formset':None, 'form':form} 

@login_required
@render_to('ebsadmin/tariff_traffictransmitnode_edit.html')
def tariff_traffictransmitnode_edit(request):

    

    item = None
    if request.method == 'POST': 
        if  not (request.user.account.has_perm('billservice.change_tariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
        id = request.POST.get("id")

        
        if id:

            model = TrafficTransmitNodes.objects.get(id=id)
            form = TrafficTransmitNodeForm(request.POST, instance=model) 

        else:

            form = TrafficTransmitNodeForm(request.POST) 


   
        if form.is_valid():
         
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, u'Настройки NetFlow тарификации трафика успешно сохранены.', extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:
            messages.error(request, u'При сохранении настроек NetFlow тарификации трафика произошла ошибка.', extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        if  not (request.user.account.has_perm('billservice.view_tariff')):
            return {'status':False}
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        tts = None
        if tariff_id:
            tts = Tariff.objects.get(id=tariff_id).traffic_transmit_service
        if id:


            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
            item = TrafficTransmitNodes.objects.get(id=id)
            form = TrafficTransmitNodeForm(instance=item)
        elif tts:
            form = TrafficTransmitNodeForm(initial={"traffic_transmit_service": tts})
            
        else:
            form = TrafficTransmitNodeForm(initial={"traffic_transmit_service": tts})
   
    return { 'formset':None, 'form':form} 

@login_required
@render_to('ebsadmin/tariff_radiustrafficnode_edit.html')
def tariff_radiustrafficnode_edit(request):

    

    item = None
    if request.method == 'POST': 
        if  not (request.user.account.has_perm('billservice.change_tariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
        id = request.POST.get("id")

        
        if id:

            model = RadiusTrafficNode.objects.get(id=id)
            form = RadiusTrafficNodeForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_radiustrafficnode')):
                return {'status':False, 'message': u'У вас нет прав на редактирование правил тарификации RADIUS трафика'}
        else:
            form = RadiusTrafficNodeForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_radiustrafficnode')):
            return {'status':False, 'message': u'У вас нет прав на добавление правил тарификации RADIUS трафика'}


        if form.is_valid():

            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, u'Правило RADIUS тарификации трафика успешно сохранены.', extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:
            messages.error(request, u'При сохранении настроек RADIUS тарификации трафика произошла ошибка.', extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        if  not (request.user.account.has_perm('billservice.view_tariff')):
            return {'status':False}
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        radius_traffic_id = request.GET.get("radius_traffic_id")
        tts = None
        if radius_traffic_id:
            tts = RadiusTraffic.objects.get(id=radius_traffic_id)
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
                return {'status':True}

            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
            item = RadiusTrafficNode.objects.get(id=id)
            form = RadiusTrafficNodeForm(instance=item)
        elif tts:
            form = RadiusTrafficNodeForm(initial={"radiustraffic": tts})
            
        else:
            form = RadiusTrafficNodeForm(initial={"radiustraffic": tts})
        print "tts", tts, tariff_id
    return { 'formset':None, 'form':form} 

@login_required
@render_to('ebsadmin/periodicalservice_edit.html')
def tariff_periodicalservice_edit(request):

    

    item = None
    if request.method == 'POST': 
        if  not (request.user.account.has_perm('billservice.change_tariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
        id = request.POST.get("id")
        if id:

            model = PeriodicalService.objects.get(id=id)
            form = PeriodicalServiceForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_periodicalservice')):
                return {'status':False, 'message': u'У вас нет прав на редактирование периодических услуг'}
        else:

            form = PeriodicalServiceForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_periodicalservice')):
            return {'status':False, 'message': u'У вас нет прав на добавление периодических услуг'}


        if form.is_valid():

            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, u'Периодическая услуга сохранена.', extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:
            messages.error(request, u'При сохранении периодической услуги произошла ошибка.', extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        if  not (request.user.account.has_perm('billservice.view_tariff')):
            return {'status':False}
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        
        if id:

            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
            item = PeriodicalService.objects.get(id=id)
            form = PeriodicalServiceForm(instance=item)
        else:
            form = PeriodicalServiceForm(initial={'tarif':tariff_id})
   
    return { 'formset':None, 'form':form} 

@login_required
@render_to('ebsadmin/speedlimit_edit.html')
def tariff_speedlimit_edit(request):

    

    item = None
    trafficlimit_id = request.GET.get("trafficlimit_id")
    trafficlimit = TrafficLimit.objects.get(id=trafficlimit_id)
    if request.method == 'POST': 
        if  not (request.user.account.has_perm('billservice.change_tariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
        id = request.POST.get("id")
        if id:

            model = SpeedLimit.objects.get(id=id)
            form = SpeedLimitForm(request.POST, instance=model) 

        else:

            form = SpeedLimitForm(request.POST) 

        if form.is_valid():

            model = form.save(commit=False)
            model.save()
            item = model
            trafficlimit.speedlimit=model
            trafficlimit.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'trafficlimit': trafficlimit, 'status': False} 
    else:
        if  not (request.user.account.has_perm('billservice.view_tariff')):
            return {'status':False}
        id = request.GET.get("id")
        trafficlimit_id = request.GET.get("trafficlimit_id")
        trafficlimit = TrafficLimit.objects.get(id=trafficlimit_id)
        
        if trafficlimit:


            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
            item = trafficlimit.speedlimit
            form = SpeedLimitForm(instance=item)
        else:
            form = SpeedLimitForm()
   
    return { 'trafficlimit':trafficlimit, 'form':form, 'item': item}

@login_required
@render_to('ebsadmin/onetimeservice_edit.html')
def onetimeservice_edit(request):

    

    item = None
    if request.method == 'POST': 
        if  not (request.user.account.has_perm('billservice.change_tariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
        id = request.POST.get("id")
        if id:
            model = OneTimeService.objects.get(id=id)
            form = OneTimeServiceForm(request.POST, instance=model) 
        else:
            form = OneTimeServiceForm(request.POST) 



        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, u'Разовая услуга сохранена.', extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:
            messages.error(request, u'При сохранении разовой  услуги произошла ошибка.', extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        if  not (request.user.account.has_perm('billservice.view_tariff')):
            return {'status':False}
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        
        if id:
            item = OneTimeService.objects.get(id=id)
            form = OneTimeServiceForm(instance=item)
        else:
            form = OneTimeServiceForm(initial={'tarif':tariff_id})
   
    return { 'formset':None, 'form':form} 

@ajax_request
@login_required
def tariff_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_tariff')):
        return {'status':False, 'message': u'У вас нет прав на удаление тарифных планов'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Tariff.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный тарифный план не найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Тарифный план удалён.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении тарифного плана произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "tariff not found"} 
    
@ajax_request
@login_required
def periodicalservice_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = PeriodicalService.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная периодическая услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Периодическая услуга удалёна.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении периодической услуги произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "PeriodicalService not found"} 

@ajax_request
@login_required
def traffictransmitnode_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TrafficTransmitNodes.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Настройка NetFlow тарификации трафика удалёна.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении настройки NetFlow тарификации трафика произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "TrafficTransmitNodes not found"} 
    

@ajax_request
@login_required
def tariff_timespeed_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TimeSpeed.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Настройка скорости удалёна.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении настройки скорости произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "TimeSpeed not found"} 
    
@ajax_request
@login_required
def tariff_onetimeservice_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = OneTimeService.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Разовая услуга удалёна.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении разовой услуги произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "OneTimeService not found"} 
    
@ajax_request
@login_required
def tariff_radiustrafficservice_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = RadiusTraffic.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Услуга RADIUS тарификации трафика удалена.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении RADIUS тарификации трафика произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "RadiusTraffic not found"} 

@ajax_request
@login_required
def tariff_timeaccessservice_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TimeAccessService.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Услуга RADIUS тарификации времени удалена.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении RADIUS тарификации времени произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "TimeAccessService not found"} 
    
@ajax_request
@login_required
def tariff_traffictransmitservice_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TrafficTransmitService.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Услуга NetFlow тарификации трафика удалена.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении NetFlow тарификации трафика произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "TrafficTransmitService not found"} 
    
@ajax_request
@login_required
def radiustrafficnode_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = RadiusTrafficNode.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Настройка RADIUS тарификации трафика удалена.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении настройки RADIUS тарификации трафика произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "RadiusTrafficNode not found"} 

@ajax_request
@login_required
def trafficlimit_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TrafficLimit.objects.get(id=id)
            item.speedlimit.delete()
            
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Лимит трафика удален.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении лимита трафика произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "TrafficLimit not found"} 
    
@ajax_request
@login_required
def speedlimit_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = SpeedLimit.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SpeedLimit not found"} 
    
@ajax_request
@login_required
def timeaccessnode_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TimeAccessNode.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Настройка тарификации времени удалена.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении настройки тарификации времени произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "TimeAccessNode not found"} 
    
@ajax_request
@login_required
def addonservicetariff_delete(request):
    if  not (request.user.account.has_perm('billservice.change_tariff')):
        return {'status':False, 'message': u'У вас нет прав на редактирование тарифного плана'} 
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = AddonServiceTarif.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, u'Подключаемая услуги удалена из тарифного плана.', extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, u'При удалении подклчюаемой услуги из тарифного плана произошла ошибка.', extra_tags='alert-danger')
        return {"status": False, "message": "AddonServiceTarif not found"} 
    