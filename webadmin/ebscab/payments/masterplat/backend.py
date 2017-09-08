# -*- coding: utf-8 -*-

import datetime

from django.utils.translation import ugettext_lazy as _

from billservice.models import Account
from getpaid.backends import PaymentProcessorBase
from getpaid.models import Payment


class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'payments.masterplat'
    BACKEND_NAME = _('Masterpay backend')
    BACKEND_ACCEPTED_CURRENCY = ('RUB',)

    @staticmethod
    def error(body, text):
        return 'status=%s' % text

    @staticmethod
    def compute_sig(body):
        return ''

    @staticmethod
    def check(request, body):
        acc = body.get('cid')
        dealer = body.get('duser')
        password = body.get('dpass')

        if PaymentProcessor.get_backend_setting('DUSER') != dealer or \
                PaymentProcessor.get_backend_setting('DPASS') != password:
            return PaymentProcessor.error(body, u'-4')

        try:
            account = Account.objects.get(contract=acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(body, u'-1')

        ret = 'status=0&summa=%.2s' % (account.ballance or 0)
        return ret

    @staticmethod
    def pay(request, body):
        acc = body.get('cid')
        dealer = body.get('duser')
        password = body.get('dpass')
        orderid = body.get('trans')
        amount = body.get('sum')

        if PaymentProcessor.get_backend_setting('DUSER') != dealer or \
                PaymentProcessor.get_backend_setting('DPASS') != password:
            return PaymentProcessor.error(body, u'-4')

        try:
            account = Account.objects.get(contract=acc)
        except Account.DoesNotExist, ex:
            return PaymentProcessor.error(body, u'-1')

        if amount > 0:
            payment = Payment.create(
                account,
                None,
                PaymentProcessor.BACKEND,
                amount=amount,
                external_id=orderid)
            dt = datetime.datetime.now()
            payment.paid_on = dt
            payment.amount_paid = payment.amount
            payment.save()
            payment.change_status('paid')
        return 'status=0&summa=%.2f' % (Account.objects
                                        .get(contract=acc).ballance)
