# -*-coding: utf-8 -*-

from lib.decorators import render_to
import commands
import uuid
import time
SUBACCOUNT_BASE_PATH_DAY='/media/statistics/subaccount/%_day.png'
SUBACCOUNT_BASE_PATH_MONTH='/media/statistics/subaccount/%_month.png'
SUBACCOUNT_BASE_PATH_YEAR='/media/statistics/subaccount/%_year.png'
RRD_PATH='rrdtool'
RRDDB_PATH='/opt/ebs/rrd_data/'
GRAPH_PATH='/home/brat002/trunk/webadmin/ebscab/media/'


"""
Переделать генерацию в соответствии со статьёй
http://martybugs.net/linux/rrdtool/traffic.cgi
"""
@render_to("statistics/account_stat.html")
def generate_graph(path, user, start_date, end_date):
    rrd=u"""%s graph %s -a PNG -h 125 -t "График загрузки канала пользователем %s" --lazy -l 0 -v bytes/sec --start %s --end %s 'DEF:in=%s.rrd:in:AVERAGE' 'DEF:out=%s.rrd:out:AVERAGE'         "CDEF:out_neg=out,-1,*","AREA:in#32CD32:Incoming", "LINE1:in#336600",    "GPRINT:in:MAX:  Max\\: %5.1lf %%s","GPRINT:in:AVERAGE: Avg\\: %5.1lf %S","GPRINT:in:LAST: Current\\: %5.1lf %Sbytes/sec\\n",        "AREA:out_neg#4169E1:Outgoing",        "LINE1:out_neg#0033CC",        "GPRINT:out:MAX:  Max\\: %5.1lf %S",        "GPRINT:out:AVERAGE: Avg\\: %5.1lf %S",    "GPRINT:out:LAST: Current\\: %5.1lf %Sbytes/sec", "HRULE:0#000000" """ % (RRD_PATH, path, user, start_date, end_date, RRDDB_PATH+'bandwidth_'+user, RRDDB_PATH+'bandwidth_'+user,)
    print rrd
    status, output = commands.getstatusoutput(rrd)
    
    
    
def account_stat(request):
    return {"":''}

@render_to("statistics/subaccount_stat.html")
def subaccount_stat(request):
    #DAY
    subaccount = request.GET.get('subaccount')
    day_path=str(uuid.uuid1())
    time_end=int(time.time())
    time_start=int(time_end-86400)
    generate_graph(GRAPH_PATH+day_path+'.png', subaccount, time_start, time_end)
    day_rrd=day_path+'.png'
    #MONTH
    month_path=str(uuid.uuid1())
    time_start=int(time_end-86400*30)
    generate_graph(GRAPH_PATH+month_path+'.png', subaccount, time_start, time_end)
    month_rrd=month_path+'.png'
    #YEAR
    year_path=str(uuid.uuid1())
    time_start=int(time_end-86400*30*365)
    generate_graph(GRAPH_PATH+year_path+'.png', subaccount, time_start, time_end)
    year_rrd=year_path+'.png'
    
    return {"day":day_rrd, 'month':month_rrd, 'year':year_rrd}


@render_to("statistics/overall_stat.html")
def overall_stat(request):
    return {"":''}
