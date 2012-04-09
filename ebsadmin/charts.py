#-*-coding:utf-8 -*-
from billservice.models import BalanceHistory
from django.shortcuts import render_to_response
import datetime
from django.contrib.auth.decorators import login_required
from ebsadmin.forms import ReportForm
from billservice import authenticate, log_in
chartdata = {
'sessionsonline':{'name':u'Сессии рользователей', 'tabs':['accountsTab', 'nassesTab']},
'sessionsdynamic':{'name':u'Динамика сессий', 'tabs':['accountsTab', 'nassesTab']},
'trafficclasses': {'name':u'Потребление трафика по классам трафика', 'tabs':['classesTab', 'nassesTab']},
'trafficgroups': {'name':u'Потребление трафика по группам трафика', 'tabs':['accountsTab', 'groupsTab', 'nassesTab']},
'selectedaccountstraffic': {'name':u'Потребление трафика выбранными аккаунтами', 'tabs':['accountsTab', 'groupsTab']},
'accountstraffic': {'name':u'Потребление трафика аккаунтами(общее)', 'tabs':['accountsTab', 'groupsTab']},
'nassestraffic': {'name':u'Потребление трафика по серверам доступа', 'tabs':['nassesTab', 'groupsTab']},
'tariffstraffic': {'name':u'Распределение трафика по тарифам', 'tabs':['tariffsTab']},
'distrtrafficclasses': {'name':u'Распределение трафика по классам трафика', 'tabs':['classesTab', 'nassesTab']},
'distrtrafficgroups': {'name':u'Распределение трафика по группам трафика', 'tabs':['accountsTab', 'groupsTab', 'nassesTab']},
'distraccountstraffic': {'name':u'Распределение трафика по аккаунтам ', 'tabs':['accountsTab', 'groupsTab']},
'distnassestraffic': {'name':u'Распределение трафика по серверам доступа', 'tabs':['nassesTab', 'groupsTab']},
'distraccountstoptraffic': {'name':u'ТОП 10 по потреблению трафика ', 'tabs':[ 'groupsTab']},
'accountsincrease': {'name':u'Динамика абонентской базы ', 'tabs':[]},
'moneydynamic': {'name':u'Динамика прибыли ', 'tabs':[]},
'disttransactiontypes': {'name':u'Распределение платежей/списаний по типам ', 'tabs':[]},
'balancehistory': {'name':u'Динамика изменения баланса ', 'tabs':['accountsTab']},
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

def charts(request):
    if not request.user.is_authenticated():
        user = authenticate(username=request.POST.get('username'), \
                        password=request.POST.get('password'))

        if user:

            log_in(request, user)
        else:

            return render_to_response('sessionschart.html', {'res':[]})
    from django.db import connection
    cur = connection.cursor()
    
    form = ReportForm(request.POST)
    res = []
    started_sessions = []
    ended_sessions = []
    groups_str = ''
    accounts_str = ''
    nasses_str = ''
    if form.is_valid():
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        accounts = form.cleaned_data.get("accounts")
        groups = form.cleaned_data.get("groups")
        report = form.cleaned_data.get("report")
        nasses = form.cleaned_data.get("nasses")
        reporttype = form.cleaned_data.get("reporttype")
        grouping = form.cleaned_data.get("grouping")
        
        rep = chartdata.get(report)
        report_name = rep.get("name")
        if accounts:
            accounts_str = " and account_id in (%s)" %  ','.join(['%s' % x.id for x in accounts])
        if groups:
            groups_str = "and group_id in (%s)" %  ','.join(['%s' % x.id for x in groups])
     
        if nasses:
            nasses_str = "and nas_id in (%s)" %  ','.join(['%s' % x.id for x in nasses])
        
        if report=='distnassestraffic':
            cur.execute("""select (select name from nas_nas WHERE id=gst.nas_id) as nas,  sum(bytes_in+bytes_out)/(1024*1024) FROM billservice_globalstat as gst WHERE True %s %s and datetime between %%s and %%s GROUP by nas_id;""" \
                        % (nasses_str, groups_str), ( start_date, end_date))
            res = cur.fetchall()
            return render_to_response('grouptrafficpiechart.html', {'res':res, 'report_name':report_name, 'reporttype':reporttype})
        
        
        if report=='distrtrafficgroups':
            cur.execute("""select (select name from billservice_group WHERE id=gst.group_id) as group,  sum(bytes)/(1024*1024) FROM billservice_groupstat as gst WHERE True %s %s and datetime between %%s and %%s GROUP by group_id;""" \
                        % (accounts_str, groups_str), ( start_date, end_date))
            res = cur.fetchall()
            return render_to_response('grouptrafficpiechart.html', {'res':res, 'report_name':report_name, 'reporttype':reporttype})
        
        if report=='distraccountstraffic':
            cur.execute("""select (select username from billservice_account WHERE id=gst.account_id) as username,  sum(bytes)/(1024*1024) FROM billservice_groupstat as gst WHERE True %s %s and datetime between %%s and %%s GROUP by account_id;""" \
                        % (accounts_str, groups_str), ( start_date, end_date))
            res = cur.fetchall()
            return render_to_response('grouptrafficpiechart.html', {'res':res, 'report_name':report_name, 'reporttype':reporttype})
        if report=='distraccountstoptraffic':
            cur.execute("""select (select username from billservice_account WHERE id=gst.account_id) as username,  sum(bytes)/(1024*1024) as b FROM billservice_groupstat as gst WHERE True %s and datetime between %%s and %%s GROUP by account_id ORDER BY b desc limit 10;""" \
                        % (groups_str,), ( start_date, end_date))
            res = cur.fetchall()
            return render_to_response('grouptrafficpiechart.html', {'res':res, 'report_name':report_name, 'reporttype':reporttype})

        if report=='accountstraffic':
            cur.execute("""select date_trunc(%%s, datetime) as dt,  sum(bytes)/(1024*1024) FROM billservice_groupstat as gst WHERE True %s %s and datetime between %%s and %%s GROUP by date_trunc(%%s, datetime) ORDER BY dt ASC;""" \
                        % (accounts_str, groups_str), ( grouping, start_date, end_date, grouping))
            res = cur.fetchall()
            return render_to_response('trafficvolumechart.html', {'res':res, 'report_name':report_name, 'reporttype':reporttype})
        if report=='accountsincrease':
            cur.execute(""" select date_trunc(%s, created),  (SELECT count(*) FROM billservice_account WHERE id<=acc.id and deleted is null)-(SELECT count(*) FROM billservice_account WHERE id<=acc.id and deleted is not null) FROM billservice_account as acc
                            WHERE created between %s and %s ORDER BY  created ASC;
            ;""" \
                        , (grouping,  start_date, end_date,))
            res = cur.fetchall()

            return render_to_response('trafficvolumechart.html', {'res':res, 'report_name':report_name, 'reporttype':reporttype})
        
        if report=='sessionsonline':
            if nasses:
                nasses_str = "and nas_int_id in (%s)" %  ','.join(['%s' % x.id for x in nasses])
                        
            cur.execute("""select (select username from billservice_account WHERE id=rst.account_id) as username,  case when date_start<%%s then %%s else date_start end as date_start, case when date_end>%%s then %%s else date_end end as date_end FROM radius_activesession as rst WHERE True %s %s and ( (date_start between %%s and %%s) and ((date_end between %%s and %%s) or date_end is Null))  order by date_start, date_end;;""" \
                        % (nasses_str, accounts_str), ( start_date, start_date, end_date, end_date,  start_date, end_date, start_date, end_date))
            res = cur.fetchall()
            
            data = {}
            for username, date_start, date_end in res:
                if not username in data:
                    data[username]=[]
                #if date_start and date_end:
                if not username: continue
                if date_end is None:
                    date_end = end_date
                data[username].append((date_start, date_end))
                

            return render_to_response('onlinesessionschart.html', {'res':data, "len":100+int(len(data)/5)+len(data)*40, 'report_name':report_name, 'reporttype':reporttype})
        #динамика прибыли+qiwi+webmoney  select tt.name,  (SELECT sum(summ*(-1)) FROM billservice_transaction WHERE type_id=tt.internal_name) FROM billservice_transactiontype as tt
    else:
        #print form._errors
        pass
    return render_to_response('chartit.html', { 'res':res})
        


