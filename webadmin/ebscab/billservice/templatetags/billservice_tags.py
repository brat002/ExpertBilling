# -*- coding: utf-8 -*-

import datetime

import mako.template as mako
from django import template
from django.db import connection
from django.db.models import Q

from radius.models import ActiveSession
from tasks import get_port_oper_status

from billservice.models import (
    AccountAddonService,
    AccountPrepaysTrafic,
    AccountViewedNews,
    AddonServiceTransaction,
    News,
    Switch,
    SwitchPort,
    Transaction,
    TransactionType
)
from billservice.utility import settlement_period_info


register = template.Library()


@register.inclusion_tag('accounts/tags/writen_of_time.html')
def writen_of_time(session, user):
    type = TransactionType.objects.get(internal_name='TIME_ACCESS')
    if session.date_end:
        transactions = (Transaction.objects
                        .filter(account=user,
                                created__gte=session.date_start,
                                created__lte=session.date_end,
                                type=type.internal_name))
    else:
        transactions = (Transaction.objects
                        .filter(account=user,
                                created__gte=session.date_start,
                                type=type.internal_name))
    sum = 0
    for transaction in transactions:
        sum += transaction.summ
    return {'sum': sum}


@register.inclusion_tag('accounts/tags/writen_of_traffic.html')
def writen_of_traffic(session, user):
    type = TransactionType.objects.get(internal_name='NETFLOW_BILL')
    if session.date_end:
        transactions = (Transaction.objects
                        .filter(account=user,
                                created__gte=session.date_start,
                                created__lte=session.date_end,
                                type=type.internal_name))
    else:
        transactions = (Transaction.objects
                        .filter(account=user,
                                created__gte=session.date_start,
                                type=type.internal_name))
    sum = 0
    for transaction in transactions:
        sum += transaction.summ
    return {
        'sum': sum
    }


@register.filter(name='format_sum')
def format_sum(value):
    return "%.2f" % float(value)


@register.inclusion_tag('accounts/tags/traffic_format.html')
def traffic_format(value, second_value=None):
    try:
        if second_value != None:
            a = float(value) + float(second_value)
        else:
            a = float(value)
        if a > 1024 and a < (1024 * 1024):
            return {
                'size': u"%.2f KB" % float(a / float(1024))
            }
        elif a >= (1024 * 1024):
            return {
                'size': u"%.2f МB" % float(a / float(1024 * 1024))
            }
        elif a < 1024:
            return {
                'size': u"%f B" % float(a)
            }
    except Exception, e:
        print e


@register.inclusion_tag('accounts/tags/traffic_size.html')
def traffic_size(traffic, account_tarif):
    try:
        size = (AccountPrepaysTrafic.objects
                .get(prepaid_traffic=traffic, account_tarif=account_tarif))
    except:
        size = None
    return {
        'size': size
    }


@register.inclusion_tag('accounts/tags/time_format.html')
def time_format(s):
    try:
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        if h == 0 and m == 0:
            return {
                'time': u"%sс" % s
            }
        elif h == 0 and m != 0:
            return {
                'time': u"%sм %sс" % (m, s,)
            }
        else:
            return {
                'time': u"%sч %sм %sс" % (h, m, s)
            }
    except:
        return {
            'time': u"0с"
        }


@register.inclusion_tag('accounts/tags/traffic_limit_row.html')
def traffic_limit_row(trafficlimit, user, iter_nom, last=False):
    settlement_period = \
        trafficlimit.settlement_period or trafficlimit.tarif.settlement_period
    cursor = connection.cursor()
    if settlement_period and settlement_period.autostart == True:
        cursor.execute("""\
SELECT datetime
FROM billservice_accounttarif
WHERE account_id=%s and datetime<now()
ORDER BY datetime DESC LIMIT 1\
""" % (user.id))
        sp_start = cursor.fetchone()
        sp_start = sp_start[0]
    else:
        settlement_period = user.get_account_tariff().settlement_period
        sp_start = settlement_period.time_start if settlement_period else None
    settlement_period_start, settlement_period_end, delta = \
        settlement_period_info(time_start=sp_start,
                               repeat_after=settlement_period.length_in,
                               repeat_after_seconds=settlement_period.length)
    # если нужно считать количество трафика за последнеие N секунд, а не за
    # рачётный период, то переопределяем значения
    if trafficlimit.mode == True:
        now = datetime.datetime.now()
        settlement_period_start = now - datetime.timedelta(seconds=delta)
        settlement_period_end = now

    cursor.execute ("""\
SELECT sum(bytes) as size
FROM billservice_groupstat
WHERE group_id=%s and account_id=%s and datetime>%s and datetime<%s
""", (trafficlimit.group_id,
      user.id,
      settlement_period_start,
      settlement_period_end))
    summ = cursor.fetchone()
    try:
        summ = summ[0] / (1024 * 1024)
    except:
        summ = 0

    try:
        stay = trafficlimit.size / (1024 * 1024)
    except:
        stay = 0

    return {
        'trafficlimit': trafficlimit,
        'settlement_period_start': settlement_period_start,
        'settlement_period_end': settlement_period_end,
        'summ': summ,
        'stay': stay,
        'iter_nom': iter_nom,
        'last': last
    }


@register.inclusion_tag('accounts/tags/subaccount_row.html')
def subaccounts_row(subaccount, iter_num, last=False):
    return {
        'subaccount': subaccount,
        'iter_num': iter_num,
        'last': last
    }


@register.filter(name='coll_bg')
def coll_bg(value):
    row_class = ''
    if value % 2 == 0:
        row_class = u'with_bg'
    return row_class


@register.filter(name='sevice_activation')
def sevice_activation(value, user=None):
    try:
        account_addon_service = (AccountAddonService.objects
                                 .get(service=value,
                                      account=user,
                                      deactivated__isnull=True))
        return '<a href="/service/del/%s/">Отключить</a>' % account_addon_service.id
    except:
        return '&nbsp;'


@register.filter(name='service_cost')
def service_cost(value):
    symm = 0
    for transaction in (AddonServiceTransaction.objects
                        .filter(accountaddonservice=value)):
        symm += transaction.summ
    return symm


@register.inclusion_tag('accounts/tags/show_last_news.html')
def show_last_news(count=5):
    news = (News.objects
            .filter(public=True)
            .filter(Q(age__gte=datetime.datetime.now()) | Q(age__isnull=True))
            .order_by('-id'))[:5]
    return {
        'news': news
    }


@register.filter(name='multiply')
def multiply(value, multiply_value):
    value = value * int(multiply_value)
    return value


@register.inclusion_tag('accounts/tags/show_last_news_private.html')
def show_last_news_private(user):
    news = (AccountViewedNews.objects
            .filter(news__private=True, account=user, viewed=False)
            .filter(Q(news__age__gte=datetime.datetime.now()) |
                    Q(news__age__isnull=True))
            .order_by('-id'))[:5]
    return {
        'news': news
    }


@register.tag('mako')
def do_mako(parser, token):
    nodelist = parser.parse(('endmako',))
    parser.delete_first_token()
    return makoNode(nodelist)


class makoNode(template.Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        block = self.nodelist.render(context)
        # turn the context into a dict
        parameters = {}
        [parameters.update(parameter) for parameter in context]
        # render with Mako
        rendered = (mako.Template(block, format_exceptions=True)
                    .render(**parameters))
        return rendered


@register.assignment_tag(takes_context=True)
def get_switch_port(context, switch, port):
    if not switch or not port:
        return

    try:
        switch = Switch.objects.get(id=switch)
    except:
        return None

    if not switch.snmp_support:
        return

    try:
        item = SwitchPort.objects.get(switch=switch, port=port)
    except:
        item = SwitchPort.objects.create(
            switch=Switch.objects.get(id=switch), port=port)

    try:
        port_status = get_port_oper_status(
            switch_ip=item.switch.ipaddress,
            community=item.switch.snmp_community,
            snmp_version=item.switch.snmp_version,
            port='')
    except:
        return

    if port_status:
        item.oper_status = port_status
        item.save()
        return item


@register.assignment_tag(takes_context=True)
def get_subaccount_sessions_info(context, subaccount, count=5):
    try:
        return (ActiveSession.objects
                .filter(subaccount=subaccount)
                .order_by('-date_start'))[:count]
    except:
        return None


@register.assignment_tag(takes_context=True)
def get_subaccount_vpn_active(context, subaccount):
    try:
        return (ActiveSession.objects
                .filter(subaccount=subaccount,
                        date_end__isnull=True,
                        session_status='ACTIVE')
                .exists())
    except:
        return None
