 #-*- coding=UTF-8 -*-
import datetime
import Pyro.core
import Pyro.protocol
import Pyro.constants
import Pyro.errors

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django import template

from django.conf import settings
from billservice.models import Account, AccountTarif, NetFlowStream, Transaction, Card, TransactionType, TrafficLimit, Tariff 
from billservice.forms import LoginForm, PasswordForm, CardForm
from radius.models import ActiveSession  
from billservice.utility import is_login_user
from nas.models import TrafficClass

from lib.decorators import render_to, ajax_request



@render_to('registration/login.html')
def login(request):
    error_message = True
    if request.method == 'POST':
        pin=request.POST.get('pin','')
        user = request.POST.get('user','')
        if pin!='':
            if user!='':
                message=None
                try:
                    connection_server = Pyro.core.getProxyForURI("PYROLOC://%s:7766/rpc" % unicode(settings.RPC_ADDRESS))
                    import hashlib
                    md1 = hashlib.md5(settings.RPC_PASSWORD)
                    md1.hexdigest()
                   
                    password = str(md1.hexdigest())
                    connection_server._setNewConnectionValidator(antiMungeValidator())
                    #print connection_server._setIdentification("%s:%s" % (str(settings.RPC_USER), str(password)))
                    connection_server.test()
                except Exception, e:
                    if isinstance(e, Pyro.errors.ConnectionDeniedError):
                        error_message = u"Отказано в авторизации."
                    else:
                        error_message  = u"Невозможно подключиться к серверу."
                message_type = connection_server.activate_card(user, pin)
                if message_type == 1:
                    message = u'Карточка успешно активирована. <br>  Выш логин %s <br> ваш пароль %s' % (user, pin)
                if message_type == 2:
                    message = u'Не верно введен логин или пароль'
                if message_type == 3:
                    message = u'Карточка уже была активирована' 
            form = LoginForm()
            return {
                    'form':form,
                    'message':message,
                    }
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = Account.objects.get(username=form.cleaned_data['username'])
                if not user.allow_webcab:
                    form = LoginForm()
                    error_message = u'У вас нет прав на вход в веб-кабинет'
                    return {
                            'error_message':error_message,
                            'form':form,
                            }
                if user.password == form.cleaned_data['password']:
                    request.session['user'] = user
                    if not cache.get(user.id):
                        cache.set(user.id, {'count':0,'last_date':datetime.datetime.now(),'blocked':False,}, 86400*365)
                    else:
                        cache_user = cache.get(user.id)
                        if cache_user['blocked']:
                            cache.set(user.id, {'count':cache_user['count'],'last_date':cache_user['last_date'],'blocked':cache_user['blocked'],}, 86400*365)
                        else:
                            cache.set(user.id, {'count':cache_user['count'],'last_date':datetime.datetime.now(),'blocked':cache_user['blocked'],}, 86400*365)    
                    cursor = connection.cursor()
                    cursor.execute("""SELECT allow_express_pay FROM billservice_tariff WHERE id=get_tarif(%s)""" % (user.id))
                    allow_express_pay = cursor.fetchone()[0]
                    if allow_express_pay:
                        request.session['express_pay']=True
                    request.session.modified = True
                    return HttpResponseRedirect('/')
                else:
                    form = LoginForm(initial={'username': form.cleaned_data['username']})
                    error_message = u'Проверьте введенные данные'
                    return {
                            'error_message':error_message,
                            'form':form,
                            }
            except:
                form = LoginForm(initial={'username': form.cleaned_data['username']})
                error_message = u'Проверьте введенные данные'
                return {
                        'error_message':error_message,
                        'form':form,
                        }
        else:
            form = LoginForm(initial={'username': request.POST.get('username', None)})
            error_message = u'Проверьте введенные данные'
            return {
                    'error_message':error_message,
                    'form':form,
                    }
    else:
         form = LoginForm()
         return {
                 'form':form,
                }  
               
def login_out(request):
    if request.session.has_key('user'):
        del request.session['user']
    return is_login_user(request)


@render_to('accounts/index.html')
def index(request):
    if not request.session.has_key('user'):
        return is_login_user(request)
    user = request.session['user']
    if not cache.get(user.id):
        del request.session['user']
        return is_login_user(request)
    cursor = connection.cursor()
    cursor.execute("""SELECT id, name FROM billservice_tariff WHERE id=get_tarif(%s)""" % (user.id)) 
    tariff_id, tariff_name = cursor.fetchone()
    cache_user = cache.get(user.id)
    if int(cache_user['count']) > settings.ACTIVATION_COUNT and bool(cache_user['blocked']):
        time = datetime.datetime.now() - cache_user['last_date']
        if time.seconds > settings.BLOCKED_TIME:
            cache.delete(user.id)
            cache.set(user.id, {'count':0,'last_date':cache_user['last_date'],'blocked':False,}, 86400*365)
    date = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    tariffs = AccountTarif.objects.filter(account=user, datetime__lt=date)
    if len(tariffs) == 0 or len(tariffs) == 1:
        tariff_flag = False
    else:
        tariff_flag = True 
    ballance = u'%.2f' % user.ballance 
    #find prepare trafick
    
    #cursor = connection.cursor()
    cursor.execute("""SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)""" % (user.id)) 
    try:
        tariff = cursor.fetchone()[0]
        traffic = TrafficLimit.objects.filter(tarif=tariff_id) 
    except:
        traffic = None
    return {
            #'account':user,
            'ballance':ballance,
            'tariff':tariff_name,
            'tariffs':tariffs,
            'status': bool(cache_user['blocked']),
            'tariff_flag':tariff_flag,
            'trafficlimit':traffic,
            'form':  CardForm(),
            }
    
@render_to('accounts/netflowstream_info.html')
def netflowstream_info(request):
    if not request.session.has_key('user'):
        return is_login_user(request)
    from lib.paginator import SimplePaginator
    paginator = SimplePaginator(request, NetFlowStream.objects.filter(account=request.session['user']).order_by('-date_start'), 500, 'page')
    return {
            'net_flow_streams':paginator.get_page_items(),
            'paginator': paginator,
            }
    

@render_to('accounts/transaction.html')
def transaction(request):
    if not request.session.has_key('user'):
        return is_login_user(request)
    from lib.paginator import SimplePaginator
    paginator = SimplePaginator(request, Transaction.objects.filter(account=request.session['user']).order_by('-created'), 100, 'page')
    return {
            'transactions':paginator.get_page_items(),
            'paginator': paginator,
            }
    
@render_to('accounts/vpn_session.html')
def vpn_session(request):
    if not request.session.has_key('user'):
        return is_login_user(request)
    from lib.paginator import SimplePaginator
    user = request.session['user']
    paginator = SimplePaginator(request, ActiveSession.objects.filter(account=user).order_by('-date_start'), 50, 'page')
    return {
            'sessions':paginator.get_page_items(),
            'paginator': paginator,
            'user': user,
            }
    
@render_to('accounts/change_password.html')
def card_form(request):
    if not request.session.has_key('user'):
        return HttpResponseRedirect('/')
    return {
            'form':PasswordForm()
            }

@ajax_request
def change_password(request):
    if not request.session.has_key('user'):
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            try:
                user = request.session['user']
                user = Account.objects.get(username=user.username)
                if user.password == form.cleaned_data['old_password'] and form.cleaned_data['new_password']==form.cleaned_data['repeat_password']:
                    user.password = form.cleaned_data['new_password']
                    user.save()
                    return {
                            'error_message': u'Пароль успешно изменен',
                            'ok':'ok',
                            }
                else:
                    return {
                            'error_message': u'Проверьте пароль',
                            }
            except:
                return {
                        'error_message': u'Проверьте пароль',
                        }
        else:
            return {
                    'error_message': u'Проверьте введенные данные',
                    }
    else:
        return {
                'error_message': u'Не предвиденная ошибка',
                }
        
@ajax_request
def card_acvation(request):
    if not request.session.has_key('user'):
        return {
                'redirect':'/login/',
               }
                #HttpResponseRedirect('/')
    if not request.session.has_key('express_pay'):
        return {
                'error_message': u'Вам не доступна услуга активации карт экспресс оплаты!',
               }
    user = request.session['user']
    if not user.allow_expresscards:
        return {
                'error_message': u'Вам не доступна услуга активации карт экспресс оплаты!',
                }
    if not cache.get(user.id):
        return {
                'redirect':'/login/',
               }
        #HttpResponseRedirect('/')
    cache_user = cache.get(user.id)
    if int(cache_user['count']) > settings.ACTIVATION_COUNT and not bool(cache_user['blocked']):
        cache.delete(user.id)
        cache.set(user.id, {'count':int(cache_user['count']),'last_date':cache_user['last_date'],'blocked':True,}, 86400*365)
    if int(cache_user['count']) > settings.ACTIVATION_COUNT and bool(cache_user['blocked']):
        time = datetime.datetime.now() - cache_user['last_date']
        if time.seconds > settings.BLOCKED_TIME:
            cache.delete(user.id)
            cache.set(user.id, {'count':0,'last_date':cache_user['last_date'],'blocked':False,}, 86400*365)
        else:
            return {
                    'redirect':'/',
                   }
            #HttpResponseRedirect('/index/')
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            try:
                card = Card.objects.get(series=form.cleaned_data['series'], pin=form.cleaned_data['pin'], sold__isnull=False, start_date__lte=datetime.datetime.now(), end_date__gte=datetime.datetime.now(), activated__isnull=True)
                
                card.activated=datetime.datetime.now()
                card.activated_by = user
                card.save()
                summ = -card.nominal
                type = TransactionType.objects.get(internal_name=u'ACTIVATION_CARD')
                #user.ballance = user.ballance-summ
                #user.save()
                request.session['user'] = user
                request.session.modified = True
                transaction = Transaction(tarif=None, bill='', description = "", account=user, type=type, approved=True, summ=summ, created=datetime.datetime.now())
                transaction.save()
                cache.delete(user.id)
                cache.add(user.id, {'count':0,'last_date':cache_user['last_date'],'blocked':False,})
                #return HttpResponseRedirect('/index/')
            except: 
                if int(cache_user['count']) <= settings.ACTIVATION_COUNT:
                    cache.delete(user.id)
                    count = int(int(cache_user['count']))
                    cache.set(user.id, {'count':count+1,'last_date':cache_user['last_date'],'blocked':False,}, 86400*365)
                form = CardForm(request.POST)
                return {
                        'error_message':u"Ваша карточка не может быть активирована!",
                        #'form': form,
                        }
        else:
            count = int(cache_user['count'])
            if int(cache_user['count']) < settings.ACTIVATION_COUNT+1:
                cache.delete(user.id)
                cache.add(user.id, {'count':count+1,'last_date':cache_user['last_date'],'blocked':False,})
            return {
                    'error_message': u"Проверьте заполнение формы",
                    #'form': form,
                    }            
    else:
        #form = CardForm()
        return {
                'error_message': u"Ошибка активации карточки",
                #'form':form,
                }

@render_to('accounts/account_prepays_traffic.html')
def account_prepays_traffic(request):
    if not request.session.has_key('user'):
        return HttpResponseRedirect('/')
    user = request.session['user']
    try:
        from billservice.models import AccountPrepaysTrafic, PrepaidTraffic
        account_tariff = AccountTarif.objects.get(account=user, datetime__lt=datetime.datetime.now())[:1]
        account_prepays_trafic = AccountPrepaysTrafic.objects.filter(account_tarif=account_tariff)
        prepaidtraffic = PrepaidTraffic.objects.filter(id__in=[ i.prepaid_traffic.id for i in account_prepays_trafic])
    except:
        prepaidtraffic = None
        account_tariff = None  
    return {
            'prepaidtraffic':prepaidtraffic,
            'account_tariff':account_tariff,
            }
    

class antiMungeValidator(Pyro.protocol.DefaultConnValidator):
    def __init__(self):
        Pyro.protocol.DefaultConnValidator.__init__(self)
    def createAuthToken(self, authid, challenge, peeraddr, URI, daemon):
        return authid
    def mungeIdent(self, ident):
        return ident
    
    
def client(request):
    if not request.session.has_key('user'):
        return HttpResponseRedirect('/')
    user = request.session['user']
    # CONNECTION TO RCP SERVER
    try:
        connection = Pyro.core.getProxyForURI("PYROLOC://%s:7766/rpc" % unicode(settings.RPC_ADDRESS))
        import hashlib
        md1 = hashlib.md5(settings.RPC_PASSWORD)
        md1.hexdigest()
       
        password = str(md1.hexdigest())
        connection._setNewConnectionValidator(antiMungeValidator())
        #print connection._setIdentification("%s:%s" % (str(settings.RPC_USER), str(password)))
        connection.test()
    except Exception, e:
        if isinstance(e, Pyro.errors.ConnectionDeniedError):
            error_message = u"Отказано в авторизации."
        else:
            error_message  = u"Невозможно подключиться к серверу."
    # create image
    from django.http import HttpResponse
    t1 = datetime.timedelta(days = 30)
    a1 = datetime.datetime.now() - t1
    a2 = datetime.datetime.now()
    cargs = ('gstat_multi', a1, a2)
    #for traffic_class in TrafficClass.objects.all().order_by('weight'):
    #    min_weight = traffic_class
    ckwargs = {'return':{}, 'options':{'autoticks':False, 'antialias':True}, 'dcname': 'nfs_web', 'speed':True, 'by_col':'classes', 'users':[user.id], 'classes':[i.id for i in TrafficClass.objects.all()]}
    imgs = connection.makeChart(*cargs, **ckwargs)
    response = HttpResponse(imgs, content_type='image/png')
    return response
            

@render_to('accounts/traffic_limit.html')        
def traffic_limit(request):
    if not request.session.has_key('user'):
        return HttpResponseRedirect('/')
    user = request.session['user']
    cursor = connection.cursor()
    cursor.execute("""SELECT id FROM billservice_tariff WHERE id=get_tarif(%s)""" % (user.id)) 
    
    try:
        tariff = cursor.fetchone()[0]
        #tariff = Tariff.objects.get(id=tariff)
        traffic = TrafficLimit.objects.filter(tarif=tariff) 
    except:
        traffic = None
    return {
            'trafficlimit':traffic,
            'user':user,
            } 
            
            
@render_to('accounts/statistics.html')
def statistics(request):
    if not request.session.has_key('user'):
        return HttpResponseRedirect('/')
    user = request.session['user']
    net_flow_streams = NetFlowStream.objects.filter(account=request.session['user']).order_by('-date_start')[:8]
    transaction = Transaction.objects.filter(account=request.session['user']).order_by('-created')[:8]
    active_session = ActiveSession.objects.filter(account=user).order_by('-date_start')[:8]  
    return {
            'net_flow_stream':net_flow_streams,
            'transactions':transaction,
            'active_session':active_session,
            }





