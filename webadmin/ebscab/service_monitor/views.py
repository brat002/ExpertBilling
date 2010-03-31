#-*- coding=UTF-8 -*-

"""
1001 - Запрос авторизации клиентом
1002 - Ответ с challenge строкой
1003 - Ответ на авторизацию с шифрованнымv challenge данынми абонента
1004 - Авторизация прошла успешно
1005 - неправильный пароль
1006 - несуществующий логин
1007 - Сервер занят
1008 - неизвестная сессия. Запросить клиентом повторную авторизацию
1009 - запрос баланса
1010 - ответ по балансу
1011 - запрос остатка на предоплаченный трафик
1012 - ответ на запрос по предоплаченному трафику
1013 - запрос остатка на предоплаченное время
1014 - ответ по остатку на предоплаченное время
1015 - logout
1016 - logout success
1017 - news request
1018 - response news for request user
1019 - no news are found for this user
"""

import os, sys
import jsonpickle
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db import connection
from django import template
from django.contrib.auth.decorators import login_required
from django.utils.encoding import iri_to_uri

from billservice.models import Account, AccountTarif, NetFlowStream, Transaction, Card, TransactionType, TrafficLimit, Tariff, TPChangeRule, AddonService, AddonServiceTarif, AccountAddonService, PeriodicalServiceHistory, AddonServiceTransaction, OneTimeServiceHistory, TrafficTransaction, AccountPrepaysTrafic, PrepaidTraffic, News, AccountViewedNews
from billservice.forms import LoginForm, PasswordForm, CardForm, ChangeTariffForm, PromiseForm, StatististicForm
from billservice import authenticate, log_in, log_out  
from billservice.utility import is_login_user, settlement_period_info
from nas.models import TrafficClass

from lib.decorators import render_to

@render_to('service_monitor/service_data.html')
def service_data(request):
    
    user = request.user
    data = ''
    data_pack = ''
  
    if user.is_authenticated():
        
        code = request.GET.get('id', None)
                
        if code != None:            
            #request of user balance
            if code == u'1009':                                
                value = '%.2f' % (user.ballance - user.credit)                
                data_pack = {'status_code' : '1010'}
                data_pack['value'] = value             
            
            #request of prepayment traffic    
            if code == u'1011':
                value = 'prepayment traffic'
                data_pack = {'status_code' : '1012'}
            
            #request of prepayment time
            if code == u'1013':
                value = 'prepayment time'
                data_pack = {'status_code' : '1014'}
                data_pack['value'] = value
                
            #request of limit rest
            if code == u'1015':
                value = 'limit_rest'
                data_pack = {'status_code' :'1016'}
                data_pack['value'] = value   
                
            #request of news
            if code == u'1017':                
                try:                                                   
                    news = (AccountViewedNews.objects.filter(account=user, viewed=False, news__agent=True).order_by('-id')[:1])
                    news_id = news[0].id
                    news = AccountViewedNews.objects.get(id = news_id)
                    news.viewed = True
                    news.save()
                    value = news.news.body.encode('utf-8')
                except:
                    value=""
                                           
                data_pack = {'status_code' :'1018'}                    
                data_pack['value'] = value
                
            #request blocked balance
            if code == u'1019':
                value = user.balance_blocked
                data_pack = {'status_code' : '1020'}
                data_pack['value'] = '%s' % value
                
            #request blocked limit
            if code == u'1021':
                value = user.disabled_by_limit
                data_pack = {'status_code' : '1022'}
                data_pack['value'] = '%s' % value
            
            #otherwise data_pack is empty
            
            #encode to JSON
            data = jsonpickle.encode(data_pack)    
            
    #user not authenticated
    else:
        data_pack = {'status_code' : '1008'}
        data = jsonpickle.encode(data_pack)
        
    response = { 'data' : data }
  
    return response
    
