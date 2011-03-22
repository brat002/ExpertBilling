# -*-coding: utf-8 -*-

from billservice.models import Account,SubAccount
from nas.models import Nas
from lib.decorators import render_to
from django.conf import settings
import commands
WWW_PREFIX='/media/statistics/'

RRDTOOL_PATH='/usr/bin/rrdtool'
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
def generate_graph(image_path, subaccount, interval):
    #rrd=unicode(u"""%s graph %s -a PNG -h 125 -t "График загрузки канала субаккаунтом %s за %s (байты)" --lazy -l 0 -v bytes/sec -s %s DEF:in=%s.rrd:in:AVERAGE  DEF:out=%s.rrd:out:AVERAGE  CDEF:out_neg=out,-1,/  CDEF:in_calc=in,1,/ AREA:in_calc#32CD32:Incoming   LINE1:in_calc#32CD32    AREA:out_neg#4169E1:Outgoing   LINE1:out_neg#4169E1  HRULE:0#000000 """ % (RRDTOOL_PATH, image_path, subaccount.username, interval[0], interval[1], RRDDB_PATH+'bandwidth_%s'%subaccount.id, RRDDB_PATH+'bandwidth_%s' % subaccount.id,)).encode('utf-8')
    rrd=unicode(u"""%s graph %s -a PNG -h 125 -w 500 -t "График загрузки канала субаккаунтом %s за %s (байты)" --lazy -l 0 -v Байты/сек -s %s DEF:in=%s.rrd:in:AVERAGE  DEF:out=%s.rrd:out:AVERAGE  CDEF:out_neg=out,1,/  CDEF:in_calc=in,1,/ LINE2:in_calc#4169E1 AREA:in_calc#4169E1AA:Incomming   GPRINT:in_calc:MAX:"Max in\\:%%5.1lf%%s" GPRINT:in_calc:AVERAGE:"Avg\\: %%5.1lf %%S" GPRINT:in_calc:LAST:" Current\\: %%5.1lf %%S\\n" LINE2:out_neg#FA0502  AREA:out_neg#FA0502AA:Outgoing GPRINT:out_neg:MAX:"Max out\\:%%4.1lf%%s" GPRINT:out_neg:AVERAGE:"Avg\\: %%5.1lf %%S" GPRINT:out_neg:LAST:" Current\\: %%5.1lf %%S\\n" """ % (RRDTOOL_PATH, image_path, subaccount.username, interval[0], interval[1], RRDDB_PATH+'bandwidth_%s'%subaccount.id, RRDDB_PATH+'bandwidth_%s' % subaccount.id,)).encode('utf-8')
    #print rrd
    status, output = commands.getstatusoutput(rrd)
    return status, rrd, output

#@render_to("statistics/account_stat.html")
def generate_packets_graph(image_path, subaccount, interval):
    rrd=unicode(u"""%s graph %s -a PNG -h 125 -w 500 -t "График загрузки канала субаккаунтом %s за %s (пакеты)" --lazy -l 0 -v Пакеты/сек -s %s DEF:packets_in=%s.rrd:packets_in:AVERAGE  DEF:packets_out=%s.rrd:packets_out:AVERAGE  CDEF:out=packets_out,1,/  CDEF:in=packets_in,1,/ LINE2:in#4169E1 AREA:in#4169E1AA:Incomming   GPRINT:in:MAX:"Max in\\:%%5.1lf%%s" GPRINT:in:AVERAGE:"Avg\\: %%5.1lf %%S" GPRINT:in:LAST:" Current\\: %%5.1lf %%S\\n" LINE2:out#FA0502  AREA:out#FA0502AA:Outgoing GPRINT:out:MAX:"Max out\\:%%5.1lf%%s" GPRINT:out:AVERAGE:"Avg\\: %%5.1lf %%S" GPRINT:out:LAST:" Current\\: %%5.1lf %%S\\n"  """ % (RRDTOOL_PATH, image_path, subaccount.username, interval[0], interval[1], RRDDB_PATH+'bandwidth_%s'%subaccount.id, RRDDB_PATH+'bandwidth_%s' % subaccount.id,)).encode('utf-8')
    #print rrd
    status, output = commands.getstatusoutput(rrd)
    return status, rrd, output

#@render_to("statistics/account_stat.html")
def generate_nas_graph(image_path, nas, interval):
    #rrd=unicode(u"""%s graph %s -a PNG -h 125 -t "График загрузки канала субаккаунтом %s за %s (байты)" --lazy -l 0 -v bytes/sec -s %s DEF:in=%s.rrd:in:AVERAGE  DEF:out=%s.rrd:out:AVERAGE  CDEF:out_neg=out,-1,/  CDEF:in_calc=in,1,/ AREA:in_calc#32CD32:Incoming   LINE1:in_calc#32CD32    AREA:out_neg#4169E1:Outgoing   LINE1:out_neg#4169E1  HRULE:0#000000 """ % (RRDTOOL_PATH, image_path, subaccount.username, interval[0], interval[1], RRDDB_PATH+'bandwidth_%s'%subaccount.id, RRDDB_PATH+'bandwidth_%s' % subaccount.id,)).encode('utf-8')
    rrd=unicode(u"""%s graph %s -a PNG -h 125 -w 500 -t "График загрузки канала на %s за %s (байты)" --lazy -l 0 -v Байты/сек -s %s DEF:in=%s.rrd:in:AVERAGE  DEF:out=%s.rrd:out:AVERAGE  CDEF:out_neg=out,1,/  CDEF:in_calc=in,1,/ LINE2:in_calc#4169E1 AREA:in_calc#4169E1AA:Incomming   GPRINT:in_calc:MAX:"Max in\\:%%5.1lf%%s" GPRINT:in_calc:AVERAGE:"Avg\\: %%5.1lf %%S" GPRINT:in_calc:LAST:" Current\\: %%5.1lf %%S\\n" LINE2:out_neg#FA0502  AREA:out_neg#FA0502AA:Outgoing GPRINT:out_neg:MAX:"Max out\\:%%4.1lf%%s" GPRINT:out_neg:AVERAGE:"Avg\\: %%5.1lf %%S" GPRINT:out_neg:LAST:" Current\\: %%5.1lf %%S\\n" """ % (RRDTOOL_PATH, image_path, nas.name, interval[0], interval[1], RRDDB_PATH+'bandwidth_nas_%s'%nas.id, RRDDB_PATH+'bandwidth_nas_%s' % nas.id,)).encode('utf-8')
    #print rrd
    status, output = commands.getstatusoutput(rrd)
    return status, rrd, output

#@render_to("statistics/account_stat.html")
def generate_nas_packets_graph(image_path, nas, interval):
    rrd=unicode(u"""%s graph %s -a PNG -h 125 -w 500 -t "График загрузки канала на %s за %s (пакеты)" --lazy -l 0 -v Пакеты/сек -s %s DEF:packets_in=%s.rrd:packets_in:AVERAGE  DEF:packets_out=%s.rrd:packets_out:AVERAGE  CDEF:out=packets_out,1,/  CDEF:in=packets_in,1,/ LINE2:in#4169E1 AREA:in#4169E1AA:Incomming   GPRINT:in:MAX:"Max in\\:%%5.1lf%%s" GPRINT:in:AVERAGE:"Avg\\: %%5.1lf %%S" GPRINT:in:LAST:" Current\\: %%5.1lf %%S\\n" LINE2:out#FA0502  AREA:out#FA0502AA:Outgoing GPRINT:out:MAX:"Max out\\:%%5.1lf%%s" GPRINT:out:AVERAGE:"Avg\\: %%5.1lf %%S" GPRINT:out:LAST:" Current\\: %%5.1lf %%S\\n"  """ % (RRDTOOL_PATH, image_path, nas.name, interval[0], interval[1], RRDDB_PATH+'bandwidth_nas_%s'%nas.id, RRDDB_PATH+'bandwidth_nas_%s' % nas.id,)).encode('utf-8')
    #print rrd
    status, output = commands.getstatusoutput(rrd)
    return status, rrd, output

#@render_to("statistics/account_stat.html")
def generate_nas_sessions_graph(image_path, nas, interval):
    rrd=unicode(u"""%s graph %s -a PNG -h 125 -w 500 -t "График количества VPN сессий на %s за %s" --lazy -l 0 -v Сессий -s %s DEF:sessions=%s.rrd:sessions:AVERAGE LINE2:sessions#4169E1 AREA:sessions#4169E1AA:Sessions   GPRINT:sessions:MAX:"Max in\\:%%5.1lf%%s" GPRINT:sessions:AVERAGE:"Avg\\: %%5.1lf %%S" GPRINT:sessions:LAST:" Current\\: %%5.1lf %%S\\n" """ % (RRDTOOL_PATH, image_path, nas.name, interval[0], interval[1],  RRDDB_PATH+'bandwidth_nas_sessions_%s' % nas.id,)).encode('utf-8')
    #print rrd
    status, output = commands.getstatusoutput(rrd)
    return status, rrd, output
    
def get_bytes_name(user,interval):
    return "bytes_%s%s.png" % (user,interval)

def get_packets_name(user,interval):
    return "packets_%s%s.png" % (user,interval)

def get_nas_bytes_name(nas,interval):
    return "nas_bytes_%s%s.png" % (nas,interval)

def get_nas_packets_name(nas,interval):
    return "nas_packets_%s%s.png" % (nas,interval)
    
def get_nas_sessions_name(nas,interval):
    return "nas_sessions_%s%s.png" % (nas,interval)
    
    
def account_stat(request):
    return {"":''}

@render_to("statistics/subaccount_stat.html")
def subaccounts_stat(request):
    #DAY
    account_id = request.GET.get('account_id')
    account = Account.objects.get(id=account_id)
    filenames=[]
    for subaccount in SubAccount.objects.filter(account=account,username__isnull=False):
        for interval in GRAPH_INTERVALS:
            
            bytes_filename=get_bytes_name(subaccount.id,interval[1])
            packets_filename=get_packets_name(subaccount.id,interval[1])
            a,b,c=generate_graph(IMAGE_PATH+'subaccounts/'+bytes_filename,  subaccount, interval)
            a,b,c=generate_packets_graph(IMAGE_PATH+'subaccounts/'+packets_filename, subaccount, interval)
            filenames.append((interval[0], bytes_filename, packets_filename))
#            print a,b,c
    return {'account':account,"filenames":filenames, 'c':'%s%s%s' % (a,b,c)}


@render_to("statistics/subaccount_stat.html")
def overall_stat(request):
    filenames=[]
    for subaccount in SubAccount.objects.all():
        for interval in GRAPH_INTERVALS:
            
            bytes_filename=get_bytes_name(subaccount.id,interval[1])
            packets_filename=get_packets_name(subaccount.id,interval[1])
            a,b,c=generate_graph(IMAGE_PATH+'subaccounts/'+bytes_filename,  subaccount, interval)
            a,b,c=generate_packets_graph(IMAGE_PATH+'subaccounts/'+packets_filename, subaccount, interval)
            filenames.append((interval[0], bytes_filename, packets_filename))
#            print a,b,c
    return {"filenames":filenames, 'c':'%s%s%s' % (a,b,c)}

@render_to("statistics/nas_stat.html")
def nasses_stat(request):
    filenames=[]
    for nas in Nas.objects.all():
        for interval in GRAPH_INTERVALS:
            
            bytes_filename=get_nas_bytes_name(nas.id,interval[1])
            packets_filename=get_nas_packets_name(nas.id,interval[1])
            sessions_filename=get_nas_sessions_name(nas.id,interval[1])            
            a,b,c=generate_nas_graph(IMAGE_PATH+'nasses/'+bytes_filename,  nas, interval)
            a,b,c=generate_nas_packets_graph(IMAGE_PATH+'nasses/'+packets_filename, nas, interval)
            a,b,c=generate_nas_sessions_graph(IMAGE_PATH+'nasses/'+sessions_filename, nas, interval)

            filenames.append((interval[0], bytes_filename, packets_filename, sessions_filename))
#            print a,b,c
    return {"filenames":filenames, 'c':'%s%s%s' % (a,b,c)}

@render_to("statistics/nas_stat.html")
def nas_stat(request):
    filenames=[]
    nas_id=request.GET.get('nas_id')
    
    nas = Nas.objects.get(id=nas_id)

    for interval in GRAPH_INTERVALS:
        bytes_filename=get_nas_bytes_name(nas.id,interval[1])
        packets_filename=get_nas_packets_name(nas.id,interval[1])
        sessions_filename=get_nas_sessions_name(nas.id,interval[1])            
        a,b,c=generate_nas_graph(IMAGE_PATH+'nasses/'+bytes_filename,  nas, interval)
        a,b,c=generate_nas_packets_graph(IMAGE_PATH+'nasses/'+packets_filename, nas, interval)
        a,b,c=generate_nas_sessions_graph(IMAGE_PATH+'nasses/'+sessions_filename, nas, interval)

        filenames.append((interval[0], bytes_filename, packets_filename, sessions_filename))
#            print a,b,c
    return {"filenames":filenames, 'c':'%s%s%s' % (a,b,c)}
