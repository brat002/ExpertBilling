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

from lib.decorators import render_to



@render_to('registration/login.html')
def login(request):
    error_message = True
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = Account.objects.get(username=form.cleaned_data['username'])
                if not user.allow_webcab:
                    form = LoginForm()
                    error_message = u'У данного пользователя нет прав пользоваться WEB Кабинетом!!!'
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
                    cursor.execute("""SELECT name, allow_express_pay FROM billservice_tariff WHERE id=get_tarif(%s)""" % (user.id))
                    tarif = cursor.fetchone()
                    tarif = tarif[1]
                    if tarif:
                        request.session['express_pay']=True
                    request.session.modified = True
                    return HttpResponseRedirect('/index/')
                else:
                    form = LoginForm(initial={'username': form.cleaned_data['username']})
                    error_message = u'Проверьте пароль'
                    return {
                            'error_message':error_message,
                            'form':form,
                            }
            except:
                form = LoginForm(initial={'username': form.cleaned_data['username']})
                error_message = u'Пользователь не найден в базе'
                return {
                        'error_message':error_message,
                        'form':form,
                        }
        else:
            form = LoginForm(initial={'username': request.POST.get('username', None)})
            error_message = u'Не введен логин или пароль'
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
    cursor.execute("""SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)""" % (user.id)) 
    tarif = cursor.fetchone()
    tarif = tarif[0]
    cache_user = cache.get(user.id)
    if int(cache_user['count']) > settings.ACTIVATION_COUNT and bool(cache_user['blocked']):
        time = datetime.datetime.now() - cache_user['last_date']
        if time.seconds > settings.BLOCKED_TIME:
            cache.delete(user.id)
            cache.set(user.id, {'count':0,'last_date':cache_user['last_date'],'blocked':False,}, 86400*365)
    date = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    tarifs = AccountTarif.objects.filter(account=user, datetime__lt=date)
    ballance = u'%.2f' % user.ballance 
    #find prepare trafick
       
    return {
            'account':user,
            'ballance':ballance,
            'tarif':tarif,
            'tarifs':tarifs,
            'status': bool(cache_user['blocked']),
            }
    
@render_to('accounts/netflowstream_info.html')
def netflowstream_info(request):
    if not request.session.has_key('user'):
        return is_login_user(request)
    from lib.paginator import SimplePaginator
    paginator = SimplePaginator(request, NetFlowStream.objects.filter(account=request.session['user']), 500, 'page')
    return {
            'net_flow_streams':paginator.get_page_items(),
            'paginator': paginator,
            }
    

@render_to('accounts/transaction.html')
def transaction(request):
    if not request.session.has_key('user'):
        return is_login_user(request)
    from lib.paginator import SimplePaginator
    paginator = SimplePaginator(request, Transaction.objects.filter(account=request.session['user']), 100, 'page')
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
    paginator = SimplePaginator(request, ActiveSession.objects.filter(account=user), 50, 'page')
    return {
            'sessions':paginator.get_page_items(),
            'paginator': paginator,
            'user': user,
            }

@render_to('accounts/change_password.html')
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
                    return HttpResponseRedirect('/index/')
                else:
                    return {
                            'error_message': u'Проверьте пароль',
                            'form':form,
                            }
            except:
                form = PasswordForm()
                return {
                        'error_message': u'Пользователь не существует',
                        'form':form,
                        }
    else:
        form = PasswordForm()
        return {
                'form': form,
                }
        
@render_to('accounts/card_acvation.html')
def card_acvation(request):
    if not request.session.has_key('user'):
        return HttpResponseRedirect('/')
    if not request.session.has_key('express_pay'):
        return HttpResponseRedirect('/index/')
    user = request.session['user']
    if not user.allow_expresscards:
        return {
                'error_message': u"Вам не доступна услуга активации карт экспресс оплаты!",
                }
    if not cache.get(user.id):
        return HttpResponseRedirect('/')
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
            return HttpResponseRedirect('/index/')
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
                user.ballance = user.ballance-summ
                user.save()
                request.session['user'] = user
                request.session.modified = True
                transaction = Transaction(tarif=None, bill='', description = "", account=user, type=type, approved=True, summ=summ, created=datetime.datetime.now())
                transaction.save()
                cache.delete(user.id)
                cache.add(user.id, {'count':0,'last_date':cache_user['last_date'],'blocked':False,})
                return HttpResponseRedirect('/index/')
            except: 
                if int(cache_user['count']) <= settings.ACTIVATION_COUNT:
                    cache.delete(user.id)
                    cache.set(user.id, {'count':count+1,'last_date':cache_user['date'],'blocked':False,}, 86400*365)
                form = CardForm(request.POST)
                return {
                        'error_message':u"Ваша карточка уже активирована или она не может быть активирована!",
                        'form': form,
                        }
        else:
            count = int(cache_user['count'])
            if int(cache_user['count']) < settings.ACTIVATION_COUNT+1:
                cache.delete(user.id)
                cache.add(user.id, {'count':count+1,'last_date':cache_user['last_date'],'blocked':False,})
            return {
                    'error_message': u"Проверьте заполнение формы",
                    'form': form,
                    }            
    else:
        form = CardForm()
        return {
                'form':form,
                }

@render_to('accounts/account_prepays_traffic.html')
def account_prepays_traffic(request):
    if not request.session.has_key('user'):
        return HttpResponseRedirect('/')
    user = request.session['user']
    try:
        from billservice.models import AccountPrepaysTrafic, PrepaidTraffic
        account_tarif = AccountTarif.objects.get(account=user, datetime__lt=datetime.datetime.now())[:1]
        account_prepays_trafic = AccountPrepaysTrafic.objects.filter(account_tarif=account_tarif)
        prepaidtraffic = PrepaidTraffic.objects.filter(id__in=[ i.prepaid_traffic.id for i in account_prepays_trafic])
    except:
        prepaidtraffic = None
        account_tarif = None  
    return {
            'prepaidtraffic':prepaidtraffic,
            'account_tarif':account_tarif,
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
        #f = open('tmp', 'wb')
        #f.write(child.password.toHex())
        connection._setNewConnectionValidator(antiMungeValidator())
        print connection._setIdentification("%s:%s" % (str(settings.RPC_USER), str(password)))
        connection.test()

        #return connection

    except Exception, e:
        #print "login connection error"
        if isinstance(e, Pyro.errors.ConnectionDeniedError):
            error_message = u"Отказано в авторизации."
        else:
            error_message  = u"Невозможно подключиться к серверу."
    # create image
    date_end = datetime.datetime.now()
    day = datetime.timedelta(seconds=86400)
    date_start = date_end-day
    args = ('nfs_user_traf', date_start, date_end)
    kwargs = {}
    kwargs['return'] ={}
    kwargs['options'] ={}
    kwargs['users'] = [user.id]
    kwargs['autoticks'] = True
    kwargs['antialias'] = True
    imgs = connection.makeChart(*args, **kwargs)
    img = imgs[0] 
    from django.http import HttpResponse
    response = HttpResponse(img, content_type='image/png')

    return response
        

@render_to('accounts/traffic_limit.html')        
def traffic_limit(request):
    if not request.session.has_key('user'):
        return HttpResponseRedirect('/')
    user = request.session['user']
    cursor = connection.cursor()
    cursor.execute("""SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)""" % (user.id)) 
    tarif = cursor.fetchone()
    tarif = tarif[0]
    try:
        tarif = Tariff.objects.get(name=tarif)
        traffic = TrafficLimit.objects.filter(tarif=tarif) 
    except:
        traffic = None
    return {
            'trafficlimit':traffic,
            'user':user,
            } 
            