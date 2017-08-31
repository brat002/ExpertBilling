# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from webmoney.models import Invoice


class Command(BaseCommand):
    help = "Clean unpayed invoces older than one day."

    def handle_noargs(self, **options):
        (Invoice.objects
            .filter(created_on__lt=datetime.utcnow() - timedelta(days=1),
                    payment__isnull=True)
            .delete())
