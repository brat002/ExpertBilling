# -*- coding: utf-8 -*-

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from payments.w1ru import PaymentProcessor
from getpaid.models import Payment
import datetime
from payments.qiwiru import PaymentProcessor, params, status_code, payment_code
from payments.qiwiru.xml_helper import xml2obj


class Command(BaseCommand):
    help = 'Process QIWI payments'

    def handle(self, *args, **options):

        a = Payment.objects.filter(status='in_progress', created_on__gte=datetime.datetime.now(
        ) - datetime.timedelta(hours=PaymentProcessor.get_backend_setting('LIFETIME')))
        pattern = '<bill txn-id="%s"/>'
        p = ''
        for x in a:
            p += pattern % x.id

        xml = PaymentProcessor.make_request(params['get_invoices_status'] % {
            "TERMINAL_PASSWORD": PaymentProcessor.get_backend_setting('TERMINAL_PASSWORD'),
            "TERMINAL_ID": PaymentProcessor.get_backend_setting('TERMINAL_ID'),
            "BILLS": p
        })
        print xml
        o = xml2obj(xml)
        if status_code(o)[0] != 0:
            return
        for x in a:
            if not o.bills_list:
                continue
            for item in o.bills_list.bill:
                p_code, p_status = payment_code(item)
                if p_code == 60 and int(item.id) == x.id:
                    x.on_success(amount=x.amount)
                    x.save()
                    continue
            if p_code > 100:
                x.deleted = True
                x.save()
