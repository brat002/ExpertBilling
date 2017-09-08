# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Operator(models.Model):
    organization = models.CharField(
        verbose_name=_(u'Название'), max_length=255)
    unp = models.CharField(
        verbose_name=_(u'УНП'), max_length=40, blank=True, default='')
    okpo = models.CharField(
        verbose_name=_(u'ОКПО'), max_length=40, blank=True, default='')
    contactperson = models.CharField(
        verbose_name=_(u'Контактное лицо'),
        max_length=255,
        blank=True,
        default=''
    )
    director = models.CharField(
        verbose_name=_(u'Директор'), max_length=255, blank=True, default='')
    phone = models.CharField(
        verbose_name=_(u'Телефон'), max_length=40, blank=True, default='')
    fax = models.CharField(
        verbose_name=_(u'Факс'), max_length=40, blank=True, default='')
    postaddress = models.CharField(
        verbose_name=_(u'Почтовый адрес'),
        max_length=255,
        blank=True,
        default=''
    )
    uraddress = models.CharField(
        verbose_name=_(u'Юр. адрес'), max_length=255, blank=True, default='')
    email = models.EmailField(
        verbose_name=_(u'E-mail'), max_length=255, blank=True, default='')

    def __unicode__(self):
        return u"%s" % self.organization

    class Meta:
        verbose_name = _(u"Информация о провайдере")
        verbose_name_plural = _(u"Информация о провайдере")
        permissions = (
            ("operator_view", _(u"Просмотр")),
        )
