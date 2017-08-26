# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class SpeedLimit(models.Model):
    change_speed_type = models.CharField(
        verbose_name=_(u"Способ изменения скорости"),
        max_length=32,
        choices=(
            ("add", "Добавить к текущей"),
            ("abs", "Абсолютное значение")
        ),
        blank=True,
        null=True
    )
    speed_units = models.CharField(
        verbose_name=_(u"Единицы"),
        max_length=32,
        choices=(
            ("Kbps", "Kbps"),
            ("Mbps", "Mbps"),
            ("%", "%")
        ),
        blank=True,
        null=True
    )
    max_tx = models.IntegerField(
        verbose_name=_(u"MAX tx (kbps)"), default=0, blank=True)
    max_rx = models.IntegerField(
        verbose_name=_(u"rx"), default=0, blank=True)
    t_tx = models.IntegerField(
        verbose_name=_(u"Burst tx (kbps)"), default=0, blank=True)
    burst_rx = models.IntegerField(
        verbose_name=_(u"rx"), blank=True, default=0)
    burst_treshold_tx = models.IntegerField(
        verbose_name=_(u"Burst treshold tx (kbps)"), default=0, blank=True)
    burst_treshold_rx = models.IntegerField(
        verbose_name=_(u"rx"), default=0, blank=True)
    burst_time_tx = models.IntegerField(
        verbose_name=_(u"Burst time tx (kbps)"), default=0, blank=True)
    burst_time_rx = models.IntegerField(
        verbose_name=_(u"rx"), default=0, blank=True)
    min_tx = models.IntegerField(
        verbose_name=_(u"Min tx (kbps)"), default=0, blank=True)
    min_rx = models.IntegerField(verbose_name=_(u"tx"), default=0, blank=True)
    priority = models.IntegerField(default=0, blank=True)

    def __unicode__(self):
        return "%s/%s %s/%s %s/%s %s/%s %s/%s %s" % (self.max_tx,
                                                     self.max_rx,
                                                     self.burst_tx,
                                                     self.burst_rx,
                                                     self.burst_treshold_tx,
                                                     self.burst_treshold_rx,
                                                     self.burst_time_tx,
                                                     self.burst_time_rx,
                                                     self.min_tx,
                                                     self.min_rx,
                                                     self.priority)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('speedlimit_delete'), self.id)
