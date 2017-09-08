# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class HardwareType(models.Model):
    name = models.TextField()

    def __unicode__(self):
        return u'%s' % self.name

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('hardwaretype_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Тип оборудования")
        verbose_name_plural = _(u"Типы оборудования")
        permissions = (
            ("hardwaretype_view", _(u"Просмотр")),
        )


class Manufacturer(models.Model):
    name = models.TextField()

    def __unicode__(self):
        return u'%s' % self.name

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('manufacturer_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Производитель")
        verbose_name_plural = _(u"Производители")
        permissions = (
            ("manufacturer_view", _(u"Просмотр")),
        )


class Model(models.Model):
    name = models.TextField(verbose_name=_(u"Модель"))
    manufacturer = models.ForeignKey(
        'billservice.Manufacturer',
        verbose_name=_(u"Производитель"),
        on_delete=models.CASCADE
    )
    hardwaretype = models.ForeignKey(
        'billservice.HardwareType',
        verbose_name=_(u"Тип оборудования"),
        on_delete=models.CASCADE
    )

    def __unicode__(self):
        return u'%s/%s/%s' % (self.hardwaretype, self.manufacturer, self.name)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('model_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Модель оборудования")
        verbose_name_plural = _(u"Модель оборудования")
        permissions = (
            ("model_view", _(u"Просмотр")),
        )


class Hardware(models.Model):
    model = models.ForeignKey(
        'billservice.Model', verbose_name=_(u"Модель"), on_delete=models.CASCADE)
    name = models.CharField(
        max_length=500, blank=True, default='', verbose_name=_(u"Название"))
    sn = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name=_(u"Серийный номер")
    )
    ipaddress = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_(u"IP адрес")
    )
    macaddress = models.CharField(
        blank=True, default='', max_length=32, verbose_name=_(u"MAC адрес"))
    comment = models.TextField(
        blank=True, default='', verbose_name=_(u"Комментарий"))

    @property
    def manufacturer(self):
        return "%s" % self.model.manufacturer

    def __unicode__(self):
        return u'%s' % self.name

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('hardware_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Устройство")
        verbose_name_plural = _(u"Устройства")
        permissions = (
            ("hardware_view", _(u"Просмотр")),
        )
