#-*-coding:utf-8-*-

from extdirect.django import ExtDirectStore, ExtRemotingProvider, ExtPollingProvider
from extdirect.django.decorators import remoting

from billservice.models import Account, SettlementPeriod
from nas.models import Nas
from radius.models import ActiveSession

# Create ExtJS direct backend
remote_provider = ExtRemotingProvider(namespace='EBS', url='/ext/remoting/router/')
polling_provider = ExtPollingProvider(url='/ext/polling/router/', event='some-event')

#TODO: упростить
# Заменить на row-level access
USERGROUP_MODEL_FIELDS = {
    'Account':{
            1: ['username', 'fullname', 'email', 'ballance', 'created'],
            2: ['username', 'fullname', 'created']
            },
    'Nas':{
            1: ['name', 'ipaddress', 'identify', 'type', 'secret'],
            2: ['name', 'ipaddress', 'identify']
            },
    'ActiveSession':{
            1: ['sessionid', 'account', 'framed_protocol'],
            2: ['sessionid', 'account', 'framed_protocol']
            },
    }


def getModelFields(model):
    #request.user.group...
    group_id = 1
    return USERGROUP_MODEL_FIELDS[model._meta.object_name][group_id]


def getModelFieldsToExclude(model, fields):
    """
    Return only accesible by user fields

    TODO:   1. Заменить на row-level access.
            2. Создать вторую Fn() для для получения списка доступных полей из джанги +
            3. Добавить кеширование
    """
    return [f.attname  for f in  Account._meta.fields if f.attname not in fields]


@remoting(remote_provider, action='accounts', len=1)
def getAccountsList(request):
    if True: # TODO: check perms
        #fields = getModelFields(Account)
        #exclude_fields = getModelFieldsToExclude(Account, fields)
        try:
            data = request.extdirect_post_data[0]
        except:
            data = {'start':1,'limit':10}
        print data
        accounts = ExtDirectStore(Account)
        return accounts.query(**data)


@remoting(remote_provider, action='nas', len=1)
def getNasList(request):
    if True: # TODO: check perms
        #fields = getModelFields(Nas)
        #exclude_fields = getModelFieldsToExclude(Nas, fields)
        try:
            data = request.extdirect_post_data[0]
        except:
            data = {'start':1,'limit':10}
        nasses = ExtDirectStore(Nas)
        return nasses.query(**data)


@remoting(remote_provider, action='settlement_period', len=1)
def getSettlementPeriod(request):
    print request
    if True: # TODO: check perms
        #fields = getModelFields(Nas)
        #exclude_fields = getModelFieldsToExclude(Nas, fields)
        #return {'success':True, 'data':{'name':'123', 'time_start':'01-01-2010 00:00:00', 'autostart':True, 'length':0, 'length_in':'MONTH'}}
        return {'success':True, 'data':{'id':1, 'name':'123', 'time_start':'01-01-2010 00:00:00', 'autostart':True, 'length':0, 'length_in_p':'MONTH'}}
    
    
@remoting(remote_provider, action='radius', len=1)
def getSessionList(request):
    if True: # TODO: check perms
        #fields = getModelFields(ActiveSession)
        #exclude_fields = getModelFieldsToExclude(Nas, fields)
        print request
        try:
            data = request.extdirect_post_data[0]
        except:
            data = {'start':1,'limit':10}
        sessions = ExtDirectStore(ActiveSession)
        return sessions.query(**data)

@remoting(remote_provider, action='settlement_period', len=1)
def getSettlementPeriods(request):
    if True: # TODO: check perms
        #fields = getModelFields(ActiveSession)
        #exclude_fields = getModelFieldsToExclude(Nas, fields)
        #print request
        try:
            data = request.extdirect_post_data[0]
        except:
            data = {'start':1,'limit':10}
        sp = ExtDirectStore(SettlementPeriod)
        return sp.query(**data)
   
@remoting(remote_provider, action='settlement_period', len=1)
def sp_types(request):
    if True: # TODO: check perms
        #fields = getModelFields(ActiveSession)
        #exclude_fields = getModelFieldsToExclude(Nas, fields)
        print request
        return {'success':True, 'data':[{u'name':'Сутки', 'value':'DAY'},{u'name':'Неделя', 'value':'WEEK'}, {u'name':'Месяц', 'value':'MONTH'}, {'name':u'Год', 'value':'YEAR'}]}
     
