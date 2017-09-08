# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from billservice.models.constants import PERIOD_CHOISES


class SettlementPeriod(models.Model):
    """
    Расчётный период
    """
    name = models.CharField(
        max_length=255, verbose_name=_(u'Название'), unique=True)
    time_start = models.DateTimeField(verbose_name=_(u'Начало периода'))
    length = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        verbose_name=_(u'Период действия в секундах')
    )
    length_in = models.CharField(
        max_length=255,
        choices=PERIOD_CHOISES,
        null=True,
        blank=True,
        default='',
        verbose_name=_(u'Длина промежутка')
    )
    autostart = models.BooleanField(
        verbose_name=_(u'Начинать при активации'),
        default=False
    )

    def __unicode__(self):
        return u"%s%s" % ("+" if self.autostart else '', self.name, )

    class Admin:
        list_display = (
            'name',
            'time_start',
            'length',
            'length_in',
            'autostart'
        )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('settlementperiod_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Расчетный период")
        verbose_name_plural = _(u"Расчетные периоды")
        permissions = (
            ("settlementperiod_view", _(u"Просмотр расчётных периодов")),
        )


class SuspendedPeriod(models.Model):
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE)
    start_date = models.DateTimeField(verbose_name=_(u"Дата начала"))
    end_date = models.DateTimeField(
        verbose_name=_(u"Дата конца"), blank=True, null=True)
    activated_by_account = models.BooleanField(
        verbose_name=_(u"Активировано аккаунтом"), blank=True, default=False)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('suspendedperiod_delete'), self.id)

    class Meta:
        ordering = ['-start_date']
        verbose_name = _(u"Период без списаний")
        verbose_name_plural = _(u"Периоды без списаний")
        permissions = (
            ("suspendedperiod_view", _(u"Просмотр")),
        )


class TimePeriod(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(
        u'Название группы временных периодов'), unique=True)

    def in_period(self):
        for time_period_node in self.time_period_nodes:
            if time_period_node.in_period() == True:
                return True
        return False

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name',)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Временной период")
        verbose_name_plural = _(u"Временные периоды")
        permissions = (
            ("timeperiod_view", _(u"Просмотр временных периодов")),
        )


class TimePeriodNode(models.Model):
    u"""Диапазон времени (с 15 00 до 18 00 каждую вторник-пятницу, утро, ночь,
    сутки, месяц, год и т.д.)
    """
    time_period = models.ForeignKey(
        'billservice.TimePeriod',
        verbose_name=_(u"Период времени"),
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_(u'Название подпериода'),
        default='',
        blank=True
    )
    time_start = models.DateTimeField(
        verbose_name=_(u'Дата и время начала'),
        default='',
        blank=True
    )
    length = models.IntegerField(
        verbose_name=_(u'Длительность в секундах'),
        default=0,
        blank=True
    )
    repeat_after = models.CharField(
        max_length=255,
        choices=PERIOD_CHOISES,
        verbose_name=_(u'Повторять через'),
        default='DAY',
        blank=True
    )

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u"Нода временного периода")
        verbose_name_plural = _(u"Ноды временных периодов")
        permissions = (
            ("timeperiodnode_view", _(u"Просмотр нод временных периодов")),
        )
