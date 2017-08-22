# -*- coding: utf-8 -*-

import datetime
import os
import sys
import time

sys.path.append(os.path.abspath('../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'ebscab.settings'

from django.conf import settings

from ebscab.billing.models import Account, Bonus, Transaction


# datetime.timedelta()
#datetime.strptime("2007-03-04 21:08:12", "%Y-%m-%d %H:%M:%S")

n = (24 * 60 * 60) / settings.TRANSACTIONS_NUMBER

while True:
    # print time.strftime('%X')
    time.sleep(n)
    today = datetime.datetime.now()
    accounts = Account.objects.filter(banned="Enabled")
    for acc in accounts:
        try:
            bonusday = Bonus.objects.get(
                period_end__gte=today, period_start__lte=today, users__exact=acc)
        except:
            if acc.ballance > 0:
                transaction_summ = ((float(acc.tarif.summ) /
                                     float(acc.tarif.period)) /
                                    float(settings.TRANSACTIONS_NUMBER))
                transaction = Transaction()
                transaction.account = acc
                transaction.summ = transaction_summ
                transaction.tarif = acc.tarif
                transaction.save()
                print acc.ballance
                if acc.ballance <= 0:
                    print "Deny access"
