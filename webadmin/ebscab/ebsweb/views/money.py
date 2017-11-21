# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic.base import RedirectView

from billservice.models import Transaction, TransactionType

from ebsweb.views.base import ProtectedFormView, UserFormKwargsMixin, UserTariffMixin
from ebsweb.forms.money import CardForm, PromiseForm, PaymentForm, TransferForm


class MoneyView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('ebsweb:money_payment')


# TODO: temporary
# class MoneyPaymentView(ProtectedFormView):
#     form_class = PaymentForm
#     template_name = 'ebsweb/money/payment.html'
class MoneyPaymentView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('ebsweb:money_promise')


class MoneyPromiseView(UserTariffMixin,
                       UserFormKwargsMixin,
                       ProtectedFormView):
    form_class = PromiseForm
    template_name = 'ebsweb/money/promise.html'

    def get_success_url(self):
        return reverse('ebsweb:money_promise')

    def dispatch(self, *args, **kwargs):
        account = self.request.user.account
        self.promise_sum = account.promise_sum_20
        self.promise_left_date = \
            datetime.now() + timedelta(days=account.promise_left_days_20)
        return super(MoneyPromiseView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super(MoneyPromiseView, self).get_initial()
        initial['tariff'] = self.tariff
        initial['promise_sum'] = self.promise_sum
        initial['promise_left_date'] = self.promise_left_date
        return initial

    def get_context_data(self, **kwargs):
        context = super(MoneyPromiseView, self).get_context_data(**kwargs)
        user = self.request.user.account

        if not self.tariff or not settings.PROMISE_ALLOWED:
            return HttpResponseRedirect(reverse('ebsweb:money'))

        promise_min_balance = user.promise_min_balance_20

        transaction_type_obj = TransactionType.objects.get(
            internal_name='PROMISE_PAYMENT')
        promises = (Transaction.objects
                    .filter(account=user,
                            type=transaction_type_obj)
                    .order_by('-created'))

        user_has_unexpired_promise = (promises
                                      .filter(promise_expired=False)
                                      .exists())
        user_has_insufficient_balance = user.ballance < promise_min_balance
        user_has_unexpired_again_date = False
        if not user_has_unexpired_promise:
            last_promise = promises.first()
            if last_promise:
                last_promise_date = last_promise.created
                promise_again_date = (
                    last_promise_date +
                    timedelta(days=settings.PROMISE_AGAIN_DAYS))
                user_has_unexpired_again_date = (promise_again_date >
                                                 datetime.now())

        if user_has_unexpired_promise:
            warning_message = _(u'У вас есть невозвращенные обещанные платежи')
        elif user_has_insufficient_balance:
            warning_message = _(
                (u'Ваш баланс меньше минимально допустимого ({0} {1}) для '
                 u'взятия обещанного платежа').format(user.credit_sum,
                                                      settings.CURRENCY))
        elif user_has_unexpired_again_date:
            warning_message = _(
                (u'Вы уже воспользовались этой услугой {0}, она станет снова '
                 u'доступна {1}').format(last_promise_date, promise_again_date)
            )
        else:
            warning_message = None

        if warning_message:
            messages.warning(self.request, warning_message)

        promise_allowed = (not user_has_unexpired_promise and
                           not user_has_insufficient_balance and
                           not user_has_unexpired_again_date)
        if promise_allowed:
            context['promise_left_date'] = self.promise_left_date
        else:
            context['latest_promises'] = promises[0:10]
        context['promise_allowed'] = promise_allowed
        return context

    def form_valid(self, form):
        form.create()
        messages.success(self.request,
                         _(u'Обещанный платеж успешно создан. Повторно '
                           u'воспользоваться этой услугой вы сможете '
                           u'после единоразового погашения всей суммы '
                           u'или истечения даты созданного платежа'))
        return super(MoneyPromiseView, self).form_valid(form)


class MoneyTransferView(UserTariffMixin,
                        UserFormKwargsMixin,
                        ProtectedFormView):
    form_class = TransferForm
    template_name = 'ebsweb/money/transfer.html'

    def get_success_url(self):
        return reverse('ebsweb:money_transfer')

    def get_context_data(self, **kwargs):
        context = super(MoneyTransferView, self).get_context_data(**kwargs)
        transfer_allowed = self.tariff.allow_ballance_transfer
        if not transfer_allowed:
            messages.error(
                self.request,
                _(u'Сервис перевода баланса не доступен для вас'))

        context['transfer_allowed'] = transfer_allowed
        return context

    def form_valid(self, form):
        form.send()
        messages.success(self.request,
                         _(u'Перевод средств успешно выполнен'))
        return super(MoneyTransferView, self).form_valid(form)


class MoneyCardView(UserFormKwargsMixin, ProtectedFormView):
    form_class = CardForm
    template_name = 'ebsweb/money/card.html'

    def dispatch(self, *args, **kwargs):
        if not self.request.user.account.allow_expresscards:
            messages.info(_(u'Вам не доступна услуга активации карт'))
            return HttpResponseRedirect('ebsweb:money')
        return super(MoneyCardView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('ebsweb:money_card')

    def form_valid(self, form):
        response_code = form.save()
        if response_code == 'CARD_NOT_FOUND':
            error_message = _(u'Ошибка активации. Карта не найдена.')
        elif response_code == 'CARD_NOT_SOLD':
            error_message = _(u'Ошибка активации. Карта не была продана.')
        elif response_code == 'CARD_ALREADY_ACTIVATED':
            error_message = _(
                u'Ошибка активации. Карта была активирована раньше.')
        elif response_code == 'CARD_EXPIRED':
            error_message = _(
                u'Ошибка активации. Срок действия карты истёк.')
        elif response_code == 'CARD_ACTIVATED':
            messages.success(self.request, _(u'Карта успешно активирована.'))
        elif response_code == 'CARD_ACTIVATION_ERROR':
            error_message = _(u'Ошибка активации карты.')
        else:
            error_message = None

        if error_message:
            messages.error(self.request, error_message)
        return super(MoneyCardView, self).form_valid(form)
