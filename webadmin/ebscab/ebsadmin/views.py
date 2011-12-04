#-*-coding:utf-8 -*-

from lib.decorators import render_to, ajax_request
from billservice.models import Account, SubAccount, TransactionType, City, Street, House, SystemUser,AccountTarif, AddonService, IPPool, IPInUse, ContractTemplate, Document
from billservice.models import Template, AccountHardware
from nas.models import Nas
from radius.models import ActiveSession
from django.contrib.auth.decorators import login_required
from django.db import connection
from billservice.forms import AccountForm, SubAccountForm, SearchAccountForm, AccountTariffForm, AccountAddonForm,AccountAddonServiceModelForm, DocumentRenderForm
from billservice.forms import DocumentModelForm
from utilites import cred
import IPy
from randgen import GenUsername as nameGen , GenPasswd as GenPasswd2
from IPy import IP
from utilites import rosClient
import datetime
from mako.template import Template as mako_template
class Object(object):
    def __init__(self, result=[], *args, **kwargs):
        for key in result:
            setattr(self, key, result[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])  
            
@ajax_request
@login_required
def jsonaccounts(request):
    if request.GET.get('action')!='search':
        items = Account.objects.all()
    else:
        f=SearchAccountForm(request.GET)
        print f.errors
        print f.cleaned_data
        query={}
        for k in f.cleaned_data:
            if f.cleaned_data.get(k):
                query[k]=f.cleaned_data.get(k)
            
        items = Account.objects.filter(**query)
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
    return {"records": res, 'total':len(res)}

@ajax_request
@login_required
def account_livesearch(request):
    from extdirect.django.store import ExtDirectStore
    query=request.POST.get('query')
    field=request.POST.get('field')
    if not (query and field):return {"records": [], 'total':0}
    items = Account.objects.filter(**{'%s__icontains' % field:query})
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
        return {'success':False, 'msg':u'Сервер доступа не указан'}
    ipn_ip_address = request.POST.get('ipn_ip_address')
    try:
        nas = Nas.objects.get(id=nas_id)
    except Exception, e:
        return {'success':False, 'msg':str(e)}
    try:
        IPy.IP(ipn_ip_address)
    except Exception, e:
        return {'success':False, 'msg':str(e)}
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
        return {'success':False, 'msg':str(e)}
    
    return {'success':True, 'mac':mac}
    
@ajax_request
@login_required
def subaccounts(request):
    account_id = request.POST.get('account_id')
    print "subaccount", account_id
    accounts = SubAccount.objects.filter(account__id=account_id)
    #print accounts
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for acc in accounts:
        #print instance_dict(acc).keys()
        res.append(instance_dict(acc,normal_fields=True))
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res}

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
def template(request):

    items = Template.objects.all().order_by('name')
    #print accounts
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        #print instance_dict(acc).keys()
        res.append({'id':item.id,'name':item.name})
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res}

@ajax_request
@login_required
def sessions(request):
    #account_id = request.POST.get('account_id')
    #print "subaccount", account_id
    items = ActiveSession.objects.all().order_by('-interrim_update')
    #print accounts
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        #print instance_dict(acc).keys()
        res.append(instance_dict(item,normal_fields=True))
        
    print instance_dict(item,normal_fields=True).keys()
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res}

@ajax_request
@login_required
def addonservices(request):
    #account_id = request.POST.get('account_id')
    #print "subaccount", account_id
    items = AddonService.objects.all()
    #print accounts
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        #print instance_dict(acc).keys()
        res.append(instance_dict(item,normal_fields=True))
    print instance_dict(item,normal_fields=True).keys()
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')

    return {"records": res}

@ajax_request
@login_required
def accounthardware(request):
    account_id = request.POST.get('account_id')
    #print "subaccount", account_id
    if account_id:
        items = AccountHardware.objects.filter(account__id=account_id)
    else:
        return {"records": []}

    res=[]
    for item in items:
        #print instance_dict(acc).keys()
        res.append(instance_dict(item,normal_fields=True))
    #print instance_dict(item,normal_fields=True).keys()

    return {"records": res}

@ajax_request
@login_required
def accounttariffs(request):
    account_id = request.POST.get('account_id')
    
    items = AccountTarif.objects.filter(account__id=account_id)
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
    items = Nas.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append({"nas":item.id, "name":item.name})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

@ajax_request
@login_required
def tariffs(request):
    from billservice.models import Tariff
    items = Tariff.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append({"tarif":item.id, "name":item.name})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

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
def tpchange(request):
    id = request.POST.get('id')

    item = AccountTarif.objects.get(id=id)
    #from django.core import serializers
    #from django.http import HttpResponse

    res=instance_dict(item)
    
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
def city(request):
    items = City.objects.all()
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
def street(request):
    city_id = request.GET.get('city_id')
    if city_id:
        items = Street.objects.filter(city__id=city_id)
    else:
        items = Street.objects.all()
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
    contract = request.POST.get('contract','')
    newcontract=False
    acc = None
    if id:
        acc = Account.objects.get(id=id)
        
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
            if contr:
                item.contract = contract
                item.save()
                contr.save()
            res={"success": True, 'account_id':item.id}
        except Exception, e:
            print e
            res={"success": False, "errors": a._errors}
    else:
        
        res={"success": False, "errors": a._errors, 'msg':u"Поля с ошибками:<br />"+unicode('<br />'.join([u'%s:%s' %(x,a._errors.get(x)) for x in a._errors]))}
    return res


@ajax_request
@login_required
def subaccount_save(request):
    
    #from django.core import serializers
    #from django.http import HttpResponse
    #print request
    id=request.POST.get('id')
    ipv4_vpn_pool = request.POST.get('ipv4_vpn_pool')
    ipv4_ipn_pool = request.POST.get('ipv4_ipn_pool')
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
       
        if cc and cc.vpn_ipinuse:
            print 2
            #vpn_pool = IPPool.objects.get(id=ipv4_vpn_pool)
            
            if  subacc.vpn_ip_address not in ['0.0.0.0','',None]:
                if vpn_pool:
                    if not IPy.IP(vpn_pool.start_ip).int()<=IPy.IP(subacc.vpn_ip_address).int()<=IPy.IP(vpn_pool.end_ip).int():
                        return {"success": False, 'msg':u'Выбранный VPN IP адрес не принадлежит указанному VPN пулу'}
                    
                
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
                return {"success": False, 'msg':u'Выбранный VPN IP адрес не принадлежит указанному VPN пулу'}
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
                        return {"success": False, 'msg':u'Выбранный IPN IP адрес не принадлежит указанному IPN пулу'}
                    
                
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
                return {"success": False, 'msg':u'Выбранный IPN IP адрес не принадлежит указанному IPN пулу'}
            print 7
            ip=IPInUse(pool=ipn_pool, ip=subacc.ipn_ip_address, datetime=datetime.datetime.now())
            ip.save()
            subacc.ipn_ipinuse = ip 
       
        try:
            subacc.save()
            print 99
            res={"success": True}
        except Exception, e:
            print e
            res={"success": False, "errors": a._errors}
    else:
        res={"success": False, "errors": a._errors}
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
        return {'records':[]}
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
            res.append({'ipaddress':str(IPy.IP(x, ipversion = ipversion))})
            i+=1
        x+=1
    return {'totalCount':str(len(res)),'records':res[start:start+limit]}

@ajax_request
@login_required
def house(request):
    street_id = request.GET.get('street_id')
    if street_id:
        items = House.objects.filter(street__id=street_id)
    else:
        items = House.objects.all()
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
def accountaddonservices(request):
    from billservice.models import AccountAddonService
    account_id = request.POST.get('account_id')
    items = AccountAddonService.objects.filter(account__id=account_id)
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item,normal_fields=True))
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

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
    form = AccountAddonForm(request.POST)
    if form.is_valid():
        print form.cleaned_data
        if id:
            #Если id найден - обновляем поля
            item = AccountAddonService.objects.filter(id=id).update(**form.cleaned_data)
            #print dir(item)
            res={"success": True}
        else:
            #Если id _не_ найден - создаём модельформ и сохраняем её.
            form = AccountAddonServiceModelForm(request.POST)
            if form.is_valid():
                form.save()
                res={"success": True}
            else:
                res={"success": False, "errors": form._errors}
    else:
        res={"success": False, "errors": form._errors}
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

def instance_dict(instance, key_format=None, normal_fields=False):
    """
    Returns a dictionary containing field names and values for the given
    instance
    """
    from django.db.models.fields import DateField,DecimalField
    from django.db.models.fields.related import ForeignKey
    if key_format:
        assert '%s' in key_format, 'key_format must contain a %s'
    key = lambda key: key_format and key_format % key or key

    pk = instance._get_pk_val()
    d = {}
    for field in instance._meta.fields:
        attr = field.name
        #print attr
        try:
            value = getattr(instance, attr)
        except:
            value=None
        if value is not None:
            if isinstance(field, ForeignKey):
                try:
                    value = value._get_pk_val() if normal_fields==False else unicode(value)
                except Exception, e:
                    print e
                    
            elif isinstance(field, DateField):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(field, DecimalField):
                value = float(value)
                               
        d[key(attr)] = value
    for field in instance._meta.many_to_many:
        if pk:
            d[key(field.name)] = [
                obj._get_pk_val()
                for obj in getattr(instance, field.attname).all()]
        else:
            d[key(field.name)] = []
    return d

@login_required
@ajax_request
def account(request):
    id=request.POST.get('id')
    acc = Account.objects.get(id=id)
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

@ajax_request
@login_required
def transactiontypes(request):
    items = TransactionType.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append({"id":item.id, "name":item.name})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

@render_to('jsongrid.html')
@login_required
def grid(request):
 
    return {}

@ajax_request
@login_required
def actions_set(request):
    subaccount = request.POST.get('subaccounts_id')
    action = request.POST.get('action')
    if subaccount:          
        cur = connection.cursor()
       
        print 'subaccount',subaccount
        #TODO: придумать что тут сделать с realdictcursor_ом
        #cur.execute("SELECT * FROM billservice_subaccount WHERE id=%s",(subaccount,))
        
        #row = cur.fetchone()
        #if not row: return {'status':False}
        sa=SubAccount.objects.get(id=subaccount)
        if action=='ipn_disable':
            sa.ipn_sleep=False
            sa.save()
            return {'success':True}
        if action=='ipn_enable':
            sa.ipn_sleep=True
            sa.save()
            return {'success':True}

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
            return {'success':False,'msg':u'Не указан или не найден указанный сервер доступа'}
            
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

        
        return {'success':sended}
    return {'success':False}
            

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
            account = self.connection.sql("SELECT id FROM billservice_account LIMIT 1" )[0].id
            #organization = self.connection.sql("SELECT * FROM billservice_organization LIMIT 1" )[0]
            #bank = self.connection.sql("SELECT * FROM billservice_bankdata LIMIT 1" )[0]
            operator = self.connection.get("SELECT * FROM billservice_operator LIMIT 1")
            try:
                data=templ.render_unicode(account=account, operator=operator,  connection=self.connection)
            except Exception, e:
                data=u"Error %s" % str(e)
    

                       

        res = {'success': True, 'body':data.encode("utf-8", 'replace')}
    else:
        res={"success": False, "errors": form._errors}
    #print instance_dict(item).keys()
    return res
