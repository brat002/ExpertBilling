# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class SheduleLog(models.Model):
    account = models.OneToOneField('billservice.Account')
    accounttarif = models.ForeignKey(
        to='billservice.AccountTarif',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    ballance_checkout = models.DateTimeField(blank=True, null=True)
    prepaid_traffic_reset = models.DateTimeField(blank=True, null=True)
    prepaid_traffic_accrued = models.DateTimeField(blank=True, null=True)
    prepaid_time_reset = models.DateTimeField(blank=True, null=True)
    prepaid_time_accrued = models.DateTimeField(blank=True, null=True)
    balance_blocked = models.DateTimeField(blank=True, null=True)

    class Admin:
        pass

    class Meta:
        verbose_name = _(u"История периодических операций")
        verbose_name_plural = _(u"История периодических операций")

    def __unicode__(self):
        return u'%s' % self.account.username
