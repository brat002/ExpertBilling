# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from billservice.models.constants import ACCESS_TYPE_METHODS


class AccessParameters(models.Model):
    access_type = models.CharField(
        max_length=255,
        choices=ACCESS_TYPE_METHODS,
        default='PPTP',
        blank=True,
        verbose_name=_(u'Способ доступа')
    )
    access_time = models.ForeignKey(
        to='billservice.TimePeriod',
        verbose_name=_(u'Доступ разрешён'),
        null=True,
        db_index=True,
        on_delete=models.SET_NULL
    )
    ipn_for_vpn = models.BooleanField(
        verbose_name=_(u'Выполнять IPN действия'), blank=True, default=False)

    speed_units = models.CharField(
        default='Kbps',
        verbose_name=_(u'Единицы измерения скорости'),
        max_length=32,
        choices=(
            ('Kbps', 'Kbps'),
            ('Mbps', 'Mbps')
        ),
        blank=True,
        null=True,
    )

    max_tx = models.IntegerField(
        verbose_name=_(u'Max Tx'), default=0)
    max_rx = models.IntegerField(
        verbose_name=_(u'Max Rx'), default=0)
    burst_tx = models.IntegerField(
        verbose_name=_(u'Burst Tx'), default=0)
    burst_rx = models.IntegerField(
        verbose_name=_(u'Burst Rx'), default=0)
    burst_treshold_tx = models.IntegerField(
        verbose_name=_(u'Burst treshold Tx'), default=0)
    burst_treshold_rx = models.IntegerField(
        verbose_name=_(u'Burst treshold Rx'), default=0)
    burst_time_tx = models.IntegerField(
        verbose_name=_(u'Burst time Tx (s)'), default=0)
    burst_time_rx = models.IntegerField(
        verbose_name=_(u'Burst time Rx (s)'), default=0)
    min_tx = models.IntegerField(
        verbose_name=_(u'Min Tx'), default=0)
    min_rx = models.IntegerField(
        verbose_name=_(u'Min Rx'), default=0)
    priority = models.IntegerField(
        verbose_name=_(u'Приоритет'), default=8)

    sessionscount = models.IntegerField(
        verbose_name=_(u"Одноверменных RADIUS сессий на субаккаунт"),
        blank=True,
        default=0
    )

    def __unicode__(self):
        return u"%s" % self.id

    class Admin:
        list_display = ('access_type',)

    class Meta:
        verbose_name = _(u"Параметры доступа")
        verbose_name_plural = _(u"Параметры доступа")
        permissions = (
            ("accessparameters_view", _(u"Просмотр параметров доступа")),
        )
