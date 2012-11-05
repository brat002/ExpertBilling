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


log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/tariff_list.html')
def tariff(request):
    res = Tariff.objects.all()
    table = TariffTable(res)
    table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
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
            if  not (request.user.is_staff==True and request.user.has_perm('nas.change_tariff')):
                return {'status':False, 'message': u'У вас нет прав на редактирование тарифных планов'}
            
        if  not (request.user.is_staff==True and request.user.has_perm('nas.add_tariff')):
            return {'status':False, 'message': u'У вас нет прав на добавление тарифных планов'}

        
        if form.is_valid() and accessparameters_form.is_valid():
            ap = accessparameters_form.save(commit=False)
            ap.save()
            model = form.save(commit=False)
            model.access_parameters = ap
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect("%s?id=%s" % (reverse("tariff_edit"), model.id))
        else:
            print form._errors
            return {'form':form, "access_parameters": accessparameters_form, 'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
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

    

    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    items = PeriodicalService.objects.filter(tarif__id=tariff_id)
    tariff = Tariff.objects.get(id=tariff_id)
    if items:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
            return {'status':True}

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
    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    items = AddonServiceTarif.objects.filter(tarif__id=tariff_id)
    tariff = Tariff.objects.get(id=tariff_id)
    if items:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
            return {'status':True}

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
        id = request.POST.get("id")
        if id:
            print 11
            model = AddonServiceTarif.objects.get(id=id)
            form = AddonServiceTarifForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_addonservicetarif')):
                return {'status':False, 'message': u'У вас нет прав на редактирование правил активации покдлчюаемых услуг'}
        else:
            print 22
            form = AddonServiceTarifForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_addonservicetarif')):
            return {'status':False, 'message': u'У вас нет прав на добавление правил активации подключаемых услуг'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:
            print form._errors
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
                return {'status':True}

            item = AddonServiceTarif.objects.get(id=id)
            form = AddonServiceTarifForm(instance=item)
        else:
            form = AddonServiceTarifForm(initial={'tarif':tariff_id})
   
    return { 'item':item, 'form':form} 

@login_required
@render_to('ebsadmin/tariff_trafficlimit.html')
def tariff_trafficlimit(request):

    

    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    items = TrafficLimit.objects.filter(tarif__id=tariff_id)
    tariff = Tariff.objects.get(id=tariff_id)
    if items:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
            return {'status':True}

        #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
        
        #formset = PeriodicalServiceFormSet(queryset=items)
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
        id = request.POST.get("id")
        if id:
            print 11
            model = TrafficLimit.objects.get(id=id)
            form = TrafficLimitForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_trafficlimit')):
                return {'status':False, 'message': u'У вас нет прав на редактирование лимитов трафика'}
        else:
            print 22
            form = TrafficLimitForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_periodicalservice')):
            return {'status':False, 'message': u'У вас нет прав на добавление лимитов трафика'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
                return {'status':True}

            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
            item = TrafficLimit.objects.get(id=id)
            form = TrafficLimitForm(instance=item)
        else:
            form = TrafficLimitForm(initial={'tarif':tariff_id})
   
    return { 'formset':None, 'form':form} 

@login_required
@render_to('ebsadmin/tariff_onetimeservice.html')
def tariff_onetimeservice(request):

    

    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    if tariff_id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
            return {'status':True}

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

    

    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    prepaidtable = None
    
    if tariff_id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
            return {'status':True}
        if request.method == 'POST': 
            id = request.POST.get("id")
            if id:
                print 11
                model = TrafficTransmitService.objects.get(id=id)
                form = TrafficTransmitServiceForm(request.POST, instance=model) 
                if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_traffictransmitservice')):
                    return {'status':False, 'message': u'У вас нет прав на редактирование правил тарификации NetFlow трафика'}
            else:
                print 22
                form = TrafficTransmitServiceForm(request.POST) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_traffictransmitservice')):
                return {'status':False, 'message': u'У вас нет прав на добавление правил тарификации NetFlow трафика'}
    
            print 2
            if form.is_valid():
                print 3
                model = form.save(commit=False)
                model.save()
                item = model
                tariff.traffic_transmit_service=model
                tariff.save()
                log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
                return HttpResponseRedirect("%s?tariff_id=%s" % (reverse("tariff_traffictransmitservice"), tariff.id))
            print form._errors
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

    

    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    prepaidtable = None
    
    print 1
    if tariff_id:
        print 2
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
            return {'status':True}
        print 3
        if request.method == 'POST':
            print 4 
            id = request.POST.get("id")
            if id:
                print 5
                
                model = RadiusTraffic.objects.get(id=id)
                form = RadiusTrafficForm(request.POST, instance=model) 
                if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_radiustraffic')):
                    return {'status':False, 'message': u'У вас нет прав на редактирование правил тарификации Radius трафика'}
            else:
                print 6
                form = RadiusTrafficForm(request.POST) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_radiustraffic')):
                return {'status':False, 'message': u'У вас нет прав на добавление правил тарификации Radius трафика'}
    
            print 7
            if form.is_valid():
                print 8
                print form
                model = form.save(commit=False)
                model.save()
                item = model
                log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
                tariff.radius_traffic_transmit_service = item
                tariff.save()
            else:
                print 9
                print form._errors
        else:
            print 10
            item = tariff.radius_traffic_transmit_service
            form = RadiusTrafficForm(instance=item)
            
        #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
        
        print 11
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

    

    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    
    print 1
    if tariff_id:
        print 2
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
            return {'status':True}
        print 3
        if request.method == 'POST':
            print 4 
            id = request.POST.get("id")
            if id:
                print 5
                
                model = TimeAccessService.objects.get(id=id)
                form = TimeAccessServiceForm(request.POST, instance=model) 
                if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_timeaccessservice')):
                    return {'status':False, 'message': u'У вас нет прав на редактирование правил тарификации Radius трафика'}
            else:
                print 6
                form = TimeAccessServiceForm(request.POST) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_timeaccessservice')):
                return {'status':False, 'message': u'У вас нет прав на добавление правил тарификации Radius трафика'}
    
            print 7
            if form.is_valid():
                print 8
                print form.cleaned_data
                model = form.save(commit=False)
                model.save()
                item = model
                log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
                tariff.time_access_service = item
                tariff.save()
            else:
                item = model
                print 9
                print form._errors
        else:
            print 10
            item = tariff.time_access_service
            form = TimeAccessServiceForm(instance=item)
            
        #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
        
        print 11
        #formset = PeriodicalServiceFormSet(queryset=items)
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
        print request.POST
        
        if id:
            print 11
            model = TimeAccessNode.objects.get(id=id)
            form = TimeAccessNodeForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_timeaccessnode')):
                return {'status':False, 'message': u'У вас нет прав на редактирование правил тарификации RADIUS времени'}
        else:
            print 22
            form = TimeAccessNodeForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_timeaccessnode')):
            return {'status':False, 'message': u'У вас нет прав на добавление правил тарификации RADIUS времени'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            item = model
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:
            
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        time_access_service_id = request.GET.get("time_access_service_id")
        tts = None
        if time_access_service_id:
            tas = TimeAccessService.objects.get(id=time_access_service_id)
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
                return {'status':True}

            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
            item = TimeAccessNode.objects.get(id=id)
            form = TimeAccessNodeForm(instance=item)
        elif tts:
            form = TimeAccessNodeForm(initial={"time_access_service": tas})
            
        else:
            form = TimeAccessNodeForm(initial={"time_access_service": tas})
        print "tts", tas, tariff_id
    return { 'item':item, 'form':form} 

@login_required
@render_to('ebsadmin/tariff_accessparameters.html')
def tariff_accessparameters(request):

    

    item = None

    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    print "tariff_id", tariff_id
    tariff = Tariff.objects.get(id=tariff_id)
    prepaidtable = None
    
    if tariff:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
            return {'status':True}
        if request.method == 'POST': 
            id = request.POST.get("id")
            if tariff.access_parameters:
                print 11
                model = tariff.access_parameters
                form = AccessParametersForm(request.POST, instance=model) 
                if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_accessparameters')):
                    return {'status':False, 'message': u'У вас нет прав на редактирование параметров доступа'}
            else:
                print 22
                form = AccessParametersForm(request.POST) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_accessparameters')):
                return {'status':False, 'message': u'У вас нет прав на добавление параметров доступа'}
    
            print 2
            if form.is_valid():
                print 3
                model = form.save(commit=False)
                model.save()
                
                item = model
                log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
                return HttpResponseRedirect("%s?tariff_id=%s" % (reverse("tariff_accessparameters"), tariff.id))
        else:
            item = tariff.access_parameters
            
        #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
        
        form = AccessParametersForm(instance=item)
        #formset = PeriodicalServiceFormSet(queryset=items)
        items =TimeSpeed.objects.filter(access_parameters=item)
        table = TimeSpeedTable(items)
        RequestConfig(request, paginate = False).configure(table)

    else:
        form = AccessParametersForm()
   
    return { 'formset':None, 'table':table, 'tariff': tariff,  'item':item, 'form':form, 'active': 'accessparameters'} 


@login_required
@render_to('ebsadmin/tariff_timespeed_edit.html')
def tariff_timespeed_edit(request):

    

    item = None
    if request.method == 'POST': 
        id = request.POST.get("id")
        if id:
            print 11
            model = TimeSpeed.objects.get(id=id)
            form = TimeSpeedForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_timespeed')):
                return {'status':False, 'message': u'У вас нет прав на редактирование правил изменения скорости'}
        else:
            print 22
            form = TimeSpeedForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_timespeed')):
            return {'status':False, 'message': u'У вас нет прав на добавление правил изменения скорости'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:   
            print form._errors
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        access_parameters = request.GET.get("access_parameters")
        ap = AccessParameters.objects.get(id=access_parameters)
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
                return {'status':True}

            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
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
        id = request.POST.get("id")
        if id:
            print 11
            model = PrepaidTraffic.objects.get(id=id)
            form = PrepaidTrafficForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_prepaidtraffic')):
                return {'status':False, 'message': u'У вас нет прав на редактирование правил начисления предоплаченного трафика'}
        else:
            print 22
            form = PrepaidTrafficForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_prepaidtraffic')):
            return {'status':False, 'message': u'У вас нет прав на добавление правил начисления предоплаченного трафика'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
                return {'status':True}

            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
            item = PrepaidTraffic.objects.get(id=id)
            form = PrepaidTrafficForm(instance=item)
        else:
            form = PrepaidTrafficForm()
   
    return { 'formset':None, 'form':form} 

@login_required
@render_to('ebsadmin/tariff_traffictransmitnode_edit.html')
def tariff_traffictransmitnode_edit(request):

    

    item = None
    if request.method == 'POST': 
        id = request.POST.get("id")
        print request.POST
        
        if id:
            print 11
            model = TrafficTransmitNodes.objects.get(id=id)
            form = TrafficTransmitNodeForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_traffictransmitnodes')):
                return {'status':False, 'message': u'У вас нет прав на редактирование правил тарификации трафика'}
        else:
            print 22
            form = TrafficTransmitNodeForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_traffictransmitnodes')):
            return {'status':False, 'message': u'У вас нет прав на добавление правил тарификации трафика'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:
            
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        tts = None
        if tariff_id:
            tts = Tariff.objects.get(id=tariff_id).traffic_transmit_service
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
                return {'status':True}

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
        id = request.POST.get("id")
        print request.POST
        
        if id:
            print 11
            model = RadiusTrafficNode.objects.get(id=id)
            form = RadiusTrafficNodeForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_radiustrafficnode')):
                return {'status':False, 'message': u'У вас нет прав на редактирование правил тарификации RADIUS трафика'}
        else:
            print 22
            form = RadiusTrafficNodeForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_radiustrafficnode')):
            return {'status':False, 'message': u'У вас нет прав на добавление правил тарификации RADIUS трафика'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:
            
            return {'form':form,  'status': False} 
    else:
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
        id = request.POST.get("id")
        if id:
            print 11
            model = PeriodicalService.objects.get(id=id)
            form = PeriodicalServiceForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_periodicalservice')):
                return {'status':False, 'message': u'У вас нет прав на редактирование периодических услуг'}
        else:
            print 22
            form = PeriodicalServiceForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_periodicalservice')):
            return {'status':False, 'message': u'У вас нет прав на добавление периодических услуг'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
                return {'status':True}

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
        id = request.POST.get("id")
        if id:
            print 11
            model = SpeedLimit.objects.get(id=id)
            form = SpeedLimitForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_speedlimit')):
                return {'status':False, 'message': u'У вас нет прав на редактирование правил изменения скорости для лимитов'}
        else:
            print 22
            form = SpeedLimitForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_speedlimit')):
            return {'status':False, 'message': u'У вас нет прав на добавление правил изменения скорости для лимитов'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            item = model
            trafficlimit.speedlimit=model
            trafficlimit.save()
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'trafficlimit': trafficlimit, 'status': False} 
    else:
        id = request.GET.get("id")
        trafficlimit_id = request.GET.get("trafficlimit_id")
        trafficlimit = TrafficLimit.objects.get(id=trafficlimit_id)
        
        if trafficlimit:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
                return {'status':True}

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
        id = request.POST.get("id")
        if id:
            print 11
            model = OneTimeService.objects.get(id=id)
            form = OneTimeServiceForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_onetimeservice')):
                return {'status':False, 'message': u'У вас нет прав на редактирование разовых услуг'}
        else:
            print 22
            form = OneTimeServiceForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_onetimeservice')):
            return {'status':False, 'message': u'У вас нет прав на добавление разовых услуг'}

        print 2
        if form.is_valid():
            print 3
            model = form.save(commit=False)
            model.save()
            print 4
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        
        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
                return {'status':True}

            #items = PeriodicalService.objects.filter(tarif__id=tariff_id)
            item = OneTimeService.objects.get(id=id)
            form = OneTimeServiceForm(instance=item)
        else:
            form = OneTimeServiceForm(initial={'tarif':tariff_id})
   
    return { 'formset':None, 'form':form} 

@ajax_request
@login_required
def tariff_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_tariff')):
        return {'status':False, 'message': u'У вас нет прав на удаление тарифных планов'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Tariff.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный тарифный план не найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "tariff not found"} 
    
@ajax_request
@login_required
def periodicalservice_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_periodicalservice')):
        return {'status':False, 'message': u'У вас нет прав на удаление периодических услуг'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = PeriodicalService.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная периодическая услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "PeriodicalService not found"} 

@ajax_request
@login_required
def traffictransmitnode_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_traffictransmitnodes')):
        return {'status':False, 'message': u'У вас нет прав на удаление правил NetFlow тарификации'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TrafficTransmitNodes.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TrafficTransmitNodes not found"} 
    

@ajax_request
@login_required
def tariff_timespeed_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_timespeed')):
        return {'status':False, 'message': u'У вас нет прав на удаление правил изменения скорости'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TimeSpeed.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TimeSpeed not found"} 
    
@ajax_request
@login_required
def tariff_onetimeservice_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_onetimeservice')):
        return {'status':False, 'message': u'У вас нет прав на удаление разовых услуг'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = OneTimeService.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "OneTimeService not found"} 
    
@ajax_request
@login_required
def tariff_radiustrafficservice_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_radiustraffic')):
        return {'status':False, 'message': u'У вас нет прав на удаление RADIUS тарификации трафика'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = RadiusTraffic.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "RadiusTraffic not found"} 

@ajax_request
@login_required
def tariff_timeaccessservice_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_timeaccessservice')):
        return {'status':False, 'message': u'У вас нет прав на удаление RADIUS тарификации трафика'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TimeAccessService.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TimeAccessService not found"} 
    
@ajax_request
@login_required
def tariff_traffictransmitservice_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_traffictransmitservice')):
        return {'status':False, 'message': u'У вас нет прав на удаление NetFlow тарфикации трафика'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TrafficTransmitService.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная услуга не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TrafficTransmitService not found"} 
    
@ajax_request
@login_required
def radiustrafficnode_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_radiustrafficnode')):
        return {'status':False, 'message': u'У вас нет прав на удаление правил RADIUS тарификации'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = RadiusTrafficNode.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "RadiusTrafficNode not found"} 

@ajax_request
@login_required
def trafficlimit_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_trafficlimit')):
        return {'status':False, 'message': u'У вас нет прав на удаление лимитов трафика'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TrafficLimit.objects.get(id=id)
            item.speedlimit.delete()
            
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TrafficLimit not found"} 
    
@ajax_request
@login_required
def speedlimit_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_speedlimit')):
        return {'status':False, 'message': u'У вас нет прав на удаление правил изменения скорости'}
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
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_timeaccessnode')):
        return {'status':False, 'message': u'У вас нет прав на удаление правил тарификации времени'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TimeAccessNode.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TimeAccessNode not found"} 
    
@ajax_request
@login_required
def addonservicetariff_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_addonservicetarif')):
        return {'status':False, 'message': u'У вас нет прав на удаление правил активации подклчюаемых услуг'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = AddonServiceTarif.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанное правило не найдено %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "AddonServiceTarif not found"} 
    