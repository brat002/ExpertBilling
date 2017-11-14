# -*- coding: utf-8 -*-

from django.db.models import F, Sum
from django.db.models.functions import Extract
from django.urls import reverse
from django.views.generic.base import RedirectView

from billservice.models import (
    Transaction,
    TransactionType,
    PeriodicalServiceHistory,
    AddonServiceTransaction,
    OneTimeServiceHistory,
    TrafficTransaction,
    Group,
    GroupStat
)
from radius.models import ActiveSession

from ebsweb.views.base import ProtectedListView


class IndexView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('ebsweb:statistics_transactions')


class TransactionsView(ProtectedListView):
    context_object_name = 'transactions'
    paginate_by = 10
    template_name = 'ebsweb/statistics/transaction_list.html'

    def get_queryset(self):
        return (Transaction.objects
                .filter(account=self.request.user.account)
                .exclude(type=(TransactionType.objects
                               .get(internal_name='PROMISE_PAYMENT')))
                .order_by('-created'))


class PromisesView(ProtectedListView):
    context_object_name = 'promises'
    paginate_by = 10
    template_name = 'ebsweb/statistics/promise_list.html'

    def get_queryset(self):
        return (Transaction.objects
                .filter(account=self.request.user.account,
                        type=(TransactionType.objects
                              .get(internal_name='PROMISE_PAYMENT')))
                .order_by('-created'))


class SessionsView(ProtectedListView):
    context_object_name = 'sessions'
    paginate_by = 10
    template_name = 'ebsweb/statistics/session_list.html'

    def get_queryset(self):
        return (ActiveSession.objects
                .filter(account=self.request.user.account)
                .order_by('-date_start'))


class PeriodicalServicesView(ProtectedListView):
    context_object_name = 'services'
    paginate_by = 10
    template_name = 'ebsweb/statistics/periodical_service_list.html'

    def get_queryset(self):
        return (PeriodicalServiceHistory.objects
                .filter(account=self.request.user.account)
                .order_by('-created'))


class AddonServicesView(ProtectedListView):
    context_object_name = 'services'
    paginate_by = 10
    template_name = 'ebsweb/statistics/addon_service_list.html'

    def get_queryset(self):
        return (AddonServiceTransaction.objects
                .filter(account=self.request.user.account)
                .order_by('-created'))


class OneTimeServicesView(ProtectedListView):
    context_object_name = 'services'
    paginate_by = 10
    template_name = 'ebsweb/statistics/one_time_service_list.html'

    def get_queryset(self):
        return (OneTimeServiceHistory.objects
                .filter(account=self.request.user.account)
                .order_by('-created'))


class TrafficTransactionsView(ProtectedListView):
    context_object_name = 'transactions'
    paginate_by = 10
    template_name = 'ebsweb/statistics/traffic_transaction_list.html'

    def get_queryset(self):
        return (TrafficTransaction.objects
                .filter(account=self.request.user.account)
                .order_by('-created'))


class TrafficView(ProtectedListView):
    context_object_name = 'groups'
    paginate_by = 10
    template_name = 'ebsweb/statistics/traffic_list.html'

    def get_queryset(self):
        return (GroupStat.objects
                .filter(account=self.request.user.account)
                .annotate(name=F('group__name'))
                .values('name')
                .annotate(
                    year=Extract('datetime', 'year'),
                    month=Extract('datetime', 'month'),
                    day=Extract('datetime', 'day'),
                    bytes_sum=Sum('bytes'))
                .order_by('year', 'month', 'day', 'name'))
