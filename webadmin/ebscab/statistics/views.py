# -*-coding: utf-8 -*-

from lib.decorators import render_to
from django.conf import settings
import commands
from hashlib import md5
import time
WWW_PREFIX='/media/statistics/'

RRD_PATH='/usr/bin/rrdtool'
RRDDB_PATH='/opt/ebs/stats/'
GRAPH_PATH='/opt/ebs/web/ebscab/media/'
IMAGE_PATH=settings.MEDIA_ROOT+'/statistics/'
GRAPH_INTERVALS=((u'Сутки','-1day'),
                 (u'Неделя','-1week'),
                 (u'Месяц','-1month'),
                 (u'Год','-1year'),
                 )
"""
Переделать генерацию в соответствии со статьёй
http://martybugs.net/linux/rrdtool/traffic.cgi
"""
#@render_to("statistics/account_stat.html")
def generate_graph(image_path, rrd_path, username, interval):
    rrd=unicode(u"""%s graph %s -a PNG -h 125 -t "График загрузки канала пользователем %s" --lazy -l 0 -v bytes/sec -s %s DEF:in=%s.rrd:in:AVERAGE  DEF:out=%s.rrd:out:AVERAGE  CDEF:out_neg=out,-1,/  CDEF:in_calc=in,1,/ AREA:in_calc#32CD32:Incoming   LINE1:in_calc#32CD32    AREA:out_neg#4169E1:Outgoing   LINE1:out_neg#4169E1  HRULE:0#000000 """ % (RRD_PATH, image_path, user, interval, RRDDB_PATH+'bandwidth_'+user, RRDDB_PATH+'bandwidth_'+user,)).encode('utf-8')
    #print rrd
    status, output = commands.getstatusoutput(rrd)
    return status, rrd
    
def get_name(user,interval):
    return md5(user+interval).hexdigest()+'.png'
    
    
def account_stat(request):
    return {"":''}

@render_to("statistics/subaccount_stat.html")
def subaccount_stat(request):
    #DAY
    subaccount = request.GET.get('subaccount')
    filenames=[]
    for interval in GRAPH_INTERVALS:
        filename=get_name(subaccount,interval[1])
        generate_graph(IMAGE_PATH+'subaccounts/'+filename, subaccount, interval[1])
        filenames.append(interval[0], filename)
    return {"filenames":filenames}


@render_to("statistics/overall_stat.html")
def overall_stat(request):
    return {"":''}
