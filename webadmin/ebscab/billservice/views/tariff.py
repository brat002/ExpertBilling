# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from ebscab.lib.decorators import render_to, ajax_request

from billservice.forms import ChangeTariffForm
from billservice.models import (
    AccountAddonService,
    AccountSuppAgreement,
    AccountTarif,
    TPChangeRule
)
from billservice.utility import settlement_period_info


@ajax_request
@render_to('accounts/change_tariff.html')
@login_required
def change_tariff_form(request):
    user = request.user.account
    account_tariff_id = (
        AccountTarif.objects
        .filter(account=user, datetime__lt=datetime.datetime.now())
        .order_by('-datetime'))[:1]
    account_tariff = account_tariff_id[0]
    tariffs = TPChangeRule.objects.filter(from_tariff=account_tariff.tarif)
    res = []
    for rule in tariffs:
        data_start_period = None
        if rule.on_next_sp:
            sp = user.get_account_tariff().settlement_period
            if sp:
                if sp.autostart:
                    start = account_tariff.datetime
                else:
                    start = sp.time_start
                td = settlement_period_info(start, sp.length_in, sp.length)
                data_start_period = td[1]
        rule.date_start = data_start_period
        res.append(rule)

    form = ChangeTariffForm(user, account_tariff)
    return {
        'form': form,
        'tariff_objects': res,
        'user': user,
        'tariff': account_tariff
    }


@ajax_request
@login_required
def change_tariff(request):
    """
    settlement_period_info
    1 - дата начала действия тарифа
    """
    if request.method == 'POST':
        now = datetime.datetime.now()
        suppagreements = (
            AccountSuppAgreement.objects
            .filter(Q(closed__isnull=True) | Q(closed__gte=now),
                    account=request.user.account,
                    created__lte=now,
                    suppagreement__disable_tarff_change=True))
        if suppagreements:
            error_message_params = {
                'SUPPAGREEMENT_NO': ', '.join([x.contract
                                               for x in suppagreements])
            }
            return {
                'error_message': _((u'Вы не можете сменить тарифный план в '
                                    u'связи с действующим доп. соглашением № '
                                    u'%(SUPPAGREEMENT_NO)s.') %
                                   error_message_params)
            }

        rule_id = request.POST.get('id_tariff_id', None)
        if rule_id != None:
            user = request.user.account
            current_tariff = user.get_account_tariff()
            account_tariff_id = (AccountTarif.objects
                                 .filter(account=user,
                                         datetime__lt=datetime.datetime.now())
                                 .order_by('-datetime'))[:1]
            account_tariff = account_tariff_id[0]

            rules_id = [x.id
                        for x in (TPChangeRule.objects
                                  .filter(from_tariff=account_tariff.tarif))]
            rule = TPChangeRule.objects.get(id=rule_id)
            data_start_period = datetime.datetime.now()
            data_start_active = False
            if rule.settlement_period_id:
                td = settlement_period_info(account_tariff.datetime,
                                            rule.settlement_period.length_in,
                                            rule.settlement_period.length)
                delta = ((datetime.datetime.now() -
                          account_tariff.datetime).seconds +
                         (datetime.datetime.now() -
                          account_tariff.datetime).days * 86400 - td[2])
                if delta < 0:
                    return {
                        'error_message': _(
                            u'Вы не можете перейти на выбранный тариф. Для '
                            u'перехода вам необходимо отработать на старом '
                            u'тарифе ещё не менее %s дней' %
                            (delta / 86400 * (-1),))
                    }
            if rule.on_next_sp:
                sp = current_tariff.settlement_period
                if sp:
                    if sp.autostart:
                        start = account_tariff.datetime
                    else:
                        start = sp.time_start
                    td = settlement_period_info(start, sp.length_in, sp.length)
                    data_start_period = td[1]
                    data_start_active = True

            if not rule.id in rules_id:
                return {
                    'error_message': _(u'Вы не можете перейти на выбранный '
                                       u'тарифный план.')
                }

            if float(rule.ballance_min) > float(user.ballance + user.credit):
                return {
                    'error_message': _(u'Вы не можете перейти на выбранный '
                                       u'тарифный план. Ваш баланс меньше '
                                       u'разрешённого для такого перехода.')
                }

            tariff = AccountTarif.objects.create(
                account=user,
                tarif=rule.to_tariff,
                datetime=data_start_period)
            for service in (AccountAddonService.objects
                            .filter(account=user, deactivated__isnull=True)):
                if service.service.cancel_subscription:
                    service.deactivated = data_start_period
                    service.save()

            if rule.cost:
                cursor = connection.cursor()
                cursor.execute(u"""\
INSERT INTO billservice_transaction(account_id, bill, type_id, approved, \
tarif_id, summ, created, promise)
VALUES(%s, 'Списание средств за переход на тарифный план %s', 'TP_CHANGE', \
True, get_tarif(%s), (-1)*%s, now(), False)\
""" % (user.id, tariff.tarif.name, user.id, rule.cost))
                cursor.connection.commit()

            if data_start_active:
                ok_message_params = {
                    'TP': td[1],
                    'SUMM': rule.cost
                }
                return {
                    'ok_message': (_(
                        u'Вы успешно сменили тариф, тарифный план будет '
                        u'изменён в следующем расчётном периоде c %(TP)s.'
                        u'<br> За переход на данный тарифный план с '
                        u'пользователя будет взыскано %(SUMM)s средств.') %
                        ok_message_params),
                }
            else:
                return {
                    'ok_message': (_(
                        u'Вы успешно сменили тариф. <br> За переход на данный '
                        u'тарифный план с пользователя будет взыскано %s '
                        u'средств.') % rule.cost),
                }
        else:
            return {
                'error_message': _(u'Системная ошибка.')
            }
    else:
        return {
            'error_message': _(u'Попытка взлома')
        }
