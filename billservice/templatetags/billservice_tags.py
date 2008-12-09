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