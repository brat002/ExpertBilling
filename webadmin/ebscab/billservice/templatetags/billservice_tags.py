# -*- coding:utf-8 -*-
from django import template
import datetime
from django.db import connection
from billservice.models import Transaction, TransactionType, AccountPrepaysTrafic, AccountAddonService
register = template.Library()

@register.inclusion_tag('accounts/tags/writen_of_time.html')
def writen_of_time(session, user):
    type = TransactionType.objects.get(internal_name='TIME_ACCESS')
    if session.date_end:
        transactions = Transaction.objects.filter(account=user, created__gte=session.date_start, created__lte=session.date_end, type=type.internal_name)
    else:
        transactions = Transaction.objects.filter(account=user, created__gte=session.date_start, type=type.internal_name)
    sum=0
    for transaction in transactions:
        sum += transaction.summ
    return {'sum':sum}

@register.inclusion_tag('accounts/tags/writen_of_traffic.html')
def writen_of_traffic(session, user):
    type = TransactionType.objects.get(internal_name='NETFLOW_BILL')
    if session.date_end:
        transactions = Transaction.objects.filter(account=user, created__gte=session.date_start, created__lte=session.date_end, type=type.internal_name)
    else:
        transactions = Transaction.objects.filter(account=user, created__gte=session.date_start, type=type.internal_name)
    sum=0
    for transaction in transactions:
        sum += transaction.summ
    return {'sum':sum}

@register.inclusion_tag('accounts/tags/traffic_format.html')    
def traffic_format(value, second_value=None):
    try:
        if second_value != None:
            a=float(value) + float(second_value)
        else:
            a=float(value)
        #res = a/1024
        if a>1024 and a<(1024*1024):
            return {
                    'size': u"%.5s KB" % unicode(a/(1024))
                    }
        elif a>=(1024*1024) and a<=(1024*1024*1024):
            return {
                    'size': u"%.5s МB" % unicode(a/(1024*1024))
                    }
        elif a>(1024*1024*1024):
            return {
                    'size': u"%.5s GB" % unicode(a/(1024*1024*1024))
                    }
        elif a<1024:
            return {
                    'size': u"%s B" % unicode(int(a))
                    } 
    except Exception, e:
        print e
        
@register.inclusion_tag('accounts/tags/traffic_size.html')
def traffic_size(traffic, account_tarif):
    try:
        size = AccountPrepaysTrafic.objects.get(prepaid_traffic=traffic, account_tarif=account_tarif)
    except:
        size = None
    return {
            'size':size,
            }
    
    
@register.inclusion_tag('accounts/tags/time_format.html')
def time_format(s):
    try:
        m,s=divmod(s,60)
        h,m=divmod(m,60)
        if h==0 and m==0:
            return {
                    'time':u"%sс" % s,
                    }
        elif h==0 and m!=0:
            return {
                    'time':u"%sм %sс" % (m,s,),
                    }
        else:
            return {
                     'time': u"%sч %sм %sс" % (h,m,s),
                   }
    except:
        return {
                'time': u"0с",
                }
        
@register.inclusion_tag('accounts/tags/traffic_limit_row.html')
def traffic_limit_row(trafficlimit, user, iter_nom, last=False):
    settlement_period = trafficlimit.settlement_period
    cursor = connection.cursor()
    if settlement_period.autostart==True:
        cursor.execute("""SELECT datetime FROM billservice_accounttarif WHERE account_id=%s and datetime<now() ORDER BY datetime DESC LIMIT 1""" % (user.id)) 
        sp_start = cursor.fetchone()
        sp_start = sp_start[0]
    else:
        sp_start = settlement_period.time_start
    from billservice.utility import settlement_period_info
    settlement_period_start, settlement_period_end, delta = settlement_period_info(time_start=sp_start, repeat_after=settlement_period.length_in, repeat_after_seconds=settlement_period.length)
    #если нужно считать количество трафика за последнеие N секунд, а не за рачётный период, то переопределяем значения
    if trafficlimit.mode==True:
        now=datetime.datetime.now()
        settlement_period_start=now-datetime.timedelta(seconds=delta)
        settlement_period_end=now
    
    cursor.execute ("""SELECT sum(bytes) as size FROM billservice_groupstat
                        WHERE group_id=%s and account_id=%s and datetime>%s and datetime<%s 
                        """, (trafficlimit.group_id, user.id, settlement_period_start,  settlement_period_end))
    summ = cursor.fetchone()
    try:
        summ = summ[0]/(1024*1024)
    except:
        summ = 0 
    try:
        stay = trafficlimit.size/(1024*1024)
    except:
        stay = 0
    return {
            'trafficlimit': trafficlimit,
            'settlement_period_start': settlement_period_start,
            'settlement_period_end': settlement_period_end,
            'summ':summ,
            'stay':stay,
            'iter_nom':iter_nom,
            'last':last,
            }
    
    
@register.filter(name='coll_bg')
def coll_bg(value):
    row_class = ''
    if value%2 == 0:
        row_class = u'with_bg'
    return row_class

@register.filter(name='sevice_activation')
def sevice_activation(value, user=None):
    if AccountAddonService.objects.filter(id=value.id, account=user, deactivated__isnull=False).count() == 0:
        return '<a href="/service/del/%s/">Отключить</a>' %value.id
    else:
        return '&nbsp;'
    
    
    
