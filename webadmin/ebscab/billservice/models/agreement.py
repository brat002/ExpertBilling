# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class SuppAgreement(models.Model):
    name = models.CharField(max_length=128, verbose_name=_(u"Название"))
    description = models.TextField(verbose_name=_(
        u'Комментарий'), blank=True, default='')
    body = models.TextField(verbose_name=_(
        u'Текст шаблона'), blank=True, default='')
    length = models.IntegerField(verbose_name=_(
        u"Длительность в днях"), blank=True, null=True)
    disable_tarff_change = models.BooleanField(
        verbose_name=_(u"Запретить смену тарифного плана"),
        blank=True,
        default=False
    )

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u"Вид доп. соглашения")
        verbose_name_plural = _(u"Виды доп. соглашения")

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('suppagreement_delete'), self.id)


class AccountSuppAgreement(models.Model):
    suppagreement = models.ForeignKey(
        SuppAgreement,
        verbose_name=_(u"Дополнительное соглашение"),
        on_delete=models.CASCADE
    )
    account = models.ForeignKey(
        'billservice.Account',
        verbose_name=_(u"Аккаунт"),
        on_delete=models.CASCADE)
    contract = models.CharField(_(u"Номер"), max_length=128)
    accounthardware = models.ForeignKey(
        'AccountHardware',
        blank=True,
        null=True,
        verbose_name=_(u"Связанное оборудование"),
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(_(u"Создано"))
    closed = models.DateTimeField(_(u"Закрыто"), blank=True, null=True)

    def __unicode__(self):
        return u"%s %s" % (self.suppagreement, self.account)

    class Meta:
        verbose_name = _(u"Дополнительное соглашение")
        verbose_name_plural = _(u"Дополнительные соглашения")

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accountsuppagreement_delete'), self.id)

    def to_end(self):
        return ((self.created +
                 datetime.timedelta(days=self.suppagreement.length)) -
                datetime.datetime.now()).days
