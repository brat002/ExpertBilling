# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse


class TotalTransactionReport(models.Model):
    service_id = models.IntegerField()
    table = models.CharField(max_length=128)
    created = models.DateTimeField()
    tariff = models.ForeignKey(
        'billservice.Tariff', blank=True, null=True, on_delete=models.CASCADE)
    summ = models.DecimalField(decimal_places=10, max_digits=30)
    prev_balance = models.DecimalField(
        verbose_name=(u'Предыдущий баланс'),
        decimal_places=5,
        max_digits=20,
        blank=True,
        default=0
    )
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE)
    type = models.ForeignKey(
        'billservice.TransactionType',
        to_field='internal_name',
        on_delete=models.CASCADE
    )
    is_bonus = models.BooleanField(
        blank=True, default=False, verbose_name=u'Бонус')
    systemuser = models.ForeignKey(
        'billservice.SystemUser',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    bill = models.TextField()
    description = models.TextField()
    end_promise = models.DateTimeField()
    promise_expired = models.BooleanField(default=False)

    def get_remove_url(self):
        return "%s?type=%s&id=%s" % (reverse('totaltransaction_delete'), (self.table, self.id))

    class Meta:
        managed = False
        abstract = False
        ordering = ['-created']
