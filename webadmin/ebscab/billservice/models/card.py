# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from nas.models import Nas


class Card(models.Model):
    series = models.CharField(
        max_length=32, verbose_name=_(u"Серия"))
    pin = models.CharField(max_length=255, verbose_name=_(u"Пин"))
    login = models.CharField(
        max_length=255, blank=True, default='', verbose_name=_(u"Логин"))
    nominal = models.FloatField(default=0, verbose_name=_(u"Номинал"))
    activated = models.DateTimeField(
        blank=True, null=True, verbose_name=_(u"Актив-на"))
    activated_by = models.ForeignKey(
        'billservice.Account', blank=True, null=True, verbose_name=_(u"Аккаунт"))
    start_date = models.DateTimeField(
        blank=True, default='', verbose_name=_(u"Актив-ть с"))
    end_date = models.DateTimeField(
        blank=True, default='', verbose_name=_(u"по"))
    disabled = models.BooleanField(
        verbose_name=_(u"Неактивна"), default=False, blank=True)
    created = models.DateTimeField(verbose_name=_(u"Создана"))
    type = models.IntegerField(
        verbose_name=_(u"Тип"),
        choices=(
            (0, _(u"Экспресс-оплаты")),
            (1, _(u'Хотспот')),
            (2, _(u'VPN доступ')),
            (3, _(u'Телефония'))
        )
    )
    tarif = models.ForeignKey(
        'billservice.Tariff', blank=True, null=True, verbose_name=_(u"Тариф"))
    nas = models.ForeignKey(Nas, blank=True, null=True)
    ip = models.CharField(max_length=20, blank=True, default='')
    ipinuse = models.ForeignKey("IPInUse", blank=True, null=True)
    ippool = models.ForeignKey(
        "IPPool", verbose_name=_(u"Пул"), blank=True, null=True)
    ext_id = models.CharField(max_length=512, blank=True, null=True)
    salecard = models.ForeignKey(
        'billservice.SaleCard',
        verbose_name=_(u"Продана"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    def get_row_class(self):
        return 'error' if self.disabled else ''

    class Meta:
        ordering = ['-series', '-created', 'activated']
        verbose_name = _(u"Карта")
        verbose_name_plural = _(u"Карты")
        permissions = (
            ("card_view", _(u"Просмотр карт")),
        )


class SaleCard(models.Model):
    dealer = models.ForeignKey('billservice.Dealer', on_delete=models.CASCADE)
    sum_for_pay = models.FloatField(
        blank=True, verbose_name=_(u"Сумма к оплате"), default=0)
    paydeffer = models.IntegerField(
        blank=True, verbose_name=_(u"Отсрочка платежа, дн."), default=0)
    discount = models.FloatField(
        blank=True, verbose_name=_(u"Сидка, %"), default=0)
    discount_sum = models.FloatField(
        blank=True, verbose_name=_(u"Сумма скидки"), default=0)
    prepayment = models.FloatField(
        blank=True, verbose_name=_(u"% предоплаты"), default=0)
    created = models.DateTimeField(
        verbose_name=_(u"Создана"), auto_now_add=True, blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Накладная на карты")
        verbose_name_plural = _(u"накладные на карты")
        permissions = (
            ("salecard_view", _(u"Просмотр")),
        )
