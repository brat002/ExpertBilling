# -*- coding: utf-8 -*-

import datetime

import IPy
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q


class IPPool(models.Model):
    name = models.CharField(verbose_name=_(u'Название'), max_length=255)
    # 0 - VPN, 1-IPN
    type = models.IntegerField(
        verbose_name=_(u'Тип'),
        choices=(
            (0, _(u"IPv4 VPN")),
            (1, _(u"IPv4 IPN")),
            (2, _(u"IPv6 VPN")),
            (3, _(u"IPv6 IPN"))
        )
    )
    start_ip = models.GenericIPAddressField(verbose_name=_(u'C IP'))
    end_ip = models.GenericIPAddressField(verbose_name=_(u'По IP'))
    next_ippool = models.ForeignKey(
        'billservice.IPPool',
        verbose_name=_(u'Следующий пул'),
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['name']
        verbose_name = _(u"IP пул")
        verbose_name_plural = _(u"IP пулы")
        permissions = (
            ("ippool_view", _(u"Просмотр")),
        )

    def __unicode__(self):
        return u"%s" % self.name

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('ippool_delete'), self.id)

    def get_pool_size(self):
        return IPy.IP(self.end_ip).int() - IPy.IP(self.start_ip).int()

    def get_used_ip_count(self):
        return (self.ipinuse_set
                .filter(Q(dynamic=True,
                          last_update__gte=datetime.datetime.now() -
                          datetime.timedelta(minutes=15)) |
                        Q(dynamic=False, disabled__isnull=True))
                .count())


class IPInUse(models.Model):
    pool = models.ForeignKey('billservice.IPPool', verbose_name=_(u'IP пул'))
    ip = models.CharField(max_length=255, verbose_name=_(u'IP адрес'))
    datetime = models.DateTimeField(verbose_name=_(u'Дата выдачи'))
    disabled = models.DateTimeField(
        blank=True, null=True, verbose_name=_(u'Дата освобождения'))
    dynamic = models.BooleanField(
        default=False, verbose_name=_(u'Выдан динамически'))
    ack = models.BooleanField(
        default=False, blank=True, verbose_name=_(u'Подтверждён'))
    last_update = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_(u'Последнее обновление'),
        help_text=_(u'Для динамической выдачи')
    )

    class Meta:
        ordering = ['ip']
        verbose_name = _(u"Занятый IP адрес")
        verbose_name_plural = _(u"Занятые IP адреса")
        permissions = (
            ("ipinuse_view", _(u"Просмотр")),
        )

    def __unicode__(self):
        return u"%s" % self.ip
