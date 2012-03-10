#-*-coding:utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from ebscab.lib.ssh_paramiko import ssh_client
from billservice.models import Account, AccessParameters, SubAccount, TransactionType, City, Street, House, SystemUser,AccountTarif, AddonService, IPPool, IPInUse, ContractTemplate, Document
from billservice.models import Organization, TimeSpeed, BankData, TimePeriod, SettlementPeriod, Template, TemplateType,  AccountHardware, SuspendedPeriod, Operator, Transaction, PeriodicalService, AddonService, Tariff
from billservice.models import OneTimeService, TimeSpeed, GroupTrafficClass, TrafficTransmitNodes, PrepaidTraffic, Group, PeriodicalService, OneTimeService, TrafficLimit, AddonServiceTarif
from billservice.models import Template, News, SaleCard, DealerPay, Card, Dealer, AccountViewedNews, TPChangeRule, Manufacturer, Model, Hardware, HardwareType, TransactionType, TimePeriodNode, AccountPrepaysTrafic, AccountPrepaysRadiusTrafic, TrafficTransmitService, RadiusAttrs, SpeedLimit,  RadiusTraffic, RadiusTrafficNode,TimeAccessNode,TimeAccessService, AddonServiceTarif

from nas.models import Nas, Switch, TrafficClass, TrafficNode
from radius.models import ActiveSession
from django.contrib.auth.decorators import login_required
from django.db import connection
from billservice.forms import AccountForm, TimeSpeedForm, GroupForm, SubAccountForm, SearchAccountForm, AccountTariffForm, AccountAddonForm,AccountAddonServiceModelForm, DocumentRenderForm
from billservice.forms import TemplateForm, DocumentModelForm, SuspendedPeriodModelForm, TransactionModelForm, AddonServiceForm, CityForm, StreetForm, HouseForm
from utilites import cred
import IPy
from randgen import GenUsername as nameGen , GenPasswd as GenPasswd2
from IPy import IP
from utilites import rosClient
import datetime
from mako.template import Template as mako_template
from ebsadmin.lib import ExtDirectStore, instance_dict
from billservice.forms import LoginForm, AccountPrepaysRadiusTraficForm, RadiusTrafficForm, RadiusTrafficNodeForm, PrepaidTrafficForm, TrafficTransmitNodeForm,TrafficTransmitServiceForm, PeriodicalServiceForm, OneTimeServiceForm,  TariffForm, AccessParametersForm, SettlementPeriodForm, OrganizationForm, BankDataForm,AccountTariffBathForm
from billservice.forms import RadiusAttrsForm, IPPoolForm, TimePeriodForm, TimePeriodNodeForm, SystemUserForm, TransactionTypeForm, AccountPrepaysTrafic, TimeAccessNodeForm, ContractTemplateForm, TimeAccessServiceForm, TrafficLimitForm, SpeedLimitForm, AddonServiceTarifForm
from billservice.forms import ManufacturerForm, OperatorForm, DealerPayForm, SaleCardForm, CardForm, DealerForm, NewsForm, TPChangeRuleForm, AccountHardwareForm, ModelHardwareForm, HardwareTypeForm, HardwareForm

from billservice import authenticate, log_in, log_out
from nas.forms import NasForm, TrafficNodeForm, TrafficClassForm, SwitchForm
from radius.forms import SessionFilterForm

from django.db.models import Q
from django.db import transaction
import json
import commands
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
                log_in(request, user)
                return {"status":True,"message":"Login succeful"}
            else:
                return {"status":False, "message":"Login forbidden to this action"}
                
        except:
            return {"status":False, "message":"Login can`t be authenticated"}
    return {"status":False,"message":"Login not found"}

@ajax_request
@login_required
def jsonaccounts(request):
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
        print f.errors
        print f.cleaned_data
        query={}
        for k in f.cleaned_data:
            if f.cleaned_data.get(k):
                query[k]=f.cleaned_data.get(k)
            
        items = Account.objects.filter(**query)
    
    print items
    #return items
    
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        r=instance_dict(item,normal_fields=True)
        r['tariff']=item.tariff
        res.append(r)
    #print instance_dict(item).keys()
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res, 'total':str(totalcount)}
    
@ajax_request
@login_required
def periodicalservice(request):
    extra={'start':int(request.POST.get('start',0)), 'limit':int(request.POST.get('limit',100))}
    if request.POST.get('sort',''):
        extra['sort'] = request.POST.get('sort','')
        extra['dir'] = request.POST.get('dir','asc')
        
    
    items = ExtDirectStore(PeriodicalService)
    items, totalcount = items.query(**extra)

    res=[]
    for item in items:
        r=instance_dict(item,normal_fields=True)
        res.append(r)
    #print instance_dict(item).keys()
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res, 'total':str(totalcount)}

@ajax_request
@login_required
def addonservice(request):
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
    #print instance_dict(item).keys()
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
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
    #print instance_dict(item).keys()
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res, 'total':len(res)}

@ajax_request
@login_required
def generate_credentials(request):
    action = request.POST.get('action')
    if action=='login':
        return {"success": True, 'generated':nameGen()}
    if action=='password':
        return {"success": True, 'generated':GenPasswd2()}
    return {"success": False}

@ajax_request
@login_required
def get_mac_for_ip(request):
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
        apiros = rosClient(nas.ipaddress, nas.login, nas.password)
        command='/ping =address=%s =count=1' % ipn_ip_address
        rosExecute(command)
        command='/ip/arp/print ?address=%s' % ipn_ip_address
        rosExecute(command)
        mac = rosExecute(command).get('mac-address', '')
        apiros.close()
        del apiros
        del rosExecute
    except Exception, e:
        return {'success':False, 'message':str(e)}
    
    return {'success':True, 'mac':mac}
    
@ajax_request
@login_required
def subaccounts(request):
    account_id = request.POST.get('account_id', None)
    id = request.POST.get('id', None)
    print "n fields", request.POST.get('normal_fields', True)
    normal_fields = request.POST.get('normal_fields', True)=='True'
    print "normal_fields",normal_fields, type(normal_fields)
    print "subaccount", account_id
    if account_id and account_id!= 'None':
        items = SubAccount.objects.filter(account__id=account_id)
    else:
        items = SubAccount.objects.filter(id=id)
    #print accounts
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        #print instance_dict(acc).keys()
        res.append(instance_dict(item,normal_fields=normal_fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def addonservices(request):
    id = request.POST.get('id', None)
    
    normal_fields = request.POST.get('normal_fields', True)=='True'
    print 'id', id, type(id), len(id)
    if id and id!= '':
        items = AddonService.objects.filter(id=id)
    else:
        items = AddonService.objects.all().order_by('name')
    #print accounts
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        #print instance_dict(acc).keys()
        res.append(instance_dict(item,normal_fields=normal_fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def document(request):
    account_id = request.POST.get('account_id')
    print "subaccount", account_id
    items = Document.objects.filter(account__id=account_id)
    #print accounts
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        #print instance_dict(acc).keys()
        res.append(instance_dict(item,normal_fields=True))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res}

@ajax_request
@login_required
def document_get(request):
    id = request.POST.get('id')
    item = Document.objects.get(id=id)
    return {"records": instance_dict(item)}

@ajax_request
@login_required
def templates(request):

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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields, normal_fields=False))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def sessions(request):
    
    form = SessionFilterForm(request.POST)
    if form.is_valid():
        id = form.cleaned_data.get('id')
        account_id = form.cleaned_data.get('account')
        date_start =form.cleaned_data.get('date_start')
        date_end = form.cleaned_data.get('date_end')
        only_active = form.cleaned_data.get('only_active')

        
        items = ActiveSession.objects.filter(date_start__gte=date_start, date_end__lte=date_end).order_by('-interrim_update')
        if only_active:
            items = items.filter(session_status='ACTIVE')
            
        if id:
             items = items.filter(id=id)
             if not items:
                return {'status':False, 'message': 'Session with id=%s not found' % id}
        elif account_id:
            items = items.filter(account__id=account_id)
        
        res=[]
        for item in items:
            res.append(instance_dict(item,normal_fields=True))
            
    
        return {"records": res, 'status':True, 'totalCount':len(res)}
    else:
        print form._errors
        return { 'status':False, 'message': u'Невозможно выполнить выборку с такими условиями'}



@ajax_request
@login_required
def settlementperiods(request):
    
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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def accessparameters(request):
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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def timeperiods(request):
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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def timeperiods_save(request):
    
    id = request.POST.get('id')
    if id:
        item = TimePeriod.objects.get(id=id)
        form = TimePeriodForm(request.POST, instance=item)
    else:
        form = TimePeriodForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def timeperiods_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        TimePeriod.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TimePeriod not found"}
   
@ajax_request
@login_required
def timeperiodnodes_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        TimePeriodNode.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TimePeriodNode not found"} 
    
@ajax_request
@login_required
def timeperiodnodes(request):
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    period_id = request.POST.get('period_id',None)
    print "period_id==", period_id
    
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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def timeperiodnodes_save(request):
    
    id = request.POST.get('id')
    if id:
        item = TimePeriodNode.objects.get(id=id)
        form = TimePeriodNodeForm(request.POST, instance=item)
    else:
        form = TimePeriodNodeForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def timeperiodnodes_m2m_save(request):
    
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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def radiustrafficservices(request):
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
    s = request.POST.get('sql','')
  
    if not s:
        return {'status':False, 'message': 'SQL not defined'}
        
    from django.db import connection
    
    cur = connection.cursor()
    

    try:
        cur.execute(s)
        
        res = dictfetchall(cur)
    except Exception, e:
        return { 'status':False, 'message':str(e)}
        
  
    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def radiustrafficservices_nodes(request):
    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    service_id = request.POST.get('service_id', None)
    normal_fields = request.POST.get('normal_fields', False)=='True'
    if id and id!='None':
        items = RadiusTrafficNode.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TimeAccessNode item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'TimeAccessNode >1 items with id=%s' % id}
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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def timespeeds(request):
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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def systemusers(request):
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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def tpchangerules(request):
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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def tpchangerules_set(request):
    
    id = request.POST.get('id')
    if id:
        item = TPChangeRule.objects.get(id=id)
        form = TPChangeRuleForm(request.POST, instance=item)
    else:
        form = TPChangeRuleForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def tpchangerules_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        TPChangeRule.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SystemUser not found"}
    
@ajax_request
@login_required
def systemusers_set(request):
    
    id = request.POST.get('id')
    if id:
        item = SystemUser.objects.get(id=id)
        form = SystemUserForm(request.POST, instance=item)
    else:
        form = SystemUserForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def systemusers_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        SystemUser.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SystemUser not found"}
    
@ajax_request
@login_required
def contracttemplates(request):
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
    id = request.POST.get('id',None)
    res = False
    if id and id!='None':
        item = Account.objects.all_with_deleted().get(id=id)
        if not item:
            return {'status':False, 'message': 'Account item with id=%s not found' % id}
       
        res = item.get_account_tariff().access_parameters.ipn_for_vpn
        return {"result": res, 'status':True}
    
    return {"result": res, 'status':False}

@ajax_request
@login_required
def session_reset(request):
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
    id = request.POST.get('id',None)
    res = False
    if id and id!='None':
        item = Account.objects.get(id=id)
        if not item:
            return {'status':False, 'message': 'Account item with id=%s not found' % id}
       
        res = instance_dict(item.get_account_tariff())
        return {"records": [res], 'status':True, 'totalCount':1}
    
    return {"records": [res], 'status':False, 'totalCount':1}

@ajax_request
@login_required
def operator(request):
   
    try:
        item = Operator.objects.all()[0]
        return {'status':True, "records":[instance_dict(item, normal_fields=False)], 'totalCount':1}
   
    except Exception, e:
        print e
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
        item = Operator.objects.get(id=op_model_id)
        form = OperatorForm(op_model, instance=item)
    else:
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
                opmodel = form.save(commit=False)
                opmodel.bank=bankitem
                opmodel.save()
                res={"status": True}
            except Exception, e:
                print e
                res={"status": False, "message": str(e)}
        else:
            res={"status": False, "errors": bankform._errors}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def get_pool_by_ipinuse(request):
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
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    normal_fields = bool(request.POST.get('normal_fields',False))
    print 'normal_fields', normal_fields
    if id and id!='None':
        items = Tariff.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Tariff item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = Tariff.objects.all().order_by('-name')
        
    res=[]
    for item in items:
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def cities(request):
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
        #print instance_dict(acc).keys()
        res.append(instance_dict(item, fields=fields))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def cities_set(request):
    
    id = request.POST.get('id')
    if id:
        item = City.objects.get(id=id)
        form = CityForm(request.POST, instance=item)
    else:
        form = CityForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def cities_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        City.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "City not found"}
    
    
@ajax_request
@login_required
def accounthardware(request):
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
        item = AccountHardware.objects.get(id=id)
        form = AccountHardwareForm(request.POST, instance=item)
    else:
        form = AccountHardwareForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def accounthardware_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        AccountHardware.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Hardware not found"}

@ajax_request
@login_required
def news(request):
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
        item = News.objects.get(id=id)
        form = NewsForm(model, instance=item)
    else:
        form = NewsForm(model)
        
    if form.is_valid():
        try:
            item = form.save(commit=False)
            item.save()
            if not id and accounts:
                for account in accounts:
                    AccountViewedNews.objects.create(news = item, account = Account.objects.get(id=account), viewed=False)
            elif not id and not accounts and (item.private or item.agent):
                for account in Account.objects.all().values('id'):
                    AccountViewedNews.objects.create(news = item, account = Account.objects.get(id=account), viewed=False)
            res={"status": True, 'id':item.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def news_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        News.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "News not found"}
    
@ajax_request
@login_required
def accounttariffs(request):
    account_id = request.POST.get('account_id')
    
    items = AccountTarif.objects.filter(account__id=account_id).order_by('-datetime')
    #print accounts
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        #print instance_dict(acc).keys()
        res.append(instance_dict(item,normal_fields=True))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def subaccount(request):
    subaccount_id = request.POST.get('id')
    print "subaccount", subaccount_id
    item = SubAccount.objects.get(id=subaccount_id)
    #print accounts
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    #for item in items:
        #print instance_dict(acc).keys()
    res=instance_dict(item)
        
    res['subaccount_id']=item.id
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res}

@ajax_request
@login_required
def nasses(request):
    from nas.models import Nas
    
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def hardware(request):
    
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def hardware_set(request):
    
    id = request.POST.get('id')
    if id:
        item = Hardware.objects.get(id=id)
        form = HardwareForm(request.POST, instance=item)
    else:
        form = HardwareForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def hardware_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        Hardware.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Hardware not found"}
    
@ajax_request
@login_required
def manufacturers(request):
    
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def manufacturers_set(request):
    
    id = request.POST.get('id')
    if id:
        item = Manufacturer.objects.get(id=id)
        form = ManufacturerForm(request.POST, instance=item)
    else:
        form = ManufacturerForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def manufacturers_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        Manufacturer.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Manufacturer not found"}
    

@ajax_request
@login_required
def models(request):
    
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def models_set(request):
    
    id = request.POST.get('id')
    if id:
        item = Model.objects.get(id=id)
        form = ModelHardwareForm(request.POST, instance=item)
    else:
        form = ModelHardwareForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def models_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        Model.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Model not found"}
    
@ajax_request
@login_required
def hardwaretypes(request):
    
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def dealers(request):
    
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def dealers_set(request):
    
    id = request.POST.get('id')
    if id:
        item = Dealer.objects.get(id=id)
        form = DealerForm(request.POST, instance=item)
    else:
        form = DealerForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def dealers_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        Dealer.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Dealer not found"}
    
@ajax_request
@login_required
def hardwaretypes_set(request):
    
    id = request.POST.get('id')
    if id:
        item = HardwareType.objects.get(id=id)
        form = HardwareTypeForm(request.POST, instance=item)
    else:
        form = HardwareTypeForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res



@ajax_request
@login_required
def getnotsoldcards(request):
    
    ids = request.POST.get('ids',None).split(',')
    print "ids=", ids
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
        item = Card.objects.get(id=id)
        form = CardForm(request.POST, instance=item)
    else:
        form = CardForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def cards_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        Card.objects.filter(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Card not found"}
    
    
    
@ajax_request
@login_required
def cardsstatus_set(request):
    
    data = json.loads(request.POST.get('data', '{}'))
    ids = data.get('ids',[])
    status = data.get('status',True)
    
    print 'ids', ids, status
    if ids:
        Card.objects.filter(id__in=ids).update(disabled=status)
        print "updated"
    
        res={"status": True}
    else:
        res={"status": False, "message": u"Карты не указаны"}
    return res

@ajax_request
@login_required
def get_model(request):
    
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
def hardwaretypes_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        HardwareType.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "HardwareType not found"}
    

@ajax_request
@login_required
def account(request):

    data = json.loads(request.POST.get('data', '{}'))
    fields = data.get('fields',[])
    id = data.get('id',None)
    limit = data.get('limit',None)
    print "fields", fields, limit
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def accountsfilter(request):

    sql = request.POST.get('sql','True')
    from django.db import connection
    cur = connection.cursor()
    
    try:
        s="""SELECT DISTINCT acc.id, acc.username, acc.room, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status, acc.last_balance_null, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name, (SELECT name FROM billservice_tariff WHERE id=get_tarif(acc.id)) as tariff, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,(SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address
            FROM billservice_account AS acc
            LEFT JOIN billservice_subaccount as subacc ON subacc.account_id=acc.id 
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id
            WHERE acc.deleted is Null  
            AND 
            %s
            ORDER BY acc.username ASC;""" % sql
        
        cur.execute(s)
        res = dictfetchall(cur)
    except Exception, e:
        return { 'status':False, 'message':str(e)}

            
        
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def trafficclasses(request):
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)

    if id:
        items = TrafficClass.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'TrafficClass item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    else:
        items = TrafficClass.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}




@ajax_request
@login_required
def trafficclasses_set(request):
    
    id = request.POST.get('id')
    if id:
        item = TrafficClass.objects.get(id=id)
        form = TrafficClassForm(request.POST, instance=item)
    else:
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
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


@ajax_request
@login_required
def trafficclasses_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        TrafficClass.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TrafficClass not found"}
    
@ajax_request
@login_required
def trafficclassnodes(request):
    
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def trafficclassnodes_set(request):
    
    id = request.POST.get('id')
    if id:
        item = TrafficNode.objects.get(id=id)
        form = TrafficNodeForm(request.POST, instance=item)
    else:
        form = TrafficNodeForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def trafficclassnodes_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        TrafficNode.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "TrafficNode not found"}
    
    
@ajax_request
@login_required
def classforgroup(request):
    
    fields = request.POST.get('fields',[])
    group = request.POST.get('group',None)

    if group:
        items = GroupTrafficClass.objects.filter(id=group)
        if not items:
            return {'status':False, 'message': 'GroupTrafficClass item with id=%s not found' % id}

        res = []
        for item in items:
            res.append(item.trafficclass.id)

    else:
        return { 'status':False, 'message': u"Group id not defined"}

    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def ippools(request):
    
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def ippools_set(request):
    
    id = request.POST.get('id')
    if id:
        item = IPPool.objects.get(id=id)
        form = IPPoolForm(request.POST, instance=item)
    else:
        form = IPPoolForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def ippools_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        IPPool.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "IPPool not found"}
    

@ajax_request
@login_required
def radiusattrs(request):

    
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}


@ajax_request
@login_required
def radiusattrs_set(request):
    
    id = request.POST.get('id')
    if id:
        item = RadiusAttrs.objects.get(id=id)
        form = RadiusAttrsForm(request.POST, instance=item)
    else:
        form = RadiusAttrsForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def radiusattrs_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        RadiusAttrs.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "RadiusAttrs not found"}
    
@ajax_request
@login_required
def radiusattrs_set(request):
    
    id = request.POST.get('id')
    if id:
        item = RadiusAttrs.objects.get(id=id)
        form = RadiusAttrsForm(request.POST, instance=item)
    else:
        form = RadiusAttrsForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def radiusattrs_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        RadiusAttrs.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "RadiusAttrs not found"}
    
@ajax_request
@login_required
def templates(request):

    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    type = request.POST.get('type',None)
    if id and id!='None':
        items = Template.objects.filter(id=id)
        if not items:
            return {'status':False, 'message': 'Template item with id=%s not found' % id}
        if len(items)>1:
            return {'status':False, 'message': 'Returned >1 items with id=%s' % id}
        
    elif type and type!='None':
        items = Template.objects.filter(type=type)
    else:
        items = Template.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def templates_save(request):
    
    id = request.POST.get('id')
    if id:
        item = Template.objects.get(id=id)
        form = TemplateForm(request.POST, instance=item)
    else:
        form = TemplateForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res


#===
@ajax_request
@login_required
def accountprepaystrafic(request):

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
        item = AccountPrepaysTrafic.objects.get(id=id)
        form = AccountPrepaysTraficForm(request.POST, instance=item)
    else:
        form = AccountPrepaysTraficForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res
#===

#===
@ajax_request
@login_required
def accountprepaysradiustrafic(request):

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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def accountprepaysradiustrafic_set(request):
    
    id = request.POST.get('id')
    if id:
        item = AccountPrepaysRadiusTrafic.objects.get(id=id)
        form = AccountPrepaysRadiusTraficForm(request.POST, instance=item)
    else:
        form = AccountPrepaysRadiusTraficForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res={"status": True, 'id':model.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res
#===


@ajax_request
@login_required
def templates_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        Template.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "RadiusAttrs not found"}
    
@ajax_request
@login_required
def templatetypes(request):

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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    return {"records": res, 'status':True, 'totalCount':len(res)}
  
@ajax_request
@login_required
def periodicalservices(request):
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    tarif_id = request.POST.get('tarif',None)
    deleted = bool(request.POST.get('deleted',None)=='True')
    normal_fields = bool(request.POST.get('normal_fields',None)=='True')
    print tarif_id, deleted
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}



@ajax_request
@login_required
def transactions(request):
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    limit = request.POST.get('limit',None)
    normal_fields = bool(request.POST.get('normal_fields',None)=='True')
    print 'limit', limit
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
def onetimeservices(request):
    
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=normal_fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def trafficlimites(request):
    
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
    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    limit_id = request.POST.get('limit_id',None)
    normal_fields = bool(request.POST.get('normal_fields',False)=='True')
    print "speedlimites_normal_fields", normal_fields
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

    from django.db import connection
    cur = connection.cursor()
    
    cur.execute("SELECT nominal FROM billservice_card GROUP BY nominal ORDER BY nominal ASC")
    
    res = cur.fetchall()
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def get_next_cardseries(request):

    from django.db import connection
    cur = connection.cursor()
    
    cur.execute("SELECT MAX(series) as series FROM billservice_card")
    
    res = cur.fetchone()[0] 
    
    print "res==", res
    res = res if res else 1
    return {"records": [res], 'status':True, 'totalCount':1}


@ajax_request
@login_required
def switches(request):

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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def switches_set(request):
    
    id = request.POST.get('id')
    if id:
        item = Switch.objects.get(id=id)
        form = SwitchForm(request.POST, instance=item)
    else:
        form = SwitchForm(request.POST)
        
    if form.is_valid():
        try:
            item = form.save(commit=False)
            item.save()
            res={"status": True, 'id':item.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def switches_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        Switch.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Switch not found"}
    
@ajax_request
@login_required
def organizations(request):

    
    fields = request.POST.get('fields',[])
    id = request.POST.get('id',None)
    account_id = request.POST.get('account_id',None)
    if id:
        items = Organization.objects.filter(id=id)
        if not item:
            return {'status':False, 'message': 'Organization item with id=%s not found' % id}
    elif account_id:
        items = Organization.objects.filter(account__id=account_id)
        if not items:
            return {'status':False, 'message': 'Organization item with account_id=%s not found' % account_id}
    else:
        items = Organization.objects.all()


    res=[]
    for item in items:
        res.append(instance_dict(item, fields=fields))
    
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def banks(request):

    
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
        item = BankData.objects.get(id=id)
        form =BankDataForm(request.POST, instance=item)
    else:
        form = BankDataForm(request.POST)
        
    if form.is_valid():
        try:
            item = form.save(commit=False)
            item.save()
            res={"status": True, 'id':item.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
    return res


@ajax_request
@login_required
def dealerpays(request):

    
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
        item = DealerPay.objects.get(id=id)
        form = DealerPayForm(request.POST, instance=item)
    else:
        form = DealerPayForm(request.POST)
        
    if form.is_valid():
        try:
            item = form.save(commit=False)
            item.save()
            res={"status": True, 'id':item.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
    return res


@ajax_request
@login_required
def returncards(request):
    
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
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "message": u"Карты не указаны"}
    return res

@ajax_request
@login_required
def salecards(request):

    
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
        item = SaleCard.objects.get(id=id)
        form =SaleCardForm(data.get('model',{}), instance=item)
    else:
        form = SaleCardForm(data.get('model',{}))
        
    if form.is_valid():
        try:
            item = form.save(commit=False)
            item.save()
            if cards:
                for card in cards:
                    c = Card.objects.get(id=card)
                    c.sold = item.created
                    c.save()
                    item.cards.add(c)
            res={"status": True, 'id':item.id}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
    return res

@ajax_request
@login_required
def salecards_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        SaleCard.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SaleCard not found"}
    
@ajax_request
@login_required
def nas(request):
    from nas.models import Nas
    items = Nas.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    res.append({"id":None, "name":u'-- Не указан --'})
    for item in items:
        res.append({"id":item.id, "name":item.name})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

@ajax_request
@login_required
def tpchange_save(request):
    
    id = request.POST.get('id')
    if id:
        item = AccountTarif.objects.get(id=id)
        form = AccountTariffForm(request.POST, instance=item)
    else:
        form = AccountTariffForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"success": True}
        except Exception, e:
            print e
            res={"success": False, "message": str(e)}
    else:
        res={"success": False, "errors": form._errors}
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return res




@login_required
@ajax_request
@transaction.commit_manually
def tariffs_set(request):
    
    data = request.POST.get("data", {})
    
    js = json.loads(data)
    print js

    if js.get('model'):
        if js.get('model').get('id'):
            item = Tariff.objects.get(id=js['model']['id'])
            form = TariffForm(js['model'], instance=item)
            print "tarif instance"
        else:
            print "tarif frompost"
            form = TariffForm(initial=js['model'])
            
        
        if form.is_valid():
            tariff = form.save(commit=False)
            tariff.save()
            print 'tarif save'
        else:
            print 'tarif errors'
            print form._errors
            transaction.rollback()
            return {'status':False, 'errors': form._errors}
        
    if js['access_parameters']:
        if 'id' in js['access_parameters']:
            item = AccessParameters.objects.get(id=js['access_parameters']['id'])
            form = AccessParametersForm(js['access_parameters'], instance=item)
            print "instance"
        else:
            print "frompost"
            form = AccessParametersForm(js['access_parameters'])
            
        
        if form.is_valid():
            print 'access parameters save pre'
            access_parameters = form.save(commit=False)
            access_parameters.save()
            print 'access parameters save post'
        else:
            print form._errors
            transaction.rollback()
            return {'status':False, 'errors': form._errors}
        
        speeditem_ids = []
        
        for speed in js.get('speeds', []):
            speed['access_parameters']=access_parameters.id
            print speed
            if speed.get('id'):
                item = TimeSpeed.objects.get(id=speed.get('id'))
                form = TimeSpeedForm(speed, instance=item)
                print "instance"
            else:
                print "frompost"
                form = TimeSpeedForm(speed)

            if form.is_valid():
                speeditem = form.save(commit=False)
                speeditem.save()
                
            else:
                print form._errors
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            speeditem_ids.append(speeditem.id)
        if speeditem_ids:
            TimeSpeed.objects.filter(access_parameters=access_parameters).exclude(id__in=speeditem_ids).delete()
        
    
    if js['periodicalservices']:
        
        periodicalservices_ids = []
        for periodicalservice in js.get('periodicalservices', []):
            periodicalservice['tarif']=tariff.id
            if periodicalservice.get('id'):
                
                item = PeriodicalService.objects.get(id=periodicalservice.get('id'))
                form = PeriodicalServiceForm(periodicalservice, instance=item)
                print "instance"
            else:
                print "frompost"
                form = PeriodicalServiceForm(periodicalservice)
            
        
            if form.is_valid():
                print "ps save"
                periodicalservice_item = form.save(commit=False)
                periodicalservice_item.save()
                
                print 'ps post save'
            else:
                print form._errors
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            periodicalservices_ids.append(periodicalservice_item.id)
        

        if periodicalservices_ids:
            PeriodicalService.objects.filter(tarif=tariff).exclude(id__in=periodicalservices_ids).delete()
    else:
        PeriodicalService.objects.filter(tarif=tariff).update(deleted=True, deactivated = datetime.datetime.now())
        
    if js['addonservices']:
        
        addonservices_ids = []
        for obj in js.get('addonservices', []):
            obj['tarif']=tariff.id
            if obj.get('id'):
                
                item = AddonServiceTarif.objects.get(id=obj.get('id'))
                form = AddonServiceTarifForm(obj, instance=item)
                print "instance"
            else:
                print "frompost"
                form = AddonServiceTarifForm(obj)
            
        
            if form.is_valid():
                print "as save"
                addonservice_item = form.save(commit=False)
                addonservice_item.save()
                
                print 'as post save'
            else:
                print form._errors
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            addonservices_ids.append(addonservice_item.id)
        

        if addonservices_ids:
            AddonServiceTarif.objects.filter(tarif=tariff).exclude(id__in=addonservices_ids).delete()
    else:
        AddonServiceTarif.objects.filter(tarif=tariff).delete()
            
    if js.get('onetimeservices'):
        
        onetimeservices_ids = []
        for onetimeservice in js.get('onetimeservices', []):
            onetimeservice['tarif']=tariff.id
            if onetimeservice.get('id'):
                
                item = OneTimeService.objects.get(id=onetimeservice.get('id'))
                form = OneTimeServiceForm(onetimeservice, instance=item)
                print "instance"
            else:
                print "frompost"
                form = OneTimeServiceForm(onetimeservice)
            
        
            if form.is_valid():
                print "os save"
                onetimeservice_item = form.save(commit=False)
                onetimeservice_item.save()
                
                print 'os post save'
            else:
                print form._errors
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            onetimeservices_ids.append(onetimeservice_item.id)
        

        if onetimeservices_ids:
            OneTimeService.objects.filter(tarif=tariff).exclude(id__in=onetimeservices_ids).delete()
    else:
        OneTimeService.objects.filter(tarif=tariff).delete()
        
    if js.get('limites'):
        
        limites_ids = []
        speedlimites_ids = []
        for (limit, speedlimit) in js.get('limites', []):
            limit['tarif']=tariff.id
            if limit.get('id'):
                print 'limit.id', limit.get("id")
                item = TrafficLimit.objects.get(id=limit.get('id'))
                form = TrafficLimitForm(limit, instance=item)
                print "instance"
            else:
                print "frompost"
                form = TrafficLimitForm(limit)
            
        
            if form.is_valid():
                print "limit save"
                limit_item = form.save(commit=False)
                limit_item.save()
                
                print 'limit post save'
            else:
                print form._errors
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            limites_ids.append(limit_item.id)
            
            if limit_item.action ==0:
                SpeedLimit.objects.filter(limit=limit_item).delete()
            elif  limit_item.action ==1:
                if speedlimit:
                    speedlimit['limit']=limit_item.id
                    if speedlimit.get('id'):
                        
                        item = SpeedLimit.objects.get(id=speedlimit.get('id'))
                        form = SpeedLimitForm(speedlimit, instance=item)
                        print "instance"
                    else:
                        print "frompost"
                        form = SpeedLimitForm(speedlimit)
    
                    if form.is_valid():
                        print "limit save"
                        speedlimit_item = form.save(commit=False)
                        speedlimit_item.save()
                        
                        print ' speed imit post save'
                    else:
                        print form._errors
                        transaction.rollback()
                        return {'status':False, 'errors': form._errors}
                    speedlimites_ids.append(speedlimit_item.id)
    
            if speedlimites_ids:
                SpeedLimit.objects.filter(limit=limit_item).exclude(id__in=speedlimites_ids).delete()
            
        if limites_ids:
            TrafficLimit.objects.filter(tarif=tariff).exclude(id__in=limites_ids).delete()
                
    else:
        for tl in TrafficLimit.objects.filter(tarif=tariff):
             SpeedLimit.objects.filter(limit=tl).delete()
             tl.delete()
            
    if js.get('time_access_service'):
        obj = js.get('time_access_service')
        if obj.get('id'):
            
            item = TimeAccessService.objects.get(id=obj.get('id'))
            form = TimeAccessServiceForm(obj, instance=item)
            print "instance"
        else:
            print "frompost"
            form = TimeAccessServiceForm(obj)
        
    
        if form.is_valid():
            print "os save"
            timeaccessservice = form.save(commit=False)
            timeaccessservice.save()
            tariff.time_access_service = timeaccessservice
            tariff.save()
            print 'os post save'
        else:
            print form._errors
            transaction.rollback()
            return {'status':False, 'errors': form._errors}

        
        time_access_nodes_ids = []
        
        for timeaccessnode in js.get('timeaccessnodes', []):

            timeaccessnode['time_access_service']=timeaccessservice.id
            if timeaccessnode.get('id'):
                item = TimeAccessNode.objects.get(id=timeaccessnode.get('id'))
                form = TimeAccessNodeForm(timeaccessnode, instance=item)
                print "instance"
            else:
                print "frompost"
                form = TimeAccessNodeForm(timeaccessnode)

            if form.is_valid():
                timeaccessnode_item = form.save(commit=False)
                timeaccessnode_item.save()
                
            else:
                print form._errors
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            time_access_nodes_ids.append(timeaccessnode_item.id)
            
        if time_access_nodes_ids:
            TimeAccessNode.objects.filter(time_access_service=timeaccessservice).exclude(id__in=time_access_nodes_ids).delete()
    else:
        if tariff.time_access_service:
            TimeAccessNode.objects.filter(id=tariff.time_access_service).delete()
            tariff.time_access_service.delete()

    if js.get('traffic_transmit_service'):
        if 'id' in js.get('traffic_transmit_service'):
            item = TrafficTransmitService.objects.get(id=js.get('traffic_transmit_service')['id'])
            form = TrafficTransmitServiceForm(js.get('traffic_transmit_service'), instance=item)
            print "instance"
        else:
            print "frompost"
            form = TrafficTransmitServiceForm(js.get('traffic_transmit_service', {}))
            
        
        if form.is_valid():
            print 'tr transmit  save pre'
            traffic_transmit_service = form.save(commit=False)
            traffic_transmit_service.save()
            tariff.traffic_transmit_service = traffic_transmit_service
            tariff.save()
            print 'tr transmit save post'
        else:
            print form._errors
            transaction.rollback()
            return {'status':False, 'errors': form._errors}
        
        traffictransmitnodes_ids = []
        for traffictransmitnode in js.get('traffictransmitnodes', []):
            print traffictransmitnode
            traffictransmitnode['traffic_transmit_service']=traffic_transmit_service.id
            if traffictransmitnode.get('id'):
                item = TrafficTransmitNodes.objects.get(id=traffictransmitnode.get('id'))
                form = TrafficTransmitNodeForm(traffictransmitnode, instance=item)
                print "instance"
            else:
                print "frompost"
                form = TrafficTransmitNodeForm(traffictransmitnode)

            if form.is_valid():
                traffictransmitnode_item = form.save(commit=False)
                traffictransmitnode_item.save()
                
            else:
                print form._errors
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            traffictransmitnodes_ids.append(traffictransmitnode_item.id)
            
        if traffictransmitnodes_ids:
            TrafficTransmitNodes.objects.filter(traffic_transmit_service=traffic_transmit_service).exclude(id__in=traffictransmitnodes_ids).delete()
            
        prepaidtraffic_ids = []
        for prepaidtrafficnode in js.get('prepaidtrafficnodes', []):
            print prepaidtrafficnode
            prepaidtrafficnode['traffic_transmit_service']=traffic_transmit_service.id
            if prepaidtrafficnode.get('id'):
                item = PrepaidTraffic.objects.get(id=prepaidtrafficnode.get('id'))
                form = PrepaidTrafficForm(prepaidtrafficnode, instance=item)
                print "instance"
            else:
                print "frompost"
                form = PrepaidTrafficForm(prepaidtrafficnode)

            if form.is_valid():
                prepaidtraffictransmitnode_item = form.save(commit=False)
                prepaidtraffictransmitnode_item.save()
                
            else:
                print form._errors
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            prepaidtraffic_ids.append(prepaidtraffictransmitnode_item.id)
        if traffictransmitnodes_ids:
            PrepaidTraffic.objects.filter(traffic_transmit_service=traffic_transmit_service).exclude(id__in=prepaidtraffic_ids).delete()
            
    else:
        if tariff.traffic_transmit_service:
            TrafficTransmitService.objects.filter(id=tariff.traffic_transmit_service.id).delete()
            TrafficTransmitNodes.objects.filter(traffic_transmit_service=tariff.traffic_transmit_service).delete()
            
    if js.get('radius_traffic_service'):
        if 'id' in js.get('radius_traffic_service'):
            item = RadiusTraffic.objects.get(id=js.get('radius_traffic_service')['id'])
            form = RadiusTrafficForm(js.get('radius_traffic_service'), instance=item)
            print "instance"
        else:
            print "frompost"
            form = RadiusTrafficForm(js.get('radius_traffic_service', {}))
            
        
        if form.is_valid():
            print 'rad tr transmit  save pre'
            radius_traffic_service = form.save(commit=False)
            radius_traffic_service.save()
            tariff.radius_traffic_transmit_service = radius_traffic_service
            tariff.save()
            print 'rad tr transmit save post'
        else:
            print form._errors
            transaction.rollback()
            return {'status':False, 'errors': form._errors}
        
        radiustraffictransmitnodes_ids = []
        for radtraffictransmitnode in js.get('radiustrafficnodes', []):
            print radtraffictransmitnode
            radtraffictransmitnode['radiustraffic']=radius_traffic_service.id
            if radtraffictransmitnode.get('id'):
                item = RadiusTrafficNode.objects.get(id=radtraffictransmitnode.get('id'))
                form = RadiusTrafficNodeForm(radtraffictransmitnode, instance=item)
                print "instance"
            else:
                print "frompost"
                form = RadiusTrafficNodeForm(radtraffictransmitnode)

            if form.is_valid():
                radtraffictransmitnode_item = form.save(commit=False)
                radtraffictransmitnode_item.save()
                
            else:
                print form._errors
                transaction.rollback()
                return {'status':False, 'errors': form._errors}
            radiustraffictransmitnodes_ids.append(radtraffictransmitnode_item.id)
            
        if radiustraffictransmitnodes_ids:
            RadiusTrafficNode.objects.filter(radiustraffic=radius_traffic_service).exclude(id__in=radiustraffictransmitnodes_ids).delete()
        
    else:
        if tariff.radius_traffic_transmit_service:
            RadiusTrafficNode.objects.filter(radiustraffic=tariff.radius_traffic_transmit_service).delete()
            tariff.radius_traffic_transmit_service.delete()
            
    transaction.commit()
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {'status':True, 'tariff_id':tariff.id}

@ajax_request
@login_required
def groups_save(request):
    
    id = request.POST.get('id')
    traffic_classes = request.POST.get('traffic_classes','').split(',')
    if id:
        item = Group.objects.get(id=id)
        form = GroupForm(request.POST, instance=item)
    else:
        form = GroupForm(request.POST)
        
    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            if id:
                GroupTrafficClass.objects.filter(group=model).delete()
            print 
            for item in traffic_classes:
                print "item", item
                GroupTrafficClass.objects.create(group=model, trafficclass = TrafficClass.objects.get(id=item))
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return res

@ajax_request
@login_required
def nas_save(request):
    id = request.POST.get('id')
    print 'id',id
    print request.POST
    if id:
        nas = Nas.objects.get(id=id)
        form = NasForm(request.POST, instance = nas)
    else:
        form = NasForm(request.POST)
        
    
    if form.is_valid():
        form.save()
        return {"status": True, "message": 'yes'}
    else:
        return {"status": False, "message": form._errors}

@ajax_request
@login_required
def contracttemplates_set(request):
    id = request.POST.get('id')

    if id:
        item = ContractTempalte.objects.get(id=id)
        form = ContractTemplateForm(request.POST, instance = item)
    else:
        form = ContractTemplateForm(request.POST)
        
    
    if form.is_valid():
        form.save()
        return {"status": True}
    else:
        return {"status": False, "message": form._errors}

@ajax_request
@login_required
def contracttemplate_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        ContractTemplate.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "ContractTemplate not found"}
    

@login_required
@ajax_request
def settlementperiod_save(request):
    id = request.POST.get('id')
    print id
    print request
    if id:
        item = SettlementPeriod.objects.get(id=id)
        form = SettlementPeriodForm(request.POST, instance = item)
    else:
        form = SettlementPeriodForm(request.POST)
        
    
    if form.is_valid():
        print "form valid"
        d = form.save(commit=False)
        d.save()
        return {"status": True}
    else:
        print "form invalid"
        return {"status": False, "message": form._errors}


@login_required
@ajax_request
def addonservices_set(request):
    data = json.loads(request.POST.get('data', "{}"))
    print data
    id = data.get('id')
    if id:
        item = AddonService.objects.get(id=id)
        form = AddonServiceForm(data, instance = item)
    else:
        form = AddonServiceForm(data)
        
    
    if form.is_valid():
        print "form valid"
        d = form.save(commit=False)
        d.save()
        return {"status": True}
    else:
        print "form invalid"
        print form
        return {"status": False, "message": form._errors}
    
@ajax_request
@login_required
def settlementperiod_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        SettlementPeriod.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Nas not found"}

@ajax_request
@login_required
def addonservices_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        AddonService.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "AddonService not found"}



@ajax_request
@login_required
def groups_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        Group.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Group not found"}


@ajax_request
@login_required
def accounttariffs_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        try:
            item = AccountTarif.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный тарифный план не найден тарифный план %s" % str(e)}
        if item.datetime<datetime.datetime.now():
            return {"status": False, "message": u"Невозможно удалить вступивший в силу тарифный план"}
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "AccountTarif not found"}
  
@ajax_request
@login_required
def suspendedperiod_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        try:
            item = SuspendedPeriod.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный период не найден %s" % str(e)}
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SuspendedPeriod not found"} 

@ajax_request
@login_required
def get_tariffs(request):
    items = Tariff.objects.all_with_deleted().order_by('name')
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append({'active':item.active,'id':item.id, 'access_type':item.access_parameters.access_type, 'name':item.name, 'deleted':item.deleted})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def accounts_for_tarif(request):
    
    tarif_id = int(request.POST.get('tarif_id', -1000))
    print 'tarif_id', tarif_id
    
    
    from django.db import connection
    
    cur = connection.cursor()
    

    items = []
    if tarif_id==-3000:
        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status, acc.last_balance_null, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name,org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,(SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address 
            FROM billservice_account AS acc 
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id 
            WHERE acc.deleted is Null and get_tarif(acc.id) is Null ORDER BY acc.username ASC;""")
            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}
    
    elif tarif_id==-1000:

        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status, acc.last_balance_null, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name, (SELECT name FROM billservice_tariff WHERE id=get_tarif(acc.id)) as tariff, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,(SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address
            FROM billservice_account AS acc 
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id
            WHERE acc.deleted is Null 
            ORDER BY acc.username ASC;""" )

            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}

    elif tarif_id==-4000:#Физ лица
        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status, acc.last_balance_null, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name, (SELECT name FROM billservice_tariff WHERE id=get_tarif(acc.id)) as tarif_name, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,(SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address
            FROM billservice_account AS acc 
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id 
            WHERE  acc.deleted is Null and  acc.id not IN (SELECT account_id FROM billservice_organization) ORDER BY acc.username ASC;""" )
            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}        

    elif tarif_id==-5000:#Юр лица
        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status, acc.last_balance_null, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name, (SELECT name FROM billservice_tariff WHERE id=get_tarif(acc.id)) as tarif_name, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,(SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address
            FROM billservice_account AS acc 
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id 
            WHERE acc.deleted is Null and  acc.id IN (SELECT account_id FROM billservice_organization)  ORDER BY acc.username ASC;""" )
            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}        

    elif tarif_id==-12000:#Архив
        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status, acc.last_balance_null, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name, (SELECT name FROM billservice_tariff WHERE id=get_tarif(acc.id)) as tariff, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,(SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address
            FROM billservice_account AS acc 
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id 
            WHERE deleted is not Null  ORDER BY acc.username ASC;""" )
            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}   
    else:
        
        try:
            cur.execute("""SELECT acc.id, acc.room, acc.username, acc.fullname, acc.email, acc.nas_id, acc.ipn_status, acc.ipn_added, acc.suspended, acc.created, acc.ballance, acc.credit, acc.contract, acc.disabled_by_limit, acc.balance_blocked, acc."comment", acc.status, acc.last_balance_null, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name, org.id as org_id, org.name as org_name,ARRAY(SELECT DISTINCT vpn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as vpn_ips,ARRAY(SELECT DISTINCT ipn_ip_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_ips,ARRAY(SELECT DISTINCT ipn_mac_address FROM billservice_subaccount as subacc WHERE subacc.account_id=acc.id) as ipn_macs,(SELECT True FROM radius_activesession WHERE account_id=acc.id and session_status='ACTIVE' limit 1) as account_online, ((SELECT name FROM billservice_street where id=acc.street_id) || ', '|| (SELECT name FROM billservice_house where id=acc.house_id)) as address
            FROM billservice_account AS acc 
            LEFT JOIN billservice_organization as org ON org.account_id=acc.id 
            WHERE acc.deleted is Null and %s=get_tarif(acc.id)  ORDER BY acc.username ASC;""", (tarif_id,) )
            items = dictfetchall(cur)
        except Exception, e:
            return { 'status':False, 'message':str(e)}   
        
    res=[]
    print "len items", len(items)
#===============================================================================
#    for item in items:
# 
#        res.append({'id':item.id,'room':item.room, 'username':item.username, 'tariff':item.tariff, 'fullname':item.fullname, 'address':"%s %s" % (item.street or '', item.house or ''), 'email':item.email, 'suspended':item.suspended, 'created':item.created, 'ballance':item.ballance, 'credit':item.credit, 'contract':item.contract, 'disabled_by_limit':item.disabled_by_limit, 'balance_blocked':item.balance_blocked, 'comment':item.comment, 'status':item.status,  'org_name': item.organization_set.all()[0].name if len(item.organization_set.all())==1 else '','vpn_ips':vpn_ips,'ipn_ips':ipn_ips,'ipn_macs':ipn_macs,})
#        
#===============================================================================
    return {"records": items, 'status':True, 'totalCount':len(items)}
    
@ajax_request
@login_required
def nas_delete(request):
    id = request.POST.get('id')
    print 'id',id
    print request.POST
    if id:
        Nas.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Nas not found"}


@ajax_request
@login_required
def subaccount_delete(request):
    id = request.POST.get('id')
    print 'id',id
    print request.POST
    if id:
        
        item = SubAccount.objects.get(id=id)
        if item.vpn_ipinuse:
            IPInUse.objects.filter(id=item.vpn_ipinuse).delete()
        if item.ipn_ipinuse:
            IPInUse.objects.filter(id=item.ipn_ipinuse).delete()
        if item.vpn_ipv6_ipinuse:
            IPInUse.objects.filter(id=item.vpn_ipv6_ipinuse).delete()
        
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SubAccount not found"}

@ajax_request
@login_required
def account_delete(request):
    id = request.POST.get('id')
    print 'id',id
    print request.POST
    if id:
        try:
           Account.objects.get(id=id).delete()
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
            form.save()
            res={"success": True}
        except Exception, e:
            print e
            res={"success": False, "message": str(e)}
    else:
        res={"success": False, "errors": form._errors}
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return res

@ajax_request
@login_required
def switch(request):
    from nas.models import Switch
    items = Switch.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    res.append({"id":None, "name":u'-- Не указан --'})
    for item in items:
        res.append({"id":item.id, "name":item.name})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

@ajax_request
@login_required
def ippool(request):

    pool_type = request.POST.get('pool_type')
    items = IPPool.objects.filter(type=pool_type)
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    res.append({"id":None, "name":u'-- Не указан --'})
    for item in items:
        res.append({"id":item.id, "name":item.name})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}


@ajax_request
@login_required
def streets(request):
    city_id = request.POST.get('city_id')
    id = request.POST.get('id')
    if city_id:
        items = Street.objects.filter(city__id=city_id)
    elif id:
        items = Street.objects.get(id=id)
    else:
        items = Street.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item))
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def streets_set(request):
    
    id = request.POST.get('id')
    if id:
        item = Street.objects.get(id=id)
        form = StreetForm(request.POST, instance=item)
    else:
        form = StreetForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def streets_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        Street.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Street not found"}
    
@ajax_request
@login_required
def accountstatus(request):
    items = [1,u'Активен'], \
            [2,u'Не активен, списывать периодические услуги'],\
            [3,u'Не активен, не списывать периодические услуги'],\
            [4,u'Пользовательская блокировка'],
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for id,name in items:
        res.append({"id":id, "name":name})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

@ajax_request
@login_required
def account_save(request):
    
    #from django.core import serializers
    #from django.http import HttpResponse
    print request
    id = request.POST.get('id')
    tarif_id = request.POST.get('tarif_id')
    print "id=", id
    contract = request.POST.get('contract','')

    bank_bank = request.POST.get('bank_bank')
    bank_bankcode = request.POST.get('bankcode')
    bank_rs = request.POST.get('rs')
    bank_currency = request.POST.get('currency')
    #model.bank_id = self.connection.save(bank, "billservice_bankdata")
    #self.bank = bank
    
    org_name = request.POST.get('org_name')
    org_uraddress = request.POST.get('uraddress')
    org_phone = request.POST.get('phone')
    org_fax = request.POST.get('fax')
    org_okpo = request.POST.get('okpo')
    org_unp = request.POST.get('unp')
    org_kpp = request.POST.get('kpp')
    org_kor_s = request.POST.get('kor_s')
        
    newcontract=False
    acc = None
    if id:
        acc = Account.objects.all_with_deleted().get(id=id)
        
        if acc.contract=='' and contract:
            #new
            newcontract=True
        a=AccountForm(request.POST, instance=acc)
    else:
        if contract!='':
            #new
            newcontract=True
        a=AccountForm(request.POST)
    p=request.POST
    res=[]
    #print "a.is_valid()",a.is_valid()
    print a._errors
    #print a.clean()
    
    #acc.username=p.get("username")
    #acc.password=p.get("password")
    #acc.fullllname=p.get("fullname")
    if a.is_valid():
        contr = None
        if contract:
            contr = ContractTemplate.objects.filter(template=contract)
            if contr:
                contr=contr[0]
            if acc:
                pass
        if newcontract:
            if not acc:
                id=Account.objects.all().order_by("-id")[0].id+1
            else:
                id = acc.id
            contract_template = contr.template if contr else contract
            contract_counter = contr.counter if contr else 0
            year=a.created.year
            month=a.created.month
            day=a.created.day
            hour=a.created.hour
            minute=a.created.minute
            second=a.created.second
            contract_num=contr.count+1
            
            
            d={'account_id':id,'year':year,'month':month, 'day':day, 'hour':hour, 'minute':minute,'second':second, 'tarif_type':tarif_type, 'contract_num':contract_num}
            d.update(model.__dict__)

            contract = contract_template % d
            if contr:
                contr.count = contr.count+1 
            #cur.execute("UPDATE billservice_account SET contract=%s WHERE id=%s", (contract, id))
            #cur.execute("UPDATE billservice_contracttemplate SET counter=counter+1 WHERE id=%s", (template_id,))
        

        
        try:
            item = a.save(commit=False)
            item.save()
            bank = None
            org = None
            organization = Organization.objects.filter(account=item)
            if organization:
                org = organization[0]
                bank = org.bank
                if org and not (rg_name or org_uraddress or org_phone):
                    bank.delete()
                    org.delete()
            elif org_name or org_uraddress or org_phone:
                org = Organization()
                if bank_bank:
                    bank = BankData()
            
                    bank.name = bank
                    bank.bankcode = bank_bankcode
                    bank.rs = bank_rs
                    bank.currency = bank_currency
                    bank.save()
            
            if org:
                org.name = org_name
                org.okpo = org_okpo
                org.uraddress = org_uraddress
                org.phone = org_phone
                org.kor_s = org_kor_s
                org.kpp = org_kpp
                org.unp = org_unp
                org.fax = org_fax
                org.account = item
                if bank:
                    org.bank = bank
                org.save()
            
                
            if not id and tarif_id and tarif_id>0:
                accounttarif = AccountTarif()
                accounttarif.account=item
                accounttarif.tarif=Tariff.objects.get(id=tarif_id)
                accounttarif.datetime = item.created
                accounttarif.save()
            if contr:
                item.contract = contract
                item.save()
                contr.save()
            res={"status": True, 'account_id':item.id}
        except Exception, e:
            print e
            res={"status": False, "errors": [{'error':str(e)}]}
    else:
        
        res={"status": False, "errors": a._errors, 'msg':u"Поля с ошибками:<br />"+unicode('<br />'.join([u'%s:%s' %(x,a._errors.get(x)) for x in a._errors]))}
    return res

@login_required
@ajax_request
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
    id=None if request.POST.get('id')=='None' else request.POST.get('id')
    ipv4_vpn_pool = None if request.POST.get('ipv4_vpn_pool')=='None' else request.POST.get('ipv4_vpn_pool')
    ipv4_ipn_pool = None if request.POST.get('ipv4_ipn_pool')=='None' else request.POST.get('ipv4_ipn_pool')
    account_id = None if request.POST.get('account')=='None' else request.POST.get('account')
    print "account_id", account_id
    vpn_pool = None
    if ipv4_vpn_pool:
        vpn_pool = IPPool.objects.get(id=ipv4_vpn_pool)
    ipn_pool = None
    if ipv4_ipn_pool:
        ipn_pool = IPPool.objects.get(id=ipv4_ipn_pool)
        
    cc=None
    if id:
        cc = SubAccount.objects.get(id=id)
        
        a=SubAccountForm(request.POST,instance=cc)
        f=SubAccountForm(request.POST)
    else:
        a=SubAccountForm(request.POST)
    #a.account=aa.account_id
    p=request.POST
    res=[]
    
    #print instance_dict(cc)
    #print "cc1",cc.vpn_ipinuse
    
    if a.is_valid():
        try:
            subacc = a.save(commit=False)
            pass
            subacc.save()
        except Exception, e:
            print e
            res={"success": False, "errors": a._errors}
            return res
        print 1
        
        # print "cc.vpn_ipinuse11",cc.vpn_ipinuse
        subaccounts = 0
        """
        bug???
        _wrapped_view() takes at least 1 argument (0 given)
        if subacc.username:
            if not id:
                subaccounts = SubAccount.objects.filter(username = subacc.username ).exclude(account__id = account).count()
            else:
                subaccounts = SubAccount.objects.exclude(id = id).filter(account__id = account, username = subacc.username).count()
            if subaccounts>0:
                return {"status": False, 'message':u'Выбранное имя пользователя используется в другом аккаунте'}

        """
        """
        if subacc.ipn_mac_address:    
            if not id:
                subaccounts = SubAccount.objects.exclude(account__id = account).filter(ipn_mac_address = subacc.ipn_mac_address).count()
            else:
                subaccounts = SubAccount.objects.exclude(id = id).exclude(account__id = account).filter(ipn_mac_address = subacc.ipn_mac_address).count()

            if subaccounts>0:
                return {"status": False, 'message':u'Выбранный мак-адрес используется в другом аккаунте'}

        if subacc.vpn_ip_address and not subacc.vpn_ip_address.startswith('0.0.0.0'):    
            if not id:
                subaccounts = SubAccount.objects.exclude(account__id = account).filter(vpn_ip_address = subacc.vpn_ip_address).count()
            else:
                subaccounts = SubAccount.objects.exclude(id = id).exclude(account__id = account).filter(vpn_ip_address = subacc.vpn_ip_address).count()

            if subaccounts>0:
                return {"status": False, 'message':u'Выбранный vpn_ip_address используется в другом аккаунте'}

        if subacc.ipn_ip_address and not subacc.ipn_ip_address.startswith('0.0.0.0'):    
            if not id:
                subaccounts = SubAccount.objects.exclude(account__id = account).filter(ipn_ip_address = subacc.ipn_ip_address, ).count()
            else:
                subaccounts = SubAccount.objects.exclude(~Q(id = id)).exclude(account__id = account).filter(ipn_ip_address = subacc.ipn_ip_address).count()

            if subaccounts>0:
                return {"status": False, 'message':u'Выбранный ipn_ip_address используется в другом аккаунте'}

        """
        if cc and cc.vpn_ipinuse:
            print 2
            #vpn_pool = IPPool.objects.get(id=ipv4_vpn_pool)
            
            if  subacc.vpn_ip_address not in ['0.0.0.0','',None]:
                if vpn_pool:
                    if not IPy.IP(vpn_pool.start_ip).int()<=IPy.IP(subacc.vpn_ip_address).int()<=IPy.IP(vpn_pool.end_ip).int():
                        return {"status": False, 'message':u'Выбранный VPN IP адрес не принадлежит указанному VPN пулу'}
                    
                
                    if cc.vpn_ipinuse.ip!=subacc.vpn_ip_address:
                        obj = subacc.vpn_ipinuse
                        obj.disabled=datetime.datetime.now()
                        obj.save()
                        
                        subacc.vpn_ipinuse = IPInUse.objects.create(pool=vpn_pool,ip=subacc.vpn_ip_address,datetime=datetime.datetime.now())
                else:
                    obj = subacc.vpn_ipinuse
                    obj.disabled=datetime.datetime.now()
                    obj.save()
                    subacc.vpn_ipinuse = None
                
                    
                
            elif subacc.vpn_ip_address in ['0.0.0.0','',None]:
                print 5
                obj = subacc.vpn_ipinuse
                obj.disabled=datetime.datetime.now()
                obj.save()
                subacc.vpn_ipinuse=None
        elif subacc.vpn_ip_address not in ['0.0.0.0','',None] and vpn_pool:
            print 6
            if not IPy.IP(vpn_pool.start_ip).int()<=IPy.IP(subacc.vpn_ip_address).int()<=IPy.IP(vpn_pool.end_ip).int():
                return {"status": False, 'message':u'Выбранный VPN IP адрес не принадлежит указанному VPN пулу'}
            print 7
            ip=IPInUse(pool=vpn_pool, ip=subacc.vpn_ip_address, datetime=datetime.datetime.now())
            ip.save()
            subacc.vpn_ipinuse = ip 
            
        if cc and cc.ipn_ipinuse:
            print 2
            #vpn_pool = IPPool.objects.get(id=ipv4_vpn_pool)
            
            if  subacc.ipn_ip_address not in ['0.0.0.0','',None]:
                if vpn_pool:
                    if not IPy.IP(ipn_pool.start_ip).int()<=IPy.IP(subacc.ipn_ip_address).int()<=IPy.IP(ipn_pool.end_ip).int():
                        return {"status": False, 'message':u'Выбранный IPN IP адрес не принадлежит указанному IPN пулу'}
                    
                
                    if cc.ipn_ipinuse.ip!=subacc.ipn_ip_address:
                        obj = subacc.ipn_ipinuse
                        obj.disabled=datetime.datetime.now()
                        obj.save()
                        
                        subacc.ipn_ipinuse = IPInUse.objects.create(pool=ipn_pool,ip=subacc.ipn_ip_address,datetime=datetime.datetime.now())
                else:
                    obj = subacc.ipn_ipinuse
                    obj.disabled=datetime.datetime.now()
                    obj.save()
                    subacc.ipn_ipinuse = None
                
                    
                
            elif subacc.vpn_ip_address in ['0.0.0.0','',None]:
                print 5
                obj = subacc.ipn_ipinuse
                obj.disabled=datetime.datetime.now()
                obj.save()
                subacc.ipn_ipinuse=None
        elif subacc.vpn_ip_address not in ['0.0.0.0','',None] and ipn_pool:
            print 6
            if not IPy.IP(ipn_pool.start_ip).int()<=IPy.IP(subacc.ipn_ip_address).int()<=IPy.IP(ipn_pool.end_ip).int():
                return {"status": False, 'message':u'Выбранный IPN IP адрес не принадлежит указанному IPN пулу'}
            print 7
            ip=IPInUse(pool=ipn_pool, ip=subacc.ipn_ip_address, datetime=datetime.datetime.now())
            ip.save()
            subacc.ipn_ipinuse = ip 
       
        try:
            subacc.save()
            print 99
            res={"status": True,'account_id':subacc.account.id}
        except Exception, e:
            print e
            res={"status": False, "errors": a._errors}
    else:
        res={"status": False, "errors": a._errors}
    return res

@ajax_request
@login_required
def subaccount_delete(request):
    
    #from django.core import serializers
    #from django.http import HttpResponse
    print request
    id=request.POST.get('id')
    if id:
        SubAccount.objects.get(id=id).delete()
        return {"success": True}
    else:
        return {"success": False,'msg':u'Субаккаунт не найден'}
    
@ajax_request
@login_required
def getipfrompool(request):
    default_ip='0.0.0.0'
    if default_ip:
        default_ip = IPy.IP(default_ip).int()
    pool_id=request.POST.get("pool_id")
    limit=int(request.POST.get("limit", 50))
    start=int(request.POST.get("start", 0))
    print request
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
    return {'totalCount':str(len(res)),'records':res[start:start+limit], 'status':True}

@ajax_request
@login_required
def houses(request):
    street_id = request.POST.get('street_id')
    id = request.POST.get('id')
    fields = request.POST.get('fields')
    if street_id:
        items = House.objects.filter(street__id=street_id)
    elif id:
        items = House.objects.get(id=id)
    else:
        items = House.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item, fields = fields))
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def houses_set(request):
    
    id = request.POST.get('id')
    if id:
        item = House.objects.get(id=id)
        form = HouseForm(request.POST, instance=item)
    else:
        form = HouseForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"status": False, "errors": form._errors}
 
    return res

@ajax_request
@login_required
def houses_delete(request):
    id = int(request.POST.get('id',0))
    if id:
        House.objects.get(id=id).delete()
        return {"status": True}
    else:
        return {"status": False, "message": "House not found"}
    
@ajax_request
@login_required
def accountaddonservices(request):
    from billservice.models import AccountAddonService
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
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item,normal_fields=normal_fields))
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def accountaddonservices_get(request):
    from billservice.models import AccountAddonService
    id = request.POST.get('id')
    item = AccountAddonService.objects.get(id=id)
    print instance_dict(item).keys()
    return {"records": instance_dict(item)}

@ajax_request
@login_required
def accountaddonservices_set(request):
    id = request.POST.get('id')
    from billservice.models import AccountAddonService
    
    if id:
        item = AccountAddonService.objects.get(id=id)
        form = AccountAddonServiceModelForm(request.POST, instance=item)
    else:
        form = AccountAddonServiceModelForm(request.POST)
        
    if form.is_valid():
        form.save()
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
        item = AccountTarif.objects.get(id=id)
        form = AccountTariffForm(request.POST, instance=item)
    else:
        form = AccountTariffForm(request.POST)
        
    if form.is_valid():
        form.save()
        res = {'status':True}
    else:
        res={"status": False, "errors": form._errors}
    #print instance_dict(item).keys()
    return res

@ajax_request
@login_required
def accounttariffs_bathset(request):
    
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
            except Exception, e:
                res={"status": False, "message": str(e)}
            
        
        res = {'status':True}
    else:
        res={"status": False, "errors": form._errors}
    #print instance_dict(item).keys()
    return res


@ajax_request
@login_required
def systemuser(request):
    items = SystemUser.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    res.append({"id":None, "name":u'-- Не указан --'})
    for item in items:
        res.append({"id":item.id, "name":"%s %s" % (item.username, item.fullname)})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

@ajax_request
@login_required
def suspendedperiods(request):
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
def suspendedperiod_get(request):
    id = request.POST.get('id')
    item = SuspendedPeriod.objects.get(id=id)

    return {"records": instance_dict(item)}

@ajax_request
@login_required
def suspendedperiod_set(request):
    id = request.POST.get('id')
    if id:
        item = SuspendedPeriod.objects.get(id=id)
        form = SuspendedPeriodModelForm(request.POST, instance=item)
    else:
        form = SuspendedPeriodModelForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"success": False, "errors": form._errors}
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return res

@ajax_request
@login_required
def transaction_set(request):
    
    form = TransactionModelForm(request.POST)
        
    if form.is_valid():
        try:
            tr=form.save(commit=False)
            #tr.update_ballance()
            tr.summ=tr.summ
            tr.systemuser = request.user.account
            tr.save()
            res={"status": True, 'transaction_id':tr.id}
        except Exception, e:
            print e
            res={"status": False, "msg": str(e)}
    else:
        res={"status": False, "errors": form._errors}
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return res




@login_required
@ajax_request
def subaccount(request):
    id=request.POST.get('id')
    acc = SubAccount.objects.get(id=id)
    from django.core import serializers
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    #data = serializers.serialize("json", [acc], ensure_ascii=False, fields=['username'])
    data=instance_dict(acc)
    #print data
    #res.append({"id":acc.id, "username":acc.username, "password":acc.password, "fullname":acc.fullname,'vpn_ip_address':'',
    #                'status':acc.status,'ipn_ip_address':'','city':'','street':'','nas_id':'','email':'','comment':'',
    #                'ballance':float(acc.ballance),'credit':float(acc.credit),'created':'02.11.1984 00:00:00',
    #                })
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": data}

@login_required
@ajax_request
def transactiontypes(request):
    
    id = request.POST.get('id')
    if id:
        items = TransactionType.objects.filter(id=id).order_by('name')
    else:
        items = TransactionType.objects.all().order_by('name')
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append({"id":item.id, "name":item.name, "internal_name":item.internal_name})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res, 'status':True, 'totalCount':len(res)}

@ajax_request
@login_required
def transactiontypes_set(request):
    id = request.POST.get('id')
    if id:
        item = TransactionType.objects.get(id=id)
        form = TransactionTypeForm(request.POST, instance=item)
    else:
        form = TransactionTypeForm(request.POST)
        
    if form.is_valid():
        try:
            form.save()
            res={"status": True}
        except Exception, e:
            print e
            res={"status": False, "message": str(e)}
    else:
        res={"success": False, "errors": form._errors}
    
    return res

@render_to('jsongrid.html')
@login_required
def grid(request):
 
    return {}

@ajax_request
@login_required
def actions_set(request):
    subaccount = request.POST.get('subaccount_id')
    action = request.POST.get('action')
    if subaccount:          

       
        print 'subaccount',subaccount
        #TODO: придумать что тут сделать с realdictcursor_ом
        #cur.execute("SELECT * FROM billservice_subaccount WHERE id=%s",(subaccount,))
        
        #row = cur.fetchone()
        #if not row: return {'status':False}
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

        #cur.execute("SELECT *, id as account_id FROM billservice_account WHERE id=%s",(subacc.account_id,))
        
        #row = cur.fetchone()
        #if not row: return {'status':False}
        #acc = Object(row)
        acc =  instance_dict(sa.account)
        acc['account_id']=acc['id']
        

        #cur.execute("SELECT *, id as nas_id FROM nas_nas WHERE id=%s",(subacc.nas_id,))
        #row = cur.fetchone()
        #if not row: return {'status':False}
        #nas = Object(row)
        try:
            n=sa.nas
            nas = instance_dict(n)
        except Exception, e:
            return {'status':False,'message':u'Не указан или не найден указанный сервер доступа'}
            
        #connection.commit()
        #print "actions", row
        #print action

        #if subacc.ipn_ip_address=="0.0.0.0":
        #    continue

        if action=='disable':
            command = n.subacc_disable_action
        elif action=='enable':
            command = n.subacc_enable_action
        elif action=='create':
            command = n.subacc_add_action
        elif action =='delete':
            command = n.subacc_delete_action
        #print command
        print command
        sended = cred(account=acc, subacc=subacc, access_type='ipn', nas=nas,  format_string=command)
        print sended
        if action=='create' and sended==True:
            #cur.execute("UPDATE billservice_subaccount SET ipn_added=%s, speed='' WHERE id=%s", (True, subacc.id))
            sa.ipn_added=True
            sa.speed=''
            sa.save()
            
            #cur.execute("UPDATE billservice_accountipnspeed SET state=False WHERE account_id=%s", (row['account_id'],))
            

        
        if action =='delete'  and sended==True:
            #cur.execute("UPDATE billservice_subaccount SET ipn_enabled=%s, ipn_added=%s WHERE id=%s", (False, False, subacc.id))
            sa.ipn_enabled=False
            sa.ipn_added=False
            sa.speed=''
            sa.save()
            #cur.execute("DELETE FROM billservice_accountipnspeed WHERE account_id=%s", (row['account_id'],))
            

        if action=='disable' and sended==True:
            #cur.execute("UPDATE billservice_subaccount SET ipn_enabled=%s WHERE id=%s", (False, subacc.id,))
            sa.ipn_enabled=False
            sa.save()
            
        if action=='enable' and sended==True:
            #cur.execute("UPDATE billservice_subaccount SET ipn_enabled=%s WHERE id=%s", (True, subacc.id,))
            sa.ipn_enabled=True
            sa.save()

        #connection.commit()

        
        return {'status':sended, 'message':'Ok'}
    return {'status':False, 'message':'Ok'}
            

@ajax_request
@login_required
def contracttemplate(request):
    items = ContractTemplate.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append({"template":item.template})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}
      
@ajax_request
@login_required 
def documentrender(request):
    form = DocumentRenderForm(request.POST)
    if form.is_valid():
        template = Template.objects.get(id=form.cleaned_data.get('template'))
        templ = mako_template(unicode(template.body), input_encoding='utf-8')
        data=''
        print "form.cleaned_data.get('template')",form.cleaned_data.get('template')
        if template.type.id==1:
    
            account = Account.objects.get(id=form.cleaned_data.get('account'))
            print account
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
def cheque_render(request):
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
            print line, e
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
            print line, e
            continue
        
        id=oid.split(".")[-1]
        ports_speed_status[id]=value
    
    return {'status':True, 'ports_status':ports_status, 'ports_speed_status':ports_speed_status}


@login_required 
@ajax_request
def set_ports_status(self, switch_id):
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
            print line, e
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
            print line, e
            continue
        id=oid.split(".")[-1]
        ports_status[id]=value
        
    return {'status':True, 'ports_status':ports_status}
    