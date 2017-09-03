# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required

from ebscab.lib.decorators import render_to
from ebscab.lib.paginator import SimplePaginator

from billservice.models import Transaction
from billservice.views.utils import addon_queryset


@render_to('accounts/transaction.html')
@login_required
def transaction(request):
    is_range, addon_query = addon_queryset(request, 'transactions', 'created')
    qs = (Transaction.objects
          .filter(account=request.user.account, **addon_query)
          .order_by('-created'))
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    transactions = paginator.get_page_items()
    if is_range:
        for trnsaction in qs:
            summ += trnsaction.summ
        for transactio in transactions:
            summ_on_page += trnsaction.summ
    summ = summ
    summ_on_page = summ_on_page
    rec_count = len(transactions) + 1
    return {
        'transactions': transactions,
        'paginator': paginator,
        'is_range': is_range,
        'summ': summ,
        'summ_on_page': summ_on_page,
        'rec_count': rec_count,
        'active_class': 'statistic-img'
    }
