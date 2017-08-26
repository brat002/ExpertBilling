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

    max_tx = models.CharField(
        verbose_name=_(u"MAX tx (kbps)"),
        max_length=64,
        blank=True,
        default=""
    )
    max_rx = models.CharField(
        verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")
    burst_tx = models.CharField(
        verbose_name=_(u"Burst tx (kbps)"),
        max_length=64,
        blank=True,
        default=""
    )
    burst_rx = models.CharField(
        verbose_name=_(u"rx (kbps)"),
        max_length=64,
        blank=True,
        default=""
    )
    burst_treshold_tx = models.CharField(
        verbose_name=_(u"Burst treshold tx (kbps)"),
        max_length=64,
        blank=True,
        default=""
    )
    burst_treshold_rx = models.CharField(
        verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")
    burst_time_tx = models.CharField(
        verbose_name=_(u"Burst time tx (s)"),
        max_length=64,
        blank=True,
        default=""
    )
    burst_time_rx = models.CharField(
        verbose_name=_(u"rx (s)"),
        max_length=64,
        blank=True,
        default=""
    )
    min_tx = models.CharField(
        verbose_name=_(u"Min tx (kbps)"),
        max_length=64,
        blank=True,
        default=""
    )
    min_rx = models.CharField(
        verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")

    # от 1 до 8
    priority = models.IntegerField(
        verbose_name=_(u"Приоритет"), blank=True, default=8)
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
