#-*-coding:utf-8 -*-

from lib.decorators import render_to, ajax_request
from billservice.models import Account, SubAccount, TransactionType, City, Street, House, SystemUser
from nas.models import Nas
from django.contrib.auth.decorators import login_required

from billservice.forms import AccountForm, SubAccountForm

@ajax_request
@login_required
def jsonaccounts(request):
    items = Account.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item))
    print instance_dict(item).keys()
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

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
        res.append(instance_dict(acc))
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
    res.append({"id":0, "name":u'-- Не указан --'})
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
    for item in items:
        res.append({"id":item.id, "name":item.name})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

@ajax_request
@login_required
def accountstatus(request):
    items = ['1','Активен'], \
            ['2','Не активен, списывать периодические услуги'],\
            ['3','Не активен, не списывать периодические услуги'],\
            ['4','Пользовательская блокировка'],
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
    acc = Account.objects.get(id=request.POST.get('id'))
    a=AccountForm(request.POST, instance=acc)
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
            print 'acc.id', acc.id
            a.save()
            res={"success": True}
        except Exception, e:
            print e
            res={"success": False, "errors": a._errors}
    else:
        res={"success": False, "errors": a._errors}
    return res


@ajax_request
@login_required
def subaccount_save(request):
    
    #from django.core import serializers
    #from django.http import HttpResponse
    print request
    cc = SubAccount.objects.get(id=request.POST.get('id'))
    a=SubAccountForm(request.POST,instance=cc)
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
    for item in items:
        res.append({"id":item.id, "name":item.name})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

@ajax_request
@login_required
def accountaddonservices(request):
    from billservice.models import AccountAddonService
    subaccount_id = request.POST.get('subaccount_id')
    items = AccountAddonService.objects.filter(subaccount__id=subaccount_id)
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append(instance_dict(item))
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}


@ajax_request
@login_required
def systemuser(request):
    items = SystemUser.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for item in items:
        res.append({"id":item.id, "name":"%s %s" % (item.username, item.fullname)})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"records": res}

def instance_dict(instance, key_format=None):
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
                value = value._get_pk_val()
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
    