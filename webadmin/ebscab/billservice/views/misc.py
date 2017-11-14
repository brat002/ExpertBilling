# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.db import connection

from ebscab.utils.decorators import render_to
from ebscab.utils.paginator import SimplePaginator
from radius.models import ActiveSession

from billservice.forms import StatististicForm
from billservice.models import (
    AddonServiceTransaction,
    OneTimeServiceHistory,
    PeriodicalServiceHistory,
    TrafficTransaction,
    Transaction
)
from billservice.views.utils import addon_queryset


@render_to('accounts/statistics.html')
@login_required
def statistics(request):
    user = request.user.account
    transaction = (Transaction.objects
                   .filter(account=user)
                   .order_by('-created'))[:8]
    active_session = (ActiveSession.objects
                      .filter(account=user)
                      .order_by('-date_start'))[:8]
    periodical_service_history = (PeriodicalServiceHistory.objects
                                  .filter(account=user)
                                  .order_by('-created'))[:8]
    addon_service_transaction = (AddonServiceTransaction.objects
                                 .filter(account=user)
                                 .order_by('-created'))[:8]
    one_time_history = (OneTimeServiceHistory.objects
                        .filter(account=user)
                        .order_by('-created'))[:8]
    traffic_transaction = (TrafficTransaction.objects
                           .filter(account=user)
                           .order_by('-created'))[:8]
    cursor = connection.cursor()
    cursor.execute("""\
SELECT (
    SELECT name FROM billservice_group
    WHERE id=group_id
) as group_name,
sum(bytes),
date_part('day', datetime) as dt_day,
date_part('month', datetime) as dt_month,
date_part('year', datetime) as dt_year
FROM billservice_groupstat
WHERE account_id=%s
GROUP BY (
    date_part('year', datetime),
    date_part('month', datetime),
    date_part('day', datetime),
    group_name
)
ORDER BY dt_year,dt_month, dt_day DESC;
""", (user.id,))
    items = cursor.fetchall()
    group_stat = []
    for item in items:
        group_stat.append({
            'day': int(item[2]),
            'month': int(item[3]),
            'year': int(item[4]),
            'group_name': item[0],
            'bytes': item[1]
        })

    if request.session.has_key('date_id_dict'):
        date_id_dict = request.session['date_id_dict']
    else:
        date_id_dict = {}
    return {
        'transactions': transaction,
        'active_session': active_session,
        'periodical_service_history': periodical_service_history,
        'addon_service_transaction': addon_service_transaction,
        'one_time_history': one_time_history,
        'traffic_transaction': traffic_transaction,
        'group_stat': group_stat,
        'form': StatististicForm(),
        'date_id_dict': date_id_dict,
        'active_class': 'statistic-img',
    }


@render_to('accounts/vpn_session.html')
@login_required
def vpn_session(request):
    user = request.user.account
    is_range, addon_query = addon_queryset(
        request, 'active_session', 'date_start', 'date_end')
    qs = (ActiveSession.objects
          .filter(account=user, **addon_query)
          .order_by('-date_start'))
    paginator = SimplePaginator(request, qs, 50, 'page')
    bytes_in = 0
    bytes_out = 0
    bytes_all = 0
    bytes_in_on_page = 0
    bytes_out_on_page = 0
    bytes_all_on_page = 0
    sessions = paginator.get_page_items()
    if is_range:
        for session in qs:
            if session.bytes_in:
                bytes_in += session.bytes_in
            if session.bytes_out:
                bytes_out += session.bytes_out
        for session in sessions:
            if session.bytes_in:
                bytes_in_on_page += session.bytes_in
            if session.bytes_out:
                bytes_out_on_page += session.bytes_out
    bytes_all_on_page = bytes_in_on_page + bytes_out_on_page
    bytes_all = bytes_in + bytes_out
    rec_count = len(sessions) + 1
    return {
        'sessions': paginator.get_page_items(),
        'paginator': paginator,
        'user': user,
        'rec_count': rec_count,
        'bytes_in': bytes_in,
        'bytes_out': bytes_out,
        'bytes_all': bytes_all,
        'bytes_in_on_page': bytes_in_on_page,
        'bytes_out_on_page': bytes_out_on_page,
        'bytes_all_on_page': bytes_all_on_page,
        'is_range': is_range,
        'active_class': 'statistic-img'
    }


@render_to('accounts/one_time_history.html')
@login_required
def one_time_history(request):
    is_range, addon_query = addon_queryset(request, 'one_time_history')
    qs = (OneTimeServiceHistory.objects
          .filter(account=request.user.account, **addon_query)
          .order_by('-created'))
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    one_time_history = paginator.get_page_items()
    if is_range:
        for one_time in qs:
            summ += one_time.summ
        for one_time in one_time_history:
            summ_on_page += one_time.summ
    rec_count = len(one_time_history) + 1
    return {
        'one_time_history': one_time_history,
        'paginator': paginator,
        'is_range': is_range,
        'summ': summ,
        'summ_on_page': summ_on_page,
        'rec_count': rec_count,
        'active_class': 'statistic-img'
    }
