# -*- coding: utf-8 -*-

import datetime

from django.dispatch import Signal
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from ebscab.utils.decorators import to_partition


new_transaction = Signal()


class TransactionType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    internal_name = models.CharField(max_length=32, unique=True)
    is_deletable = models.BooleanField(
        verbose_name=_(u'Может быть удалён'), blank=True, default=True)
    allowed_systemusers = models.ManyToManyField(
        'billservice.SystemUser',
        verbose_name=_(u'Разрешено выполнять'),
        blank=True
    )
    is_bonus = models.BooleanField(
        verbose_name=_(u'Является бонусной'), blank=True, default=False)

    def __unicode__(self):
        return u"%s" % (self.name,)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('transactiontype_delete'), self.id)

    class Admin:
        pass

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Тип проводки")
        verbose_name_plural = _(u"Типы проводок")
        permissions = (
            ("transactiontype_view", _(u"Просмотр")),
        )


class Transaction(models.Model):
    bill = models.CharField(
        blank=True,
        default="",
        max_length=255,
        verbose_name=_(u"Платёжный документ")
    )
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE, verbose_name=_(u"Аккаунт"))
    accounttarif = models.ForeignKey(
        'billservice.AccountTarif', blank=True, null=True, on_delete=models.CASCADE)
    type = models.ForeignKey(
        to='billservice.TransactionType',
        null=True,
        to_field='internal_name',
        verbose_name=_(u"Тип"),
        on_delete=models.SET_NULL
    )

    is_bonus = models.BooleanField(
        default=False, blank=True, verbose_name=_(u'Бонус'))
    approved = models.BooleanField(default=True)
    tarif = models.ForeignKey(
        'billservice.Tariff', blank=True, null=True, on_delete=models.SET_NULL)
    summ = models.DecimalField(
        default=0,
        blank=True,
        verbose_name=_(u"Сумма"),
        decimal_places=10,
        max_digits=20
    )
    prev_balance = models.DecimalField(
        verbose_name=(u'Предыдущий баланс'),
        decimal_places=5,
        max_digits=20,
        blank=True,
        default=0
    )
    description = models.TextField(
        default='', blank=True, verbose_name=_(u"Комментарий"))
    created = models.DateTimeField(verbose_name=_(u"Дата"))
    end_promise = models.DateTimeField(
        blank=True, null=True, verbose_name=_(u"Закрыть ОП"))
    promise_expired = models.BooleanField(
        default=False, verbose_name=_(u"ОП истек"))
    systemuser = models.ForeignKey(
        to='billservice.SystemUser',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_(u"Выполнил")
    )

    @to_partition
    def save(self, *args, **kwargs):
        if not self.id:
            new_transaction.send(sender=self)
        if not (self.id and self.created):
            self.created = datetime.datetime.now()
        super(Transaction, self).save(*args, **kwargs)

    class Admin:
        list_display = ('account', 'tarif', 'summ', 'description', 'created')

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Проводка")
        verbose_name_plural = _(u"Проводки")
        permissions = (
            ("transaction_view", _(u"Просмотр")),
        )

    @staticmethod
    def create_payment(account, summ, created, bill, trtype):
        tr = Transaction()
        tr.account = account
        tr.bill = bill
        tr.summ = summ
        tr.created = created
        tr.type = TransactionType.objects.get(internal_name=trtype)
        tr.save()

    def human_sum(self):
        return self.summ

    def __unicode__(self):
        return u"%s, %s, %s" % (self.account, self.summ, self.created)
