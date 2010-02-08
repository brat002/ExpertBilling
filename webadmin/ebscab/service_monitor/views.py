#-*- coding=UTF-8 -*-

import os, sys
from django.conf import settings

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db import connection
from django import template
from django.contrib.auth.decorators import login_required

from billservice.models import Account, AccountTarif, NetFlowStream, Transaction, Card, TransactionType, TrafficLimit, Tariff, TPChangeRule, AddonService, AddonServiceTarif, AccountAddonService, PeriodicalServiceHistory, AddonServiceTransaction, OneTimeServiceHistory, TrafficTransaction, AccountPrepaysTrafic, PrepaidTraffic, News, AccountViewedNews

from billservice.forms import LoginForm, PasswordForm, CardForm, ChangeTariffForm, PromiseForm, StatististicForm
from billservice import authenticate, log_in, log_out  
from billservice.utility import is_login_user, settlement_period_info
from nas.models import TrafficClass


from lib.decorators import render_to

from django.utils.encoding import iri_to_uri

import jsonpickle

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
                news = AccountViewedNews.objects.filter(news__private=True, account=user, viewed=False).order_by('-id')[:1]
                value = news[0].news.body.encode('utf-8')
                data_pack = {'status_code' :'1018'}
                data_pack['value'] = value
                
            #otherwise data_pack is empty
            
            #encode to JSON
            data = jsonpickle.encode(data_pack)    
            
    #user not authenticated
    else:
        data_pack = {'status_code' : '1008'}
        data = jsonpickle.encode(data_pack)
        
    response = { 'data' : data }
  
    return response
    
