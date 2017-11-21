# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from ebscab.utils.decorators import render_to
from getpaid.forms import SelectPaymentMethodForm

from billservice.forms import PromiseForm
from billservice.models import (
    Account,
    SystemUser,
    Transaction,
    TransactionType
)


@render_to('accounts/get_promise.html')
@login_required
def get_promise(request):
    if isinstance(request.user.account, SystemUser):
        return HttpResponseRedirect('/')

    tarif = request.user.account.get_account_tariff()
    if not settings.ALLOW_PROMISE and not tarif.allow_ballance_transfer:
        return HttpResponseRedirect('/')
    if not tarif:
        return {
            'error_message': _(u'Вам не назначен тарифный план'),
            'disable_promise': True
        }

    user = request.user.account

    if user.promise_summ not in [None, 0, '']:
        promise_summ = user.promise_summ
    else:
        promise_summ = settings.MAX_PROMISE_SUM

    if user.promise_min_ballance not in [None, 0, '']:
        promise_min_ballance = user.promise_min_ballance
    else:
        promise_min_ballance = settings.MIN_BALLANCE_FOR_PROMISE

    allow_transfer_summ = "%.2f" % (0 if user.ballance <= 0 else user.ballance)
    LEFT_PROMISE_DATE = (
        datetime.datetime.now() +
        datetime.timedelta(
            days=user.promise_days or settings.LEFT_PROMISE_DAYS))

    if settings.ALLOW_PROMISE == True and \
        (Transaction.objects
            .filter(account=user,
                    type=(TransactionType.objects
                          .get(internal_name='PROMISE_PAYMENT')),
                    promise_expired=False)
            .count()) >= 1:
        last_promises = (Transaction.objects
                         .filter(account=user,
                                 type=(TransactionType.objects
                                       .get(internal_name='PROMISE_PAYMENT')))
                         .order_by('-created'))[0:10]
        error_message = _(u"У вас есть незакрытые обещанные платежи")
        return {
            'error_message': error_message,
            'MAX_PROMISE_SUM': promise_summ,
            'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
            'disable_promise': True,
            'last_promises': last_promises,
            'allow_ballance_transfer': tarif.allow_ballance_transfer,
            'allow_transfer_summ': allow_transfer_summ,
            'active_class': 'promise-img'
        }

    if settings.ALLOW_PROMISE == True and user.ballance < promise_min_ballance:
        last_promises = (Transaction.objects
                         .filter(account=user,
                                 type=(TransactionType.objects
                                       .get(internal_name='PROMISE_PAYMENT')))
                         .order_by('-created'))[0:10]
        error_message_params = {
            'MIN_BALLANCE': promise_min_ballance,
            'CURRENCY': settings.CURRENCY
        }
        error_message = (
            _(u"Ваш баланс меньше разрешённого для взятия обещанного платежа. "
              u"Минимальный баланс: %(MIN_BALLANCE)s %(CURRENCY)s") %
            error_message_params)

        return {
            'error_message': error_message,
            'MAX_PROMISE_SUM': promise_summ,
            'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
            'disable_promise': True,
            'last_promises': last_promises,
            'allow_ballance_transfer': tarif.allow_ballance_transfer,
            'allow_transfer_summ': allow_transfer_summ,
            'active_class': 'promise-img'
        }

    last_promise = (Transaction.objects
                    .filter(account=user,
                            type=(TransactionType.objects
                                  .get(internal_name='PROMISE_PAYMENT')))
                    .order_by('-created'))
    if last_promise:
        last_promise_date = last_promise[0].created
        reactivation_date = last_promise_date + \
            datetime.timedelta(days=settings.PROMISE_REACTIVATION_DAYS)

        if settings.ALLOW_PROMISE == True and \
                reactivation_date > datetime.datetime.now():
            last_promises = (Transaction.objects
                             .filter(
                                account=user,
                                 type=(TransactionType.objects
                                       .get(internal_name='PROMISE_PAYMENT')))
                             .order_by('-created'))[0:10]
            error_message_params = {
                'LAST_PROMISE_DATE': last_promise_date,
                'REACTIVATION_DATE': reactivation_date
            }
            error_message = (
                _(u"Вы уже воспользовались услугой обещанного платежа "
                  u"%(LAST_PROMISE_DATE)s. Услуга обещанного платежа станет "
                  u"доступна %(REACTIVATION_DATE)s") % error_message_params)

            return {
                'error_message': error_message,
                'MAX_PROMISE_SUM': promise_summ,
                'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
                'disable_promise': True,
                'last_promises': last_promises,
                'allow_ballance_transfe': tarif.allow_ballance_transfer,
                'allow_transfer_summ': allow_transfer_summ,
                'active_class': 'promise-img'
            }

    if request.method == 'POST':
        operation = request.POST.get("operation")
        if operation == 'promise':
            rf = PromiseForm(request.POST)
            if not rf.is_valid():
                last_promises = (
                    Transaction.objects
                    .filter(account=user,
                            type=(TransactionType.objects
                                  .get(internal_name='PROMISE_PAYMENT')))
                    .order_by('-created'))[0:10]
                error_message = _(u"Проверьте введённые в поля данные")

                return {
                    'MAX_PROMISE_SUM': promise_summ,
                    'error_message': error_message,
                    'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
                    'disable_promise': False,
                    'allow_ballance_transfer': tarif.allow_ballance_transfer,
                    'allow_transfer_summ': allow_transfer_summ,
                    'last_promises': last_promises,
                    'active_class': 'promise-img'
                }

            sum = rf.cleaned_data.get("sum", 0)
            if sum > promise_summ:
                last_promises = (
                    Transaction.objects
                    .filter(account=user,
                            type=(TransactionType.objects
                                  .get(internal_name='PROMISE_PAYMENT')))
                    .order_by('-created'))[0:10]
                error_message = _(u"Вы превысили максимальный размер "
                                  u"обещанного платежа")
                return {
                    'MAX_PROMISE_SUM': promise_summ,
                    'error_message': error_message,
                    'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
                    'disable_promise': False,
                    'allow_ballance_transfer': tarif.allow_ballance_transfer,
                    'allow_transfer_summ': allow_transfer_summ,
                    'last_promises': last_promises,
                    'active_class': 'promise-img'
                }
            if sum <= 0:
                last_promises = (
                    Transaction.objects
                    .filter(account=user,
                            type=(TransactionType.objects
                                  .get(internal_name='PROMISE_PAYMENT')))
                    .order_by('-created'))[0:10]
                error_message = _(u"Сумма обещанного платежа должна быть "
                                  u"положительной")
                return {
                    'MAX_PROMISE_SUM': user.promise_summ,
                    'error_message': error_message,
                    'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
                    'disable_promise': False,
                    'allow_ballance_transfer': tarif.allow_ballance_transfer,
                    'allow_transfer_summ': allow_transfer_summ,
                    'last_promises': last_promises,
                    'active_class': 'promise-img'
                }

            cursor = connection.cursor()
            cursor.execute(u"""\
INSERT INTO billservice_transaction(account_id, bill, type_id, approved, \
tarif_id, summ, created, end_promise, promise_expired)
VALUES(%s, 'Обещанный платёж', 'PROMISE_PAYMENT', True, get_tarif(%s), %s, \
now(), '%s', False)""" % (user.id, user.id, sum, LEFT_PROMISE_DATE))
            cursor.connection.commit()

            last_promises = (
                Transaction.objects
                .filter(account=user,
                        type=(TransactionType.objects
                              .get(internal_name='PROMISE_PAYMENT')))
                .order_by('-created'))[0:10]

            return {
                'error_message': _(u'Обещанный платёж выполнен успешно. '
                                   u'Обращаем ваше внимание на то, что повторно '
                                   u'воспользоваться услугой обещанного платежа вы сможете '
                                   u'после единоразового погашения всей суммы платежа или '
                                   u'истечения даты созданного платежа.'),
                'disable_promise': True,
                'last_promises': last_promises,
                'active_class': 'promise-img'
            }

        elif operation == 'moneytransfer':
            last_promises = (
                Transaction.objects
                .filter(account=user,
                        type=(TransactionType.objects
                              .get(internal_name='PROMISE_PAYMENT')))
                .order_by('-created'))[0:10]

            if tarif.allow_ballance_transfer == False:
                return {
                    'error_message': _(u'Вам запрещено пользоваться сервисом '
                                       u'перевода баланса.'),
                    'MAX_PROMISE_SUM': promise_summ,
                    'last_promises': last_promises,
                    'disable_promise': False,
                    'allow_ballance_transfer': tarif.allow_ballance_transfer,
                    'allow_transfer_summ': allow_transfer_summ,
                    'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
                    'active_class': 'promise-img'
                }

            sum = request.POST.get("sum", 0)
            username = request.POST.get("username", '')
            if username:
                try:
                    to_user = Account.objects.get(username=username)
                except:
                    return {
                        'error_message': _(u'Абонент с указанным логином не '
                                           u'найден'),
                        'MAX_PROMISE_SUM': promise_summ,
                        'last_promises': last_promises,
                        'disable_promise': False,
                        'allow_ballance_transfer':
                            tarif.allow_ballance_transfer,
                        'allow_transfer_summ': allow_transfer_summ,
                        'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
                        'active_class': 'promise-img'
                    }
            else:
                return {
                    'error_message': _(u'Логин абонента, которому вы хотите '
                                       u'перевести средства, не указан.'),
                    'MAX_PROMISE_SUM': promise_summ,
                    'last_promises': last_promises,
                    'disable_promise': False,
                    'allow_ballance_transfer': tarif.allow_ballance_transfer,
                    'allow_transfer_summ': allow_transfer_summ,
                    'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
                    'active_class': 'promise-img'
                }

            try:
                sum = float(sum)
            except:
                return {
                    'error_message': _(u'Указанная сумма не является числом. '
                                       u'Разрешено вводить цифры 0-9 и точку, '
                                       u'как разделитель разрядов.'),
                    'MAX_PROMISE_SUM': promise_summ,
                    'last_promises': last_promises,
                    'disable_promise': False,
                    'allow_ballance_transfer': tarif.allow_ballance_transfer,
                    'allow_transfer_summ': allow_transfer_summ,
                    'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
                    'active_class': 'promise-img'
                }

            if sum > allow_transfer_summ:
                return {
                    'error_message': _(u'Указанная сумма слишком велика.'),
                    'MAX_PROMISE_SUM': promise_summ,
                    'last_promises': last_promises,
                    'disable_promise': False,
                    'allow_ballance_transfer': tarif.allow_ballance_transfer,
                    'allow_transfer_summ': allow_transfer_summ,
                    'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
                    'active_class': 'promise-img'
                }

            cursor = connection.cursor()
            cursor.execute(u"""\
INSERT INTO billservice_transaction(account_id, bill, description, type_id, \
approved, tarif_id, summ, created, promise)
VALUES(%s, %s, %s, 'MONEY_TRANSFER_TO', True, get_tarif(%s), %s, now(), \
False)""" , (user.id,
             to_user.id,
             _(u'Перевод средств на аккаунт %s' % to_user.username),
             user.id,
             -1 * sum))
            cursor.execute(u"""\
INSERT INTO billservice_transaction(account_id, bill, description, type_id, \
approved, tarif_id, summ, created, promise)
VALUES(%s, %s, %s, 'MONEY_TRANSFER_FROM', True, get_tarif(%s), %s, now(), \
False)""" , (to_user.id,
             user.id,
             _(u'Перевод средств с аккаунта %s' % user.username),
             to_user.id,
             sum))
            cursor.connection.commit()

            allow_transfer_summ = "%.2f" % (0 if user.ballance <= 0
                                            else user.ballance - Decimal(sum))
            return {
                'error_message': _(u'Перевод средств успешно выполнен.'),
                'disable_promise': False,
                'last_promises': last_promises,
                'allow_ballance_transfer': tarif.allow_ballance_transfer,
                'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
                'allow_transfer_summ': allow_transfer_summ,
                'active_class': 'promise-img'
            }
    else:
        last_promises = (
            Transaction.objects
            .filter(account=user, type__internal_name__in=['PROMISE_PAYMENT'])
            .order_by('-created'))[0:10]
        return {
            'MAX_PROMISE_SUM': promise_summ,
            'last_promises': last_promises,
            'disable_promise': not settings.ALLOW_PROMISE,
            'allow_ballance_transfer': tarif.allow_ballance_transfer,
            'allow_transfer_summ': allow_transfer_summ,
            'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE,
            'active_class': 'promise-img'
        }


@login_required
@render_to('accounts/make_payment.html')
def make_payment(request):
    form = SelectPaymentMethodForm()
    return {
        'payment_form': form
    }


class SelectPaymentView(TemplateView):
    template_name = 'billservice/payment_select.html'

    def get_context_data(self, **kwargs):
        context = super(SelectPaymentView, self).get_context_data(**kwargs)
        context['payment_form'] = SelectPaymentMethodForm()
        return context
