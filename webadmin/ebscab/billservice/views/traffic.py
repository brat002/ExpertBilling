# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.db import connection

from ebscab.lib.decorators import render_to
from ebscab.lib.paginator import SimplePaginator

from billservice.models import TrafficLimit, TrafficTransaction
from billservice.views.utils import addon_queryset


@render_to('accounts/groupstat.html')
@login_required
def traffic_volume(request):
    is_range, addon_query = addon_queryset(request, 'gpst', 'datetime')
    user = request.user.account
    cursor = connection.cursor()
    sql = """\
SELECT (SELECT name FROM billservice_group WHERE id=group_id) as group_name, \
sum(bytes), date_part('day',datetime) as dt_day, date_part('month', datetime) \
as dt_month, date_part('year',datetime) as dt_year
FROM billservice_groupstat
WHERE account_id=%s %%s
GROUP BY date_part('year',datetime),date_part('month',datetime),date_part(\
'day',datetime), group_name ORDER BY dt_year,dt_month, dt_day DESC;
""" % (user.id,)

    if is_range and addon_query.has_key('datetime__gte') and \
            addon_query.has_key('datetime__lte'):
        sql = sql % " and datetime between '%s' and '%s' " % \
            (addon_query['datetime__gte'], addon_query['datetime__lte'])
    else:
        sql = sql % ' '
    cursor.execute(sql)

    items = cursor.fetchall()
    group_stat = []
    summ_bytes = 0

    for item in items:
        group_stat.append({
            'day': int(item[2]),
            'month': int(item[3]),
            'year': int(item[4]),
            'group_name': item[0],
            'bytes': item[1]
        })
        summ_bytes += item[1]

    rec_count = len(items) + 1

    return {
        'group_stat': group_stat,
        'is_range': is_range,
        'summ_bytes': summ_bytes,
        'rec_count': rec_count,
        'active_class': 'statistic-img'
    }


@render_to('accounts/traffic_limit.html')
@login_required
def traffic_limit(request):
    user = request.user.account
    tariff = user.get_account_tariff()
    traffic = TrafficLimit.objects.filter(tarif=tariff)
    return {
        'trafficlimit': traffic,
        'user': user
    }


@render_to('accounts/traffic_transaction.html')
@login_required
def traffic_transaction(request):
    is_range, addon_query = addon_queryset(
        request, 'traffic_transaction', 'created')
    qs = (TrafficTransaction.objects
          .filter(account=request.user.account, **addon_query)
          .order_by('-created'))
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    traffic_transaction = paginator.get_page_items()
    if is_range:
        for ttr in qs:
            summ += ttr.summ
        for ttr in traffic_transaction:
            summ_on_page += ttr.summ
    rec_count = len(traffic_transaction) + 1

    return {
        'traffic_transaction': traffic_transaction,
        'paginator': paginator,
        'is_range': is_range,
        'summ': summ,
        'summ_on_page': summ_on_page,
        'rec_count': rec_count,
        'active_class': 'statistic-img'
    }
