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
    rrd=u"""%s graph %s -a PNG -h 125 -v "Bandwidth data %s" --start %s --end %s 'DEF:in=%s.rrd:in:AVERAGE' 'DEF:out=%s.rrd:out:AVERAGE' 'CDEF:kbin=in,3,*,1024,/' 'CDEF:kbout=out,3,*,1024,/' 'AREA:in#1ED103:In' 'AREA:out#5AA5DA:Out' 'GPRINT:kbin:L:Last value In\: %%3.2lf kb/s' 'GPRINT:kbout:LAST:Last value Out\: %%3.2lfk\j'""" % (RRD_PATH, path, user, start_date, end_date, RRDDB_PATH+'bandwidth_'+user, RRDDB_PATH+'bandwidth_'+user,)
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
