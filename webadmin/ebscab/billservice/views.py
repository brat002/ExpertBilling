 #-*- coding=UTF-8 -*-

#NEWRPC = True
#if NEWRPC:

import os, sys
import logging




#print os.path.abspath('../../../')
sys.path.append(os.path.abspath('../../'))

#from rpc2 import rpc_protocol, client_networking

import datetime

CUR_PATH = os.getcwd()
ROLE = 2

from django.conf import settings


from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db import connection
#from django.core.cache import cache
from django import template
from django.contrib.auth.decorators import login_required

from lib.http import JsonResponse
from billservice.models import Account, AccountTarif, Transaction, Card, TransactionType, TrafficLimit, Tariff, TPChangeRule, AddonService, AddonServiceTarif, AccountAddonService, PeriodicalServiceHistory, AddonServiceTransaction, OneTimeServiceHistory, TrafficTransaction, AccountPrepaysTrafic, PrepaidTraffic, SubAccount
from billservice.models import SystemUser, AccountPrepaysRadiusTrafic, AccountPrepaysTime, SuspendedPeriod, GroupStat

from billservice.forms import LoginForm, PasswordForm, EmailForm, SimplePasswordForm, ActivationCardForm, ChangeTariffForm, PromiseForm, StatististicForm
from billservice import authenticate, log_in, log_out
from radius.models import ActiveSession
from billservice.utility import is_login_user, settlement_period_info
from nas.models import TrafficClass
from lib.decorators import render_to, ajax_request#, login_required
from paymentgateways.qiwi.models import Invoice as QiwiInvoice
from paymentgateways.qiwi.forms import QiwiPaymentRequestForm
import math

#rpc_protocol.install_logger(logger)
#client_networking.install_logger(logger)
from ebsadmin.cardlib import add_addonservice, del_addonservice, activate_pay_card
from ebsadmin.cardlib import activate_card
from django.utils.translation import ugettext_lazy as _

def addon_queryset(request, id_begin, field='datetime', field_to=None):
    if field_to == None:
        field_to = field
    addon_query = {}
    form = StatististicForm(request.GET)
    date_id_dict = request.session.get('date_id_dict',{})
    if form.is_valid():
        if form.cleaned_data['date_from']:
            addon_query[field+'__gte'] = form.cleaned_data['date_from']
            date_id_dict[id_begin+'_date_from'] = request.GET.get('date_from','')
        else:
            if date_id_dict.has_key(id_begin+'_date_from'):
                del(date_id_dict[id_begin+'_date_from'])
        if form.cleaned_data['date_to']:
            from datetime import timedelta
            addon_query[field_to+'__lte'] = form.cleaned_data['date_to'] + timedelta(hours = 23, minutes=59, seconds=59)
            date_id_dict[id_begin+'_date_to'] = request.GET.get('date_to', '')
        else:
            if date_id_dict.has_key(id_begin+'_date_to'):
                del(date_id_dict[id_begin+'_date_to'])
        request.session['date_id_dict'] = date_id_dict
        request.session.modified = True
    if request.GET.has_key('date_from') or request.GET.has_key('date_to'):
        is_range = True
    else:
        is_range = False
    return is_range, addon_query


@render_to('registration/login.html')
def login(request):
    error_message = True

    if request.method == 'POST':
        pin = request.POST.get('pin')
        user = request.POST.get('user')
        if pin:
            if user:
                
                message = None
                message_type = activate_card(user, pin)
                ok_message = False
                if message_type == 1:
                    message = _(u'Карточка успешно активирована. <br>  Ваш логин %(USERNAME)s <br> ваш пароль %(PASSWORD)s') % {
                                                                                                                                'USERNAME': user, 
                                                                                                                                'PASSWORD': pin}
                    ok_message = True
                if message_type == 2:
                    message = _(u'Неверно введен логин или пин')
                if message_type == 3:
                    message = _(u'Карточка уже была активирована')
            form = LoginForm()
            return {
                    'form':form,
                    'message':message,
                    'ok_message':ok_message,
                    }
        form = LoginForm(request.POST)
        if form.is_valid():
            
            user = authenticate(username=form.cleaned_data['username'], \
                                password=form.cleaned_data['password'])
            if user and isinstance(user.account, Account) and not user.account.allow_webcab:
                form = LoginForm()
                error_message = _(u'У вас нет прав на вход в веб-кабинет')
                return {
                        'error_message':error_message,
                        'form':form,
                        }
            elif user:
                log_in(request, user)
                
                if isinstance(user.account, SystemUser):
                    if request.META.get("HTTP_REFERER"):
                        if len(request.META.get("HTTP_REFERER").split('?next='))==2:
                            return HttpResponseRedirect(request.META.get("HTTP_REFERER").split('?next=')[1])
                    return HttpResponseRedirect(reverse("admin_dashboard"))
                tariff = user.account.get_account_tariff()
                if tariff and tariff.allow_express_pay:
                    request.session['express_pay']=True
                request.session.modified = True
                return HttpResponseRedirect('/')
            else:
                form = LoginForm(initial={'username': form.cleaned_data['username']})
                error_message = _(u'Проверьте введенные данные')
                return {
                        'error_message':error_message,
                        'form':form,
                        }

        else:
            form = LoginForm(initial={'username': request.POST.get('username', None)})
            error_message = _(u'Проверьте введенные данные')
            return {
                    'error_message':error_message,
                    'form':form,
                    }
    else:
        form = LoginForm()
        return {
                'form':form,
               }
@ajax_request
def simple_login(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        try:
            user = authenticate(username=form.cleaned_data['username'], \
                                password=form.cleaned_data['password'])
    
            log_in(request, user)
            return {"status":1,"fullname":user.account.fullname, "tariff_name":user.account.get_account_tariff().name,"message":"Login succeful"}
        except:
            return {"status":0,"fullname":'','tariff_name':'', "message":"User not found"}
    return {"status":0,"message":"User not found"}

@login_required
@ajax_request
def get_ballance(request):
    f = lambda v, l: [v[i*l:(i+1)*l] for i in range(int(math.ceil(len(v)/float(l))))]
    from models import AccountViewedNews,News
    
    #avn = AccountViewedNews.objects.filter(account=request.user.account, viewed=False).select_related().order_by('news.created')
    #avn=News.objects.filter().select_related().filter()
    
    cursor = connection.cursor()
    cursor.execute("""SELECT news.id, news.body FROM billservice_news as news
    WHERE agent=True and 
    (news.id in (SELECT news_id FROM billservice_accountviewednews WHERE account_id=%s and viewed is not True));
    """, (request.user.account.id,))
    avn=cursor.fetchall()

    news_arr=[]
    for n in avn:
        news_arr.append({'id':n[0],'title':n[1]})
        cursor.execute("UPDATE billservice_accountviewednews SET viewed=True where account_id=%s and news_id=%s", (request.user.account.id, n[0]))
        cursor.connection.commit()
        
    try:
        
        return {"status":1,"ballance_float":float(request.user.account.ballance), "ballance":"%.2f" % request.user.account.ballance,"message":"Ok", 'news':news_arr}
    except:
        return {"status":0,"ballance":-1,"message":"User not found"}
        
def login_out(request):
    log_out(request)
    return HttpResponseRedirect('/')


@render_to('accounts/index.html')
@login_required
def index(request):

    if isinstance(request.user.account, SystemUser):
        return HttpResponseRedirect(reverse("admin_dashboard"))

    user = request.user.account
    tariff_id, tariff_name = user.get_account_tariff_info()
    date = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    tariffs = AccountTarif.objects.filter(account=user, datetime__lt=date).order_by('-datetime')

    if len(tariffs) == 0 or len(tariffs) == 1:
        tariff_flag = False
    else:
        tariff_flag = True
    try:
        ballance = user.ballance - user.credit
        ballance = u'%.2f' % user.ballance
    except:
        ballance = 0
    
    subaccounts = SubAccount.objects.filter(account=user)
    traffic = None
    account_tariff = None
    account_prepays_traffic = None
    if tariff_id:
        traffic = TrafficLimit.objects.filter(tarif=tariff_id)
        account_tariff = AccountTarif.objects.filter(account=user, datetime__lte=datetime.datetime.now()).order_by('-datetime')[0]
        account_prepays_traffic = AccountPrepaysTrafic.objects.filter(account_tarif=account_tariff, current=True)

    prepaydtime = None
    try:
        prepaydtime = AccountPrepaysTime.objects.get(account_tarif=account_tariff, current=True)
    except:
        pass
    prepaydradiustraffic=None
    try:
        prepaydradiustraffic = AccountPrepaysRadiusTrafic.objects.get(account_tarif=account_tariff, current=True)
    except:
        pass

    try:
        next_tariff = AccountTarif.objects.filter(account=user, datetime__gte=datetime.datetime.now()).order_by('-datetime')[0]
    except:
        next_tariff = None
    return {
            'account_tariff':account_tariff or '',
            'ballance':ballance,
            'tariff':tariff_name,
            'tariffs':tariffs,
            #'status': bool(user.blocked),
            'tariff_flag':tariff_flag,
            'prepaydtime':prepaydtime,
            'prepaydradiustraffic':prepaydradiustraffic,
            'trafficlimit':traffic,
            'account_prepays_traffic':account_prepays_traffic,
            'active_class':'user-img',
            'next_tariff':next_tariff,
            'subaccounts':subaccounts,
            'user':request.user.account
            }


@render_to('accounts/get_promise.html')
@login_required
def get_promise(request):
    if  isinstance(request.user.account, SystemUser): 
        return HttpResponseRedirect('/')
    tarif=request.user.account.get_account_tariff()

    if not settings.ALLOW_PROMISE and not tarif.allow_ballance_transfer:
        return HttpResponseRedirect('/')
    if not tarif:
        return {'error_message': _(u'Вам не назначен тарифный план'), 'disable_promise': True}
    user = request.user.account
    promise_summ = user.promise_summ if user.promise_summ not in [None, 0, ''] else settings.MAX_PROMISE_SUM
    promise_min_ballance = user.promise_min_ballance if user.promise_min_ballance not in [None, 0, ''] else settings.MIN_BALLANCE_FOR_PROMISE
    allow_transfer_summ= "%.2f" % (0 if user.ballance<=0 else user.ballance)
    LEFT_PROMISE_DATE = datetime.datetime.now()+datetime.timedelta(days = user.promise_days or settings.LEFT_PROMISE_DAYS)
    if settings.ALLOW_PROMISE==True and Transaction.objects.filter(account=user, type=TransactionType.objects.get(internal_name='PROMISE_PAYMENT'), promise_expired=False).count() >= 1:
        last_promises = Transaction.objects.filter(account=user,  type=TransactionType.objects.get(internal_name='PROMISE_PAYMENT')).order_by('-created')[0:10]
        error_message = _(u"У вас есть незакрытые обещанные платежи")
        return {'error_message': error_message, 'MAX_PROMISE_SUM': promise_summ, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'disable_promise': True, 'last_promises': last_promises, 'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'active_class':'promise-img',}
    if settings.ALLOW_PROMISE==True and user.ballance<promise_min_ballance:
        last_promises = Transaction.objects.filter(account=user, type=TransactionType.objects.get(internal_name='PROMISE_PAYMENT')).order_by('-created')[0:10]
        error_message = _(u"Ваш баланс меньше разрешённого для взятия обещанного платежа. Минимальный баланс: %(MIN_BALLANCE)s %(CURRENCY)s") % {'MIN_BALLANCE': promise_min_ballance, 'CURRENCY': settings.CURRENCY}
        return {'error_message': error_message, 'MAX_PROMISE_SUM': promise_summ, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'disable_promise': True, 'last_promises': last_promises, 'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'active_class':'promise-img',}
    
    
    if request.method == 'POST':
        operation= request.POST.get("operation")
        if operation=='promise':
            rf = PromiseForm(request.POST)
            if not rf.is_valid():
                last_promises = Transaction.objects.filter(account=user, type=TransactionType.objects.get(internal_name='PROMISE_PAYMENT')).order_by('-created')[0:10]
                error_message = _(u"Проверьте введённые в поля данные")
                return {'MAX_PROMISE_SUM': promise_summ, 'error_message': error_message, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'disable_promise': False,  'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'last_promises': last_promises, 'active_class':'promise-img',}
            sum=rf.cleaned_data.get("sum", 0)
            if sum>promise_summ:
                last_promises = Transaction.objects.filter(account=user, type=TransactionType.objects.get(internal_name='PROMISE_PAYMENT')).order_by('-created')[0:10]
                error_message = _(u"Вы превысили максимальный размер обещанного платежа")
                return {'MAX_PROMISE_SUM': promise_summ,'error_message': error_message, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'disable_promise': False,  'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'last_promises': last_promises, 'active_class':'promise-img',}
            if sum<=0:
                last_promises = Transaction.objects.filter(account=user, type=TransactionType.objects.get(internal_name='PROMISE_PAYMENT')).order_by('-created')[0:10]
                error_message = _(u"Сумма обещанного платежа должна быть положительной")
                return {'MAX_PROMISE_SUM': user.promise_summ,'error_message': error_message, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'disable_promise': False,  'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'last_promises': last_promises, 'active_class':'promise-img',}
            cursor = connection.cursor()
            cursor.execute(u"""INSERT INTO billservice_transaction(account_id, bill, type_id, approved, tarif_id, summ, created, end_promise, promise_expired)
                              VALUES(%s, 'Обещанный платёж', 'PROMISE_PAYMENT', True, get_tarif(%s), %s, now(), '%s', False)""" % (user.id, user.id, sum, LEFT_PROMISE_DATE))
            cursor.connection.commit()
    
    
            last_promises = Transaction.objects.filter(account=user, type=TransactionType.objects.get(internal_name='PROMISE_PAYMENT')).order_by('-created')[0:10]
    
            return {'error_message': _(u'Обещанный платёж выполнен успешно. Обращаем ваше внимание на то, что повторно воспользоваться услугой обещанного платежа вы сможете после единоразового погашения всей суммы платежа или истечения даты созданного платежа.'), 'disable_promise': True, 'last_promises': last_promises, 'active_class':'promise-img',}
        elif operation=='moneytransfer':
            last_promises = Transaction.objects.filter(account=user, type=TransactionType.objects.get(internal_name='PROMISE_PAYMENT')).order_by('-created')[0:10]
            if tarif.allow_ballance_transfer==False:
                return {'error_message': _(u'Вам запрещено пользоваться сервисом перевода баланса.'),'MAX_PROMISE_SUM': promise_summ, 'last_promises': last_promises, 'disable_promise': False, 'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'active_class':'promise-img',}
                
            sum = request.POST.get("sum", 0)
            username = request.POST.get("username", '')
            if username:
                try:
                    to_user=Account.objects.get(username=username)
                except:
                    return {'error_message': _(u'Абонент с указанным логином не найден'),'MAX_PROMISE_SUM': promise_summ, 'last_promises': last_promises, 'disable_promise': False, 'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'active_class':'promise-img',}
                    
            else:
                return {'error_message': _(u'Логин абонента, которому вы хотите перевести средства, не указан.'),'MAX_PROMISE_SUM': promise_summ, 'last_promises': last_promises, 'disable_promise': False, 'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'active_class':'promise-img',}
            
            try:
                sum = float(sum)
            except:
                return {'error_message': _(u'Указанная сумма не является числом. Разрешено вводить цифры 0-9 и точку, как разделитель разрядов.'),'MAX_PROMISE_SUM': promise_summ, 'last_promises': last_promises, 'disable_promise': False, 'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'active_class':'promise-img',}
            
            if sum>allow_transfer_summ:
                return {'error_message': _(u'Указанная сумма слишком велика.'),'MAX_PROMISE_SUM': promise_summ, 'last_promises': last_promises, 'disable_promise': False, 'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'active_class':'promise-img',}    
            from decimal import Decimal
            cursor=connection.cursor()
            cursor.execute(u"""INSERT INTO billservice_transaction(account_id, bill, description, type_id, approved, tarif_id, summ, created, promise)
                              VALUES(%s, %s, %s, 'MONEY_TRANSFER_TO', True, get_tarif(%s), %s, now(), False)""" , (user.id, to_user.id, u'Перевод средств на аккаунт %s' % to_user.username, user.id, -1*sum))
            cursor.execute(u"""INSERT INTO billservice_transaction(account_id, bill, description, type_id, approved, tarif_id, summ, created, promise)
                              VALUES(%s, %s, %s, 'MONEY_TRANSFER_FROM', True, get_tarif(%s), %s, now(), False)""" , (to_user.id, user.id, u'Перевод средств с аккаунта %s' % user.username, to_user.id, sum))

            cursor.connection.commit()
            allow_transfer_summ= "%.2f" % (0 if user.ballance<=0 else user.ballance-Decimal(sum))
            return {'error_message': _(u'Перевод средств успешно выполнен.'), 'disable_promise': False, 'last_promises': last_promises, 'allow_ballance_transfer':tarif.allow_ballance_transfer,  'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'allow_transfer_summ':allow_transfer_summ, 'active_class':'promise-img',}
    else:
        last_promises = Transaction.objects.filter(account=user, type__internal_name__in=['PROMISE_PAYMENT']).order_by('-created')[0:10]
        return {'MAX_PROMISE_SUM': promise_summ, 'last_promises': last_promises, 'disable_promise': not settings.ALLOW_PROMISE, 'allow_ballance_transfer':tarif.allow_ballance_transfer, 'allow_transfer_summ':allow_transfer_summ, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'active_class':'promise-img',}


@login_required
@render_to('accounts/make_payment.html')
def make_payment(request):
    wm_form = None
    qiwi_form = None
    if settings.ALLOW_QIWI:
        last_qiwi_invoice = None
        try:
            last_qiwi_invoice = QiwiInvoice.objects.filter(account=request.user.account).order_by('-created')[0]
        except Exception, e:
            #print e
            pass
        if last_qiwi_invoice:
            qiwi_form = QiwiPaymentRequestForm(initial={'phone':last_qiwi_invoice.phone})
        else:
             qiwi_form = QiwiPaymentRequestForm(initial={'phone':request.user.account.phone_m})
    from getpaid.forms import SelectPaymentMethodForm
    form = SelectPaymentMethodForm()
    return {'allow_qiwi':settings.ALLOW_QIWI, 'allow_webmoney':settings.ALLOW_WEBMONEY, 'qiwi_form':qiwi_form, 'payment_form': form}



@ajax_request
@login_required
def qiwi_payment(request):
    from django.utils.translation import ugettext as _
    if request.method != 'POST': return {'status_message':_(u"Неправильный вызов функции")}
    form = QiwiPaymentRequestForm(request.POST)
    if not form.is_valid():return {'status_message':_(u"Ошибка в заполнении полей")}
    summ = form.cleaned_data.get('summ', 0)
    phone = form.cleaned_data.get('phone', '')
    password = form.cleaned_data.get('password', '')
    autoaccept = form.cleaned_data.get("autoaccept", False)

    if autoaccept==True and not (password): return {'status_message':_(u"Для автоматического зачисления необходимо указать пароль")}
    if summ<settings.QIWI_MIN_SUMM: return {'status_message':_(u"Минимальная сумма платежа %s") % settings.QIWI_MIN_SUMM}

    if summ>=1 and len(phone)==10:
        from paymentgateways.qiwi.qiwiapi import create_invoice, accept_invoice_id, lifetime, get_balance
        #if autoaccept:
        #    balance, message = get_balance(phone=phone, password=password)
        #    if float(balance)<summ: return {'status_message':_(u"Сбой автозачисления: баланс вашего кошелька меньше суммы оплаты или включено sms подтверждение действий."}
        invoice = QiwiInvoice()
        invoice.account = request.user.account
        invoice.phone = phone
        invoice.summ = summ
        invoice.created = datetime.datetime.now()
        invoice.autoaccept=autoaccept
        invoice.lifetime = lifetime
        invoice.save()
        comment = _(u"Пополнение счёта %s") % request.user.account.username
        status, message=create_invoice(phone_number=phone,transaction_id=invoice.id, summ=invoice.summ, comment=comment)
        #print 'status', type(status)
        payed=False
        if status!=0:
            #invoice.delete()
            return {'status_message':_(u'Произошла ошибка выставления счёта. %s') % message}
        payment_url=''
        if not invoice.autoaccept:
            from paymentgateways.qiwi.qiwiapi import term_id
            if status==0:
                payment_url="https://w.qiwi.ru/externalorder.action?shop=%s&transaction=%s" % (term_id,invoice.id)
                message = _(u'Счёт удачно создан. Пройдите по ссылке для его оплаты.')
                payed=True
        else:
            status, message = accept_invoice_id(phone=phone, password=password, transaction_id=invoice.id, date=invoice.created)
            if status==0:
                message=_(u"Платёж успешно выполнен.")
                invoice.accepted=True
                invoice.date_accepted=datetime.datetime.now()
                invoice.save()
                payed=True


        return {'status_message':message, 'payment_url':payment_url,'payed':payed, 'invoice_id':invoice.id, 'invoice_summ':float(invoice.summ), 'invoice_date':"%s-%s-%s %s:%s:%s" % (invoice.created.day, invoice.created.month, invoice.created.year,invoice.created.hour, invoice.created.minute, invoice.created.second)}
    else:
        return {'status_message':_(u'Сумма<1 или неправильный формат телефонного номера.')}

@ajax_request
@login_required
def qiwi_balance(request):
    from django.utils.translation import ugettext as _
    if request.method != 'POST': return {'balance':0, 'status_message':_(u"Неправильный вызов функции")}
    phone = request.POST.get('phone', None)
    password = request.POST.get('password', None)
    if phone and password:
        from paymentgateways.qiwi.qiwiapi import get_balance
        balance, message = get_balance(phone=phone, password=password)
        #print balance, message
        return {'balance':balance, 'status_message':message}
    else:
        message = _(u"Не указан телефон или пароль")
        return {'balance':0, 'status_message':message}


@render_to('accounts/transaction.html')
@login_required
def transaction(request):
    from lib.paginator import SimplePaginator
    is_range, addon_query = addon_queryset(request, 'transactions', 'created')
    qs = Transaction.objects.filter(account=request.user.account, **addon_query).order_by('-created')
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    transactions = paginator.get_page_items()
    if is_range:
        for trnsaction in qs:
            summ += trnsaction.summ
        for transactio in transactions:
            summ_on_page += trnsaction.summ
    summ = summ
    summ_on_page = summ_on_page
    rec_count = len(transactions)+1
    return {
            'transactions':transactions,
            'paginator': paginator,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }

@render_to('accounts/groupstat.html')
@login_required
def traffic_volume(request):
    from lib.paginator import SimplePaginator
    is_range, addon_query = addon_queryset(request, 'gpst', 'datetime')
    #print is_range, addon_query
    user = request.user.account
    cursor = connection.cursor()
    sql="""
        SELECT (SELECT name FROM billservice_group WHERE id=group_id) as group_name,sum(bytes), date_part('day',datetime) as dt_day, date_part('month',datetime) as dt_month, date_part('year',datetime) as dt_year  
        FROM billservice_groupstat 
        WHERE account_id=%s %%s
        GROUP BY date_part('year',datetime),date_part('month',datetime),date_part('day',datetime), group_name ORDER BY dt_year,dt_month, dt_day DESC;
    
    """ % (user.id,)
    
    if is_range and addon_query.has_key('datetime__gte') and addon_query.has_key('datetime__lte'):
        sql = sql % " and datetime between '%s' and '%s' " % (addon_query['datetime__gte'],addon_query['datetime__lte'])
    else:
        sql = sql % ' '
    cursor.execute(sql)
    items=cursor.fetchall()
    group_stat=[]
    summ_bytes = 0
    for item in items:
        group_stat.append({'day':int(item[2]),'month':int(item[3]),'year':int(item[4]),'group_name':item[0],'bytes':item[1],})
        summ_bytes += item[1]


    rec_count = len(items)+1
    return {
            'group_stat':group_stat,
            #'paginator': paginator,
            'is_range':is_range,
            'summ_bytes':summ_bytes,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }
    
@render_to('accounts/vpn_session.html')
@login_required
def vpn_session(request):
    from lib.paginator import SimplePaginator
    user = request.user.account
    is_range, addon_query = addon_queryset(request, 'active_session', 'date_start', 'date_end')
    qs = ActiveSession.objects.filter(account=user, **addon_query).order_by('-date_start')
    paginator = SimplePaginator(request, qs, 50, 'page')
    bytes_in = 0
    bytes_out = 0
    bytes_all = 0
    bytes_in_on_page = 0
    bytes_out_on_page = 0
    bytes_all_on_page = 0
    sessions = paginator.get_page_items()
    if is_range:
        for session in qs:
            if session.bytes_in:
                bytes_in += session.bytes_in
            if session.bytes_out:
                bytes_out += session.bytes_out
        for session in sessions:
            if session.bytes_in:
                bytes_in_on_page += session.bytes_in
            if session.bytes_out:
                bytes_out_on_page += session.bytes_out
    bytes_all_on_page = bytes_in_on_page + bytes_out_on_page
    bytes_all = bytes_in + bytes_out
    rec_count = len(sessions)+1
    return {
            'sessions':paginator.get_page_items(),
            'paginator': paginator,
            'user': user,
            'rec_count':rec_count,
            'bytes_in':bytes_in,
            'bytes_out':bytes_out,
            'bytes_all':bytes_all,
            'bytes_in_on_page':bytes_in_on_page,
            'bytes_out_on_page':bytes_out_on_page,
            'bytes_all_on_page':bytes_all_on_page,
            'is_range':is_range,
            'active_class':'statistic-img',
            }


@render_to('accounts/services_info.html')
@login_required
def services_info(request):
    from lib.paginator import SimplePaginator
    user = request.user.account
    is_range, addon_query = addon_queryset(request, 'services', 'activated')
    qs = AccountAddonService.objects.filter(account=user, **addon_query).order_by('-activated')
    paginator = SimplePaginator(request, qs, 50, 'page')
    summ = 0
    summ_on_page = 0
    services = paginator.get_page_items()
    if is_range:
        for service in qs:
            service_summ = 0
            for transaction in AddonServiceTransaction.objects.filter(accountaddonservice=service):
                service_summ += transaction.summ
            summ += service_summ
        for service in services:
            service_summ = 0
            for transaction in AddonServiceTransaction.objects.filter(accountaddonservice=service):
                service_summ += transaction.summ
            summ_on_page += service_summ
    services = paginator.get_page_items()
    rec_count = len(services)+1
    return {
            'services':services,
            'paginator': paginator,
            'user': user,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }


@render_to('accounts/change_password.html')
@login_required
def password_form(request):
    return {
            'password_form':PasswordForm(),
            'email_form':EmailForm(),
            }

@render_to('accounts/subaccount_change_password.html')
@login_required
def subaccount_password_form(request, subaccount_id):
    subaccount = SubAccount.objects.get(id=subaccount_id)
    return {
            'form':SimplePasswordForm(), "subaccount":subaccount,
            }

@ajax_request
@login_required
def subaccount_change_password(request):
    from django.utils.translation import ugettext as _
    if request.method == 'POST':
        form = SimplePasswordForm(request.POST)
        if form.is_valid():
            try:
                user = request.user.account
                subaccount_id = request.POST.get("subaccount_id", 0)
                if subaccount_id:
                    try:
                        subaccount = SubAccount.objects.get(id=subaccount_id, account=request.user.account)
                    except Exception, e:
                        #print e
                        return {
                                'error_message': _(u'Обнаружена попытка взлома.'),
                                }
                else:
                    return {
                            'error_message': _(u'Обнаружена попытка взлома.'),
                            }


                if form.cleaned_data['new_password']==form.cleaned_data['repeat_password'] and subaccount.password!='':

                    subaccount.password = form.cleaned_data['new_password']
                    subaccount.save()
                    return {
                            'error_message': _(u'Пароль успешно изменен'),
                            }
                else:
                    return {
                            'error_message': _(u'Пароли не совпадают'),
                            }
            except Exception, e:
                return {
                        'error_message': _(u'Возникла ошибка. Обратитесь к администратору.'),
                        }
        else:
            return {
                    'error_message': _(u'Одно из полей не заполнено'),
                    }
    else:
        return {
                'error_message': _(u'Не предвиденная ошибка'),
                }


@ajax_request
@login_required
def change_password(request):
    from django.utils.translation import ugettext as _
    if request.method == 'POST':
        user = request.user.account
  
        form = PasswordForm(request.POST)
        if form.is_valid():
            try:
                
                if user.password == form.cleaned_data['old_password'] and form.cleaned_data['new_password']==form.cleaned_data['repeat_password']:
                    user.password = form.cleaned_data['new_password']
                    user.save()
                    return {
                            'error_message': _(u'Пароль успешно изменен'),
                            }
                else:
                    return {
                            'error_message': _(u'Проверьте пароль. '),
                            }
            except Exception, e:
                return {
                        'error_message': _(u'Возникла ошибка. Обратитесь к администратору.'),
                        }
        else:
            return {
                    'error_message': _(u'Проверьте введенные данные'),
                    }
    else:
        return {
                'error_message': _(u'Не предвиденная ошибка'),
                }


@ajax_request
@login_required
def change_email(request):
    from django.utils.translation import ugettext as _
    if request.method == 'POST':
        user = request.user.account
        form = EmailForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['new_email'] and form.cleaned_data['repeat_email'] and form.cleaned_data['new_email']==form.cleaned_data['repeat_email']:
                user.email=form.cleaned_data['new_email']
                user.save()
                return {
                        'error_message': _(u'E-mail успешно изменен'),
                        'ok':'ok',
                        }
            else:
                return {
                        'error_message': _(u'Введённые e-mail не совпадают'),
                        }

        else:
            return {
                    'error_message': _(u'Проверьте введенные данные'),
                    }


@ajax_request
@render_to('accounts/change_tariff.html')
@login_required
def change_tariff_form(request):
    from datetime import datetime, date
    from django.utils.translation import ugettext as _
    user = request.user.account
    account_tariff_id =  AccountTarif.objects.filter(account = user, datetime__lt=datetime.now()).order_by('-datetime')[:1]
    account_tariff = account_tariff_id[0]
    tariffs = TPChangeRule.objects.filter(from_tariff = account_tariff.tarif)
    res=[]
    for rule in tariffs:
        data_start_period=None
        if rule.on_next_sp:
            sp = user.get_account_tariff().settlement_period
            if sp:
                if sp.autostart:
                    start = account_tariff.datetime
                else:
                    start = sp.time_start
                td = settlement_period_info(start, sp.length_in, sp.length)
                data_start_period = td[1]
        rule.date_start=data_start_period        
        res.append(rule)
            
    form = ChangeTariffForm(user, account_tariff)
    return {
            'form': form,
            'tariff_objects':res,
            'user':user,
            'tariff':account_tariff,
            #'time':time,
            }


@ajax_request
@login_required
def change_tariff(request):
    """
        settlement_period_info
        1 - дата начала действия тарифа

    """
    from django.utils.translation import ugettext as _
    from datetime import datetime
    if request.method == 'POST':
        rule_id = request.POST.get('id_tariff_id', None)
        if rule_id != None:
            user = request.user.account
            current_tariff=user.get_account_tariff()
            account_tariff_id = \
                AccountTarif.objects.filter(account=user, \
                            datetime__lt=datetime.now()).order_by('-datetime')[:1]
            account_tariff = account_tariff_id[0]

            rules_id =[x.id for x in TPChangeRule.objects.filter(from_tariff = account_tariff.tarif)]
            rule = TPChangeRule.objects.get(id=rule_id)
            data_start_period = datetime.now()
            data_start_active = False
            if rule.settlement_period_id:
                td = settlement_period_info(account_tariff.datetime, rule.settlement_period.length_in, rule.settlement_period.length)
                delta = (datetime.now() - account_tariff.datetime).seconds+(datetime.now() - account_tariff.datetime).days*86400 - td[2]
                if delta < 0:
                    return {
                            'error_message':_(u'Вы не можете перейти на выбранный тариф. Для перехода вам необходимо отработать на старом тарифе ещё не менее %s дней') % (delta/86400*(-1), ),
                            }
            if rule.on_next_sp:
                sp = current_tariff.settlement_period
                if sp:
                    if sp.autostart:
                        start = account_tariff.datetime
                    else:
                        start = sp.time_start
                    td = settlement_period_info(start, sp.length_in, sp.length)
                    data_start_period = td[1]
                    data_start_active = True
            if not rule.id in rules_id:
                return {
                        'error_message':_(u'Вы не можете перейти на выбранный тарифный план.'),
                        }
            
            if float(rule.ballance_min)>float(user.ballance+user.credit):
                return {
                        'error_message':_(u'Вы не можете перейти на выбранный тарифный план. Ваш баланс меньше разрешённого для такого перехода.'),
                        }
                
            tariff = AccountTarif.objects.create(
                                                    account = user,
                                                    tarif = rule.to_tariff,
                                                    datetime = data_start_period,
                                                )
            #from billservice.models import AddonServiceTarif
            for service in AccountAddonService.objects.filter(account=user, deactivated__isnull=True):
                #addt=AddonServiceTarif.objects.filter(tarif=current_tariff,service=service.service)
                if service.service.cancel_subscription:
                    service.deactivated = data_start_period
                    service.save()
                    
            if rule.cost:
                cursor = connection.cursor()

                cursor.execute(u"""INSERT INTO billservice_transaction(account_id, bill, type_id, approved, tarif_id, summ, created, promise)
                                  VALUES(%s, 'Списание средств за переход на тарифный план %s', 'TP_CHANGE', True, get_tarif(%s), (-1)*%s, now(), False)""" % (user.id, tariff.tarif.name, user.id, rule.cost))
                cursor.connection.commit()
            if data_start_active:
                ok_str = _(u'Вы успешно сменили тариф, тарифный план будет изменён в следующем расчётном периоде c %(TP)s.<br> За переход на данный тарифный план с пользователя будет взыскано %(SUMM)s средств.') %{'TP': td[1], 'SUMM': rule.cost}
                return {
                         'ok_message':ok_str,
                        }
            else:
                return {
                        'ok_message':_(u'Вы успешно сменили тариф. <br> За переход на данный тарифный план с пользователя будет взыскано %s средств.') % rule.cost,
                        }
        else:
            return {
                    'error_message':_(u'Системная ошибка.'),
                    }
    else:
        return {
                'error_message':_(u'Попытка взлома'),
                }


@render_to('accounts/card_form.html')
@login_required
def card_form(request):
    return {
            'form':ActivationCardForm()
            }


@ajax_request
@login_required
def card_acvation(request):
    from django.utils.translation import ugettext as _
    user = request.user.account
    if not user.allow_expresscards:
        return {
                'error_message': _(u'Вам не доступна услуга активации карт экспресс оплаты.'),
                }


    if request.method == 'POST':
        form = ActivationCardForm(request.POST)
        error_message = ''
        if form.is_valid():

            res = activate_pay_card(user.id, form.cleaned_data['card_id'], form.cleaned_data['pin'])
            #print res
            if res == 'CARD_NOT_FOUND':
                error_message = _(u'Ошибка активации. Карта не найдена.')
            elif res == 'CARD_NOT_SOLD':
                error_message = _(u'Ошибка активации. Карта не была продана.')
            elif res == 'CARD_ALREADY_ACTIVATED':
                error_message = _(u'Ошибка активации. Карта была активирована раньше.')
            elif res == 'CARD_EXPIRED':
                error_message = _(u'Ошибка активации. Срок действия карты истёк.')
            elif res == 'CARD_ACTIVATED':
                error_message = _(u'Карта успешно активирована.')
            elif res == 'CARD_ACTIVATION_ERROR':
                error_message = _(u'Ошибка активации карты.')

            #if int(cache_user['count']) <= settings.ACTIVATION_COUNT:
            #    cache.delete(user.id)
            #    count = int(int(cache_user['count']))
            #    cache.set(user.id, {'count':count+1,'last_date':cache_user['last_date'],'blocked':False,}, 86400*365)
            #form = CardForm(request.POST)
            return {
                    'error_message':error_message,
                    #'form': form,
                    }
        else:
            #count = int(cache_user['count'])
            #if int(cache_user['count']) < settings.ACTIVATION_COUNT+1:
            #    cache.delete(user.id)
            #    cache.add(user.id, {'count':count+1,'last_date':cache_user['last_date'],'blocked':False,})
            return {
                    'error_message': _(u"Проверьте заполнение формы"),
                    #'form': form,
                    }
    else:
        #form = CardForm()
        return {
                'error_message': _(u"Ошибка активации карточки"),
                #'form':form,
                }

@render_to('accounts/account_prepays_traffic.html')
@login_required
def account_prepays_traffic(request):
    user = request.user.account
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




@render_to('accounts/traffic_limit.html')
@login_required
def traffic_limit(request):
    user = request.user.account
    tariff = user.get_account_tariff()
    traffic = TrafficLimit.objects.filter(tarif=tariff)
    return {
            'trafficlimit':traffic,
            'user':user,
            }


@render_to('accounts/statistics.html')
@login_required
def statistics(request):
    user = request.user.account
    transaction = Transaction.objects.filter(account=user).order_by('-created')[:8]
    active_session = ActiveSession.objects.filter(account=user).order_by('-date_start')[:8]
    periodical_service_history = PeriodicalServiceHistory.objects.filter(account=user).order_by('-created')[:8]
    addon_service_transaction = AddonServiceTransaction.objects.filter(account=user).order_by('-created')[:8]
    one_time_history = OneTimeServiceHistory.objects.filter(account=user).order_by('-created')[:8]
    traffic_transaction = TrafficTransaction.objects.filter(account=user).order_by('-created')[:8]
    #groupstat = GroupStat.objects.filter(account=user).order_by('-datetime')[:8]
    cursor = connection.cursor()
    cursor.execute("""
        SELECT (SELECT name FROM billservice_group WHERE id=group_id) as group_name,sum(bytes), date_part('day',datetime) as dt_day, date_part('month',datetime) as dt_month, date_part('year',datetime) as dt_year  
        FROM billservice_groupstat WHERE account_id=%s GROUP BY date_part('year',datetime),date_part('month',datetime),date_part('day',datetime), group_name ORDER BY dt_year,dt_month, dt_day DESC;
    
    """, (user.id,))
    items=cursor.fetchall()
    group_stat=[]
    for item in items:
        group_stat.append({'day':int(item[2]),'month':int(item[3]),'year':int(item[4]),'group_name':item[0],'bytes':item[1],})
    #connection.commit()
    if request.session.has_key('date_id_dict'):
        date_id_dict = request.session['date_id_dict']
    else:
        date_id_dict = {}
    return {
            #'net_flow_stream':net_flow_streams,
            'transactions':transaction,
            'active_session':active_session,
            #'services':services,
            'periodical_service_history':periodical_service_history,
            'addon_service_transaction':addon_service_transaction,
            'one_time_history':one_time_history,
            'traffic_transaction':traffic_transaction,
            'group_stat':group_stat,
            'form':StatististicForm(),
            'date_id_dict':date_id_dict,
            'active_class':'statistic-img',
            }


@render_to('accounts/addonservice.html')
@login_required
def addon_service(request):
    user = request.user.account
    #account_tariff_id =  AccountTarif.objects.filter(account = user, datetime__lt=datetime.datetime.now()).order_by('id')[:1]
    #account_tariff = account_tariff_id[0]
    addontarif_services = AddonServiceTarif.objects.filter(tarif=user.get_account_tariff(), type=0).order_by("service__name")
    
    #s_ids = [x.service_id for x in addontarif_services]
    account_services = AccountAddonService.objects.filter(account=user, subaccount__isnull=True, deactivated__isnull=True)
    accountservices = []
    for uservice in account_services:
        if uservice.service.wyte_period_id:
            delta = settlement_period_info(uservice.activated, uservice.service.wyte_period.length_in, uservice.service.wyte_period.length)[2]
            if uservice.activated + datetime.timedelta(seconds = delta)>datetime.datetime.now():
                uservice.wyte = True
                uservice.end_wyte_date = uservice.activated + datetime.timedelta(seconds = delta)
            else:
                uservice.wyte = False
        elif uservice.service.wyte_cost:
            uservice.wyte = True
        else:
            uservice.wyte = False
        accountservices.append(uservice)

    user_services_id = [x.service.id for x in accountservices if not x.deactivated]
    addon_srvcs=[]
    for adds in addontarif_services:
        accs = AccountAddonService.objects.filter(service=adds.service,account=user, subaccount__isnull=True, deactivated__isnull=True)
        
        for uservice in accs:
            if uservice.service.wyte_period_id:
                delta = settlement_period_info(uservice.activated, uservice.service.wyte_period.length_in, uservice.service.wyte_period.length)[2]
                if uservice.activated + datetime.timedelta(seconds = delta)>datetime.datetime.now():
                    uservice.wyte = True
                    uservice.end_wyte_date = uservice.activated + datetime.timedelta(seconds = delta)
                else:
                    uservice.wyte = False
            elif uservice.service.wyte_cost:
                uservice.wyte = True
            else:
                uservice.wyte = False
        addon_srvcs.append((adds,accs))
    #account_services = addontarif_services.exclude(service__id__in=user_services_id).order_by("service__name")
    return_dict = {
                   'addontarif_services':addontarif_services,
                   'addon_srvcs':addon_srvcs,
                   'account_services_id':user_services_id,
                   'account_services':account_services,
                   'user':user,
                   'active_class':'services-img',
                   }
    if request.session.has_key('service_message'):
        return_dict['service_message'] = request.session['service_message']
        del(request.session['service_message'])
    return return_dict

@login_required
def service_action(request, action, id):
    """
    в случее set id являеться идентификатором добавляемой услуги
    в случее del id являеться идентификатором accountaddon_service
    """
    user = request.user.account



    if action == u'set':
        try:
            account_addon_service = AddonService.objects.get(id=id)
        except:
            request.session['service_message'] = _(u'Вы не можете подключить данную услугу')
            return HttpResponseRedirect('/services/')
        
        result = add_addonservice(account_id=user.id, service_id=id)
        if result == True:
            request.session['service_message'] = _(u'Услуга подключена')
            return HttpResponseRedirect('/services/')
        elif result == 'ACCOUNT_DOES_NOT_EXIST':
            request.session['service_message'] = _(u'Указанный пользователь не найден')
            return HttpResponseRedirect('/services/')
        elif result == 'ADDON_SERVICE_DOES_NOT_EXIST':
            request.session['service_message'] = _(u'Указанныя подключаемая услуга не найдена')
            return HttpResponseRedirect('/services/')
        elif result == 'NOT_IN_PERIOD':
            request.session['service_message'] = _(u'Активация выбранной услуги в данный момент не доступна')
            return HttpResponseRedirect('/services/')
        elif result == 'ALERADY_HAVE_SPEED_SERVICE':
            request.session['service_message'] = _(u'У вас уже подключенны изменяющие скорость услуги')
            return HttpResponseRedirect('/services/')
        elif result == 'ACCOUNT_BLOCKED':
            request.session['service_message'] = _(u'Услуга не может быть подключена. Проверьте Ваш баланс или обратитесь в службу поддержки')
            return HttpResponseRedirect('/services/')
        elif result == 'ADDONSERVICE_TARIF_DOES_NOT_ALLOWED':
            request.session['service_message'] = _(u'На вашем тарифном плане активация выбранной услуги невозможна')
            return HttpResponseRedirect('/services/')
        elif result == 'TOO_MUCH_ACTIVATIONS':
            request.session['service_message'] = _(u'Превышенно допустимое количество активаций. Обратитесь в службу поддержки')
            return HttpResponseRedirect('/services/')
        elif result == 'SERVICE_ARE_ALREADY_ACTIVATED':
            request.session['service_message'] = _(u'Указанная услуга уже подключена и не может быть активирована дважды.')
            return HttpResponseRedirect('/services/')
        else:
            request.session['service_message'] = _(u'Услугу не возможно подключить')
            return HttpResponseRedirect('/services/')
    elif action == u'del':
        result = del_addonservice(user.id, id)
        if result == True:
            request.session['service_message'] = _(u'Услуга отключена')
            return HttpResponseRedirect('/services/')
        elif result == 'ACCOUNT_DOES_NOT_EXIST':
            request.session['service_message'] = _(u'Указанный пользователь не найден')
            return HttpResponseRedirect('/services/')
        elif result == 'ADDON_SERVICE_DOES_NOT_EXIST':
            request.session['service_message'] = _(u'Указанныя подключаемая услуга не найдена')
            return HttpResponseRedirect('/services/')
        elif result == 'ACCOUNT_ADDON_SERVICE_DOES_NOT_EXIST':
            request.session['service_message'] = _(u'Вы не можите отключить выбранную услугу')
            return HttpResponseRedirect('/services/')
        elif result == 'NO_CANCEL_SUBSCRIPTION':
            request.session['service_message'] = _(u'Даннная услуга не может быть отключена. Обратитесь в службу поддержки')
            return HttpResponseRedirect('/services/')
        else:
            request.session['service_message'] = _(u'Услугу не возможно отключить')
            return HttpResponseRedirect('/services/')
    else:
        request.session['service_message'] = _(u'Невозможно совершить действие')
        return HttpResponseRedirect('/services/')

@render_to('accounts/periodical_service_history.html')
@login_required
def periodical_service_history(request):
    from lib.paginator import SimplePaginator
    is_range, addon_query = addon_queryset(request, 'periodical_service_history', 'created')
    qs = PeriodicalServiceHistory.objects.filter(account=request.user.account, \
                                       **addon_query).order_by('-created')
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    periodical_service_history = paginator.get_page_items()
    if is_range:
        for periodical_service in qs:
            summ += periodical_service.summ
        for periodical_service in periodical_service_history:
            summ_on_page += periodical_service.summ
    rec_count = len(periodical_service_history) + 1
    return {
            'periodical_service_history':periodical_service_history,
            'paginator': paginator,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }

@render_to('accounts/addon_service_transaction.html')
@login_required
def addon_service_transaction(request):
    from lib.paginator import SimplePaginator
    is_range, addon_query = addon_queryset(request, 'addon_service_transaction', 'created')
    qs = AddonServiceTransaction.objects.filter(account=request.user.account, \
                                     **addon_query).order_by('-created')
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    addon_service_transaction = paginator.get_page_items()
    if is_range:
        for addon_service in qs:
            summ += addon_service.summ
        for addon_service in addon_service_transaction:
            summ_on_page += addon_service.summ
    addon_service_transaction = paginator.get_page_items()
    rec_count = len(addon_service_transaction)+1
    return {
            'addon_service_transaction':addon_service_transaction,
            'paginator': paginator,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }

@render_to('accounts/traffic_transaction.html')
@login_required
def traffic_transaction(request):
    from lib.paginator import SimplePaginator
    is_range, addon_query = addon_queryset(request, 'traffic_transaction', 'created')
    #print addon_query
    qs = TrafficTransaction.objects.filter(account=request.user.account, \
                                           **addon_query).order_by('-created')
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    traffic_transaction = paginator.get_page_items()
    if is_range:
        for ttr in qs:
            summ += ttr.summ
        for ttr in traffic_transaction:
            summ_on_page += ttr.summ
    rec_count = len(traffic_transaction)+1
    
    return {
            'traffic_transaction':traffic_transaction,
            'paginator': paginator,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }

@render_to('accounts/one_time_history.html')
@login_required
def one_time_history(request):
    from lib.paginator import SimplePaginator
    is_range, addon_query = addon_queryset(request, 'one_time_history')
    qs = OneTimeServiceHistory.objects.filter(account=request.user.account, **addon_query).order_by('-created')
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    one_time_history = paginator.get_page_items()
    if is_range:
        for one_time in qs:
            summ += one_time.summ
        for one_time in one_time_history:
            summ_on_page += one_time.summ
    rec_count = len(one_time_history)+1
    return {
            'one_time_history':one_time_history,
            'paginator': paginator,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }

@ajax_request
@login_required
def news_delete(request):
    from django.utils.translation import ugettext as _
    message = _(u'Невозможно удалить новость, попробуйте позже')
    if request.method == 'POST':
        from billservice.models import AccountViewedNews
        news_id = request.POST.get('news_id', '')
        try:
            news = AccountViewedNews.objects.get(id = news_id, account = request.user.account)
        except:
            return {
                    'message':message,
                    }
        news.viewed = True
        news.save()
        return {
                'message':_(u'Новость успешно удалена'),
                }

@render_to('accounts/popup_userblock.html')
@login_required
def user_block(request):
    account = request.user.account
    tarif=account.get_account_tariff()
    account_status=account.status
    sp = SuspendedPeriod.objects.filter(account=account, end_date__isnull=True)
    if sp:
        sp=sp[0]
    return {
            'account_status':account_status,'tarif':tarif,'sp':sp,
            }
    

@login_required
@ajax_request
def userblock_action(request):
    
    from django.utils.translation import ugettext as _
    message = _(u'Невозможно заблокировать учётную записть')
    print 1
    if request.method == 'POST':
        account=request.user.account
        print 2
        if account.status==4:
            now=datetime.datetime.now()
            account.status=1
            account.save()
            result=True
            message=_(u'Аккаунт успешно активирован')
            print 3
        elif account.status==1:
            tarif=account.get_account_tariff()
            print 4
            if tarif.allow_userblock:
                #print 1
                if tarif.userblock_require_balance!=0 and tarif.userblock_require_balance>account.ballance+account.credit:
                    #print 1.5
                    result=False
                    message=_(u'Аккаунт не может быть заблокирован. </br>Минимальный остаток на балансе должен составлять %s.') % tarif.userblock_require_balance
                    print 5
                    return {
                            'message':message, 'result':result,
                            }
                #print 2
                account.status=4
                account.save()
                #print 3
                cursor = connection.cursor()

                cursor.execute(u"""INSERT INTO billservice_transaction(account_id, bill, type_id, approved, tarif_id, summ, created, promise)
                                  VALUES(%s, 'Списание средств за пользовательскую блокировку', 'USERBLOCK_PAYMENT', True, get_tarif(%s), (-1)*%s, now(), False)""" , (account.id, account.id, tarif.userblock_cost,))
                cursor.connection.commit()
                #print 4
                message=_(u'Аккаунт успешно заблокирован')
                result=True
                print 6
            else:
                message=_(u'Блокировка аккаунта запрещена')
                result=False
                print 7
        else:
            message=_(u'Блокировка аккаунта невозможна. Обратитесь в служюу поддержки провайдера.')
            result=False
            print 8
    return {
            'message':message, 'result':result,
            }
    print 9


from django.views.generic.detail import DetailView
from django.views.generic import TemplateView

class SelectPaymentView(TemplateView):
    template_name = 'billservice/payment_select.html'
    
    def get_context_data(self, **kwargs):
        from getpaid.forms import SelectPaymentMethodForm
        context = super(SelectPaymentView, self).get_context_data(**kwargs)
        context['payment_form'] = SelectPaymentMethodForm()
        return context
        