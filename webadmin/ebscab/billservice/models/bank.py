# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class BankData(models.Model):
    bank = models.CharField(max_length=255, verbose_name=_(u"Название банка"))
    bankcode = models.CharField(
        blank=True, default='', max_length=40, verbose_name=_(u"Код банка"))
    rs = models.CharField(
        blank=True,
        default='',
        max_length=60,
        verbose_name=_(u"Расчётный счёт")
    )
    currency = models.CharField(
        blank=True,
        default='',
        max_length=40,
        verbose_name=_(u"Валюта расчётов")
    )

    def __unicode__(self):
        return u"%s" % self.id

    class Meta:
        ordering = ['bank']
        verbose_name = _(u"Банк")
        verbose_name_plural = _(u"Банки")
        permissions = (
            ("view", _(u"Просмотр банков")),
        )
