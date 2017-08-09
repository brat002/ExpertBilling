# -*- coding: utf-8 -*-

from django.db import models

from billservice.models import Account


PAYMENT_MODE_CHOICES = (
    (0, 'REAL'),
    (1, 'TEST')
)


class Payment(models.Model):
    account = models.ForeignKey(Account, related_name='webmoney_account_set')
    created = models.DateTimeField(auto_now_add=True, editable=False)

    purse = models.CharField(max_length=32)

    amount = models.DecimalField(decimal_places=2, max_digits=9)

    mode = models.PositiveSmallIntegerField(choices=PAYMENT_MODE_CHOICES)

    sys_invs_no = models.PositiveIntegerField()
    sys_trans_no = models.PositiveIntegerField()
    sys_trans_date = models.DateTimeField()

    payer_purse = models.CharField(max_length=13)
    payer_wm = models.CharField(max_length=12)

    paymer_number = models.CharField(max_length=30, blank=True)
    paymer_email = models.EmailField(blank=True)

    telepat_phonenumber = models.CharField(max_length=30, blank=True)
    telepat_orderid = models.CharField(max_length=30, blank=True)

    payment_creditdays = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        return "%s - %s WM%s" % (self.payment_no, self.amount, self.purse)
