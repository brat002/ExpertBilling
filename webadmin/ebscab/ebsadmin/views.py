#-*-coding:utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from ebscab.lib.ssh_paramiko import ssh_client
from billservice.models import Account, AccessParameters, SubAccount, TransactionType, City, Street, House, SystemUser,AccountTarif, AddonService, IPPool, IPInUse, ContractTemplate, Document
from billservice.models import Organization, TimeSpeed, BankData, TimePeriod, SettlementPeriod, Template, TemplateType,  AccountHardware, SuspendedPeriod, Operator, Transaction, PeriodicalService, AddonService, Tariff
from billservice.models import OneTimeService, TimeSpeed,  TrafficTransmitNodes, PrepaidTraffic, Group, PeriodicalService, OneTimeService, TrafficLimit, AddonServiceTarif
from billservice.models import Template, News, AccountAddonService, SaleCard, DealerPay, Card, Dealer, AccountViewedNews, TPChangeRule, Manufacturer, Model, Hardware, HardwareType, TransactionType, TimePeriodNode, AccountPrepaysTrafic, AccountPrepaysRadiusTrafic, TrafficTransmitService, RadiusAttrs, SpeedLimit,  RadiusTraffic, RadiusTrafficNode,TimeAccessNode,TimeAccessService, AddonServiceTarif

import os
from nas.models import Nas,  TrafficClass, TrafficNode
from radius.models import ActiveSession
from django.contrib.auth.decorators import login_required
from django.db import connection
from billservice.forms import AccountForm, TimeSpeedForm, GroupForm, SubAccountForm, SearchAccountForm, AccountTariffForm, AccountAddonForm,AccountAddonServiceModelForm, DocumentRenderForm
from billservice.forms import TemplateForm, DocumentModelForm, SuspendedPeriodModelForm, TransactionModelForm, AddonServiceForm, CityForm, StreetForm, HouseForm
from utilites import cred, rosClient, rosExecute
import IPy
from randgen import GenUsername as nameGen , GenPasswd as GenPasswd2
from IPy import IP

import datetime
from mako.template import Template as mako_template
from ebsadmin.lib import ExtDirectStore, instance_dict
from billservice.forms import LoginForm, AccountPrepaysRadiusTraficForm, RadiusTrafficForm, RadiusTrafficNodeForm, PrepaidTrafficForm, TrafficTransmitNodeForm,TrafficTransmitServiceForm, PeriodicalServiceForm, OneTimeServiceForm,  TariffForm, AccessParametersForm, SettlementPeriodForm, OrganizationForm, BankDataForm,AccountTariffBathForm
from billservice.forms import RadiusAttrsForm, IPPoolForm, TimePeriodForm, TimePeriodNodeForm, SystemUserForm, TransactionTypeForm, AccountPrepaysTrafic, TimeAccessNodeForm, ContractTemplateForm, TimeAccessServiceForm, TrafficLimitForm, SpeedLimitForm, AddonServiceTarifForm
from billservice.forms import ActionLogFilterForm, ManufacturerForm, OperatorForm, DealerPayForm, SaleCardForm, CardForm, DealerForm, NewsForm, TPChangeRuleForm, AccountHardwareForm, ModelHardwareForm, HardwareTypeForm, HardwareForm
from billservice.utility import settlement_period_info
from billservice import authenticate, log_in, log_out
from nas.forms import NasForm, TrafficNodeForm, TrafficClassForm
from radius.forms import SessionFilterForm
import ipaddr
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import Group as AuthGroup

from django.contrib.auth.models import User
from django.core.cache import cache
from object_log.models import LogItem
log = LogItem.objects.log_action

try:
    import json
    json.loads("{}")
except:
    import simplejson as json
    
import commands

from django.contrib.auth.decorators import permission_required

class Object(object):
    def __init__(self, result=[], *args, **kwargs):
        for key in result:
            setattr(self, key, result[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])  

@ajax_request
def simple_login(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        try:
            user = authenticate(username=form.cleaned_data['username'], \
                                password=form.cleaned_data['password'])
            if isinstance(user.account, SystemUser):
                if user.account.host!='0.0.0.0/0':
                    try:
                        if not (IPy.IP(request.META.get("REMOTE_ADDR")) in IPy.IP(user.account.host)):
                            return {"status":False,"message":"Access for your IP address forbidden"}
                    except Exception, e:
                        return {"status":False,"message":"Login error. May be systemuser host syntax error"}
                log_in(request, user)
                user.account.last_login = datetime.datetime.now()
                user.account.last_ip = request.META.get("REMOTE_ADDR")
                user.account.save()
                return {"status":True,"message":"Login succeful"}
            else:
                return {"status":False, "message":"Login forbidden to this action"}
                
        except Exception, e:
            return {"status":False, "message":"Login can`t be authenticated"}
    return {"status":False,"message":"Login not found"}

@ajax_request
@login_required
def jsonaccounts(request):
    if  not request.user.is_staff==True:
        return {'status':False, 'message':u'Недостаточно прав для выполнения операции'}
    extra={'start':int(request.POST.get('start',0)), 'limit':int(request.POST.get('limit',100))}
    if request.POST.get('sort',''):
        extra['sort'] = request.POST.get('sort','')
        extra['dir'] = request.POST.get('dir','asc')
        
    if request.POST.get('action')!='search':
        #items = Account.objects.all()
        items = ExtDirectStore(Account)
        items, totalcount = items.query(**extra)
    else:
        f=SearchAccountForm(request.POST)

        query={}
        for k in f.cleaned_data:
            if f.cleaned_data.get(k):
                query[k]=f.cleaned_data.get(k)
            
        items = Account.objects.filter(**query)
    
    res=[]
    for item in items:
        r=instance_dict(item,normal_fields=True)
        r['tariff']=item.tariff
        res.append(r)

    return {"records": res, 'total':str(totalcount)}
    


@ajax_request
@login_required
def addonservice(request):
    if  not request.user.is_staff==True:
        return {'status':False, 'message':u'Недостаточно прав для выполнения операции'}
    
    extra={'start':int(request.POST.get('start',0)), 'limit':int(request.POST.get('limit',100))}
    if request.POST.get('sort',''):
        extra['sort'] = request.POST.get('sort','')
        extra['dir'] = request.POST.get('dir','asc')
        
    
    items = ExtDirectStore(AddonService)
    items, totalcount = items.query(**extra)

    res=[]
    for item in items:
        r=instance_dict(item,normal_fields=True)
        res.append(r)
    return {"records": res, 'total':str(totalcount)}


@ajax_request
@login_required
def account_livesearch(request):

    query=request.POST.get('query')
    field=request.POST.get('field')
    #if not (query and field):return {"records": [], 'total':0}
    if query:
        items = Account.objects.filter(**{'%s__icontains' % field:query})
    else:
        items = Account.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append({'id':item.id, 'username':item.username, 'contract':item.contract,'fullname':item.fullname, 'created':item.created.strftime('%Y-%m-%d %H:%M:%S')})

    return {"records": res, 'total':len(res)}

@ajax_request
@login_required
def generate_credentials(request):
    action = request.POST.get('action') or request.GET.get('action')
    
    if action=='login':
        return {"success": True, 'generated':nameGen()}
    if action=='password':
        return {"success": True, 'generated':GenPasswd2()}
    return {"success": False}

@ajax_request
@login_required
def get_mac_for_ip(request):
    if  not (request.user.is_staff==True and request.user.has_perm('subaccount.getmacforip')):
        return {'status':False, 'message':u'Недостаточно прав для выполнения операции'}
    
    nas_id = request.POST.get('nas_id', None)
    if not nas_id:
        return {'status':False, 'message':u'Сервер доступа не указан'}
    ipn_ip_address = request.POST.get('ipn_ip_address')
    try:
        nas = Nas.objects.get(id=nas_id)
    except Exception, e:
        return {'status':False, 'message':str(e)}
    try:
        IPy.IP(ipn_ip_address)
    except Exception, e:
        return {'status':False, 'message':str(e)}
    try:
        from utilites import rosExecute
        apiros = rosClient(nas.ipaddress, nas.login, nas.password)
        command='/ping =address=%s =count=1' % ipn_ip_address
        rosExecute(apiros, command)
        command='/ip/arp/print ?address=%s' % ipn_ip_address
        rosExecute(apiros, command)
        mac = rosExecute(apiros, command).get('mac-address', '')
        apiros.close()
        del apiros
        del rosExecute
    except Exception, e:
        return {'success':False, 'message':str(e)}
    
    return {'success':True, 'mac':mac}
    
@login_required
@ajax_request
def subaccounts(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.subaccount_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    account_id = request.POST.get('account_id', None)
    id = request.POST.get('id', None)

    normal_fields = request.POST.get('normal_fields', True)=='True'

    if account_id and account_id!= 'None':
        items = SubAccount.objects.filter(account__id=account_id)
    else:
        items = SubAccount.objects.filter(id=id)

    res=[]
    for item in items:
        res.append(instance_dict(item,normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def addonservices(request):
    if  not (request.user.is_staff==True and  request.user.has_perm('billservice.addonservice_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    id = request.POST.get('id', None)
    
    normal_fields = request.POST.get('normal_fields', True)=='True'
    if id and id!= '':
        items = AddonService.objects.filter(id=id)
    else:
        items = AddonService.objects.all().order_by('name')

    res=[]
    for item in items:
        res.append(instance_dict(item,normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def authgroups(request):
    if  not request.user.is_staff==True:
        return {'status':True, 'records':[], 'totalCount':0}
    id = request.POST.get('id', None)
    

    if id and id!= '':
        items = AuthGroup.objects.filter(id=id)
    else:
        items = AuthGroup.objects.all().order_by('name')

    res=[]
    for item in items:
        res.append(instance_dict(item))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def document(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.document_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    account_id = request.POST.get('account_id')

    items = Document.objects.filter(account__id=account_id)

    res=[]
    for item in items:
        res.append(instance_dict(item,normal_fields=True))

    return {"records": res}


@ajax_request
@login_required
def templates(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.template_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    type_id = request.POST.get('type_id',None)

    if id and id!='None':
        items = Template.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Template item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
    elif type_id:
        items = Template.objects.filter(type__id=type_id)
    else:
        items = Template.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=False))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def sessions(request):
    if  not (request.user.is_staff==True and  request.user.has_perm('radius.activesession_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    form = SessionFilterForm(request.POST)
    if form.is_valid():
        id = form.cleaned_data.get('id')
        account_id = form.cleaned_data.get('account')
        date_start =form.cleaned_data.get('date_start')
        date_end = form.cleaned_data.get('date_end')
        only_active = request.POST.get('only_active')=='True'


        items = ActiveSession.objects.filter( Q(date_end__lte=date_end) | Q(date_end__isnull=True)).filter(date_start__gte=date_start).order_by('-interrim_update')
        if only_active:
            items = items.filter(session_status='ACTIVE')
            
        if id:
             items = items.filter(id=id)
             if not items:
                return {'status':False, 'message': 'Session with id=%s not found' % id}
        elif account_id:
            items = items.filter(account__id=account_id)
 
        items = items.values("id","sessionid","account__username","account__id","subaccount__username", "account__ballance", "account__credit", "caller_id", "framed_ip_address", "nas_int_id__name", "framed_protocol", "date_start", "date_end", "bytes_out", "bytes_in", "session_time", "session_status","acct_terminate_cause")
        res = []
        for item in items:
            res.append(item)
            
        return {"records": res, 'status':True, 'totalCount':len(res)}
    else:
        return { 'status':False, 'message': u'Невозможно выполнить выборку с такими условиями'}



@ajax_request
@login_required
def settlementperiods(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_settlementperiod')):
        return {'status':True, 'records':[], 'totalCount':0}
    js = json.loads(request.POST.get('data','{}'))
    fields = js.get('fields',[])
    id = js.get('id',None)
    autostart = js.get('autostart',None)
    if id and id!='None':
        if autostart is not None:
            items = SettlementPeriod.objects.filter(id=id, autostart=autostart)
        else:
            items = SettlementPeriod.objects.filter(id=id)
            
        if not items:
            return {'status':False, 'message': 'SettlementPeriod item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        if autostart is not None:
            items = SettlementPeriod.objects.filter(autostart=autostart)
        else:
            items = SettlementPeriod.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def accessparameters(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    if id and id!='None':
        items = AccessParameters.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'AccessParameters item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = AccessParameters.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def timeperiods(request):
    if  not (request.user.is_staff==True and  request.user.has_perm('billservice.timeperiod_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    if id and id!='None':
        items = TimePeriod.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TimePeriod item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = TimePeriod.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def timeperiods_save(request):

    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.timeperiod_change')):
            return {'status':False, 'message':u'У вас недостатчно прав для изменения периодов тарификации'}
        item = TimePeriod.objects.get(id=id)
        form = TimePeriodForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and  request.user.has_perm('billservice.timeperiod_add')):
            return {'status':False, 'message':u'У вас недостатчно прав для создания периодов тарификации'}
        form = TimePeriodForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:

            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def timeperiods_delete(request):
    if  not (request.user.is_staff==True and  request.user.has_perm('billservice.timeperiod_delete')):
        return {'status':False, 'message':u'У вас недостатчно прав для удаления периодов тарификации'}
    id = int(request.POST.get('id',0))
    if id:
        model = TimePeriod.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TimePeriod not found"}
   

@ajax_request
@login_required
def timeperiodnodes_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.timeperiod_delete')):
        return {'status':False, 'message':u'У вас недостатчно прав для удаления периодов тарификации'}
    id = int(request.POST.get('id',0))
    if id:
        model = TimePeriodNode.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TimePeriodNode not found"} 
    
@ajax_request
@login_required
def timeperiodnodes(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.timeperiodnode_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    period_id = request.POST.get('period_id',None)
    
    if id:
        items = TimePeriodNode.objects.filter(id=id)
        
    elif period_id and period_id!='None':
        try:
            period = TimePeriod.objects.get(id=period_id)
        except:
            return {'status':True, "records":[], 'totalCount':0}
        items = period.time_period_nodes.all()
    else:
        items = TimePeriodNode.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def timeperiodnodes_save(request):

    id = request.POST.get('id')
    if id:
        item = TimePeriodNode.objects.get(id=id)
        form = TimePeriodNodeForm(request.POST, instance=item)
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_timeperiodnode')):
            return {'status':False, 'message':u"У вас недостаточно прав для изменения составляющих периодов"}
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_timeperiodnode')):
            return {'status':False, 'message':u"У вас недостаточно прав для добавления составляющих периодов"}
        form = TimePeriodNodeForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:

            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def timeperiodnodes_m2m_save(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.timeperiod_change')):
        return {'status':False, 'message':u'У вас недостатчно прав для изменения периодов тарификации'}
    timeperiod_id = request.POST.get('timeperiod')
    timeperiodnode_id = request.POST.get('timeperiodnode')
    if timeperiod_id and timeperiodnode_id :
        timeperiodnode = TimePeriodNode.objects.get(id=timeperiodnode_id)
        timeperiod = TimePeriod.objects.get(id=timeperiod_id)
        
        timeperiod.time_period_nodes.add(timeperiodnode)
        
        res={"status": True}
    else:
        res={"status": False, "errors": u"Ошибка в создании связи"}
 
    return res

@ajax_request
@login_required
def timeperiodnodes_m2m_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.timeperiod_change')):
        return {'status':False, 'message':u'У вас недостатчно прав для изменения периодов тарификации'}
    timeperiod_id = request.POST.get('period_id')
    timeperiodnode_id = request.POST.get('node_id')
    if timeperiod_id and timeperiodnode_id :
        timeperiodnode = TimePeriodNode.objects.get(id=timeperiodnode_id)
        timeperiod = TimePeriod.objects.get(id=timeperiod_id)
        
        timeperiod.time_period_nodes.remove(timeperiodnode)
        
        #TODO: Сделать. чтобы при удалении последней связи удалялась и сама нода
        res={"status": True}
    else:
        res={"status": False, "errors": u"Ошибка в создании связи"}
 
    return res


@ajax_request
@login_required
def timeaccessservices(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.timeaccessservice_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    if id and id!='None':
        items = TimeAccessService.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TimeAccessService item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'TimeAccessService >1 items with id=%s' % id}
        
    else:
        items = TimeAccessService.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def radiustrafficservices(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.radiustraffic_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    normal_fields = request.POST.get('normal_fields', False)=='True'
    if id and id!='None':
        items = RadiusTraffic.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'RadiusTraffic item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'RadiusTraffic >1 items with id=%s' % id}
        
    else:
        items = RadiusTraffic.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def traffictransmitservices(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.traffictransmitservice_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    normal_fields = request.POST.get('normal_fields', False)=='True'
    if id and id!='None':
        items = TrafficTransmitService.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TrafficTransmitService item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'TrafficTransmitService >1 items with id=%s' % id}
        
    else:
        items = TrafficTransmitService.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
    
@ajax_request
@login_required
def sql(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.rawsqlexecution')):
        return {'status':False, 'records':[], 'totalCount':0}
    
    s = request.POST.get('sql','')
  
    if not s:
        return {'status':False, 'message': 'SQL not defined'}
        
    from django.db import connection
    
    cur = connection.cursor()
    try:
        log('RAWSQL', request.user,  request.user.account, data={'sql':unicode(s, errors="ignore")})
    except:
        pass
    try:
        cur.execute(s)
        
        res = dictfetchall(cur)
    except Exception, e:
        return { 'status':False, 'message':str(e)}
        
  
    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def radiustrafficservices_nodes(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.radiustrafficnode_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    service_id = request.POST.get('service_id', None)
    normal_fields = request.POST.get('normal_fields', False)=='True'
    if id and id!='None':
        items = RadiusTrafficNode.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'RadiusTrafficNode item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'RadiusTrafficNode >1 items with id=%s' % id}
    elif service_id:
        items = RadiusTrafficNode.objects.filter(radiustraffic__id=service_id)
    else:
        items = RadiusTrafficNode.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def traffictransmit_nodes(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.traffictransmitnodes_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    service_id = request.POST.get('service_id', None)
    normal_fields = request.POST.get('normal_fields', False)=='True'
    if id and id!='None':
        items = TrafficTransmitNodes.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TrafficTransmitNodes item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'TrafficTransmitNodes >1 items with id=%s' % id}
    elif service_id:
        items = TrafficTransmitNodes.objects.filter(traffic_transmit_service__id=service_id)
    else:
        items = TrafficTransmitNodes.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def prepaidtraffic(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.prepaidtraffic_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    service_id = request.POST.get('service_id', None)
    normal_fields = request.POST.get('normal_fields', False)=='True'
    if id and id!='None':
        items = PrepaidTraffic.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'PrepaidTraffic item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'PrepaidTraffic >1 items with id=%s' % id}
    elif service_id:
        items = PrepaidTraffic.objects.filter(traffic_transmit_service__id=service_id)
    else:
        items = PrepaidTraffic.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def timeaccessservices_nodes(request):
    if  not (request.user.is_staff==True and  request.user.has_perm('billservice.timeaccessnode_/admin/auth/group/view')):
        return {'status':False, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    service_id = request.POST.get('service_id', None)
    normal_fields = request.POST.get('normal_fields', False)=='True'
    if id and id!='None':
        items = TimeAccessNode.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TimeAccessNode item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'TimeAccessNode >1 items with id=%s' % id}
    elif service_id:
        items = TimeAccessNode.objects.filter(time_access_service__id=service_id)
    else:
        items = TimeAccessNode.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def timespeeds(request):
    if  not (request.user.is_staff==True and  request.user.has_perm('billservice.timespeed_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    access_parameters = request.POST.get('access_parameters',None)
    normal_fields = bool(request.POST.get('normal_fields',False))
    if id and id!='None':
        items = TimeSpeed.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TimeSpeed item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
    elif access_parameters:
        items = TimeSpeed.objects.filter(access_parameters__id=access_parameters)
    else:
        items = TimeSpeed.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def systemusers(request):

    if  not (request.user.is_staff==True and request.user.has_perm('billservice.systemuser_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    if id and id!='None':
        items = SystemUser.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'SettlementPeriod item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = SystemUser.objects.all()
        
    res=[]
    for item in items:
        is_superuser = False
        u = User.objects.filter(username=item.username)
        if u:
            is_superuser = u[0].is_superuser
        data = instance_dict(item, fields=fields)
        data["is_superuser"] = is_superuser
        res.append(data)

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def tpchangerules(request):
    if  not (request.user.is_staff==True and  request.user.has_perm('billservice.tpchangerule_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    normal_fields = bool(request.POST.get('normal_fields',None)=='True')
    if id and id!='None':
        items = TPChangeRule.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TPChangeRule item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = TPChangeRule.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def tpchangerules_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and  request.user.has_perm('billservice.change_tpchangerule')):
            return {'status':False, 'message': u'У вас нет прав на изменение правила смены тарифных планов'}
        item = TPChangeRule.objects.get(id=id)
        form = TPChangeRuleForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and  request.user.has_perm('billservice.add_tpchangerule')):
            return {'status':False,  'message': u'У вас нет прав на добавление правила смены тарифных планов'}
        form = TPChangeRuleForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            res={"status": True, 'id':model.id}
        except Exception, e:

            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def tpchangerules_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_tpchangerule')):
        return {'status':False,  'message': u'У вас нет прав на удаление правила смены тарифных планов'}
    id = int(request.POST.get('id',0))
    if id:
        model = TPChangeRule.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SystemUser not found"}
    
@ajax_request
@login_required
def systemusers_set(request):
    
    
    data = json.loads(request.POST.get('data'))
    groups_to_add, groups_to_del = data.get("groups_to_add"), data.get("groups_to_del")
    model = data.get('model')
    id = model.get("id")

    if id:
        if  not (request.user.is_staff==True and  request.user.has_perm('billservice.change_systemuser')):
            return {'status':False,  'message': u'У вас нет прав на изменение администратора'}
        item = SystemUser.objects.get(id=id)
        form = SystemUserForm(model, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_systemuser')):
            return {'status':False,  'message': u'У вас нет прав на добавление администратора'}
        form = SystemUserForm(model)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            u = User.objects.filter(username=model.username)
            if not u:
                u = User.objects.create_user(model.username, model.email, model.text_password)
            else:
                u=u[0]
            for item in groups_to_add:
                u.groups.add(AuthGroup.objects.get(id=item))
            for item in groups_to_del:
                u.groups.remove(AuthGroup.objects.get(id=item))
                
            u.is_staff = True
            u.is_active = model.status
            u.is_superuser = data.get("model").get("is_superuser")
            u.save()
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            res={"status": True, 'id':model.id}
        except Exception, e:

            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def systemusers_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_systemuser')):
        return {'status':False,  'message': u'У вас нет прав на удаление администратора'}
    id = int(request.POST.get('id',0))
    if id:
        model = SystemUser.objects.get(id=id)
        User.objects.filter(username=model.username).delete()
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SystemUser not found"}
    
@ajax_request
@login_required
def contracttemplates(request):
    if  not (request.user.is_staff==True and  request.user.has_perm('billservice.contracttemplate_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    if id and id!='None':
        items = ContractTemplate.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'ContractTemplate item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = ContractTemplate.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def ipnforvpn(request):

    if  not (request.user.is_staff==True and request.user.has_perm('billservice.account_view')):
        return {'status':True, 'result':False}
    id = request.POST.get('id',None)
    res = False
    if id and id!='None':
        item = Account.objects.all_with_deleted().get(id=id)
        if not item:
            return {'status':False, 'message': 'Account item with id=%s not found' % id}
       
        res = item.get_account_tariff()
        if res:
          res = res.access_parameters.ipn_for_vpn
        return {"result": res, 'status':True}
    
    return {"result": res, 'status':False}

@ajax_request
@login_required
def session_reset(request):
    if  not (request.user.is_staff==True and request.user.has_perm('activesessions.session_reset')):
        return {'status':False, 'message':u'У вас нет прав на сброс сессии'}
    
    id = request.POST.get('id',None)
    sessionid = request.POST.get('sessionid',None)
    res = False
    if id and id!='None' and sessionid:
        session = ActiveSession.objects.get(id=id, sessionid=sessionid)
        if not session:
            return {'status':False, 'message': 'Session item with id=%s and sessionid %s not found' % (id, sessionid)}
       


        nas = instance_dict(session.nas_int)

        account = instance_dict(session.account)

        subaccount = instance_dict(session.subaccount)
        
        """
        res = PoD(dict=vars.DICT, 
                  account=account, 
                  subacc=subaccount, 
                  nas=nas,
                  access_type=session.framed_protocol, 
                  session_id=session.sessionid,
                  vpn_ip_address=session.framed_ip_address,
                  caller_id=session.caller_id,
                  format_string=nas.reset_action)
        """
        return {"message": u"Данная функция временно не реализована", 'status':False}
    
    return {"message": u"Данная функция временно не реализована", 'status':False}



@login_required
@ajax_request
def tariffforaccount(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.get_tariff')):
        return {'status':False, 'message':u'У вас нет прав на получение тарифа пользователя'}
    id = request.POST.get('id',None)
    res = False
    if id and id!='None':
        item = Account.objects.get(id=id)
        if not item:
            return {'status':False, 'message': 'Account item with id=%s not found' % id}
       
        #print item.get_account_tariff()
        res = instance_dict(item.get_account_tariff())
        return {"records": [res], 'status':True, 'totalCount':1}
    
    return {"records": [res], 'status':False, 'totalCount':1}

@ajax_request
@login_required
def operator(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.operator_view')):
        return {'status':False, 'message':u'У вас нет прав на получение информации о провайдере'}
    try:
        item = Operator.objects.all()[0]
        return {'status':True, "records":[instance_dict(item, normal_fields=False)], 'totalCount':1}
   
    except Exception, e:
        return {'status':False, 'message': u'Провайдер не найден. Задайте информацию о себе в меню Help'}


@ajax_request
@login_required
def operator_set(request):

    data = json.loads(request.POST.get('data'))
    op_model = data.get('op_model')
    bank_model = data.get('bank_model')
    bank_model_id = bank_model.get('id')
    op_model_id = op_model.get('id')
    if op_model_id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_operator')):
            return {'status':False, 'message':u'У вас нет прав на изменение информации о провайдере'}
        item = Operator.objects.get(id=op_model_id)
        form = OperatorForm(op_model, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_operator')):
            return {'status':False, 'message':u'У вас нет прав на сохранение информации о провайдере'}
        form = OperatorForm(op_model)

    if form.is_valid():
        if bank_model_id:
            bankitem = BankData.objects.get(id=bank_model_id)
            bankform = BankDataForm(bank_model, instance=bankitem)
        else:
            bankform = BankDataForm(bank_model)
        
        if bankform.is_valid():
            
            try:
                bankitem = bankform.save(commit=False)
                bankitem.save()
                log('EDIT', request.user, bankitem) if id else log('CREATE', request.user, bankitem) 
                opmodel = form.save(commit=False)
                opmodel.bank=bankitem
                opmodel.save()
                res={"status": True}
                log('EDIT', request.user, opmodel) if id else log('CREATE', request.user, opmodel) 
            except Exception, e:
                res={"status": False, "message": str(e)}
        else:
            res={"status": False, "errors": bankform._errors}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def get_pool_by_ipinuse(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.ippool_view')):
        return {'status':True,'result':None}
    ipinuse = request.POST.get('ipinuse',None)
    res = None
    if ipinuse and ipinuse!='None':
        item = IPInUse.objects.filter(id=ipinuse)
        if not item:
            return {'status':False, 'message': 'Pool id item with id=%s not found' % ipinuse}
       
        res = item[0].pool.id
        return {"result": res, 'status':True}
    
    return {"result": res, 'status':False}


@ajax_request
@login_required
def account_exists(request):
    if  not request.user.is_staff==True:
        return {'status':False,'message': u'У вас нет прав на просмотр этой информации'}
    username = request.POST.get('username',None)
    res = False
    if username and username!='None':
        item = Account.objects.filter(username=username)
        if item:
            return {'status':True, 'message': 'Account item with username=%s found' % username}
  
        return {'status':False}
    
    return {'status':False}

@ajax_request
@login_required
def tariffs(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
        return {'status':True,'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    normal_fields = bool(request.POST.get('normal_fields',False))

    if id and id!='None':
        items = Tariff.objects.all_with_deleted().filter(id=id)
        if not items:
            return {'status':False, 'message': 'Tariff item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = Tariff.objects.all().order_by('-name')
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def cities(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.city_view')):
        return {'status':True,'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    if id and id!='None':
        items = City.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'City item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = City.objects.all().order_by('name')
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def cities_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_city')):
            return {'status':False, 'message':u'У вас нет прав на изменение городов'}
        item = City.objects.get(id=id)
        form = CityForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_city')):
            return {'status':False, 'message':u'У вас нет прав на добавление городов'}
        form = CityForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def cities_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_city')):
        return {'status':False, 'message':u'У вас нет прав на удаление городов'}
    id = int(request.POST.get('id',0))
    if id:
        model = City.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "City not found"}
    
    
@ajax_request
@login_required
def accounthardware(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.accounthardware_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    account_id = request.POST.get('account_id',None)
    hardware_id = request.POST.get('hardware_id',None)
    if id and id!='None':
        items = AccountHardware.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'AccountHardware item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
    elif account_id:
        items = AccountHardware.objects.filter(account__id=account_id)
    elif hardware_id:
        items = AccountHardware.objects.filter(hardware__id=v)
    else:
        items = AccountHardware.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def accounthardware_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_accounthardware')):
            return {'status':False, 'message':u'У вас нет прав на изменение оборудования аккаунта'}
        item = AccountHardware.objects.get(id=id)
        form = AccountHardwareForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_accounthardware')):
            return {'status':False, 'message':u'У вас нет прав на добавление оборудования аккаунта'}
        form = AccountHardwareForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            res={"status": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def accounthardware_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_accounthardware')):
        return {'status':False, 'message':u'У вас нет прав на удаление оборудования аккаунта'}
    id = int(request.POST.get('id',0))
    if id:
        model = AccountHardware.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "AccountHardware not found"}

@ajax_request
@login_required
def news(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.news_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)

    if id and id!='None':
        items = News.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'News item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
    else:
        items = News.objects.all()
        
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def news_set(request):
    
    
    data = json.loads(request.POST.get('data', '{}'))
    id = data.get('id')
    accounts = data.get('accounts')
    model = data.get('model')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_news')):
            return {'status':False, 'message':u'У вас нет прав на изменение новости'}
        item = News.objects.get(id=id)
        form = NewsForm(model, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_news')):
            return {'status':False, 'message':u'У вас нет прав на добавление новости'}
        form = NewsForm(model)
        
    if form.is_valid():
        try:
            item = form.save(commit=False)

            item.save()
            log('EDIT', request.user, item) if id else log('CREATE', request.user, item) 
            if not id and accounts:
                for account in accounts:
                    AccountViewedNews.objects.create(news = item, account = Account.objects.get(id=account), viewed=False)
            elif not id and not accounts and (item.private or item.agent):
                for account in Account.objects.all().values('id'):
                    AccountViewedNews.objects.create(news = item, account = Account.objects.get(id=account), viewed=False)
            res={"status": True, 'id':item.id}
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def news_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_news')):
        return {'status':False, 'message':u'У вас нет прав на удаление новости'}
    id = int(request.POST.get('id',0))
    if id:
        model = News.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "News not found"}
    
@ajax_request
@login_required
def accounttariffs(request):
    
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.accounttarif_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    account_id = request.POST.get('account_id')
    
    items = AccountTarif.objects.filter(account__id=account_id).order_by('-datetime')

    res=[]
    for item in items:
        res.append(instance_dict(item,normal_fields=True))

    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def nasses(request):

    if  not (request.user.is_staff==True and request.user.has_perm('nas.nas_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)

    if id:
        items = Nas.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Nas item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = Nas.objects.all()
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def hardware(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.hardware_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    model_id = request.POST.get('model_id',None)
    normal_fields = bool(request.POST.get('normal_fields',None)=='True')
    if id:
        items = Hardware.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Hardware item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
    elif model_id:
         items = Hardware.objects.filter(model__id=model_id)
    else:
        items = Hardware.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def hardware_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_hardware')):
            return {'status':False, 'message': u'У вас нет прав на изменение оборудования'}
        item = Hardware.objects.get(id=id)
        form = HardwareForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_hardware')):
            return {'status':False, 'message': u'У вас нет прав на добавление оборудования'}
        form = HardwareForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit =False)
            model.save()
            res={"status": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def hardware_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_hardware')):
        return {'status':False, 'message': u'У вас нет прав на удаление оборудования'}
    id = int(request.POST.get('id',0))
    if id:
        model = Hardware.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Hardware not found"}
    
@ajax_request
@login_required
def actionlogs(request):
    if  not request.user.is_superuser==True:
        return {'status':False, 'records': [], 'totalCount':0}
    
    data = json.loads(request.POST.get("data", "{}"))
    form = ActionLogFilterForm(data)
    if form.is_valid():
        start_date =form.cleaned_data.get('start_date')
        end_data = form.cleaned_data.get('end_date')
        systemuser = form.cleaned_data.get('systemuser')

        items = LogItem.objects.filter(timestamp__gte=start_date, timestamp__lte=end_data).order_by("-timestamp")
        
        if systemuser:
            items = items.filter(user__username=systemuser.username)
    
        items = items.values("id", 'action__name', 'user__username', 'timestamp', 'serialized_data')
        res=[]
        for item in items:
            res.append(item)
        
        return {"records": res, 'status':True, 'totalCount':len(res)}
    else:
        return {'status':False, "errors": form._errors, 'message': 'Malformed request'}

@ajax_request
@login_required
def manufacturers(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.manufacturer_view')):
        return {'status':False, 'records': [], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)

    if id:
        items = Manufacturer.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Manufacturer item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = Manufacturer.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def manufacturers_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_manufacturer')):
            return {'status':False, 'message': u'У вас нет прав на изменение производителя'}
        item = Manufacturer.objects.get(id=id)
        form = ManufacturerForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_manufacturer')):
            return {'status':False, 'message': u'У вас нет прав на добавление производителя'}
        form = ManufacturerForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            res={"status": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def manufacturers_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_manufacturer')):
        return {'status':False, 'message': u'У вас нет прав на удаление производителя'}
    id = int(request.POST.get('id',0))
    if id:
        model = Manufacturer.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Manufacturer not found"}
    

@ajax_request
@login_required
def models(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.model_view')):
        return {'status':False, 'records': [], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    hardwaretype_id  = request.POST.get('hardwaretype_id',None)
    manufacturer_id  = request.POST.get('manufacturer_id',None)
    normal_fields = bool(request.POST.get('normal_fields',None)=='True')
    if id:
        items = Model.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Model item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
    else:
        items = Model.objects.all()
        if hardwaretype_id:
            items = items.filter(hardwaretype__id=hardwaretype_id)
        if manufacturer_id:
            items = items.filter(manufacturer__id=manufacturer_id)

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def models_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_model')):
            return {'status':False, 'message': u'У вас нет прав на изменение модели'}
        item = Model.objects.get(id=id)
        form = ModelHardwareForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_model')):
            return {'status':False, 'message': u'У вас нет прав на изменение модели'}
        form = ModelHardwareForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            res={"status": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def models_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_model')):
        return {'status':False, 'message': u'У вас нет прав на удаление модели'}
    id = int(request.POST.get('id',0))
    if id:
        model = Model.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Model not found"}
    
@ajax_request
@login_required
def hardwaretypes(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.hardwaretype_view')):
        return {'status':False, 'records': [], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)

    if id:
        items = HardwareType.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'HardwareType item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = HardwareType.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def dealers(request):
    
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.dealer_view')):
        return {'status':False, 'records': [], 'totalCount':0}
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)

    if id:
        items = Dealer.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Dealer item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = Dealer.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def dealers_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_dealer')):
            return {'status':False, 'message': u'У вас нет прав на изменение дилера'}
        item = Dealer.objects.get(id=id)
        form = DealerForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_dealer')):
            return {'status':False, 'message': u'У вас нет прав на изменение дилера'}
        form = DealerForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            res={"status": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def dealers_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_dealer')):
        return {'status':False, 'message': u'У вас нет прав на удаление дилера'}
    id = int(request.POST.get('id',0))
    if id:
        model = Dealer.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Dealer not found"}
    
@ajax_request
@login_required
def hardwaretypes_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_hardwaretype')):
            return {'status':False, 'message': u'У вас нет прав на изменение типа оборудования'}
        item = HardwareType.objects.get(id=id)
        form = HardwareTypeForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_hardwaretype')):
            return {'status':False, 'message': u'У вас нет прав на добавление типа оборудования'}
        form = HardwareTypeForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            res={"status": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res



@ajax_request
@login_required
def getnotsoldcards(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.card_view')):
        return {'status':False, 'records': [], 'totalCount':0}
    ids = request.POST.get('ids',None).split(',')

    if ids:
        items = Card.objects.filter(id__in=ids, sold__isnull=True)
    else:
        return { 'status':False, u'message':u'Карты не указаны'}

    res=[]
    for item in items:
        res.append(instance_dict(item, normal_fields=True))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def cards(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.card_view')):
        return {'status':False, 'records': [], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)

    if id:
        items = Card.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Card item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = Card.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def cards_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_card')):
            return {'status':False, 'message': u'У вас нет прав на изменение карты'}
        item = Card.objects.get(id=id)
        form = CardForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_card')):
            return {'status':False, 'message': u'У вас нет прав на добавление карты'}
        form = CardForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            res={"status": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def cards_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_card')):
        return {'status':False, 'message': u'У вас нет прав на удаление карт'}
    id = int(request.POST.get('id',0))
    if id:
        model = Card.objects.filter(id=id)
        if model:
            log('DELETE', request.user, model[0])
            model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Card not found"}
    
    
    
@ajax_request
@login_required
def cardsstatus_set(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_card')):
        return {'status':False, 'message': u'У вас нет прав на изменение карты'}
    data = json.loads(request.POST.get('data', '{}'))
    ids = data.get('ids',[])
    status = data.get('status',True)
    
    if ids:
        Card.objects.filter(id__in=ids).update(disabled=status)
        res={"status": True}
    else:
        res={"status": False, "message": u"Карты не указаны"}
    return res

@ajax_request
@login_required
def get_model(request):
    
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.get_model')):
        return {'status':False, 'message': u'У вас нет прав на выполнение такого запроса'}
    
    data = json.loads(request.POST.get('data', '{}'))
    id = data.get('id',None)
    table = data.get('table',None)
    fields = data.get('fields',[])
    where = data.get('where',{})

    if id:
        sql = u"SELECT %s from %s WHERE id=%s ORDER BY id ASC;" % (",".join(fields) or "*", table, id)
        from django.db import connection
        cur = connection.cursor()
        
        cur.execute(sql)
        d = dictfetchall(cur)
        res={"status": True, 'records':d, 'totalCount':len(d)}
    else:
        res={"status": False, "message": u"id не указан"}
    return res

@ajax_request
@login_required
def get_models(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.get_model')):
        return {'status':False, 'message': u'У вас нет прав на выполнение такого запроса'}
    data = json.loads(request.POST.get('data', '{}'))

    table = data.get('table',None)
    fields = data.get('fields',[])
    where = data.get('where',{})
    order = data.get('order',{})
    order_str = "ORDER BY %s" % ','.join(["%s %s" % (x, order[x]) for x in order])
     
    from django.db import connection
    cur = connection.cursor()
    
    cur.execute("SELECT %s FROM %s WHERE %s ORDER BY id ASC;" % (",".join(fields) or "*", table, " AND ".join("%s=%s" % (wh, where[wh]) for wh in where) or 'id>0'))
    d = dictfetchall(cur)
    res={"status": True, 'records':d, 'totalCount':len(d)}

    return res



@ajax_request
@login_required
def systemuser_groups(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.auth_groups')):
        return {'status':False, 'message': u'У вас нет прав на получение груп пользователя'}
    
    data = json.loads(request.POST.get('data', '{}'))

    systemuser_id = data.get('systemuser_id',None)

    if systemuser_id:
        res = User.objects.filter(username=SystemUser.objects.get(id=systemuser_id).username)
        if not res:
            return {"records": [], 'status':True, 'totalCount':0}
        res = res[0]
        res = res.groups.all().values("id")
        res = [x.get("id") for x in res]
    else:
            return {'status':False, 'message': u'Не выбран пользвоатель'}
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def hardwaretypes_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_hardwaretype')):
        return {'status':False, 'message': u'У вас нет прав на удаление типа оборудования'}
    id = int(request.POST.get('id',0))
    if id:
        model = HardwareType.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "HardwareType not found"}
    

@ajax_request
@login_required
def account(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.account_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    
    data = json.loads(request.POST.get('data', '{}'))
    fields = data.get('fields',[])
    id = data.get('id',None)
    limit = data.get('limit',None)

    if id:
        items = Account.objects.all_with_deleted().filter(id=id)
        if not items:
            return {'status':False, 'message': 'Account item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = Account.objects.all()
        if limit:
            items = items[:limit]

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def accountsfilter(request):

    if  not (request.user.is_staff==True and request.user.has_perm('billservice.account_view')):
        return {'status':True, 'records':[], 'totalCount':0}

    data = json.loads(request.POST.get('data', '[]'))
    from django.db import connection
    cur = connection.cursor()
    


    try:
        sql= u" AND ".join([u" %s %s '%s' " % (x[0],x[1], x[2].replace("%", "%%")) if type(x[2])==unicode else u" %s %s %s " % (x[0],x[1],x[2])  for x in data]) or True
        #print sql
        s=u"""SELECT DISTINCT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status, acc.last_balance_null, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name, (SELECT name FROM billservice_tariff WHERE id=get_tarif(acc.id)) as tariff_name, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,(SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address
            FROM billservice_account AS acc
            LEFT JOIN billservice_subaccount as subacc ON subacc.account_id=acc.id 
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id
            WHERE acc.deleted is Null  
            AND 
            %s
            ORDER BY acc.username ASC;"""  % unicode(sql)
        #print s
        

        cur.execute(s)

        res = dictfetchall(cur)

    except Exception, e:
        return { 'status':False, 'message':str(e)}

            
        
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def trafficclasses(request):
    if  not (request.user.is_staff==True and request.user.has_perm('nas.trafficclass_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)

    if id:
        items = TrafficClass.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TrafficClass item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = TrafficClass.objects.all().order_by("weight")

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}




@ajax_request
@login_required
def trafficclasses_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('nas.change_trafficclass')):
            return {'status':False, 'message':u'У вас нет прав на изменение класса трафика'}
        item = TrafficClass.objects.get(id=id)
        form = TrafficClassForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('nas.add_trafficclass')):
            return {'status':False, 'message':u'У вас нет прав на добавление класса трафика'}
        form = TrafficClassForm(request.POST)
        
    if form.is_valid():
        try:
            item = form.save(commit=False)
            
            if not id:
                w = TrafficClass.objects.all().order_by('-weight')
                
                if len(w):
                    m = w[0].weight+1
                else:
                    m=0
                item.weight=m
            item.save()
            res={"status": True}
            log('EDIT', request.user, item) if id else log('CREATE', request.user, item) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def trafficclasses_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('nas.delete_trafficclass')):
        return {'status':True, 'message':u'У вас нет прав на удаление класса трафика'}
    id = int(request.POST.get('id',0))
    if id:
        model = TrafficClass.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TrafficClass not found"}
    
@ajax_request
@login_required
def trafficclassnodes(request):
    if  not (request.user.is_staff==True and request.user.has_perm('nas.trafficclass_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    traffic_class_id = request.POST.get('traffic_class_id',None)

    if id:
        items = TrafficNode.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TrafficNode item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
    elif traffic_class_id:
        items = TrafficNode.objects.filter(traffic_class__id=traffic_class_id)
    else:
        items = TrafficNode.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def trafficclassnodes_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('nas.change_trafficclass')):
            return {'status':False, 'message':u'У вас нет прав на изменение класса трафика'}
        item = TrafficNode.objects.get(id=id)
        form = TrafficNodeForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('nas.add_trafficclass')):
            return {'status':False, 'message':u'У вас нет прав на добавление класса трафика'}
        form = TrafficNodeForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            #model.next_hop = '0.0.0.0'
            model.save()
            res={"status": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def trafficclassnodes_delete(request):
    if  not (request.user.is_staff==True and  request.user.has_perm('nas.delete_trafficclass')):
        return {'status':False, 'message':u'У вас нет прав на изменение класса трафика'}
    id = int(request.POST.get('id',0))
    if id:
        model = TrafficNode.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TrafficNode not found"}
    
    
@ajax_request
@login_required
def classforgroup(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.group_view')):
        return {'status':False, 'message':u'У вас нет прав на просмотр группы трафика'}
    
    fields = request.POST.get('fields',[])
    gr = request.POST.get('group',None)

    if gr:
        items = GroupTrafficClass.objects.filter(group__id=gr)
        if not items:
            return {'status':False, 'message': 'GroupTrafficClass item with id=%s not found' % id}

        res = []
        for item in items:
            res.append(item.trafficclass.id)
    else:
        return { 'status':False, 'message': u"Group id not defined"}
    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def ippools(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.ippool_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    type = request.POST.get('type',None)
    if id and id!='None':
        items = IPPool.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'IPPool item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    elif type and type!='None':
        items = IPPool.objects.filter(type=type)
    else:
        items = IPPool.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def ippools_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_ippool')):
            return {'status':False, 'message': u"У вас нет прав на изменение IP пула"}
        item = IPPool.objects.get(id=id)
        form = IPPoolForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_ippool')):
            return {'status':False, 'message': u"У вас нет прав на добавление IP пула"}
        form = IPPoolForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            res={"status": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def ippools_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_ippool')):
        return {'status':False, 'message': u"У вас нет прав на удаление IP пула"}
    id = int(request.POST.get('id',0))
    if id:
        model = IPPool.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "IPPool not found"}
    

@ajax_request
@login_required
def radiusattrs(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.radiusattrs_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    nas_id = request.POST.get('nas_id',None)
    tarif_id = request.POST.get('tarif_id',None)
    if id and id!='None':
        items = RadiusAttrs.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'RadiusAttrs item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    elif tarif_id and tarif_id!='None':
        items = RadiusAttrs.objects.filter(tarif__id=tarif_id)
    elif nas_id and nas_id!='None':
        items = RadiusAttrs.objects.filter(nas__id=nas_id)
    else:
        items = RadiusAttrs.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def radiusattrs_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_radiusattrs')):
            return {'status':False, 'message': u"У вас нет прав на изменение RADIUS атрибутов"}
        item = RadiusAttrs.objects.get(id=id)
        form = RadiusAttrsForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_radiusattrs')):
            return {'status':False, 'message': u"У вас нет прав на добавление RADIUS атрибутов"}
        form = RadiusAttrsForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            res={"status": True}
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def radiusattrs_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_radiusattrs')):
        return {'status':False, 'message': u"У вас нет прав на удаление RADIUS атрибутов"}
    id = int(request.POST.get('id',0))
    if id:
        model = RadiusAttrs.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "RadiusAttrs not found"}
    

@ajax_request
@login_required
def templates_save(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_template')):
            return {'status':False, 'message': u"У вас нет прав на изменение шаблона"}
        item = Template.objects.get(id=id)
        form = TemplateForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_template')):
            return {'status':False, 'message': u"У вас нет прав на добавление шаблона"}
        form = TemplateForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


#===
@ajax_request
@login_required
def accountprepaystrafic(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.accountprepaystraffic_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)

    if id and id!='None':
        items = AccountPrepaysTrafic.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'AccountPrepaysTrafic item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'AccountPrepaysTrafic >1 items with id=%s' % id}

    else:
        items = AccountPrepaysTrafic.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def accountprepaystrafic_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and  request.user.has_perm('billservice.change_accountprepaystraffic')):
            return {'status':True, 'message': u'У вас нет прав на изменение размера предоплаченного трафика'}
        item = AccountPrepaysTrafic.objects.get(id=id)
        form = AccountPrepaysTraficForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_accountprepaystraffic')):
            return {'status':True, 'message': u'У вас нет прав на добавление предоплаченного трафика'}
        form = AccountPrepaysTraficForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res
#===

#===
@ajax_request
@login_required
def accountprepaysradiustrafic(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.accountprepaysradiustrafic_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)

    if id and id!='None':
        items = AccountPrepaysRadiusTrafic.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'AccountPrepaysRadiusTrafic item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'AccountPrepaysRadiusTrafic >1 items with id=%s' % id}

    else:
        items = AccountPrepaysRadiusTrafic.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def accountprepaysradiustrafic_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_accountprepaysradiustraffic')):
            return {'status':True, 'message': u'У вас нет прав на изменение размера предоплаченного RADIUS трафика'}

        item = AccountPrepaysRadiusTrafic.objects.get(id=id)
        form = AccountPrepaysRadiusTraficForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_accountprepaysradiustraffic')):
            return {'status':True, 'message': u'У вас нет прав на добавление предоплаченного RADIUS трафика'}
        form = AccountPrepaysRadiusTraficForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def templates_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_template')):
        return {'status':False, 'message': u'У вас нет прав на удаление шаблона'}
    id = int(request.POST.get('id',0))
    if id:
        model = Template.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "RadiusAttrs not found"}
    
@ajax_request
@login_required
def templatetypes(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.templatetype_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    type = request.POST.get('type',None)
    if id and id!='None':
        items = TemplateType.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TemplateType item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    elif type and type!='None':
        items = Template.objects.filter(type=type)
    else:
        items = TemplateType.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}
  
@ajax_request
@login_required
def periodicalservices(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.periodicalservice_view')):
        return {'status':True, 'records':[], 'totalCount':0}

    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    tarif_id = request.POST.get('tarif',None)
    deleted = bool(request.POST.get('deleted',None)=='True')
    normal_fields = bool(request.POST.get('normal_fields',None)=='True')

    if id and id!='None':
        items = PeriodicalService.objects.filter(id=id, deleted=deleted)
        if not items:
            return {'status':False, 'message': 'PeriodicalService item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    elif tarif_id and tarif_id!='None':
        items = PeriodicalService.objects.filter(tarif__id=tarif_id, deleted=deleted)
    else:
        items = PeriodicalService.objects.filter( deleted=deleted)

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def transactions(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.transaction_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    limit = request.POST.get('limit',None)
    normal_fields = bool(request.POST.get('normal_fields',None)=='True')

    if id and id!='None':
        items = Transaction.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Transaction item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
    else:
        items = Transaction.objects.filter()
        if limit:
            items = items[:limit]
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def groups(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.group_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    normal_fields = bool(request.POST.get('normal_fields',None)=='True')
    if id and id!='None':
        items = Group.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Group item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Group >1 items with id=%s' % id}
    else:
        items = Group.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def groups_detail(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.group_view')):
        return {'status':True, 'records':[], 'totalCount':0}

    from django.db import connection
    
    cur = connection.cursor()
    cur.execute("SELECT gr.*  FROM billservice_group as gr")

    items = cur.fetchall()
    
    res=[]
    for item in items:
        id, name, direction, grtype = item
        cur.execute("SELECT name FROM nas_trafficclass WHERE id IN (SELECT trafficclass_id FROM billservice_group_trafficclass WHERE group_id=%s)", (id,))

        d = cur.fetchall()
        classnames=''
        if d:
            classnames = ''.join([unicode(x[0]) for x in d])
        res.append({'id':id, 'name': name, 'direction':direction, 'type': grtype, 'classnames': classnames})

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def onetimeservices(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.onetimeservice_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    tarif_id = request.POST.get('tarif_id',None)
    normal_fields = bool(request.POST.get('normal_fields',False)=='True')

    if id and id!='None':
        items = OneTimeService.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'OneTimeService item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    elif tarif_id and tarif_id!='None':
        items = OneTimeService.objects.filter(tarif__id=tarif_id)
    else:
        items = OneTimeService.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def trafficlimites(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.trafficlimit_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    tarif_id = request.POST.get('tarif_id',None)
    normal_fields = bool(request.POST.get('normal_fields',False)=='True')

    if id and id!='None':
        items = TrafficLimit.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TrafficLimit item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    elif tarif_id and tarif_id!='None':
        items = TrafficLimit.objects.filter(tarif__id=tarif_id)
    else:
        items = TrafficLimit.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
   
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def speedlimites(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.speedlimit_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    limit_id = request.POST.get('limit_id',None)
    normal_fields = bool(request.POST.get('normal_fields',False)=='True')

    if id and id!='None':
        items = SpeedLimit.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'SpeedLimit item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    elif limit_id and limit_id!='None':
        items = SpeedLimit.objects.filter(limit__id=limit_id)
    else:
        items = SpeedLimit.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
   
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def addonservicetariff(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.addonservicetarif_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    tarif_id = request.POST.get('tarif_id',None)
    normal_fields = bool(request.POST.get('normal_fields',False)=='True')

    if id and id!='None':
        items = AddonServiceTarif.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'AddonServiceTarif item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'AddonServiceTarif >1 items with id=%s' % id}
        
    elif tarif_id and tarif_id!='None':
        items = AddonServiceTarif.objects.filter(tarif__id=tarif_id)
    else:
        items = AddonServiceTarif.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
   
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def get_cards_nominal(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.card_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    from django.db import connection
    cur = connection.cursor()
    
    cur.execute("SELECT nominal FROM billservice_card GROUP BY nominal ORDER BY nominal ASC")
    
    res = cur.fetchall()
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def get_next_cardseries(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.card_view')):
        return {'status':True, 'records':[0], 'totalCount':1}
    from django.db import connection
    cur = connection.cursor()
    
    cur.execute("SELECT MAX(series) as series FROM billservice_card")
    
    res = cur.fetchone()[0] 
    

    res = res if res else 0
    return {"records": [res+1], 'status':True, 'totalCount':1}


@ajax_request
@login_required
def switches(request):
    if  not (request.user.is_staff==True and request.user.has_perm('nas.switch_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    if id:
        items = Switch.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Switch item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = Switch.objects.all()
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def switches_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_switch')):
            return {'status':False, 'message': u'У вас нет прав на изменение коммутаторов'}
        item = Switch.objects.get(id=id)
        form = SwitchForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_switch')):
            return {'status':False, 'message': u'У вас нет прав на добавление коммутаторов'}
        form = SwitchForm(request.POST)
        
    if form.is_valid():
        try:
            item = form.save(commit=False)
            item.save()
            res={"status": True, 'id':item.id}
            log('EDIT', request.user, item) if id else log('CREATE', request.user, item) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def switches_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_switch')):
        return {'status':False, 'message': u'У вас нет прав на удаление коммутаторов'}
        
    id = int(request.POST.get('id',0))
    if id:
        model = Switch.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Switch not found"}
    
@ajax_request
@login_required
def organizations(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.organization_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    account_id = request.POST.get('account_id',None)
    if id:
        items = Organization.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Organization item with id=%s not found' % id}
    elif account_id:
        items = Organization.objects.filter(account__id=account_id)

    else:
        items = Organization.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def banks(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.bankdata_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    if id:
        items = BankData.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Bank item with id=%s not found' % id}
    else:
        items = BankData.objects.all()


    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def banks_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_bankdata')):
            return {'status':False, 'message': u'У вас нет прав на изменение банка'}
        item = BankData.objects.get(id=id)
        form =BankDataForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_bankdata')):
            return {'status':False, 'message': u'У вас нет прав на добавление банка'}
        form = BankDataForm(request.POST)
        
    if form.is_valid():
        try:
            item = form.save(commit=False)
            item.save()
            res={"status": True, 'id':item.id}
            log('EDIT', request.user, item) if id else log('CREATE', request.user, item) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
    return res


@ajax_request
@login_required
def dealerpays(request):

    if  not (request.user.is_staff==True and request.user.has_perm('billservice.dealerpay_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    dealer_id = request.POST.get('dealer_id',None)
    
    if id:
        items = DealerPay.objects.filter(id=id)
        if not item:
            return {'status':False, 'message': 'DealerPay item with id=%s not found' % id}
    elif dealer_id:
        items = DealerPay.objects.filter(dealer__id=dealer_id)
    else:
        items = DealerPay.objects.all()


    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def dealerpay_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_dealerpay')):
            return {'status':False, 'message': u'У вас нет прав на изменение платежа'}
        item = DealerPay.objects.get(id=id)
        form = DealerPayForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_dealerpay')):
            return {'status':False, 'message': u'У вас нет прав на добавление платежа'}
        form = DealerPayForm(request.POST)
        
    if form.is_valid():
        try:
            item = form.save(commit=False)
            item.save()
            res={"status": True, 'id':item.id}
            log('EDIT', request.user, item) if id else log('CREATE', request.user, item) 
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
    return res


@ajax_request
@login_required
def returncards(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_card')):
        return {'status':False, 'message': u'У вас нет прав на изменение состояния карт'}
    data = json.loads(request.POST.get('data', '{}'))
    dealer_id = data.get('dealer_id',None)
    cards = data.get('cards',[])
    if cards and dealer_id:
        from django.db import connection
        
        cur = connection.cursor()
        
        try:
            for card in cards:
                cur.execute("DELETE FROM billservice_salecard_cards WHERE card_id=%s", (card, ))
            Card.objects.filter(id__in=cards).update(sold=None)
            res={"status": True}
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "message": u"Карты не указаны"}
    return res

@ajax_request
@login_required
def salecards(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.salecard_view')):
        return {'status':False, 'records':[], 'totalCount':0}
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    dealer_id = request.POST.get('dealer_id',None)
    
    if id:
        items = SaleCard.objects.filter(id=id)
        if not item:
            return {'status':False, 'message': 'SaleCard item with id=%s not found' % id}
    elif dealer_id:
        items = SaleCard.objects.filter(dealer__id=dealer_id)
    else:
        items = SaleCard.objects.all()


    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def salecards_set(request):
    
    data = json.loads(request.POST.get('data', '{}'))
    id = data.get('model',{}).get('id')
    cards = data.get('cards',[])
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_salecard')):
            return {'status':False, 'message': u'У вас нет прав на изменение продажи карт'}
        item = SaleCard.objects.get(id=id)
        form =SaleCardForm(data.get('model',{}), instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_salecard')):
            return {'status':False, 'message': u'У вас нет прав на добавление продажи карт'}
        form = SaleCardForm(data.get('model',{}))
        
    if form.is_valid():
        try:
            item = form.save(commit=False)
            item.save()
            log('EDIT', request.user, item) if id else log('CREATE', request.user, item) 
            if cards:
                for card in cards:
                    c = Card.objects.get(id=card)
                    c.sold = item.created
                    c.save()
                    item.cards.add(c)
                    log('EDIT', request.user, c)
            res={"status": True, 'id':item.id}
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
    return res

@ajax_request
@login_required
def salecards_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_salecard')):
        return {'status':False, 'message': u'У вас нет прав на удаление продажи карт'}
    id = int(request.POST.get('id',0))
    if id:
        model = SaleCard.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SaleCard not found"}
    

@ajax_request
@login_required
def tpchange_save(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_accounttarif')):
            return {'status':False, 'message': u'У вас нет прав на изменение связки тарифного плана'}
        item = AccountTarif.objects.get(id=id)
        form = AccountTariffForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_accounttarif')):
            return {'status':False, 'message': u'У вас нет прав на добавяление связки тарифного плана продажи карт'}
        form = AccountTariffForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            res={"success": True}
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        except Exception, e:
            res={"success": False, "message": str(e)}
    else:
        res={"success": False, "errors": form._errors}
    
    return res




@login_required
@ajax_request
#@transaction.commit_manually
def tariffs_set(request):
    
    if  not request.user.is_staff==True:
        return {'status':False, 'message': u'У вас нет прав на создание/изменение тарифного плана'}

    
    data = request.POST.get("data", {})
    
    js = json.loads(data)


    if js['access_parameters']:
        if 'id' in js['access_parameters']:
            item = AccessParameters.objects.get(id=js['access_parameters']['id'])
            form = AccessParametersForm(js['access_parameters'], instance=item)
        else:
            form = AccessParametersForm(js['access_parameters'])
        
        
        if form.is_valid():
            access_parameters = form.save(commit=False)
            access_parameters.save()
            log('EDIT', request.user, access_parameters) if 'id' in js['access_parameters'] else log('CREATE', request.user, access_parameters) 
        else:
            transaction.rollback()
            return {'status':False, 'errors': form._errors}
        
        speeditem_ids = []
        
        for speed in js.get('speeds', []):
            speed['access_parameters']=access_parameters.id
            if speed.get('id'):
                item = TimeSpeed.objects.get(id=speed.get('id'))
                form = TimeSpeedForm(speed, instance=item)
            else:
                form = TimeSpeedForm(speed)

            if form.is_valid():
                speeditem = form.save(commit=False)
                speeditem.save()
                log('EDIT', request.user, speeditem) if speed.get('id') else log('CREATE', request.user, speeditem) 
                
            else:
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            speeditem_ids.append(speeditem.id)


        for d in TimeSpeed.objects.filter(access_parameters=access_parameters).exclude(id__in=speeditem_ids):
            log('DELETE', request.user, d)
            d.delete()
                
    if js.get('model'):
        if js.get('model').get('id'):
            if not request.user.has_perm('billservice.change_tariff'):
                transaction.rollback()
                return {'status':False, 'message': u'У вас нет прав на изменение тарифного плана'}
            item = Tariff.objects.get(id=js['model']['id'])
            form = TariffForm(js['model'], instance=item)
        else:
            if not request.user.has_perm('billservice.add_tariff'):
                transaction.rollback()
                return {'status':False, 'message': u'У вас нет прав на добавление тарифного плана'}
            js['model']['access_parameters']=access_parameters.id
            form = TariffForm(js['model'])
            
        
        if form.is_valid():
            tariff = form.save(commit=False)
            tariff.save()
        else:
            transaction.rollback()
            return {'status':False, 'errors': form._errors}
        

        
    
    if js['periodicalservices']:
        
        periodicalservices_ids = []
        for periodicalservice in js.get('periodicalservices', []):
            periodicalservice['tarif']=tariff.id
            if periodicalservice.get('id'):
                
                item = PeriodicalService.objects.get(id=periodicalservice.get('id'))
                form = PeriodicalServiceForm(periodicalservice, instance=item)
            else:
                form = PeriodicalServiceForm(periodicalservice)
            
        
            if form.is_valid():
                periodicalservice_item = form.save(commit=False)
                periodicalservice_item.save()
                log('EDIT', request.user, periodicalservice_item) if periodicalservice.get('id') else log('CREATE', request.user, periodicalservice_item) 

            else:
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            periodicalservices_ids.append(periodicalservice_item.id)
        

        if periodicalservices_ids:
            for d in PeriodicalService.objects.filter(tarif=tariff).exclude(id__in=periodicalservices_ids):
                log('DELETE', request.user, d)
                d.delete()
    else:
        PeriodicalService.objects.filter(tarif=tariff).update(deleted=True, deactivated = datetime.datetime.now())
        
    if js['addonservices']:
        
        addonservices_ids = []
        for obj in js.get('addonservices', []):
            obj['tarif']=tariff.id
            if obj.get('id'):
                
                item = AddonServiceTarif.objects.get(id=obj.get('id'))
                form = AddonServiceTarifForm(obj, instance=item)

            else:

                form = AddonServiceTarifForm(obj)
            
        
            if form.is_valid():

                addonservice_item = form.save(commit=False)
                addonservice_item.save()
                
                log('EDIT', request.user, addonservice_item) if obj.get('id') else log('CREATE', request.user, addonservice_item)
            else:

                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            addonservices_ids.append(addonservice_item.id)
        

        if addonservices_ids:
            for d in AddonServiceTarif.objects.filter(tarif=tariff).exclude(id__in=addonservices_ids):
                log('DELETE', request.user, d)
                d.delete()
    else:
        for d in AddonServiceTarif.objects.filter(tarif=tariff):
            log('DELETE', request.user, d)
            d.delete()
            
    if js.get('onetimeservices'):
        
        onetimeservices_ids = []
        for onetimeservice in js.get('onetimeservices', []):
            onetimeservice['tarif']=tariff.id
            if onetimeservice.get('id'):
                
                item = OneTimeService.objects.get(id=onetimeservice.get('id'))
                form = OneTimeServiceForm(onetimeservice, instance=item)

            else:

                form = OneTimeServiceForm(onetimeservice)
            
        
            if form.is_valid():

                onetimeservice_item = form.save(commit=False)
                onetimeservice_item.save()
                log('EDIT', request.user, onetimeservice_item) if onetimeservice.get('id') else log('CREATE', request.user, onetimeservice_item)

            else:

                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            onetimeservices_ids.append(onetimeservice_item.id)
        

        if onetimeservices_ids:
            for d in OneTimeService.objects.filter(tarif=tariff).exclude(id__in=onetimeservices_ids):
                log('DELETE', request.user, d)
                d.delete()
    else:
        for d in OneTimeService.objects.filter(tarif=tariff):
            log('DELETE', request.user, d)
            d.delete()
        
    if js.get('limites'):
        
        limites_ids = []
        speedlimites_ids = []
        for (limit, speedlimit) in js.get('limites', []):
            limit['tarif']=tariff.id
            if limit.get('id'):

                item = TrafficLimit.objects.get(id=limit.get('id'))
                form = TrafficLimitForm(limit, instance=item)

            else:

                form = TrafficLimitForm(limit)
            
        
            if form.is_valid():

                limit_item = form.save(commit=False)
                limit_item.save()
                log('EDIT', request.user, limit_item) if limit.get('id') else log('CREATE', request.user, limit_item)

            else:

                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            limites_ids.append(limit_item.id)
            
            if limit_item.action ==0:
                for d in SpeedLimit.objects.filter(limit=limit_item):
                    log('DELETE', request.user, d)
                    d.delete()
            elif  limit_item.action ==1:
                if speedlimit:
                    speedlimit['limit']=limit_item.id
                    if speedlimit.get('id'):
                        
                        item = SpeedLimit.objects.get(id=speedlimit.get('id'))
                        form = SpeedLimitForm(speedlimit, instance=item)
                    else:
                        form = SpeedLimitForm(speedlimit)
    
                    if form.is_valid():
                        speedlimit_item = form.save(commit=False)
                        speedlimit_item.save()
                        log('EDIT', request.user, speedlimit_item) if speedlimit.get('id') else log('CREATE', request.user, speedlimit_item)

                    else:

                        transaction.rollback()
                        return {'status':False, 'errors': form._errors}
                    speedlimites_ids.append(speedlimit_item.id)
    
            if speedlimites_ids:
                for d in SpeedLimit.objects.filter(limit=limit_item).exclude(id__in=speedlimites_ids):
                    log('DELETE', request.user, d)
                    d.delete()
            
        if limites_ids:
            for d in TrafficLimit.objects.filter(tarif=tariff).exclude(id__in=limites_ids):
                log('DELETE', request.user, d)
                d.delete()
                
    else:
        for tl in TrafficLimit.objects.filter(tarif=tariff):
             for d in SpeedLimit.objects.filter(limit=tl):
                 log('DELETE', request.user, d)
                 d.delete()
             log('DELETE', request.user, tl)
             tl.delete()
            
    if js.get('time_access_service'):
        obj = js.get('time_access_service')
        if obj.get('id'):
            
            item = TimeAccessService.objects.get(id=obj.get('id'))
            form = TimeAccessServiceForm(obj, instance=item)

        else:

            form = TimeAccessServiceForm(obj)
        
    
        if form.is_valid():

            timeaccessservice = form.save(commit=False)
            timeaccessservice.save()
            log('EDIT', request.user, timeaccessservice) if obj.get('id') else log('CREATE', request.user, timeaccessservice)
            tariff.time_access_service = timeaccessservice
            tariff.save()

        else:

            transaction.rollback()
            return {'status':False, 'errors': form._errors}

        
        time_access_nodes_ids = []
        
        for timeaccessnode in js.get('timeaccessnodes', []):

            timeaccessnode['time_access_service']=timeaccessservice.id
            if timeaccessnode.get('id'):
                item = TimeAccessNode.objects.get(id=timeaccessnode.get('id'))
                form = TimeAccessNodeForm(timeaccessnode, instance=item)

            else:

                form = TimeAccessNodeForm(timeaccessnode)

            if form.is_valid():
                timeaccessnode_item = form.save(commit=False)
                timeaccessnode_item.save()
                log('EDIT', request.user, timeaccessnode_item) if timeaccessnode.get('id') else log('CREATE', request.user, timeaccessnode_item)
            else:
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            time_access_nodes_ids.append(timeaccessnode_item.id)
            
        if time_access_nodes_ids:
            for d in TimeAccessNode.objects.filter(time_access_service=timeaccessservice).exclude(id__in=time_access_nodes_ids):
                log('DELETE', request.user, d)
                d.delete()
    else:
        if tariff.time_access_service:
            for d in TimeAccessNode.objects.filter(id=tariff.time_access_service):
                log('DELETE', request.user, d)
                d.delete()
            log('DELETE', request.user, tariff.time_access_service)
            tariff.time_access_service.delete()

    if js.get('traffic_transmit_service'):
        if 'id' in js.get('traffic_transmit_service'):
            item = TrafficTransmitService.objects.get(id=js.get('traffic_transmit_service')['id'])
            form = TrafficTransmitServiceForm(js.get('traffic_transmit_service'), instance=item)

        else:

            form = TrafficTransmitServiceForm(js.get('traffic_transmit_service', {}))
            
        
        if form.is_valid():

            traffic_transmit_service = form.save(commit=False)
            traffic_transmit_service.save()
            log('EDIT', request.user, traffic_transmit_service) if 'id' in js.get('traffic_transmit_service') else log('CREATE', request.user, traffic_transmit_service)
            tariff.traffic_transmit_service = traffic_transmit_service
            tariff.save()

        else:
            transaction.rollback()
            return {'status':False, 'errors': form._errors}
        
        traffictransmitnodes_ids = []
        for traffictransmitnode in js.get('traffictransmitnodes', []):

            traffictransmitnode['traffic_transmit_service']=traffic_transmit_service.id
            if traffictransmitnode.get('id'):
                item = TrafficTransmitNodes.objects.get(id=traffictransmitnode.get('id'))
                form = TrafficTransmitNodeForm(traffictransmitnode, instance=item)

            else:

                form = TrafficTransmitNodeForm(traffictransmitnode)

            if form.is_valid():
                traffictransmitnode_item = form.save(commit=False)
                traffictransmitnode_item.save()
                log('EDIT', request.user, traffictransmitnode_item) if traffictransmitnode.get('id') else log('CREATE', request.user, traffictransmitnode_item)
            else:

                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            traffictransmitnodes_ids.append(traffictransmitnode_item.id)
            
        if traffictransmitnodes_ids:
            for d in TrafficTransmitNodes.objects.filter(traffic_transmit_service=traffic_transmit_service).exclude(id__in=traffictransmitnodes_ids):
                log('DELETE', request.user, d)
                d.delete()
            
        prepaidtraffic_ids = []
        for prepaidtrafficnode in js.get('prepaidtrafficnodes', []):

            prepaidtrafficnode['traffic_transmit_service']=traffic_transmit_service.id
            if prepaidtrafficnode.get('id'):
                item = PrepaidTraffic.objects.get(id=prepaidtrafficnode.get('id'))
                form = PrepaidTrafficForm(prepaidtrafficnode, instance=item)

            else:

                form = PrepaidTrafficForm(prepaidtrafficnode)

            if form.is_valid():
                prepaidtraffictransmitnode_item = form.save(commit=False)
                prepaidtraffictransmitnode_item.save()
                log('EDIT', request.user, prepaidtraffictransmitnode_item) if prepaidtrafficnode.get('id') else log('CREATE', request.user, prepaidtraffictransmitnode_item)
            else:

                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            prepaidtraffic_ids.append(prepaidtraffictransmitnode_item.id)
        if traffictransmitnodes_ids:
            for d in PrepaidTraffic.objects.filter(traffic_transmit_service=traffic_transmit_service).exclude(id__in=prepaidtraffic_ids):
                log('DELETE', request.user, d)
                d.delete()
            
    else:
        if tariff.traffic_transmit_service:
            for d in TrafficTransmitService.objects.filter(id=tariff.traffic_transmit_service.id):
                log('DELETE', request.user, d)
                d.delete()
            for d in TrafficTransmitNodes.objects.filter(traffic_transmit_service=tariff.traffic_transmit_service):
                log('DELETE', request.user, d)
                d.delete()
            
    if js.get('radius_traffic_service'):
        if 'id' in js.get('radius_traffic_service'):
            item = RadiusTraffic.objects.get(id=js.get('radius_traffic_service')['id'])
            form = RadiusTrafficForm(js.get('radius_traffic_service'), instance=item)

        else:

            form = RadiusTrafficForm(js.get('radius_traffic_service', {}))
            
        
        if form.is_valid():

            radius_traffic_service = form.save(commit=False)
            radius_traffic_service.save()
            log('EDIT', request.user, radius_traffic_service) if 'id' in js.get('radius_traffic_service') else log('CREATE', request.user, radius_traffic_service)
            tariff.radius_traffic_transmit_service = radius_traffic_service
            tariff.save()

        else:

            transaction.rollback()
            return {'status':False, 'errors': form._errors}
        
        radiustraffictransmitnodes_ids = []
        for radtraffictransmitnode in js.get('radiustrafficnodes', []):

            radtraffictransmitnode['radiustraffic']=radius_traffic_service.id
            if radtraffictransmitnode.get('id'):
                item = RadiusTrafficNode.objects.get(id=radtraffictransmitnode.get('id'))
                form = RadiusTrafficNodeForm(radtraffictransmitnode, instance=item)

            else:

                form = RadiusTrafficNodeForm(radtraffictransmitnode)

            if form.is_valid():
                radtraffictransmitnode_item = form.save(commit=False)
                radtraffictransmitnode_item.save()
                #log('EDIT', request.user, radtraffictransmitnode_item) if 'id' in radtraffictransmitnode.get('id') else log('CREATE', request.user, radtraffictransmitnode_item)
            else:

                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            radiustraffictransmitnodes_ids.append(radtraffictransmitnode_item.id)
            
        if radiustraffictransmitnodes_ids:
            for d in RadiusTrafficNode.objects.filter(radiustraffic=radius_traffic_service).exclude(id__in=radiustraffictransmitnodes_ids):
                log('DELETE', request.user, d)
                d.delete()
        
    else:
        if tariff.radius_traffic_transmit_service:
            for d in RadiusTrafficNode.objects.filter(radiustraffic=tariff.radius_traffic_transmit_service):
                log('DELETE', request.user, d)
                d.delete()
            log('DELETE', request.user, tariff.radius_traffic_transmit_service)
            tariff.radius_traffic_transmit_service.delete()
            
    log('EDIT', request.user, tariff) if js.get('model').get('id') else log('CREATE', request.user, tariff) 
    transaction.commit()

    return {'status':True, 'tariff_id':tariff.id}

@ajax_request
@login_required
def groups_save(request):
    
    id = request.POST.get('id')
    traffic_classes = request.POST.get('traffic_classes','').split(',')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_group')):
            return {'status':False, 'message': u'У вас нет прав на изменение группы трафика'}

        item = Group.objects.get(id=id)
        form = GroupForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_group')):
            return {'status':False, 'message': u'У вас нет прав на добавление группы трафика'}
        form = GroupForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model)
            if id:
                for d in GroupTrafficClass.objects.filter(group=model):
                    log('DELETE', request.user, d)
                    d.delete()
            for item in traffic_classes:
                gt = GroupTrafficClass.objects.create(group=model, trafficclass = TrafficClass.objects.get(id=item))
                log('CREATE', request.user, gt)
            res={"status": True}
        except Exception, e:
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
    
    return res

@ajax_request
@login_required
def nas_save(request):
    id = request.POST.get('id')

    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('nas.change_nas')):
            return {'status':False, 'message': u'У вас нет прав на изменение сервера доступа'}
        nas = Nas.objects.get(id=id)
        form = NasForm(request.POST, instance = nas)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('nas.add_nas')):
            return {'status':False, 'message': u'У вас нет прав на добавление сервера доступа'}
        form = NasForm(request.POST)
        
    
    if form.is_valid():
        item = form.save(commit=False)
        item.save()
        log('EDIT', request.user, item) if id else log('CREATE', request.user, item) 
        return {"status": True, "message": 'yes'}
    else:
        return {"status": False, "message": form._errors}

@ajax_request
@login_required
def contracttemplates_set(request):
    id = request.POST.get('id')

    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_contracttemplate')):
            return {'status':False, 'message': u'У вас нет прав на изменение шаблона номера договора'}
        item = ContractTemplate.objects.get(id=id)
        form = ContractTemplateForm(request.POST, instance = item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_contracttemplate')):
            return {'status':False, 'message': u'У вас нет прав на добавление шаблона номера договора'}
        form = ContractTemplateForm(request.POST)
        
    
    if form.is_valid():
        model = form.save(commit = False)
        model.save()
        log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        return {"status": True}
    else:
        return {"status": False, "message": form._errors}

@ajax_request
@login_required
def contracttemplate_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_contracttemplate')):
        return {'status':False, 'message': u'У вас нет прав на удаление шаблона номера договора'}
    id = int(request.POST.get('id',0))
    if id:
        model = ContractTemplate.objects.get(id=id)
        log('DELETE', request.user, model)
        model.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "ContractTemplate not found"}
    

@login_required
@ajax_request
def settlementperiod_save(request):
    id = request.POST.get('id')

    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_settlementperiod')):
            return {'status':False, 'message': u'У вас нет прав на изменение расчётного периода'}
        item = SettlementPeriod.objects.get(id=id)
        form = SettlementPeriodForm(request.POST, instance = item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_settlementperiod')):
            return {'status':False, 'message': u'У вас нет прав на добавление расчётного периода'}
        form = SettlementPeriodForm(request.POST)
        
    
    if form.is_valid():
        d = form.save(commit=False)
        d.save()
        log('EDIT', request.user, d) if id else log('CREATE', request.user, d) 
        return {"status": True}
    else:
        return {"status": False, "message": form._errors}


@login_required
@ajax_request
def addonservices_set(request):
    data = json.loads(request.POST.get('data', "{}"))
    id = data.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_addonservice')):
            return {'status':False, 'message': u'У вас нет прав на изменение подключаемой услуги'}
        item = AddonService.objects.get(id=id)
        form = AddonServiceForm(data, instance = item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_addonservice')):
            return {'status':False, 'message': u'У вас нет прав на изменение подключаемой услуги'}
        form = AddonServiceForm(data)
        
    
    if form.is_valid():
        d = form.save(commit=False)
        d.save()
        log('EDIT', request.user, d) if id else log('CREATE', request.user, d) 
        return {"status": True}
    else:
        return {"status": False, "message": form._errors}
    
@ajax_request
@login_required
def settlementperiod_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_settlementperiod')):
        return {'status':False, 'message': u'У вас нет прав на удаление расчётного периода'}
    id = int(request.POST.get('id',0))
    if id:
        for d in SettlementPeriod.objects.filter(id=id):
            log('DELETE', request.user, d)
            d.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Settlementperiod not found"}

@ajax_request
@login_required
def addonservices_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_addonservice')):
        return {'status':False, 'message': u'У вас нет прав на удаление подключаемой услуги'}
    id = int(request.POST.get('id',0))
    if id:
        for d in AddonService.objects.filter(id=id):
            log('DELETE', request.user, d)
            d.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "AddonService not found"}



@ajax_request
@login_required
def groups_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_group')):
        return {'status':False, 'message': u'У вас нет прав на удаление группы трафика'}
    id = int(request.POST.get('id',0))
    if id:
        for d in Group.objects.filter(id=id):
            log('DELETE', request.user, d)
            d.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Group not found"}


@ajax_request
@login_required
def tariffs_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_tariff')):
        return {'status':False, 'message': u'У вас нет прав на удаление тарифа'}
    id = int(request.POST.get('id',0))
    if id:
        try:
            item = Tariff.objects.all_with_deleted().get(id=id)
            log('DELETE', request.user, item)
            item.delete()
        except Exception, e:
            return {"status": False, "message": u"Указанный тарифный план не найден %s" % str(e)}
 

        
        

        return {"status": True}
    else:
        return {"status": False, "message": "AccountTarif not found"}
  
  
@ajax_request
@login_required
def accounttariffs_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_accounttarif')):
        return {'status':False, 'message': u'У вас нет прав на удаление связки тарифа'}
    id = int(request.POST.get('id',0))
    if id:
        try:
            item = AccountTarif.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный тарифный план не найден тарифный план %s" % str(e)}
        if item.datetime<datetime.datetime.now():
            return {"status": False, "message": u"Невозможно удалить вступивший в силу тарифный план"}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "AccountTarif not found"}
  
@ajax_request
@login_required
def suspendedperiod_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_suspendedperiod')):
        return {'status':False, 'message': u'У вас нет прав на удаление периода простоя'}
    id = int(request.POST.get('id',0))
    if id:
        try:
            item = SuspendedPeriod.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный период не найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SuspendedPeriod not found"} 

@ajax_request
@login_required
def get_tariffs(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.tariff_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    items = Tariff.objects.all_with_deleted().order_by('name')
    res=[]
    for item in items:
        try:
            access_type = item.access_parameters.access_type
        except:
            access_type = ''
        res.append({'active':item.active,'id':item.id, 'access_type':access_type, 'name':item.name, 'deleted':item.deleted})
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def accounts_for_tarif(request):
    
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.account_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    
    tarif_id = int(request.POST.get('tarif_id', -1000))
    

    items = cache.get(str(tarif_id))
    if items:
        return {"records": items, 'status':True, 'totalCount':len(items)}
    
    from django.db import connection
    
    cur = connection.cursor()
    
    items = []
    if tarif_id==-3000:
        try:
            
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status,  org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,COALESCE((SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1), False) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address 
            FROM billservice_account AS acc 
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id 
            WHERE acc.deleted is Null and get_tarif(acc.id) is Null ORDER BY acc.username ASC;""")
            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}
    
    elif tarif_id==-1000:

        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status,  tariff.name as tariff_name, tariff.settlement_period_id, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,COALESCE((SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1), False) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address, at.datetime as accounttarif_datetime
            FROM billservice_account AS acc 
            LEFT JOIN billservice_accounttarif as at ON at.id=(SELECT id FROM billservice_accounttarif WHERE account_id=acc.id and datetime<now() ORDER BY datetime DESC LIMIT 1)
            JOIN billservice_tariff as tariff ON tariff.id=at.tarif_id
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id
            WHERE acc.deleted is Null 
            ORDER BY acc.username ASC;""" )

            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}

    elif tarif_id==-4000:#Физ лица
        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status,  tariff.name as tariff_name, tariff.settlement_period_id, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,COALESCE((SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1), False) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address, at.datetime as accounttarif_datetime
            FROM billservice_account AS acc 
            LEFT JOIN billservice_accounttarif as at ON at.id=(SELECT id FROM billservice_accounttarif WHERE account_id=acc.id and datetime<now() ORDER BY datetime DESC LIMIT 1)
            JOIN billservice_tariff as tariff ON tariff.id=at.tarif_id
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id 
            WHERE  acc.deleted is Null and  acc.id not IN (SELECT account_id FROM billservice_organization) ORDER BY acc.username ASC;""" )
            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}        

    elif tarif_id==-5000:#Юр лица
        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status,  tariff.name as tariff_name, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,COALESCE((SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1), False) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address, at.datetime as accounttarif_datetime
            FROM billservice_account AS acc 
            LEFT JOIN billservice_accounttarif as at ON at.id=(SELECT id FROM billservice_accounttarif WHERE account_id=acc.id and datetime<now() ORDER BY datetime DESC LIMIT 1)
            JOIN billservice_tariff as tariff ON tariff.id=at.tarif_id
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id 
            WHERE acc.deleted is Null and  acc.id IN (SELECT account_id FROM billservice_organization)  ORDER BY acc.username ASC;""" )
            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}        

    elif tarif_id==-12000:#Архив
        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status,   tariff.name as tariff_name, tariff.settlement_period_id, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,COALESCE((SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1), False) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address, at.datetime as accounttarif_datetime
            FROM billservice_account AS acc 
            LEFT JOIN billservice_accounttarif as at ON at.id=(SELECT id FROM billservice_accounttarif WHERE account_id=acc.id and datetime<now() ORDER BY datetime DESC LIMIT 1)
            JOIN billservice_tariff as tariff ON tariff.id=at.tarif_id
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id 
            WHERE acc.deleted is not Null  ORDER BY acc.username ASC;""" )
            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}   
    else:
        
        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status, tariff.settlement_period_id, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs, COALESCE((SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1), False) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address, at.datetime as accounttarif_datetime
            FROM billservice_account AS acc 
            JOIN billservice_accounttarif as at ON at.id=(SELECT id FROM billservice_accounttarif WHERE account_id=acc.id and datetime<now() ORDER BY datetime DESC LIMIT 1)
            JOIN billservice_tariff as tariff ON tariff.id=at.tarif_id
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id 
            WHERE acc.deleted is Null and %s=get_tarif(acc.id)  ORDER BY acc.username ASC;""", (tarif_id,) )
            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}   
    sps = SettlementPeriod.objects.all().values("id", "time_start", "autostart", "length", "length_in")
    sps_dict = {}
    for sp in sps:
        sps_dict[sp.get("id")] = sp
    #iterate accounts
    res = []
    for item in items:
        sp = sps_dict.get(item.get("settlement_period_id"))
        if sp:
                
            if sp.get("autostart"):
                time_start = item.get("accounttarif_datetime")
            else:
                time_start = sp.get("time_start")
            start, end,length = settlement_period_info(time_start, sp.get("length_in"), sp.get("length"))
            item['sp_end'] = end
        res.append(item)


    cache.set(str(tarif_id), res, 60)
    return {"records": res, 'status':True, 'totalCount':len(res)}
    
@ajax_request
@login_required
def get_accounts_for_cashier(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.cashier_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    
    data = json.loads(request.POST.get("data", "{}"))
    fullname, city, street, house, bulk, room, username, contract, phone_h, phone_m = \
    data.get("fullname"), data.get("city"), data.get("street"),  data.get("house"), data.get("bulk"),data.get("room"),  data.get("username"), data.get("agreement"), data.get("phone_h"),data.get("phone_m"),  
    items = Account.objects.all()
    
    if fullname:
        items = items.filter(fullname__icontains=fullname)
        
    if city:
        items = items.filter(city__id=city)
    
    if street:
        items = items.filter(street__id=street)
    
    if house:
        items = items.filter(house__id=house)

    if bulk:
        items = items.filter(hbulk__icontains=bulk)

    if room:
        items = items.filter(room__icontains=room)
        
    if username:
        items = items.filter(username__icontains=username)

    if contract:
        items = items.filter(contract__icontains=contract)
      
    if phone_h:
        items = items.filter(phone_h__icontains=phone_h)

    if phone_m:
        items = items.filter(phone_m__icontains=phone_m)
     
    #id, contract,username,fullname,ballance,credit,status,created,(SELECT name FROM billservice_street WHERE id=account.street_id) as street,(SELECT name FROM billservice_house WHERE id=account.house_id) as house,house_bulk,room, (SELECT name FROM billservice_tariff WHERE id=get_tarif(account.id)) as tarif_name
    items = items.extra(select={"tarif_name": "(SELECT name FROM billservice_tariff WHERE id=get_tarif(billservice_account.id))"}).values('id', 'contract','username','fullname','ballance','credit','status','created', "street__name", 'house__name', 'house_bulk', 'room', 'tarif_name')
    res = []             
    for item in items:
        
        res.append(item)
        
    return {"records": res, 'status':True, 'totalCount':len(res)}
@ajax_request
@login_required
def nas_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('nas.delete_nas')):
        return {'status':True, 'message': u'У вас нет прав на удаление сервера доступа'}
    id = request.POST.get('id')
    if id:
        for d in Nas.objects.filter(id=id):
            log('DELETE', request.user, d)
            d.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Nas not found"}


@ajax_request
@login_required
def subaccount_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_subaccount')):
        return {'status':True, 'message': u'У вас нет прав на удаление субаккаунта'}
    id = request.POST.get('id') or request.GET.get('id')
    if id:
        #TODO: СДелать удаление субаккаунта с сервера доступа, если он там был
        item = SubAccount.objects.get(id=id)
        if item.vpn_ipinuse:
            for d in IPInUse.objects.filter(id=item.vpn_ipinuse):
                log('DELETE', request.user, d)
                d.delete()
        if item.ipn_ipinuse:
            for d in IPInUse.objects.filter(id=item.ipn_ipinuse):
                log('DELETE', request.user, d)
                d.delete()
        if item.vpn_ipv6_ipinuse:
            for d in IPInUse.objects.filter(id=item.vpn_ipv6_ipinuse):
                log('DELETE', request.user, d)
                d.delete()
        
        log('DELETE', request.user, item)
        item.delete()
        
        return {"status": True}
    else:
        return {"status": False, "message": "SubAccount not found"}

@ajax_request
@login_required
def account_delete(request):
    id = request.POST.get('id')
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_account')):
        return {'status':True, 'message': u'У вас нет прав на удаление аккаунта'}
    if id:
        try:
           model = Account.objects.all_with_deleted().get(id=id)
           log('DELETE', request.user, model)
           model.delete()
        except Exception, e:
            return {"status": False, "message": "%s" % str(e)}
        
        return {"status": True}
    else:
        return {"status": False, "message": "Account not found"}
    
@ajax_request
@login_required
def document_save(request):
    
    id = request.POST.get('id')
    if id:
        item = Document.objects.get(id=id)
        form = DocumentModelForm(request.POST, instance=item)
    else:
        form = DocumentModelForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            res={"success": True}
        except Exception, e:

            res={"success": False, "message": str(e)}
    else:
        res={"success": False, "errors": form._errors}
    return res

@ajax_request
@login_required
def streets(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.street_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    city_id = request.POST.get('city_id')
    term = request.POST.get('term')
    id = request.POST.get('id')
    items = []
    if city_id:
        if city_id and term:
            items = Street.objects.filter(city__id=city_id, name__icontains=term)
        else:
            items = Street.objects.filter(city__id=city_id)
    elif id:
        items = [Street.objects.get(id=id)]
    else:
        if term:
            items = Street.objects.filter(name__icontains=term)
        else:
            items = Street.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item))
    return {"records": res, 'status':True, 'totalCount':len(items)}

@ajax_request
@login_required
def streets_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_street')):
            return {'status':False, 'message':u'У вас нет прав на изменение улицы'}
        item = Street.objects.get(id=id)
        form = StreetForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_street')):
            return {'status':False, 'message':u'У вас нет прав на добавление улицы'}
        form = StreetForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            res={"status": True}
        except Exception, e:

            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def streets_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_street')):
        return {'status':False, 'message':u'У вас нет прав на удаление улицы'}
    id = int(request.POST.get('id',0))
    if id:
        for d in Street.objects.filter(id=id):
            log('DELETE', request.user, d)
            d.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Street not found"}
    

@ajax_request
@login_required
@transaction.commit_manually
def account_save(request):
    
    
    data = json.loads(request.POST.get("data", "{}"))
    
    model = data.get("model")
    bank = data.get("bank")
    organization = data.get("organization")
    id = model.get('id')
    tarif_id = data.get('tarif_id')

    contract = model.get('contract','')

    contracttemplate_id = model.get('contracttemplate_id',None)

    username = model.get('username','')
  
        

    newcontract=False
    acc = None
    if id:
        #print "change", request.user.has_perm('billservice.change_account')
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_account')):
            transaction.rollback()
            return {'status':False, 'message':u'У вас нет прав на изменение аккаунта'}
        acc = Account.objects.all_with_deleted().get(id=id)
        
        if acc.contract!= contract or contracttemplate_id:
            #new

            newcontract=True
        a=AccountForm(model, instance=acc)
    else:
        if  not (request.user.is_staff==True and  request.user.has_perm('billservice.add_account')):
            transaction.rollback()
            return {'status':False, 'message':u'У вас нет прав на добавление аккаунта'}
            newcontract=True
        a=AccountForm(model)

    res=[]



    if a.is_valid():

        contr = None
        if contract and contracttemplate_id:

            contr = ContractTemplate.objects.filter(template=contract)

            if contr:

                contr=contr[0]
        else:
            contr = None
            if contracttemplate_id:
                contr = ContractTemplate.objects.get(id=contracttemplate_id)

        if newcontract and contr:

            if not acc:
                accid=Account.objects.all().order_by("-id")[0].id+1
            else:
                accid = acc.id

            contract_template = contr.template if contr else contract
            contract_counter = contr.counter if contr else 0

            year=a.cleaned_data.get("created").year
            month=a.cleaned_data.get("created").month
            day=a.cleaned_data.get("created").day
            hour=a.cleaned_data.get("created").hour
            minute=a.cleaned_data.get("created").minute
            second=a.cleaned_data.get("created").second
            contract_num=contr.counter
            
            
            d={'account_id':accid,'username':username, 'year':year,'month':month, 'day':day, 'hour':hour, 'minute':minute,'second':second, 'contract_num':contract_num}
            #d.update(model.__dict__)

            contract = contract_template % d
            if contr:
                contr.count = contr.counter+1 

        
        try:
            item = a.save(commit=False)
            item.save()
            

            o = Organization.objects.filter(account=item)
            if o:
                org = o[0]
                bankdata = org.bank
                if org and not organization:
                    log('DELETE', request.user, bankdata)
                    bankdata.delete()
                    log('DELETE', request.user, org)
                    org.delete()
                org = OrganizationForm(organization, instance = org)
                if not org.is_valid(): 
                    transaction.rollback()
                    return {"status": False, "errors": org._errors, 'message': u'Организация указана с ошибками'}
                    
                bank = BankDataForm(bank, instance = bankdata)
                if not bank.is_valid(): 
                    transaction.rollback()
                    return {"status": False, "errors": bank._errors, 'message': u'Банковские данные  должны быть указаны правильно'}

                bank = bank.save(commit = False)
                bank.save()
                organization = org.save(commit = False)
                organization.save()
                log('EDIT', request.user, bank)
                log('EDIT', request.user, organization)
            elif organization:

                org = OrganizationForm(organization)
           
                if org.is_valid(): 
              
                    organization = org.save(commit = False)
               
                    b = BankDataForm(bank)
                    if  b.is_valid():
                        bank = b.save(commit=False)
                        bank.save()
                        log('CREATE', request.user, bank) 
                        organization.bank = bank
                        
                        organization.account = item
                        organization.save()
                        log('CREATE', request.user, organization) 
                    else:
                        transaction.rollback()
                        return {"status": False, "errors": b._errors, 'message': u'Банковские данные  должны быть указаны правильно'}
                else:
                    transaction.rollback()
                    return {"status": False, "errors": org._errors, 'message': u'Организация указана с ошибками'}

            if not id and tarif_id and tarif_id>0:
                accounttarif = AccountTarif()
                accounttarif.account=item
                accounttarif.tarif=Tariff.objects.get(id=tarif_id)
                accounttarif.datetime = item.created
                accounttarif.save()
                log('CREATE', request.user, accounttarif) 
            if newcontract:

                item.contract = contract
                item.save()
                if contr:
                    contr.save()

            log('EDIT', request.user, item) if id else log('CREATE', request.user, item) 
            res={"status": True, 'id':item.id}
        except Exception, e:
            transaction.rollback()
            res={"status": False, "message": {'error':unicode(e)}}
    else:
        
        res={"status": False, "errors": a._errors, 'msg':u"Поля с ошибками:"+unicode('\n'.join([u'%s:%s' %(x,a._errors.get(x)) for x in a._errors]))}
    transaction.commit()
    cache.clear()
    return res

@login_required
@ajax_request
#@transaction.commit_manually()
def subaccount_save(request):
    
    #from django.core import serializers
    #from django.http import HttpResponse
    #print request
    """
    #проверить существование такого юзернейма у дрегого аккаунта
    в системе существует такой IPn ip адрес у дргого аккаунта
    в системе существует такой VPN IP адрес у другого аккаунта
     в системе существует такой IPv6 VPN IP адрес у другого аккаунта
   # в системе существует такой мак у другого аккаунта
    
    """
    if  not request.user.has_perm('billservice.add_subaccount'):
        transaction.rollback()
        return {'status':False, 'message':u'У вас нет прав на создание субаккаунтов'}
    id=None if request.POST.get('id')=='None' else request.POST.get('id')
    ipv4_vpn_pool = None if request.POST.get('ipv4_vpn_pool')=='None' else request.POST.get('ipv4_vpn_pool')
    ipv4_ipn_pool = None if request.POST.get('ipv4_ipn_pool')=='None' else request.POST.get('ipv4_ipn_pool')
    account_id = None if request.POST.get('account')=='None' else request.POST.get('account')
  
    vpn_pool = None
    if ipv4_vpn_pool:
        vpn_pool = IPPool.objects.get(id=ipv4_vpn_pool)
    ipn_pool = None
    if ipv4_ipn_pool:
        ipn_pool = IPPool.objects.get(id=ipv4_ipn_pool)
        
    cc=None
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_subaccount')):
            transaction.rollback()
            return {'status':False, 'message':u'У вас нет прав на изменение субаккаунта'}
        cc = SubAccount.objects.get(id=id)
        
        a=SubAccountForm(request.POST,instance=cc)
        f=SubAccountForm(request.POST)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_subaccount')):
            transaction.rollback()
            return {'status':False, 'message':u'У вас нет прав на добавление субаккаунта'}
        a=SubAccountForm(request.POST)

    p=request.POST
    res=[]

    
    if a.is_valid():
        try:
            subacc = a.save(commit=False)
            pass
            subacc.save()
            
        except Exception, e:
            transaction.rollback()
            res={"success": False, "errors": a._errors}
            return res

        
        # print "cc.vpn_ipinuse11",cc.vpn_ipinuse
        subaccs = 0

        #_wrapped_view() takes at least 1 argument (0 given)
        if subacc.username:
            if not id:
                subaccs = SubAccount.objects.filter(username = subacc.username ).exclude(account__id = account_id).count()
            else:
                subaccs = SubAccount.objects.exclude(id = id).filter(account__id = account_id, username = subacc.username).count()
            if subaccs>0:
                return {"status": False, 'message':u'Выбранное имя пользователя используется в другом аккаунте'}


        if subacc.ipn_mac_address:    
            if not id:
                subaccs = SubAccount.objects.exclude(account__id = account_id).filter(ipn_mac_address = subacc.ipn_mac_address).count()
            else:
                subaccs = SubAccount.objects.exclude(id = id, account__id = account_id).filter(ipn_mac_address = subacc.ipn_mac_address).count()

            if subaccs>0:
                return {"status": False, 'message':u'Выбранный мак-адрес используется в другом аккаунте'}

        if str(subacc.vpn_ip_address) not in ('','0.0.0.0', '0.0.0.0/32'):    
            if not id:
                subaccs = SubAccount.objects.exclude(account__id = account_id).filter(vpn_ip_address = subacc.vpn_ip_address).count()
            else:
                subaccs = SubAccount.objects.exclude(id = id, account__id = account_id).filter(vpn_ip_address = subacc.vpn_ip_address).count()

            if subaccs>0:
                return {"status": False, 'message':u'Выбранный vpn_ip_address используется в другом аккаунте'}

        if str(subacc.ipn_ip_address) not in ('', '0.0.0.0', '0.0.0.0/32'):    

            if not id:

                subaccs = SubAccount.objects.exclude(account__id = account_id).filter(ipn_ip_address = subacc.ipn_ip_address ).count()
            else:

                subaccs = SubAccount.objects.exclude(id = id, account__id = account_id).filter(ipn_ip_address = subacc.ipn_ip_address).count()

            if subaccs>0:
                transaction.rollback()
                return {"status": False, 'message':u'Выбранный ipn_ip_address используется в другом аккаунте'}


        if cc and cc.vpn_ipinuse:

            #vpn_pool = IPPool.objects.get(id=ipv4_vpn_pool)
            
            if  str(subacc.vpn_ip_address) not in ['0.0.0.0', '0.0.0.0/32','',None]:
                if vpn_pool:
                    if not IPy.IP(vpn_pool.start_ip).int()<=IPy.IP(subacc.vpn_ip_address).int()<=IPy.IP(vpn_pool.end_ip).int():
                        transaction.rollback()
                        return {"status": False, 'message':u'Выбранный VPN IP адрес не принадлежит указанному VPN пулу'}
                    
                
                    if cc.vpn_ipinuse.ip!=subacc.vpn_ip_address:
                        obj = subacc.vpn_ipinuse
                        obj.disabled=datetime.datetime.now()
                        obj.save()
                        log('EDIT', request.user, obj)
                        subacc.vpn_ipinuse = IPInUse.objects.create(pool=vpn_pool,ip=subacc.vpn_ip_address,datetime=datetime.datetime.now())
                        log('EDIT', request.user, subacc.vpn_ipinuse)
                else:
                    obj = subacc.vpn_ipinuse
                    obj.disabled=datetime.datetime.now()
                    obj.save()
                    subacc.vpn_ipinuse = None
                
                    
                
            elif str(subacc.vpn_ip_address) in ['','0.0.0.0', '0.0.0.0/32','',None]:

                obj = subacc.vpn_ipinuse
                obj.disabled=datetime.datetime.now()
                obj.save()
                log('EDIT', request.user, obj)
                subacc.vpn_ipinuse=None
        elif str(subacc.vpn_ip_address) not in ['','0.0.0.0', '0.0.0.0/32','',None] and vpn_pool:

            if not IPy.IP(vpn_pool.start_ip).int()<=IPy.IP(subacc.vpn_ip_address).int()<=IPy.IP(vpn_pool.end_ip).int():
                transaction.rollback()
                return {"status": False, 'message':u'Выбранный VPN IP адрес не принадлежит указанному VPN пулу'}

            ip=IPInUse(pool=vpn_pool, ip=subacc.vpn_ip_address, datetime=datetime.datetime.now())
            ip.save()
            log('CREATE', request.user, ip)
            subacc.vpn_ipinuse = ip 
            
        if cc and cc.ipn_ipinuse:


            
            if  str(subacc.ipn_ip_address) not in ['0.0.0.0', '0.0.0.0/32','',None]:
                if ipn_pool:
                    if not ipaddr.IPv4Network(ipn_pool.start_ip)<=ipaddr.IPv4Network(subacc.ipn_ip_address)<=ipaddr.IPv4Network(ipn_pool.end_ip):
                        transaction.rollback()
                        return {"status": False, 'message':u'Выбранный IPN IP адрес не принадлежит указанному IPN пулу'}
                    
                
                    if cc.ipn_ipinuse.ip!=subacc.ipn_ip_address:
                        obj = subacc.ipn_ipinuse
                        obj.disabled=datetime.datetime.now()
                        obj.save()
                        log('EDIT', request.user, obj)
                        subacc.ipn_ipinuse = IPInUse.objects.create(pool=ipn_pool,ip=subacc.ipn_ip_address,datetime=datetime.datetime.now())
                        log('CREATE', request.user, subacc.ipn_ipinuse)
                else:
                    obj = subacc.ipn_ipinuse
                    obj.disabled=datetime.datetime.now()
                    obj.save()
                    log('EDIT', request.user, obj)
                    subacc.ipn_ipinuse = None
                
                    
                
            elif str(subacc.ipn_ip_address) in ['','0.0.0.0', '0.0.0.0/32','',None]:

                obj = subacc.ipn_ipinuse
                obj.disabled=datetime.datetime.now()
                obj.save()
                log('EDIT', request.user, obj)
                subacc.ipn_ipinuse=None
        elif str(subacc.ipn_ip_address) not in ['','0.0.0.0', '0.0.0.0/32','',None] and ipn_pool:

            if not ipaddr.IPv4Network(ipn_pool.start_ip)<=ipaddr.IPv4Network(subacc.ipn_ip_address)<=ipaddr.IPv4Network(ipn_pool.end_ip):
                transaction.rollback()
                return {"status": False, 'message':u'Выбранный IPN IP адрес не принадлежит указанному IPN пулу'}

            ip=IPInUse(pool=ipn_pool, ip=subacc.ipn_ip_address, datetime=datetime.datetime.now())
            ip.save()
            log('CREATE', request.user, ip)
            subacc.ipn_ipinuse = ip 
       
        try:
            subacc.save()
            log('EDIT', request.user, subacc) if id else log('CREATE', request.user, subacc) 
            res={"status": True,'account_id':subacc.account.id}
        except Exception, e:
            transaction.rollback()
            res={"status": False, "errors": a._errors}
    else:
        res={"status": False, "errors": a._errors}
    transaction.commit()
    return res

@ajax_request
@login_required
def subaccount_delete(request):
    
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_subaccount')):
        return {'status':False, 'message':u'У вас нет прав на удаление субаккаунта'}
    id=request.POST.get('id')
    if id:
        for d in SubAccount.objects.filter(id=id):
            log('DELETE', request.user, d)
            d.delete()
        return {"success": True}
    else:
        return {"success": False,'msg':u'Субаккаунт не найден'}
    
@ajax_request
@login_required
def getipfrompool(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.ippool_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    default_ip='0.0.0.0'
    if default_ip:
        default_ip = IPy.IP(default_ip).int()
    pool_id=request.POST.get("pool_id")
    limit=int(request.POST.get("limit", 500))
    start=int(request.POST.get("start", 0))
    term=request.POST.get("term", '')
    if not pool_id:
        return {'records':[], 'status':False}
    pool = IPPool.objects.get(id=pool_id)
    #pool = IPPool.objects.all()[0]
    ipinuse = IPInUse.objects.filter(pool=pool, disabled__isnull=True)
    
    accounts_ip = SubAccount.objects.values_list('ipn_ip_address', 'vpn_ip_address')
    if term:
        ipinuse = ipinuse.filter(ip__contains=term)
    #accounts_ip = connection.sql("SELECT ipn_ip_address, vpn_ip_address FROM billservice_subaccount")
    #connection.commit()
    ipversion = 4 if pool.type<2 else  6
    accounts_used_ip = []
    for accip in accounts_ip:
        if accip[0]:
            accounts_used_ip.append(IPy.IP(accip[0]).int())
        if accip[1]:
            accounts_used_ip.append(IPy.IP(accip[1]).int())


    start_pool_ip = IPy.IP(pool.start_ip).int()
    end_pool_ip = IPy.IP(pool.end_ip).int()
    
    ipinuse_list = [IPy.IP(x.ip).int() for x in ipinuse]
    
    ipinuse_list+= accounts_used_ip
    
                 
    find = False
    res = []
    x = start_pool_ip
    i=0
    #limit=20
    while x<=end_pool_ip:
        if x not in ipinuse_list and x!=default_ip:
            if not term or term and str(IPy.IP(x, ipversion = ipversion)).rfind(term)!=-1:
                res.append(str(IPy.IP(x, ipversion = ipversion)))
            i+=1
        x+=1
    return {'totalCount':str(len(res)),'records':res[start:start+limit], 'status':True}

@ajax_request
@login_required
def getipfrompool2(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.ippool_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    default_ip='0.0.0.0'
    if default_ip:
        default_ip = IPy.IP(default_ip).int()
    pool_id=request.POST.get("pool_id") or request.GET.get("pool_id")
    limit=int(request.POST.get("limit", 500))
    start=int(request.POST.get("start", 0))
    if not pool_id:
        return {'records':[], 'status':False}
    pool = IPPool.objects.get(id=pool_id)
    #pool = IPPool.objects.all()[0]
    ipinuse = IPInUse.objects.filter(pool=pool, disabled__isnull=True)
    accounts_ip = SubAccount.objects.values_list('ipn_ip_address', 'vpn_ip_address')
    #accounts_ip = connection.sql("SELECT ipn_ip_address, vpn_ip_address FROM billservice_subaccount")
    #connection.commit()
    ipversion = 4 if pool.type<2 else  6
    accounts_used_ip = []
    for accip in accounts_ip:
        accounts_used_ip.append(IPy.IP(accip[0]).int())
        accounts_used_ip.append(IPy.IP(accip[1]).int())


    start_pool_ip = IPy.IP(pool.start_ip).int()
    end_pool_ip = IPy.IP(pool.end_ip).int()
    
    ipinuse_list = [IPy.IP(x.ip).int() for x in ipinuse]
    
    ipinuse_list+= accounts_used_ip
    
                 
    find = False
    res = []
    x = start_pool_ip
    i=0
    #limit=20
    while x<=end_pool_ip:
        if x not in ipinuse_list and x!=default_ip:
            res.append(str(IPy.IP(x, ipversion = ipversion)))
            i+=1
        x+=1
    return [res[start:start+limit]]

@ajax_request
@login_required
def houses(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.house_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    street_name = request.POST.get('street_name')
    city_id = request.POST.get('city_id')
    term = request.POST.get('term')
    id = request.POST.get('id')
    fields = request.POST.get('fields')
    if street_name:
        if term:
            items = House.objects.filter(street__name__icontains=street_name, name__icontains = term)
        else:
            items = House.objects.filter(street__name__icontains=street_name)
    elif id:
        items = [House.objects.get(id=id)]
    else:
        if term:
            items = House.objects.filter(street__name__icontains=street_name)
        else:
            items = House.objects.all()

    res=[]
    for item in items:
        res.append(instance_dict(item, fields = fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def houses_set(request):
    
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_house')):
            return {'status':False, 'message': u'У вас нет прав на редактирование домов'}
        item = House.objects.get(id=id)
        form = HouseForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_house')):
            return {'status':False, 'message': u'У вас нет прав на добавление домов'}
        form = HouseForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            res={"status": True}
        except Exception, e:

            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def houses_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_house')):
        return {'status':False, 'message': u'У вас нет прав на удаление домов'}
    id = int(request.POST.get('id',0))
    if id:
        for d in House.objects.filter(id=id):
            log('DELETE', request.user, d)
            d.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "House not found"}
    
@ajax_request
@login_required
def accountaddonservices(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.accountaddonservice_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    account_id = request.POST.get('account_id')
    subaccount_id = request.POST.get('subaccount_id')
    id = request.POST.get('id')
    normal_fields = request.POST.get('normal_fields', False)=='True'
    if id and id!='None':
        items = AccountAddonService.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'AccountAddon with id=%s not found' % id}
        
    elif account_id and account_id!='None':
        items = AccountAddonService.objects.filter(account__id=account_id)
    
    elif subaccount_id and subaccount_id!='None':
        items = AccountAddonService.objects.filter(subaccount__id=subaccount_id)

    res=[]
    for item in items:
        res.append(instance_dict(item,normal_fields=normal_fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def accountaddonservices_set(request):
    id = request.POST.get('id')
    
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_accountaddonservice')):
            return {'status':False, 'message': u'У вас нет прав на редактирование связок подключаемых услуг'}
        item = AccountAddonService.objects.get(id=id)
        form = AccountAddonServiceModelForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_accountaddonservice')):
            return {'status':False, 'message': u'У вас нет прав на добавление связок подключаемых услуг'}

        form = AccountAddonServiceModelForm(request.POST)
        
    if form.is_valid():
        model = form.save(commit = False)
        model.save()
        log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        res = {'status':True}
    else:
        res={"status": False, "errors": form._errors}
    #print instance_dict(item).keys()
    return res

@ajax_request
@login_required
def accounttariffs_set(request):
    id = request.POST.get('id')
    
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_accounttariff')):
            return {'status':False, 'message': u'У вас нет прав на редактирование связок тарифных планов'}

        item = AccountTarif.objects.get(id=id)
        form = AccountTariffForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_accounttariff')):
            return {'status':False, 'message': u'У вас нет прав на добавление связок тарифных планов'}
        form = AccountTariffForm(request.POST)
        
    if form.is_valid():
        model = form.save(commit = False)
        model.save()
        log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
        res = {'status':True}
    else:
        res={"status": False, "errors": form._errors}

    return res

@ajax_request
@login_required
def accounttariffs_bathset(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_accounttariff')):
        return {'status':False, 'message': u'У вас нет прав на добавление связок тарифных планов'}

    form = AccountTariffBathForm(request.POST)
    

    if form.is_valid():
        accounts = form.cleaned_data.get('accounts')
        tariff =  form.cleaned_data.get('tariff')
        date = form.cleaned_data.get('date')
        
        for account in accounts.split(','):
            try:
                item = AccountTarif()
                item.account = Account.objects.get(id=account)
                item.tarif = Tariff.objects.get(id=tariff)
                item.datetime = date
                item.save()
                log('CREATE', request.user, item) 
            except Exception, e:
                res={"status": False, "message": str(e)}
            
        
        res = {'status':True}
    else:
        res={"status": False, "errors": form._errors}

    return res


@ajax_request
@login_required
def suspendedperiods(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.suspendedperiod_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    account_id = request.POST.get('account_id')
    id = request.POST.get('id')
    if id:
        items = SuspendedPeriod.objects.filter(id=id)
    elif account_id:
        items = SuspendedPeriod.objects.filter(account__id=account_id)
    res=[]
    for item in items:
        res.append(instance_dict(item,normal_fields=True))
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def suspendedperiod_set(request):
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_suspendedperiod')):
            return {'status':False, 'message': u'У вас нет прав на редактирование периодов без списаний'}

        item = SuspendedPeriod.objects.get(id=id)
        form = SuspendedPeriodModelForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_suspendedperiod')):
            return {'status':False, 'message': u'У вас нет прав на создание периодов без списаний'}

        form = SuspendedPeriodModelForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            res={"status": True}
        except Exception, e:

            res={"status": False, "message": str(e)}
    else:
        res={"success": False, "errors": form._errors}
    
    return res

@ajax_request
@login_required
def transaction_set(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_transaction')):
        return {'status':False, 'message': u'У вас нет прав на создание платежей'}
    
    js = json.loads(request.POST.get('data','{}'))
    form = TransactionModelForm(js)
        
    if form.is_valid():
        try:
            tr=form.save(commit=False)
            tr.systemuser = request.user.account
            tr.save()
            log('EDIT', request.user, tr) if id else log('CREATE', request.user, tr) 
            res={"status": True, 'transaction_id':tr.id}
        except Exception, e:

            res={"status": False, "msg": str(e)}
    else:
        res={"status": False, "errors": form._errors}
    
    return res


@login_required
@ajax_request
def transactiontypes(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.transactiontype_view')):
        return {'status':True, 'records':[], 'totalCount':0}
    id = request.POST.get('id')
    if id:
        items = TransactionType.objects.filter(id=id).order_by('name')
    else:
        items = TransactionType.objects.all().order_by('name')

    res=[]
    for item in items:
        res.append({"id":item.id, "name":item.name, "internal_name":item.internal_name})
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def transactiontypes_set(request):
    id = request.POST.get('id')
    if id:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_transactiontype')):
            return {'status':False, 'message': u'У вас нет прав на редактирование типов списаний'}
        item = TransactionType.objects.get(id=id)
        form = TransactionTypeForm(request.POST, instance=item)
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_transactiontype')):
            return {'status':False, 'message': u'У вас нет прав на создание типов списаний'}
        form = TransactionTypeForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit = False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            res={"status": True}
        except Exception, e:

            res={"status": False, "message": str(e)}
    else:
        res={"success": False, "errors": form._errors}
    
    return res

@ajax_request
@login_required
def actions_set(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.actions_set')):
        return {'status':False, 'message': u'У вас нет прав на управление состоянием субаккаунтов'}
    subaccount = request.POST.get('subaccount_id')
    action = request.POST.get('action')
    if subaccount:          

        sa=SubAccount.objects.get(id=subaccount)
        if action=='ipn_disable':
            sa.ipn_sleep=False
            sa.save()
            return {'status':True, 'message':'Ok'}
        if action=='ipn_enable':
            sa.ipn_sleep=True
            sa.save()
            return {'status':True, 'message':'Ok'}

        subacc = instance_dict(SubAccount.objects.get(id=subaccount))

        acc =  instance_dict(sa.account)
        acc['account_id']=acc['id']
        
        try:
            n=sa.nas
            nas = instance_dict(n)
        except Exception, e:
            return {'status':False,'message':u'Не указан или не найден указанный сервер доступа'}
            

        if action=='disable':
            command = n.subacc_disable_action
        elif action=='enable':
            command = n.subacc_enable_action
        elif action=='create':
            command = n.subacc_add_action
        elif action =='delete':
            command = n.subacc_delete_action
        #print command

        sended = cred(account=acc, subacc=subacc, access_type='ipn', nas=nas,  format_string=command)

        if action=='create' and sended==True:
            sa.ipn_added=True
            sa.speed=''
            sa.save()
            log('EDIT', request.user, sa)
            #TODO: IPN Actions action

        
        if action =='delete'  and sended==True:
            sa.ipn_enabled=False
            sa.ipn_added=False
            sa.speed=''
            sa.save()
            log('EDIT', request.user, sa)
            #TODO: IPN Actions action

        if action=='disable' and sended==True:
            sa.ipn_enabled=False
            sa.save()
            log('EDIT', request.user, sa)
            #TODO: IPN Actions action
            
        if action=='enable' and sended==True:
            sa.ipn_enabled=True
            sa.save()
            log('EDIT', request.user, sa)
            #TODO: IPN Actions action

        
        return {'status':sended, 'message':'Ok'}
    return {'status':False, 'message':'Ok'}
            
      
@ajax_request
@login_required 
def documentrender(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.documentrender')):
        return {'status':False, 'message': u'У вас нет прав на рендеринг документов'}
    form = DocumentRenderForm(request.POST)
    if form.is_valid():
        template = Template.objects.get(id=form.cleaned_data.get('template'))
        templ = mako_template(unicode(template.body), input_encoding='utf-8')
        data=''
        if template.type.id==1:
    
            account = Account.objects.get(id=form.cleaned_data.get('account'))

            #tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)" % account.id)
            try:
                data=templ.render_unicode(account=account)
            except Exception, e:
                data=u"Error %s" % str(e)
        if template.type.id==2:
            account = connection.sql("SELECT id FROM billservice_account LIMIT 1" )[0].id
            #organization = self.connection.sql("SELECT * FROM billservice_organization LIMIT 1" )[0]
            #bank = self.connection.sql("SELECT * FROM billservice_bankdata LIMIT 1" )[0]
            operator = connection.get("SELECT * FROM billservice_operator LIMIT 1")
            try:
                data=templ.render_unicode(account=account, operator=operator,  connection=self.connection)
            except Exception, e:
                data=u"Error %s" % str(e)
    

                       

        res = {'success': True, 'body':data.encode("utf-8", 'replace')}
    else:
        res={"success": False, "errors": form._errors}
    #print instance_dict(item).keys()
    return res

@ajax_request
@login_required 
def templaterender(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.documentrender')):
        return {'status':False, 'message': u'У вас нет прав на рендеринг документов'}
    form = TemplateForm(request.POST)
    if form.is_valid():
        templatetype = form.cleaned_data.get('type')
        print form.cleaned_data.get('body')
        templ = mako_template(unicode(form.cleaned_data.get('body')), input_encoding='utf-8')
        data=''
        from django.db import connection
        if templatetype.id==1:
    
            #account = Account.objects.get(id=form.cleaned_data.get('account'))
            account = Account.objects.all()[0]

            #tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)" % account.id)
            try:
                data=templ.render_unicode(account=account,  connection=connection)
            except Exception, e:
                data=u"Error %s" % str(e)
        if templatetype.id==2:
            account = connection.sql("SELECT id FROM billservice_account LIMIT 1" )[0].id
            #organization = self.connection.sql("SELECT * FROM billservice_organization LIMIT 1" )[0]
            #bank = self.connection.sql("SELECT * FROM billservice_bankdata LIMIT 1" )[0]
            operator = connection.get("SELECT * FROM billservice_operator LIMIT 1")
            try:
                data=templ.render_unicode(account=account, operator=operator,  connection=connection)
            except Exception, e:
                data=u"Error %s" % str(e)
    

                       

        res = {'success': True, 'body':data.encode("utf-8", 'replace')}
    else:
        res={"success": False, "errors": form._errors}
    #print instance_dict(item).keys()
    return res

@ajax_request
@login_required 
def cheque_render(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.documentrender')):
        return {'status':False, 'message': u'У вас нет прав на рендеринг документов'}
    id = request.POST.get('id')#transaction_id
    transaction = Transaction.objects.get(id=id)
    template = Template.objects.get(type__id=5)
    templ = mako_template(unicode(template.body), input_encoding='utf-8')
    data=''
   
   

    account = transaction.account
    #TODO:Сделать дефолтного оператора
    
    operator = Operator.objects.all()
    if operator:
        operator = operator[0]
    try:
        data=templ.render_unicode(account=account, transaction=transaction, operator=operator)
        
    except Exception, e:
        data=u"Error %s" % str(e)


                       
    res = {'success': True, 'body':data.encode("utf-8", 'replace')}
    

    #print instance_dict(item).keys()
    return res

@login_required 
@ajax_request
def testCredentials(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.testcredentials')):
        return {'status':False, 'message': u'У вас нет на тестирование подключения'}
    host, login, password = request.POST.get('host'),request.POST.get('login'),request.POST.get('password')
    try:
        #print host, login, password
        a=ssh_client(host, login, password, '')
    except Exception, e:
        
        return {'status': False, 'message':str(e)}
    return {'status': True}
    
@login_required 
@ajax_request
def get_ports_status(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.getportsstatus')):
        return {'status':False, 'message': u'У вас нет прав на получение статуса портов'}
    switch_id = request.POST.get('switch_id')
    if not switch_id: 
        return {'status':False}
    
    switch = Switch.objects.get(id=switch_id)
    version = '2c' if switch.snmp_version==1 else '1'
    #oper status .1.3.6.1.2.1.2.2.1.8.
    status, output = commands.getstatusoutput("snmpwalk -v %s -Oeqsn -c %s %s .1.3.6.1.2.1.2.2.1.7" % (version, switch.snmp_community, switch.ipaddress))
    if status!=0:
        return {'status':False, 'message': u'Невоззможно получить состояние портов'}
    ports_status={}
    for line in output.split("\n"):
        #print 'line=',line
        if line.rfind(".")==-1:continue
        try:
            oid, value=line.split(" ")
        except Exception, e:

            continue
        
        id=oid.split(".")[-1]
        ports_status[id]=value
    status, output = commands.getstatusoutput("snmpwalk -v %s -Oeqsn -c %s %s .1.3.6.1.2.1.2.2.1.5" % (version, switch.snmp_community, switch_ipaddress))
    if status!=0:
        return {'status':False, 'message': u'Невоззможно получить состояние портов'}
    ports_speed_status={}
    for line in output.split("\n"):
        #print 'line=',line
        if line.rfind(".")==-1:continue
        try:
            oid, value=line.split(" ")
        except Exception, e:
            continue
        
        id=oid.split(".")[-1]
        ports_speed_status[id]=value
    
    return {'status':True, 'ports_status':ports_status, 'ports_speed_status':ports_speed_status}


@login_required 
@ajax_request
def set_ports_status(self, switch_id):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.setportsstatus')):
        return {'status':False, 'message': u'У вас нет на установку статуса портов'}
    switch_id = request.POST.get('switch_id')
    if not switch_id: 
        return {'status':False}
    
    switch = Switch.objects.get(id=switch_id)
    version = '2c' if switch.snmp_version==1 else '1'
    #получили статусы, чтобы было с чем сравнивать
    status, output = commands.getstatusoutput("snmpwalk -v %s -Oeqsn -c %s %s .1.3.6.1.2.1.2.2.1.7" % (version, switch.snmp_community, switch_ipaddress))
    if status!=0:
        return {'status':False, 'message': u'Невоззможно сохранить состояние портов'}
    ports_status={}
    for line in output.split("\n"):
        #print 'line=',line
        if line.rfind(".")==-1:continue
        try:
            oid, value=line.split(" ")
        except Exception, e:

            continue
        
        id=oid.split(".")[-1]
        ports_status[id]=value
        
    for port, status in ports:
        if ports_status[port]!=status:
            status, output = commands.getstatusoutput("snmpset -v %s -Oeqsn -c %s %s .1.3.6.1.2.1.2.2.1.7.%s i %s" % (version, switch.snmp_community, switch_ipaddress, port, 1 if status==True else 2))
    
    status, output = commands.getstatusoutput("snmpwalk -v %s -Oeqsn -c %s %s .1.3.6.1.2.1.2.2.1.7" % (version, switch.snmp_community, switch_ipaddress))
    if status!=0:
        return {'status':False, 'message': u'Невоззможно сохранить состояние портов'}
    ports_status={}
    for line in output.split("\n"):
        #print 'line=',line
        if line.rfind(".")==-1:continue
        try:
            oid, value=line.split(" ")
        except Exception, e:
            continue
        id=oid.split(".")[-1]
        ports_status[id]=value
        
    return {'status':True, 'ports_status':ports_status}
    
@login_required 
@ajax_request
def list_logfiles(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.list_log_files')):
        return {'status':False, 'message': u'У вас нет на получение списка лог-файлов'}
    
    logfiles = os.listdir('/opt/ebs/data/log/')
    return {'status':True, 'records':logfiles, 'totalCount':len(logfiles)}

@login_required 
@ajax_request
def get_tail_log(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.view_log_files')):
        return {'status':False, 'message': u'У вас нет на получение списка лог-файлов'}
    log_name = request.POST.get("log_name")
    count =  request.POST.get("log_count", 0)
    all_file = request.POST.get('all_file')=='True'
    

    if all_file:
        s, o = commands.getstatusoutput("cat /opt/ebs/data/log/%s" % log_name.replace('/',''))
        return {'status': True, 'data': unicode(o, errors='ignore')}

    s, o = commands.getstatusoutput("tail -n %s /opt/ebs/data/log/%s" % (count, log_name.replace('/','')))

    return {'status': True, 'data': unicode(o, errors='ignore')}

@ajax_request
@login_required
def transactions_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.transactions_delete')):
        return {'status':False, 'message':u'У вас недостатчно прав для удаления проводок'}
    js = json.loads(request.POST.get('data','{}'))
    if js:
        cursor = connection.cursor()
        for id,date, table in js:
            cursor.execute("DELETE FROM %s WHERE id=%%s and created=%%s" % table, (id, date))
    return {"status": True}

@ajax_request
@login_required
def sp_info(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.sp_info')):
        return {'status':False, 'message': u'У вас нет прав на выполнение этой функции'}
    
    js = json.loads(request.POST.get('data','{}'))
    settlement_period_id = js.get("settlement_period_id")
    time_start=js.get("time_start")
    curdatetime=js.get("curdatetime")
    sp = SettlementPeriod.objects.get(id=settlement_period_id)
    
    if not curdatetime:
        curdatetime = datetime.datetime.now()
    else:
        curdatetime = datetime.datetime.strptime(curdatetime, "%Y-%m-%d %H:%M:%S")
    if sp.autostart and time_start:
        time_start=datetime.datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S")
    elif not sp.autostart or (sp.autostart and not time_start):
        time_start=sp.time_start
        
    start, end, length = settlement_period_info(time_start, sp.length_in, sp.length, curdatetime)
    return {"status": True, 'records': [{'start':start, 'end': end, 'length':length}], 'totalCount':1}
    
    