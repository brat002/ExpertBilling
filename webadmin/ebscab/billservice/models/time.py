# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class TimeAccessService(models.Model):
    """
    Доступ с тарификацией по времени
    """
    prepaid_time = models.IntegerField(
        verbose_name=_(u'Предоплаченное время'), default=0, blank=True)
    reset_time = models.BooleanField(
        verbose_name=_(u'Сбрасывать  предоплаченное время'),
        blank=True,
        default=False
    )
    tarification_step = models.IntegerField(
        verbose_name=_(u"Тарифицировать по, c."), blank=True, default=60)
    rounding = models.IntegerField(
        verbose_name=_(u"Округлять"),
        default=0,
        blank=True,
        choices=(
            (0, _(u"Не округлять")),
            (1, _(u"В большую сторону"))
        )
    )

    def __unicode__(self):
        return u"%s" % self.id

    class Admin:
        list_display = ('prepaid_time',)

    class Meta:
        verbose_name = _(u"Доступ с учётом времени")
        verbose_name_plural = _(u"Доступ с учётом времени")
        permissions = (
            ("timeaccessservice_view", _(u"Просмотр услуг доступа по времени")),
        )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('tariff_timeaccessservice_delete'), self.id)


class TimeAccessNode(models.Model):
    """
    Нода тарификации по времени
    """
    time_access_service = models.ForeignKey(
        to='billservice.TimeAccessService',
        related_name="time_access_nodes",
        on_delete=models.CASCADE
    )
    time_period = models.ForeignKey(
        to='billservice.TimePeriod',
        verbose_name=_(u'Промежуток'),
        null=True,
        on_delete=models.SET_NULL
    )
    cost = models.FloatField(verbose_name=_(u'Стоимость за минуту'), default=0)

    def __unicode__(self):
        return u"%s %s" % (self.time_period, self.cost)

    class Admin:
        ordering = ['name']
        list_display = ('time_period', 'cost')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('timeaccessnode_delete'), self.id)

    class Meta:
        verbose_name = _(u"Период доступа")
        verbose_name_plural = _(u"Периоды доступа")
        permissions = (
            ("timeacessnode_view", _(u"Просмотр")),
        )


class TimeSpeed(models.Model):
    """
    Настройки скорости в интервал времени
    """
    access_parameters = models.ForeignKey(
        to='billservice.AccessParameters',
        related_name="access_speed",
        on_delete=models.CASCADE
    )
    time = models.ForeignKey(
        'billservice.TimePeriod', on_delete=models.CASCADE)
    # от 1 до 8
    priority = models.IntegerField(
        verbose_name=_(u"Приоритет"), blank=True, default=8)

    max_tx = models.CharField(
        verbose_name=_(u"MAX tx (kbps)"),
        max_length=64,
        blank=True,
        default=""
    )
    max_rx = models.CharField(
        verbose_name=_(u"rx"), max_length=64, blank=True, default="")
    burst_tx = models.CharField(
        verbose_name=_(u"Burst tx (kbps)"),
        max_length=64,
        blank=True,
        default=""
    )
    burst_rx = models.CharField(
        verbose_name=_(u"rx"), max_length=64, blank=True, default="")
    burst_treshold_tx = models.CharField(
        verbose_name=_(u"Burst treshold tx (kbps)"),
        max_length=64,
        blank=True,
        default=""
    )
    burst_treshold_rx = models.CharField(
        verbose_name=_(u"rx"), max_length=64, blank=True, default="")
    burst_time_tx = models.CharField(
        verbose_name=_(u"Burst time tx (s)"),
        max_length=64,
        blank=True,
        default=""
    )
    burst_time_rx = models.CharField(
        verbose_name=_(u"rx"), max_length=64, blank=True, default="")
    min_tx = models.CharField(
        verbose_name=_(u"Min tx (kbps)"),
        max_length=64,
        blank=True,
        default=""
    )
    min_rx = models.CharField(
        verbose_name=_(u"tx"), max_length=64, blank=True, default="")

    def __unicode__(self):
        return u"%s" % self.time

    class Admin:
        pass

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('tariff_timespeed_delete'), self.id)

    class Meta:
        verbose_name = _(u"Настройка скорости")
        verbose_name_plural = _(u"Настройки скорости")
        permissions = (
            ("timespeed_view", _(u"Просмотр")),
        )


class TimeTransaction(models.Model):
    timeaccessservice = models.ForeignKey(
        'billservice.TimeAccessService', null=True, on_delete=models.SET_NULL)
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE)
    summ = models.FloatField()
    prev_balance = models.DecimalField(
        verbose_name=_(u'Предыдущий баланс'),
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
        verbose_name = _(u"Списание за время")
        verbose_name_plural = _(u"Списания за время")
        permissions = (
            ("transaction_view", _(u"Просмотр")),
        )
