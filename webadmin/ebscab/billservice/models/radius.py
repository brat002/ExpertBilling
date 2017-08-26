# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from nas.models import Nas


class RadiusAttrs(models.Model):
    tarif = models.ForeignKey(
        'billservice.Tariff', blank=True, null=True, on_delete=models.CASCADE)
    nas = models.ForeignKey(
        Nas, blank=True, null=True, on_delete=models.CASCADE)
    vendor = models.IntegerField(blank=True, null=True, default=0)
    attrid = models.IntegerField(blank=True, null=True, default=0)
    account_status = models.IntegerField(
        choices=(
            (0, _(u'Всегда')),
            (1, _(u'Активен')),
            (2, _(u'Не активен'))
        ),
        default=0,
        verbose_name=_(u'Статус аккаунта'),
        help_text=_(u'Добавлять атрибут в Access Accept, если '
                    u'срабатывает условие')
    )
    attribute = models.CharField(
        max_length=255,
        verbose_name=_(u'Radius attribute name'),
        help_text=_(u"Radius attribute name like Service-Type")
    )
    value = models.CharField(
        max_length=255,
        verbose_name=_(u'Value'),
        help_text=_(u"Here you can use variables like $account_id, "
                    u'$tariff_id, ...')
    )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('radiusattr_delete'), self.id)

    class Meta:
        ordering = ['vendor', 'attrid']
        verbose_name = _(u"Custom RADIUS атрибут")
        verbose_name_plural = _(u"Custom RADIUS атрибуты")
        permissions = (
            ("radiusattrs_view", _(u"Просмотр")),
        )


class RadiusTraffic(models.Model):
    direction = models.IntegerField(
        verbose_name=_(u"Направление"),
        blank=True,
        default=2,
        choices=(
            (0, _(u"Входящий")),
            (1, _(u"Исходящий")),
            (2, _(u"Сумма")),
            (3, _(u"Максимум"))
        )
    )
    tarification_step = models.IntegerField(
        verbose_name=_(u"Единица тарификации, кб."),
        blank=True,
        default=1024
    )
    rounding = models.IntegerField(
        verbose_name=_(u"Округление"),
        default=0,
        blank=True,
        choices=(
            (0, _(u"Не округлять")),
            (1, _(u"В большую сторону"))
        )
    )
    prepaid_direction = models.IntegerField(
        blank=True,
        default=2,
        verbose_name=_(u"Предоплаченное направление"),
        choices=(
            (0, _(u"Входящий")),
            (1, _(u"Исходящий")),
            (2, _(u"Сумма")),
            (3, _(u"Максимум"))
        )
    )
    prepaid_value = models.IntegerField(
        verbose_name=_(u"Объём, мб."), blank=True, default=0)
    reset_prepaid_traffic = models.BooleanField(
        verbose_name=_(u"Сбрасывать предоплаченный трафик"),
        blank=True,
        default=False)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _(u"Услуга тарификации RADIUS трафика")
        verbose_name_plural = _(u"Услуги тарификации RADIUS трафика")
        permissions = (
            ("radiustraffic_view", _(u"Просмотр")),
        )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('radiustrafficservice_delete'), self.id)


class RadiusTrafficNode(models.Model):
    radiustraffic = models.ForeignKey(
        'billservice.RadiusTraffic', on_delete=models.CASCADE)
    value = models.BigIntegerField(
        verbose_name=_(u"Объём"),
        help_text=_(u"Объём, с которого действует указаная цена"),
        default=0
    )
    timeperiod = models.ForeignKey(
        'billservice.TimePeriod',
        verbose_name=_(u"Период тарификации"),
        on_delete=models.CASCADE)
    cost = models.DecimalField(
        verbose_name=_(u"Цена"),
        help_text=_(u"Цена за единицу тарификации"),
        default=0,
        max_digits=30,
        decimal_places=3
    )

    class Meta:
        ordering = ['value']
        verbose_name = _(u"Настройка тарификации RADIUS трафика")
        verbose_name_plural = _(u"Настройка тарификации RADIUS трафика")
        permissions = (
            ("radiustrafficnode_view", _(u"Просмотр")),
        )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('radiustrafficnode_delete'), self.id)
