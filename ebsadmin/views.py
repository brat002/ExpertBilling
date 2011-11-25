#-*-coding:utf-8 -*-

from lib.decorators import render_to, ajax_request
from billservice.models import Account, SubAccount, TransactionType, City, Street, House, SystemUser,AccountTarif, AddonService
from nas.models import Nas
from django.contrib.auth.decorators import login_required

from billservice.forms import AccountForm, SubAccountForm, SearchAccountForm, AccountTariffForm, AccountAddonForm,AccountAddonServiceModelForm

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
    from billservice.models import IPPool
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
    if id:
        acc = Account.objects.get(id=id)
        a=AccountForm(request.POST, instance=acc)
    else:
        a=AccountForm(request.POST)
    p=request.POST
    res=[]
    print "a.is_valid()",a.is_valid()
    print a._errors
    #print a.clean()
    
    #acc.username=p.get("username")
    #acc.password=p.get("password")
    #acc.fullllname=p.get("fullname")
    if a.is_valid():
        try:
            item = a.save(commit=False)
            item.save()
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
    print request
    id=request.POST.get('id')
    if id:
        cc = SubAccount.objects.get(id=id)
        a=SubAccountForm(request.POST,instance=cc)
    else:
        a=SubAccountForm(request.POST)
    #a.account=aa.account_id
    p=request.POST
    res=[]
    print "a.is_valid()",a.is_valid()
    print a._errors
    #print a.clean()
    
    #acc.username=p.get("username")
    #acc.password=p.get("password")
    #acc.fullllname=p.get("fullname")
    try:
        #print 'subacc.id', acc.id
        #acc.save()
        a.save()
        res={"success": True}
    except Exception, e:
        print e
        res={"success": False, "errors": a._errors}
    return res


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
    