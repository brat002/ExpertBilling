# -*- coding: utf-8 -*-

import datetime

from django.core.management.base import BaseCommand

from sendsms.models import Message


class Command(BaseCommand):
    help = 'Process QIWI payments'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        items = Message.objects.filter(
            publish_date__lte=now, sended__isnull=True)

        for item in items:
            item.send()
