 #-*- coding=UTF-8 -*-
import time, sys, os
import datetime
from IPy import IP

ip
sys.path.append(os.path.abspath('../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'
from mikrobill.billing.models import Account, Pay, Bonus, Tarif, Transaction

from django.conf import settings
import settings

#datetime.timedelta()
#datetime.strptime("2007-03-04 21:08:12", "%Y-%m-%d %H:%M:%S")

n=(24*60*60)/settings.TRANSACTIONS_NUMBER

while True:
    #print time.strftime('%X')
    time.sleep(n)
    today=datetime.datetime.now()
    accounts=Account.objects.filter(banned="Enabled")
    for acc in accounts:
        try:
            bonusday=Bonus.objects.get(period_end__gte=today,period_start__lte=today,users__exact=acc)
        except:
            if acc.ballance>0:
                transaction_summ=(float(acc.tarif.summ)/float(acc.tarif.period))/float(settings.TRANSACTIONS_NUMBER)
                transaction=Transaction()
                transaction.account=acc
                transaction.summ=transaction_summ
                transaction.tarif=acc.tarif
                transaction.save()
                print acc.ballance
                if acc.ballance<=0:
                    print "Deny access"


