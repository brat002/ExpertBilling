# -*- coding=utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from sendsms.models import Message
from billservice.models import Account, Template
import datetime
from django.conf import settings

class Command(BaseCommand):
    help = 'Check ballance amount and send notifications'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        try:
            body = Template.objects.filter(type__id=10)[0]
        except:
            print u"Создайте шаблон SMS сообщения"
        for acc in Account.objects.filter(ballance__lte=settings.SENDSMS_IF_BALLANCE_AMOUNT, ballance__gte=settings.SENDSMS_NOT_SEND_IF_BALANCE_LESS):
            if not acc.phone_m: continue
            if Message.objects.filter(account=acc, created__gte=datetime.datetime.now()-datetime.timedelta(days=settings.SENDSMS_SEND_EVERY_N_DAY)).count()>0: continue
            acc.ballance = '%.2f' % acc.ballance 
            item = Message()
            item.account = acc
            item.backend = settings.SENDSMS_DEFAULT_BACKEND
            item.to = acc.phone_m
            item.body = body.body
            item.save() 
            #item.send()



