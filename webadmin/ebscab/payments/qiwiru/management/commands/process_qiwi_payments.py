# -*- coding: utf-8 -*-

import datetime

from django.core.management.base import BaseCommand

from getpaid.models import Payment

from payments.qiwiru.backend import (
    params,
    payment_code,
    PaymentProcessor,
    status_code
)
from payments.qiwiru.utils import xml2obj


class Command(BaseCommand):
    help = 'Process QIWI payments'

    def handle(self, *args, **options):
        lifetime = PaymentProcessor.get_backend_setting('LIFETIME')
        terminal_id = PaymentProcessor.get_backend_setting('TERMINAL_ID')
        terminal_password = PaymentProcessor.get_backend_setting(
            'TERMINAL_PASSWORD')

        a = (Payment.objects
             .filter(status='in_progress',
                     created_on__gte=(datetime.datetime.now() -
                                      datetime.timedelta(hours=lifetime))))
        pattern = '<bill txn-id="%s"/>'
        p = ''
        for x in a:
            p += pattern % x.id

        xml = PaymentProcessor.make_request(params['get_invoices_status'] % {
            'TERMINAL_PASSWORD': terminal_password,
            'TERMINAL_ID': terminal_id,
            'BILLS': p
        })
        print xml

        o = xml2obj(xml)
        if status_code(o)[0] != 0:
            return
        for x in a:
            if not o.bills_list:
                continue
            for item in o.bills_list.bill:
                p_code, _ = payment_code(item)
                if p_code == 60 and int(item.id) == x.id:
                    x.on_success(amount=x.amount)
                    x.save()
                    continue
            if p_code > 100:
                x.deleted = True
                x.save()
