# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from nas.models import TrafficClass


class TrafficLimit(models.Model):
    tarif = models.ForeignKey('billservice.Tariff', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_(u'Название'))
    settlement_period = models.ForeignKey(
        to='billservice.SettlementPeriod',
        verbose_name=_(u'Период'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_(u"Если период не указан-берётся период тарифного плана. "
                    u"Если установлен автостарт-началом периода будет "
                    u"считаться день привязки тарифного плана пользователю. "
                    u"Если не установлен-старт берётся из расчётного периода")
    )
    size = models.IntegerField(verbose_name=_(u'Размер в байтах'), default=0)
    group = models.ForeignKey(
        'billservice.Group',
        verbose_name=_(u"Группа"),
        on_delete=models.CASCADE
    )
    mode = models.BooleanField(
        default=False,
        blank=True,
        verbose_name=_(u'За длинну расчётного периода'),
        help_text=_(u'Если флаг установлен-то количество трафика считается '
                    u'за последние N секунд, указанные в расчётном периоде')
    )
    action = models.IntegerField(
        verbose_name=_(u"Действие"),
        blank=True,
        default=0,
        choices=(
            (0, _(u"Заблокировать пользователя")),
            (1, _(u"Изменить скорость"))
        )
    )
    speedlimit = models.ForeignKey(
        'billservice.SpeedLimit',
        verbose_name=_(u"Изменить скорость"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name', 'settlement_period')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('trafficlimit_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Лимит трафика")
        verbose_name_plural = _(u"Лимиты трафика")
        permissions = (
            ("trafficlimit_view", _(u"Просмотр")),
        )


class TrafficTransaction(models.Model):
    traffictransmitservice = models.ForeignKey(
        'billservice.TrafficTransmitService',
        null=True,
        on_delete=models.SET_NULL
    )
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE)
    summ = models.FloatField()
    prev_balance = models.DecimalField(
        verbose_name=(u'Предыдущий баланс'),
        decimal_places=5,
        max_digits=20,
        blank=True,
        default=0
    )
    created = models.DateTimeField()
    accounttarif = models.ForeignKey(
        'billservice.AccountTarif', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Списание за трафик")
        verbose_name_plural = _(u"Списания за трафик")
        permissions = (
            ("traffictransaction_view", _(u"Просмотр")),
        )


class TrafficTransmitNodes(models.Model):
    traffic_transmit_service = models.ForeignKey(
        to='billservice.TrafficTransmitService',
        verbose_name=_(u"Услуга доступа по трафику"),
        related_name="traffic_transmit_nodes",
        on_delete=models.CASCADE
    )
    timeperiod = models.ForeignKey(
        to='billservice.TimePeriod',
        verbose_name=_(u'Промежуток времени'),
        null=True,
        on_delete=models.SET_NULL
    )
    group = models.ForeignKey(
        to='billservice.Group',
        verbose_name=_(u'Группа трафика'),
        null=True,
        on_delete=models.SET_NULL
    )
    cost = models.FloatField(default=0, verbose_name=_(u'Цена за мб.'))

    def __unicode__(self):
        return u"%s" % (self.cost)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('traffictransmitnode_delete'), self.id)

    class Meta:
        ordering = ['timeperiod', 'group']
        verbose_name = _(u"Цена за направление")
        verbose_name_plural = _(u"Цены за направления трафика")
        permissions = (
            ("traffictransmitnodes_view", _(u"Просмотр")),
        )


class TrafficTransmitService(models.Model):
    reset_traffic = models.BooleanField(
        verbose_name=_(u'Сбрасывать предоплаченный трафик'),
        blank=True,
        default=False
    )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('traffictransmitservice_delete'), self.id)

    class Meta:
        verbose_name = _(u"Доступ с учётом трафика")
        verbose_name_plural = _(u"Доступ с учётом трафика")
        permissions = (
            ("traffictransmitservice_view", _(u"Просмотр")),
        )


class PrepaidTraffic(models.Model):
    """
    Настройки предоплаченного трафика для тарифного плана
    """
    traffic_transmit_service = models.ForeignKey(
        to='billservice.TrafficTransmitService',
        verbose_name=_(u"Услуга доступа по трафику"),
        related_name="prepaid_traffic",
        on_delete=models.CASCADE
    )
    size = models.FloatField(
        verbose_name=_(u'Размер в байтах'), default=0, blank=True)
    group = models.ForeignKey(
        'billservice.Group', on_delete=models.CASCADE)

    def __unicode__(self):
        return u"%s" % self.size

    class Admin:
        ordering = ['traffic_class']
        list_display = ('size',)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('prepaidtraffic_delete'), self.id)

    class Meta:
        verbose_name = _(u"Предоплаченный трафик")
        verbose_name_plural = _(u"Предоплаченный трафик")
        permissions = (
            ("prepaidtraffic_view", _(u"Просмотр")),
        )


class Group(models.Model):
    # make it an array
    name = models.CharField(verbose_name=_(u'Название'), max_length=255)
    trafficclass = models.ManyToManyField(
        TrafficClass, verbose_name=_(u'Классы трафика'))
    # 1 - in, 2-out, 3 - sum, 4-max
    direction = models.IntegerField(
        verbose_name=_(u'Направление'),
        choices=(
            (0, _(u"Входящий")),
            (1, _(u"Исходящий")),
            (2, _(u"Вх.+Исх."))
        )
    )
    # 1 -sum, 2-max
    type = models.IntegerField(
        verbose_name=_(u'Тип'),
        choices=(
            (1, _(u"Сумма классов")),
            (2, _(u"Максимальный класс"))
        )
    )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('group_delete'), self.id)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Группа трафика")
        verbose_name_plural = _(u"Группы трафика")
        permissions = (
            ("group_view", _(u"Просмотр")),
        )
