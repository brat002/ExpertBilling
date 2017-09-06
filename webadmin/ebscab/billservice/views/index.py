# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from ebscab.utils.decorators import render_to

from billservice.models import (
    AccountPrepaysRadiusTrafic,
    AccountPrepaysTime,
    AccountPrepaysTrafic,
    AccountTarif,
    SubAccount,
    SystemUser,
    TrafficLimit
)


@render_to('accounts/index.html')
@login_required
def index(request):
    if isinstance(request.user.account, SystemUser):
        return HttpResponseRedirect(reverse("admin_dashboard"))

    user = request.user.account
    tariff_id, tariff_name = user.get_account_tariff_info()
    date = datetime.date(
        datetime.datetime.now().year,
        datetime.datetime.now().month,
        datetime.datetime.now().day)
    tariffs = (AccountTarif.objects
               .filter(account=user, datetime__lt=date)
               .order_by('-datetime'))

    if len(tariffs) == 0 or len(tariffs) == 1:
        tariff_flag = False
    else:
        tariff_flag = True

    try:
        ballance = user.ballance - user.credit
        ballance = u'%.2f' % user.ballance
    except:
        ballance = 0

    subaccounts = SubAccount.objects.filter(account=user)
    traffic = None
    account_tariff = None
    account_prepays_traffic = None
    if tariff_id:
        traffic = TrafficLimit.objects.filter(tarif=tariff_id)
        account_tariff = (AccountTarif.objects
                          .filter(account=user,
                                  datetime__lte=datetime.datetime.now())
                          .order_by('-datetime'))[0]
        account_prepays_traffic = (AccountPrepaysTrafic.objects
                                   .filter(account_tarif=account_tariff,
                                           current=True))

    prepaydtime = None
    try:
        prepaydtime = (AccountPrepaysTime.objects
                       .get(account_tarif=account_tariff, current=True))
    except:
        pass

    prepaydradiustraffic = None
    try:
        prepaydradiustraffic = (AccountPrepaysRadiusTrafic.objects
                                .get(account_tarif=account_tariff,
                                     current=True))
    except:
        pass

    try:
        next_tariff = (AccountTarif.objects
                       .filter(account=user,
                               datetime__gte=datetime.datetime.now())
                       .order_by('-datetime'))[0]
    except:
        next_tariff = None

    return {
        'account_tariff': account_tariff or '',
        'ballance': ballance,
        'tariff': tariff_name,
        'tariffs': tariffs,
        'tariff_flag': tariff_flag,
        'prepaydtime': prepaydtime,
        'prepaydradiustraffic': prepaydradiustraffic,
        'trafficlimit': traffic,
        'account_prepays_traffic': account_prepays_traffic,
        'active_class': 'user-img',
        'next_tariff': next_tariff,
        'subaccounts': subaccounts,
        'user': request.user.account
    }
