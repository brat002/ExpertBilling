
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from sendsms.models import Message
from billservice.models import NotificationsSettings, AccountNotification, Account
import datetime


class Command(BaseCommand):
    help = 'Process email/sms ballance notifications'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        items = NotificationsSettings.objects.all()
        notifications = {}
        
        for n in items:
            for t in n.tariffs:
                notifications[t.id] = n
        
        accounts = Account.objects.extra(select={'tarif_id': 'get_tarif(billservice_account.id)'})
        
        for account in accounts:
            notification = notifications.get(account.tarif_id)
            if not notification: continue
            if notification.balance_notifications and (account.ballance+account.credit)<=notification.balance_edge:
                an = AccountNotification.objects.filter(account = account, notificationsettings=notification)
                if an:
                    an = an[0]
                    if an.ballance_notification_count>=notification.balance_notifications_limit or (datetime.datetime.now()-an.ballance_notification_last_date)<an.balance_notifications_each:
                        # вставить обнуление an
                        continue
                else:
                    an = AccountNotification()
                    an.account = account
                an.ballance_notification_count+=1
                an.ballance_notification_last_date = datetime.datetime.now()
                item = Message()
                item.account = account
                item.backend = notification.provider
                if notification.notification_type=='SMS':
                    item.to = account.phone_m
                else:
                    item.to = account.email
                item.body = notification.balance_notifications_template
                item.publish_date = datetime.datetime.now()
                item.save() 
                item.send()
                an.save()



