# -*- coding: utf-8 -*-

import datetime
import math

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.utils.translation import ugettext_lazy as _

from ebscab.lib.decorators import ajax_request, render_to

from billservice.models import (
    AccountPrepaysTrafic,
    AccountTarif,
    PrepaidTraffic,
    SuspendedPeriod
)


@login_required
@ajax_request
def get_ballance(request):
    f = lambda v, l: [v[i * l:(i + 1) * l]
                      for i in range(int(math.ceil(len(v) / float(l))))]

    cursor = connection.cursor()
    cursor.execute(
        'SELECT news.id, news.body FROM billservice_news as news'
        'WHERE agent=True and'
        '(news.id in (SELECT news_id FROM billservice_accountviewednews '
        'WHERE account_id=%s and viewed is not True));',
        (request.user.account.id,)
    )
    avn = cursor.fetchall()

    news_arr = []
    for n in avn:
        news_arr.append({'id': n[0], 'title': n[1]})
        cursor.execute(
            'UPDATE billservice_accountviewednews'
            'SET viewed=True where account_id=%s and news_id=%s',
            (request.user.account.id, n[0])
        )
        cursor.connection.commit()

    try:
        return {
            "status": 1,
            "ballance_float": float(request.user.account.ballance),
            "ballance": "%.2f" % request.user.account.ballance,
            "message": "Ok",
            'news': news_arr
        }
    except:
        return {
            "status": 0,
            "ballance": -1,
            "message": "User not found"
        }


@render_to('accounts/account_prepays_traffic.html')
@login_required
def account_prepays_traffic(request):
    user = request.user.account
    try:
        account_tariff = AccountTarif.objects.get(
            account=user, datetime__lt=datetime.datetime.now())[:1]
        account_prepays_trafic = AccountPrepaysTrafic.objects.filter(
            account_tarif=account_tariff)
        prepaidtraffic = PrepaidTraffic.objects.filter(
            id__in=[i.prepaid_traffic.id for i in account_prepays_trafic])
    except:
        prepaidtraffic = None
        account_tariff = None
    return {
        'prepaidtraffic': prepaidtraffic,
        'account_tariff': account_tariff,
    }


@render_to('accounts/popup_userblock.html')
@login_required
def user_block(request):
    account = request.user.account
    tarif = account.get_account_tariff()
    account_status = account.status
    sp = SuspendedPeriod.objects.filter(account=account, end_date__isnull=True)
    if sp:
        sp = sp[0]
    return {
        'account_status': account_status,
        'tarif': tarif,
        'sp': sp
    }


@login_required
@ajax_request
def userblock_action(request):
    message = _(u'Невозможно заблокировать учётную записть')
    if request.method == 'POST':
        account = request.user.account
        if account.status == 4:
            now = datetime.datetime.now()
            account.status = 1
            account.save()
            result = True
            message = _(u'Аккаунт успешно активирован')

        elif account.status == 1:
            tarif = account.get_account_tariff()
            if tarif.allow_userblock:
                if tarif.userblock_require_balance != 0 and \
                        tarif.userblock_require_balance > \
                        account.ballance + account.credit:
                    result = False
                    message = (_(u'Аккаунт не может быть заблокирован. </br>'
                                 u'Минимальный остаток на балансе должен '
                                 u'составлять %s.') %
                               tarif.userblock_require_balance)
                    return {
                        'message': message,
                        'result': result
                    }
                account.status = 4
                account.save()

                cursor = connection.cursor()
                cursor.execute(u"""\
INSERT INTO billservice_transaction(account_id, bill, type_id, approved, \
tarif_id, summ, created, promise)
VALUES(%s, 'Списание средств за пользовательскую блокировку', \
'USERBLOCK_PAYMENT', True, get_tarif(%s), (-1)*%s, now(), False)\
""" , (account.id, account.id, tarif.userblock_cost,))
                cursor.connection.commit()
                message = _(u'Аккаунт успешно заблокирован')
                result = True
            else:
                message = _(u'Блокировка аккаунта запрещена')
                result = False
        else:
            # TODO: fix type
            message = _(u'Блокировка аккаунта невозможна. Обратитесь в '
                        u'служюу поддержки провайдера.')
            result = False
    return {
        'message': message,
        'result': result
    }
