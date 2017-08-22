# -*- coding: utf-8 -*-

import datetime

from django.core.management.base import BaseCommand
from django.template import Template

from sendsms.models import Message

from billservice.models import (
    Account,
    AccountNotification,
    NotificationsSettings,
    Transaction
)


class Command(BaseCommand):
    help = 'Process email/sms ballance notifications'

    def handle(self, *args, **options):
        items = NotificationsSettings.objects.all()
        notifications = {}
        now = datetime.datetime.now()
        for n in items:
            for t in n.tariffs.all():
                notifications[t.id] = n

        accounts = Account.objects.extra(
            select={'tarif_id': 'get_tarif(billservice_account.id)'})
        print 'Accounts fetched'

        for account in accounts:
            notification = notifications.get(account.tarif_id)
            print account
            if not notification:
                continue

            an = AccountNotification.objects.filter(
                account=account, notificationsettings=notification)
            if an:
                an = an[0]
            else:
                an = AccountNotification()
                an.account = account
                an.notificationsettings = notification

            print account, an
            if notification.balance_notifications:
                if an.ballance_notification_count >= \
                    notification.balance_notifications_limit and \
                        (account.ballance + account.credit) > \
                        notification.balance_edge:
                    an.ballance_notification_count = 0
                    an.ballance_notification_last_date = None
                    an.save()
                    continue

                if an.ballance_notification_count >= \
                    notification.balance_notifications_limit or \
                    (an.ballance_notification_last_date and
                     an.ballance_notification_last_date <
                     (now - datetime.timedelta(
                         days=notification.balance_notifications_each))):
                    # if notifications count reached and nothing changed
                    continue

                if (account.ballance + account.credit) <= \
                        notification.balance_edge:
                    an.ballance_notification_count += 1
                    an.ballance_notification_last_date = now
                    if account.disable_notifications:
                        item = Message()
                        item.account = account
                        item.backend = notification.backend
                        if notification.notification_type == 'SMS':
                            item.to = account.phone_m
                        else:
                            item.to = account.email
                        t = Template(
                            notification.balance_notifications_template)
                        c = {"account": account}
                        item.body = t.render(c)
                        item.publish_date = now
                        item.save()
                        item.send()
                an.save()

            if notification.payment_notifications:
                if not an.payment_notification_last_date:
                    # If have no payment notifications - skip
                    an.payment_notification_last_date = now
                    an.save()
                    continue
                for item in (
                        Transaction.objects.filter(
                            account=account,
                            created__gte=an.payment_notification_last_date)):
                    if account.disable_notifications:
                        item = Message()
                        item.account = account
                        item.backend = notification.backend
                        if notification.notification_type == 'SMS':
                            item.to = account.phone_m
                        else:
                            item.to = account.email
                        t = Template(
                            notification.payment_notifications_template)
                        c = {
                            "account": account,
                            'transaction': item
                        }
                        item.body = t.render(c)
                        item.publish_date = now
                        item.save()
                        an.payment_notification_last_date = now

                        item.send()
                    an.save()
