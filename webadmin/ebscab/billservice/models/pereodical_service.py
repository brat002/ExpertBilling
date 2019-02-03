# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from billservice.models.constants import CASH_METHODS
from ebscab.utils.decorators import to_partition


class PeriodicalService(models.Model):
    """
    Справочник периодических услуг
    TODO: Сделать справочники валют
    """
    ps_condition = (
        (0, _(u'При любом балансе')),
        (1, _(u'Меньше')),
        (2, _(u'Меньше или равно')),
        (3, _(u'Равно')),
        (4, _(u'Больше или равно')),
        (5, _(u'Больше'))
    )
    tarif = models.ForeignKey('billservice.Tariff', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_(u'Название'))
    settlement_period = models.ForeignKey(
        to='billservice.SettlementPeriod',
        verbose_name=_(u'Период'),
        null=True,
        on_delete=models.SET_NULL
    )
    cost = models.DecimalField(
        verbose_name=_(u'Стоимость'),
        default=0,
        blank=True,
        decimal_places=2,
        max_digits=30
    )
    cash_method = models.CharField(
        verbose_name=_(u'Способ списания'),
        max_length=255,
        choices=CASH_METHODS,
        default='AT_START',
        blank=True
    )
    tpd = models.SmallIntegerField(
        verbose_name=_(u'Кол-во списаний в сутки'),
        default=1,
        blank=True,
        null=True
    )
    ps_condition = models.IntegerField(
        verbose_name=_(u"Условие списания"),
        default=0,
        choices=ps_condition
    )
    condition_summ = models.DecimalField(
        verbose_name=_(u'Сумма для условия'),
        default=0,
        blank=True,
        decimal_places=2,
        max_digits=30
    )
    delta_from_ballance = models.BooleanField(
        verbose_name=_(u"Пропорциональное списание"),
        help_text=_(u"Рассчитать сумму списания, пропорционально моменту "
                    u"срабатывания условия по баллансу в расчётном периоде."),
        blank=True,
        default=True
    )
    deactivated = models.DateTimeField(
        verbose_name=_(u"Отключить"), blank=True, null=True)
    created = models.DateTimeField(
        verbose_name=_(u"Активировать"),
        help_text=_(u'Не указывайте, если списания должны начаться с начала '
                    u"расчётного периода"),
        blank=True,
        null=True
    )
    deleted = models.BooleanField(blank=True, default=False, db_index=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name', 'settlement_period', 'cost', 'cash_method')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('periodicalservice_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Периодическая услуга")
        verbose_name_plural = _(u"Периодические услуги")
        permissions = (
            ("periodicalservice_view", _(u"Просмотр периодических услуг")),
        )


class PeriodicalServiceHistory(models.Model):
    service = models.ForeignKey(
        to='billservice.PeriodicalService',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    accounttarif = models.ForeignKey(
        to='billservice.AccountTarif', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    summ = models.DecimalField(decimal_places=5, max_digits=20)
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
        null=True,
        on_delete=models.SET_NULL
    )
    real_created = models.DateTimeField(
        verbose_name=_(u'Реальная дата списания'), auto_now_add=True)

    def __unicode__(self):
        return u"%s" % (self.service)

    class Admin:
        list_display = ('service', 'transaction', 'datetime')

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"История по пер. услугам")
        verbose_name_plural = _(u"История по пер. услугам")
        permissions = (
            ("periodicalservicehistory_view", _(u"Просмотр списаний")),
        )

    @to_partition
    def save(self, *args, **kwargs):
        super(PeriodicalServiceHistory, self).save(*args, **kwargs)


class PeriodicalServiceLog(models.Model):
    service = models.ForeignKey(
        'billservice.PeriodicalService',
        verbose_name=_(u'Услуга'),
        on_delete=models.CASCADE
    )
    accounttarif = models.ForeignKey(
        'billservice.AccountTarif',
        verbose_name=_(u'Тариф аккаунта'),
        on_delete=models.CASCADE
    )
    datetime = models.DateTimeField(verbose_name=_(u'Последнее списание'))

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('periodicalservicelog_delete'), self.id)

    class Meta:
        ordering = ['-datetime']
