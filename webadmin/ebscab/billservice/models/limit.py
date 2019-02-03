# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class SpeedLimit(models.Model):
    change_speed_type = models.CharField(
        verbose_name=_(u"Способ изменения скорости"),
        max_length=32,
        choices=(
            ("add", _(u"Добавить к текущей")),
            ("abs", _(u"Абсолютное значение"))
        ),
        blank=True,
        null=True
    )
    speed_units = models.CharField(
        default='Kbps',
        verbose_name=_(u'Единицы измерения скорости'),
        max_length=32,
        choices=(
            ('Kbps', 'Kbps'),
            ('Mbps', 'Mbps')
        ),
        blank=True,
        null=True
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
        verbose_name=_(u'Приоритет'), default=0)

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
