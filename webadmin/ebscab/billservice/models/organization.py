# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from billservice.models.utils import validate_phone


class Organization(models.Model):
    account = models.ForeignKey('billservice.Account', blank=True, null=True)
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_(u"Название организации")
    )
    uraddress = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_(u"Юр. адрес"))
    okpo = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_(u"ОКПО")
    )
    kpp = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_(u"КПП")
    )
    kor_s = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_(u"Корреспонденский счёт")
    )
    unp = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_(u"УНП")
    )
    phone = models.CharField(
        validators=[validate_phone],
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_(u"Телефон")
    )
    fax = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_(u"Факс")
    )
    bank = models.ForeignKey(
        'billservice.BankData',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_(u"Банк")
    )

    def __unicode__(self):
        return u"%s" % (self.name, )

    class Meta:
        permissions = (
            ("organization_view", _(u"Просмотр организации")),
        )
