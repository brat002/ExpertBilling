# -*- coding:utf-8 -*-
from django import template
from django.db import connection
from billservice.models import Transaction, TransactionType, AccountPrepaysTrafic
register = template.Library()

@register.inclusion_tag('accounts/tags/writen_off_time.html')
def writen_off_time(session, user):
    type = TransactionType.objects.get(internal_name='TIME_ACCESS')
    if session.date_end:
        transactions = Transaction.objects.filter(account=user, created__gte=session.date_start, created__lte=session.date_end, type=type.internal_name)
    else:
        transactions = Transaction.objects.filter(account=user, created__gte=session.date_start, type=type.internal_name)
    sum=0
    for transaction in transactions:
        sum += transaction.summ
    return {'sum':sum}

@register.inclusion_tag('accounts/tags/writen_off_trafic.html')
def writen_off_trafic(session, user):
    type = TransactionType.objects.get(internal_name='NETFLOW_BILL')
    if session.date_end:
        transactions = Transaction.objects.filter(account=user, created__gte=session.date_start, created__lte=session.date_end, type=type.internal_name)
    else:
        transactions = Transaction.objects.filter(account=user, created__gte=session.date_start, type=type.internal_name)
    sum=0
    for transaction in transactions:
        sum += transaction.summ
    return {'sum':sum}

@register.inclusion_tag('accounts/tags/trafic_format.html')    
def trafic_format(value):
    try:
        a=float(value)
        #res = a/1024
        if a>1024 and a<(1024*1000):
            return {
                    'size': u"%.5s KB" % unicode(a/(1024))
                    }
        elif a>=(1024*1000) and a<=(1024*1000*1000):
            return {
                    'size': u"%.5s МB" % unicode(a/(1024*1000))
                    }
        elif a>(1024*1000*1000):
            return {
                    'size': u"%.5s GB" % unicode(a/(1024*1000*1000))
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
        
@register.inclusion_tag('accounts/tags/traffic_limit_coll.html')
def traffic_limit_coll(trafficlimit, user):
    settlement_period = trafficlimit.settlement_period
    if settlement_period.autostart==True:
        from django.db import connection
        cursor = connection.cursor()
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
        settlement_period_end=datetime.datetime.now()
    
    cursor.execute = """SELECT sum(octets) FROM billservice_netflowstream AS bnf 
                        JOIN billservice_trafficlimit AS btl ON btl.id=%s AND bnf.tarif_id=btl.tarif_id AND ((bnf.direction = 'INPUT') AND (btl.in_direction = TRUE) OR (bnf.direction = 'OUTPUT') AND (btl.out_direction = TRUE))
                        JOIN billservice_trafficlimit_traffic_class as bttc ON btl.id=bttc.trafficlimit_id and ARRAY[bttc.trafficclass_id] <@ bnf.traffic_class_id WHERE
                        account_id=%s AND (bnf.date_start BETWEEN '%s' AND '%s')""" % (trafficlimit.id, user.id, settlement_period_start,  settlement_period_end)
    summ = cursor.fetchone()
    try:
        summ = summ[0]
    except:
        summ = 0 
    return {
            'trafficlimit': trafficlimit,
            'settlement_period_start': settlement_period_start,
            'settlement_period_end': settlement_period_end,
            'summ':summ/1024000,
            'stay':trafficlimit.size/1024000,
            }
    
    
    
    
    