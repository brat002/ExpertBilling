#-*-coding:utf-8 -*-
from billservice.models import BalanceHistory
from django.shortcuts import render_to_response
import datetime
from django.contrib.auth.decorators import login_required
from billservice.forms import ReportForm
from billservice import authenticate, log_in
{
'sessionsonline':[{'name':u'Сессии рользователей', 'tabs':['accountsTab', 'nassesTab']}],
'sessionsdynamic':[{'name':u'Динамика сессий', 'tabs':['accountsTab', 'nassesTab']}],
'trafficclasses': [{'name':u'Потребление трафика по классам трафика', 'tabs':['classesTab', 'nassesTab']}],
'trafficgroups': [{'name':u'Потребление трафика по группам трафика', 'tabs':['accountTab', 'groupsTab', 'nassesTab']}],
'selectedaccountstraffic': [{'name':u'Потребление трафика выбранными аккаунтами', 'tabs':['accountTab', 'groupsTab']}],
'accountstraffic': [{'name':u'Потребление трафика аккаунтами(общее)', 'tabs':['accountTab', 'groupsTab']}],
'nassestraffic': [{'name':u'Потребление трафика по серверам доступа', 'tabs':['nassesTab', 'groupsTab']}],
'tariffstraffic': [{'name':u'Распределение трафика по тарифам', 'tabs':['tariffsTab']}],
'distrtrafficclasses': [{'name':u'Распределение трафика по классам трафика', 'tabs':['classesTab', 'nassesTab']}],
'distrtrafficgroups': [{'name':u'Распределение трафика по группам трафика', 'tabs':['accountTab', 'groupsTab', 'nassesTab']}],
'distraccountstraffic': [{'name':u'Распределение трафика по аккаунтам ', 'tabs':['accountTab', 'groupsTab']}],
'distnassestraffic': [{'name':u'Распределение трафика по серверам доступа', 'tabs':['nassesTab', 'groupsTab']}],
'distraccountstoptraffic': [{'name':u'Распределение трафика по аккаунтам ', 'tabs':['accountTab', 'groupsTab']}],
'accountsincrease': [{'name':u'Динамика абонентской базы ', 'tabs':[]}],
'moneydynamic': [{'name':u'Динамика прибыли ', 'tabs':[]}],
'disttransactiontypes': [{'name':u'Распределение платежей/списаний по типам ', 'tabs':[]}],
'balancehistory': [{'name':u'Динамика изменения баланса ', 'tabs':['accountTab']}],
}

"""
Сессии:
1. Сессии онлайн(гант) с выбором:
   аккаунты
   сервера доступа
2. Открытие и закрытие сессий
    сервера доступа
    
Трафик:
1. Получено/передано байт с группировкой по часам/дням, выбором серверов доступа и/или аккаунтов и/или (групп или классов)
указываем по чему группировать байты : - выбор. кривая
   по классам
   серерам доступа
   аккаунтам
    отдельно галочка "Только тарифицированный трафик" - только billservice_groupstat без сервера доступа
    отдельно галочка Суммировать ВХ + Исх
Названия:
   распределение трафика по классам трафика(выбор классов, серверов доступа)
   распределение трафика по группам трафика(выбор групп, серверов доступа, аккаунтов)
   потребление трафика выбранными аккаунтами(выбор аккаунтов, групп)
   потребление трафика аккаунтами(выбор аккаунтов, групп)
   распределение трафика по серверам доступа(выбор серверов доступа, групп)
   потребление трафика на тарифах(выбор тарифов)

2. Объём потреблённого трафика с группировкой по часам/дням, выбором серверов доступа и/или аккаунтов и/или (групп или классов)
   по классам
   серерам доступа
   аккаунтам
   
    отдельно галочка "Только тарифицированный трафик" - только billservice_groupstat без сервера доступа
Названия:
   распределение трафика по классам(выбор классов, серверов доступа)
   распределение трафика по серверам доступа(выбор серверов доступа, групп)
   распределение трафика по аккаунтам(выбор аккаунтов, групп)
   ТОП N аккаунтов по трафику(выбор групп)
   
3. Прирост абонентской базы за период
4. Прибыль за период
5. АБонентов на тарифных планах за период
6. Распределение платежей по типам
7. История изменения баланса у аккаунта(-ов

"""
@login_required
def rainfall_pivot_chart_view(request):

    res = []
    total = []
    
    for i in xrange(100, 110):
        items = BalanceHistory.objects.filter(account__id=i, datetime__gte=datetime.datetime.now()-datetime.timedelta(days=7)).order_by("datetime")
        if not items: continue
        try:
            """
            protection against deleted accounts
            """
            res.append((items[0].account.username, [(x.datetime, x.balance) for x in items]))
        except:
            pass
        

    return render_to_response('chartit.html', { 'res':res})


def session_count_chart_view(request):
    
    print 1
    print request.POST
    if not request.user.is_authenticated():
        user = authenticate(username=request.POST.get('username'), \
                        password=request.POST.get('password'))
        print 2
        if user:
            print 3
            log_in(request, user)
        else:
            print 4
            return render_to_response('sessionschart.html', {'res':[]})
        
            
    from django.db import connection
    cur = connection.cursor()
    print 5
    form = ReportForm(request.POST)
    res = []
    started_sessions = []
    ended_sessions = []
    if form.is_valid():
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        
        td = end_date-start_date
        
        if td.days*86400+ td.seconds>5*86400:
            trunc = 'days'
        else:
            trunc = 'hours'
        cur.execute("select date_trunc(%s, date_start), count(*) FROM radius_activesession WHERE date_start between %s and %s GROUP BY date_trunc(%s, date_start) ORDER BY date_trunc(%s, date_start)  ASC", (trunc, start_date, end_date, trunc, trunc))
        started_sessions = cur.fetchall()
        cur.execute("select date_trunc(%s, date_end), count(*) FROM radius_activesession WHERE date_end between %s and %s GROUP BY date_trunc(%s, date_end) ORDER BY date_trunc(%s, date_end)  ASC", (trunc, start_date, end_date, trunc, trunc))
        ended_sessions = cur.fetchall()


    return render_to_response('sessionschart.html', {'started_sessions':started_sessions, 'ended_sessions':ended_sessions})

def traffic_volume_chart_view(request):
    

    if not request.user.is_authenticated():
        user = authenticate(username=request.POST.get('username'), \
                        password=request.POST.get('password'))

        if user:
            log_in(request, user)
        else:
            return render_to_response('trafficvolumechart.html', {'res':[]})
        
            
    from django.db import connection
    cur = connection.cursor()

    form = ReportForm(request.POST)
    res = []

    if form.is_valid():
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        accounts = form.cleaned_data.get("accounts")
        td = end_date-start_date
        
        if td.days*86400+ td.seconds>5*86400:
            trunc = 'days'
        else:
            trunc = 'hours'
        cur.execute("select date_trunc(%s, datetime) as dt, sum(bytes) FROM billservice_groupstat WHERE datetime between %s and %s GROUP by date_trunc(%s, datetime)  ORDER BY dt asc;", ( trunc, start_date, end_date, trunc))
        res = cur.fetchall()




    return render_to_response('trafficvolumechart.html', {'res':res, })


def groupstraffic_chart_view(request):
    
    print 1
    print request.POST
    if not request.user.is_authenticated():
        user = authenticate(username=request.POST.get('username'), \
                        password=request.POST.get('password'))
        print 2
        if user:
            print 3
            log_in(request, user)
        else:
            print 4
            return render_to_response('grouptrafficpiechart.html', {'res':[]})
        
            
    from django.db import connection
    cur = connection.cursor()
    print 5
    form = ReportForm(request.POST)
    res = []
    started_sessions = []
    ended_sessions = []
    if form.is_valid():
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        accounts = form.cleaned_data.get("accounts")
        print accounts
        
        #accounts
        #cur.execute("select (select username from billservice_account WHERE id=gst.account_id) as username,  sum(bytes)/(1024*1024) FROM billservice_groupstat as gst WHERE account_id in (%s) and datetime between %%s and %%s GROUP by account_id;" % ','.join(['%s' % x.id for x in accounts]), ( start_date, end_date))
        
        #max 5 accounts
        cur.execute("select (select username from billservice_account WHERE id=gst.account_id) as username,  sum(bytes)/(1024*1024) as bytes FROM billservice_groupstat as gst WHERE datetime between %s and %s GROUP by account_id ORDER BY bytes DESC LIMIT 10;", ( start_date, end_date))
        res = cur.fetchall()


    return render_to_response('grouptrafficpiechart.html', {'res':res,})



