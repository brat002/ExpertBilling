#-*-coding:utf-8 -*-
from billservice.models import BalanceHistory
from django.shortcuts import render_to_response
import datetime
from django.contrib.auth.decorators import login_required
from ebsadmin.forms import ReportForm
from billservice import authenticate, log_in
from forms import chartdata

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

    from django.db import connection
    cur = connection.cursor()
    
    
    res = []
    started_sessions = []
    ended_sessions = []
    groups_str = ''
    accounts_str = ''
    nasses_str = ''
    print request.GET
    report = request.GET.get("report")
    if request.GET:
        form = ReportForm(request.GET)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
            end_date = form.cleaned_data.get("end_date")
            accounts = form.cleaned_data.get("accounts")
            tariffs = form.cleaned_data.get("tariffs")
            groups = form.cleaned_data.get("groups")
            report = form.cleaned_data.get("report")
            nasses = form.cleaned_data.get("nasses")
            #reporttype = form.cleaned_data.get("reporttype")
            grouping = form.cleaned_data.get("grouping")
            
            rep = chartdata.get(report)
            report_name = rep.get("name")
            yname = rep.get("yname")
            reporttype = rep.get("type", 'line')
            if accounts:
                accounts_str = " and account_id in (%s)" %  ','.join(['%s' % x for x in accounts])
            if groups:
                groups_str = "and group_id in (%s)" %  ','.join(['%s' % x.id for x in groups])
         
            if nasses:
                nasses_str = "and nas_id in (%s)" %  ','.join(['%s' % x.id for x in nasses])
            
            tariffs_str=''
            if tariffs:
                tariffs_str = "and get_tariff in (%s)" %  ','.join(['%s' % x.id for x in tariffs])
            
            print report
            if report=='distnassestraffic':
                print "distnassestraffic"
                cur.execute("""select (select name from nas_nas WHERE id=gst.nas_id) as nas,  sum(bytes_in+bytes_out)/(1024*1024) FROM billservice_globalstat as gst WHERE True %s %s and datetime between %%s and %%s GROUP by nas_id;""" \
                            % (nasses_str, groups_str), ( start_date, end_date))
                res = cur.fetchall()
                return render_to_response('ebsadmin/charts_pie.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})
            if report=='nassestraffic':

                cur.execute("""select (select name from nas_nas WHERE id=gst.nas_id) as nas,  date_trunc(%%s, gst.datetime) as dt, sum(bytes_in+bytes_out)/(1024*1024) FROM billservice_globalstat as gst WHERE True %s %s and gst.datetime between %%s and %%s GROUP by nas_id, date_trunc(%%s, gst.datetime) order by nas,dt;""" \
                            % (nasses_str, groups_str), (grouping, start_date, end_date, grouping))
                res = []
                subitems = []
                previtem = None
                for item in  cur.fetchall():
                    if item[0]==previtem or previtem==None :
                        subitems.append((item[1], item[2]))
                    else:
                        res.append((previtem, subitems))
                        subitems=[]
                        subitems.append((item[1], item[2]))
                    previtem = item[0]
                return render_to_response('ebsadmin/charts_multiline.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})
            
            if report=='distrtrafficgroups':
                cur.execute("""select (select name from billservice_group WHERE id=gst.group_id) as group,  sum(bytes)/(1024*1024) FROM billservice_groupstat as gst WHERE True %s %s and datetime between %%s and %%s GROUP by group_id;""" \
                            % (accounts_str, groups_str), ( start_date, end_date))
                res = cur.fetchall()
                return render_to_response('ebsadmin/charts_pie.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})
            
            if report=='tariffstraffic':
                cur.execute("""SELECT name,
                                    COALESCE((SELECT sum(bytes) FROM billservice_groupstat WHERE account_id in 
                                           (SELECT account_id FROM billservice_accounttarif WHERE tarif_id=t.id and datetime <%%s)
                                           and datetime between %%s and %%s  %s %s),0) as s 
                                           FROM billservice_tariff as t ;""" \
                            % (accounts_str, groups_str), (end_date,  start_date, end_date))
                res = cur.fetchall()
                items = []
                for name, value in res:
                    if value<>0:
                        items.append((name, value))
                return render_to_response('ebsadmin/charts_pie.html', {'rep': rep, 'res':items, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})
            
            

       
            if report=='disttransactiontypessumm':
                cur.execute("""select name, COALESCE((select sum(summ) from billservice_transaction WHERE type_id=tt.internal_name and created between %%s and %%s),0) as summ FROM billservice_transactiontype as tt WHERE  True and %s  COALESCE((select sum(summ) from billservice_transaction WHERE type_id=tt.internal_name and created between %%s and %%s),0)<>0;""" \
                            % (accounts_str, ), ( start_date, end_date,  start_date, end_date))
                res = cur.fetchall()
                return render_to_response('ebsadmin/charts_pie.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})
            if report=='disttransactiontypescount':
                cur.execute("""select name, COALESCE((select count(summ) from billservice_transaction WHERE type_id=tt.internal_name and created between %%s and %%s),0) as summ FROM billservice_transactiontype as tt WHERE  True and %s  COALESCE((select sum(summ) from billservice_transaction WHERE type_id=tt.internal_name and created between %%s and %%s),0)<>0;""" \
                            % (accounts_str, ), ( start_date, end_date,  start_date, end_date))
                res = cur.fetchall()
                return render_to_response('ebsadmin/charts_pie.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})
            
            if report=='distraccountstraffic':
                cur.execute("""select (select username from billservice_account WHERE id=gst.account_id) as username,  sum(bytes)/(1024*1024) FROM billservice_groupstat as gst WHERE True %s %s and datetime between %%s and %%s GROUP by account_id;""" \
                            % (accounts_str, groups_str), ( start_date, end_date))
                res = cur.fetchall()
                return render_to_response('ebsadmin/charts_pie.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})
            if report=='distraccountstoptraffic':
                cur.execute("""select (select username from billservice_account WHERE id=gst.account_id) as username,  sum(bytes)/(1024*1024) as b FROM billservice_groupstat as gst WHERE True %s and datetime between %%s and %%s GROUP by account_id ORDER BY b desc limit 10;""" \
                            % (groups_str,), ( start_date, end_date))
                res = cur.fetchall()
                return render_to_response('ebsadmin/charts_pie.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})
    
            if report=='balancehistory':
                cur.execute("""select (select username from billservice_account WHERE id=bh.account_id) as username, date_trunc(%%s, datetime) as dt, avg(balance)  FROM billservice_balancehistory as bh WHERE True %s and datetime between %%s and %%s GROUP BY account_id, date_trunc(%%s, datetime) ORDER BY account_id, dt asc;""" \
                            % (accounts_str,), (grouping, start_date, end_date, grouping))
                res = []
                subitems = []
                previtem = None
                for item in  cur.fetchall():
                    if item[0]==previtem or previtem==None :
                        subitems.append((item[1], item[2]))
                    else:
                        res.append((previtem, subitems))
                        subitems=[]
                        subitems.append((item[1], item[2]))
                    previtem = item[0]
                
                return render_to_response('ebsadmin/charts_multiline.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})
    
            if report=='accountstraffic':
                cur.execute("""select date_trunc(%%s, datetime) as dt,  sum(bytes)/(1024*1024) FROM billservice_groupstat as gst WHERE True %s %s and datetime between %%s and %%s GROUP by date_trunc(%%s, datetime) ORDER BY dt ASC;""" \
                            % (accounts_str, groups_str), ( grouping, start_date, end_date, grouping))
                res = cur.fetchall()
                return render_to_response('ebsadmin/charts_line.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})
            
            if report=='selectedaccountstraffic':
                cur.execute("""select (select username from billservice_account WHERE id=gst.account_id) as username, date_trunc(%%s, datetime) as dt,  sum(bytes)/(1024*1024) FROM billservice_groupstat as gst WHERE True %s %s and datetime between %%s and %%s GROUP by account_id, date_trunc(%%s, datetime) ORDER BY username, dt ASC;""" \
                            % (accounts_str, groups_str), ( grouping, start_date, end_date, grouping))
                res = []
                subitems = []
                previtem = None
                for item in  cur.fetchall():
                    if item[0]==previtem or previtem==None :
                        subitems.append((item[1], item[2]))
                    else:
                        res.append((previtem, subitems))
                        subitems=[]
                        subitems.append((item[1], item[2]))
                    previtem = item[0]
                return render_to_response('ebsadmin/charts_multiline.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form, 'report_name':report_name, 'reporttype':reporttype})


            if report=='accountsincrease':
                cur.execute(""" select date_trunc(%s, created),  (SELECT count(*) FROM billservice_account WHERE id<=acc.id and deleted is null)-(SELECT count(*) FROM billservice_account WHERE id<=acc.id and deleted is not null) FROM billservice_account as acc
                                WHERE created between %s and %s ORDER BY  created ASC;
                ;""" \
                            , (grouping,  start_date, end_date,))
                res = cur.fetchall()
    
                return render_to_response('ebsadmin/charts_line.html', {'rep': rep, 'res':res, 'yname': yname, 'form': form,  'report_name':report_name, 'reporttype':reporttype})
            
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
                    
    
                return render_to_response('ebsadmin/charts_onlinesession.html', {'rep': rep, 'res':data, 'yname': yname, "len":100+int(len(data)/5)+len(data)*40, 'report_name':report_name, 'reporttype':reporttype, 'form': form})
                #динамика прибыли+qiwi+webmoney  select tt.name,  (SELECT sum(summ*(-1)) FROM billservice_transaction WHERE type_id=tt.internal_name) FROM billservice_transactiontype as tt
            else:
                print form._errors
                pass

    rep = chartdata.get(report)
    form = ReportForm({'report': report})
    return render_to_response('ebsadmin/charts.html', {'rep': rep,  'res':res, 'form': form})
        


