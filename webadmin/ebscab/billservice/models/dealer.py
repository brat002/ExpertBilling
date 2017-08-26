# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from billservice.models.managers import SoftDeleteManager


class Dealer(models.Model):
    organization = models.CharField(
        max_length=400, verbose_name=_(u"Организация"))
    unp = models.CharField(
        max_length=255, blank=True, default='', verbose_name=_(u"УНП"))
    okpo = models.CharField(
        max_length=255, blank=True, default='', verbose_name=_(u"ОКПО"))
    contactperson = models.CharField(
        max_length=255, blank=True, default='', verbose_name=_(u"Контактное лицо"))
    director = models.CharField(
        max_length=255, blank=True, default='', verbose_name=_(u"Директор"))
    phone = models.CharField(
        max_length=255, blank=True, default='', verbose_name=_(u"Телефон"))
    fax = models.CharField(
        max_length=255, blank=True, default='', verbose_name=_(u"Факс"))
    postaddress = models.CharField(
        max_length=400,
        blank=True,
        default='',
        verbose_name=_(u"Почтовый адрес")
    )
    uraddress = models.CharField(
        max_length=400, blank=True, default='', verbose_name=_(u"Юр. адрес"))
    email = models.EmailField(
        verbose_name=_(u'E-mail'), max_length=255, blank=True, null=True)
    prepayment = models.FloatField(
        blank=True, default=0, verbose_name=_(u"% предоплаты"))
    paydeffer = models.IntegerField(
        blank=True, default=0, verbose_name=_(u"Отсрочка платежа"))
    discount = models.FloatField(
        blank=True, default=0, verbose_name=_(u"Скидка"))
    always_sell_cards = models.BooleanField(default=False)

    bank = models.ForeignKey(
        'billservice.BankData',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    deleted = models.BooleanField(blank=True, default=False)
    objects = SoftDeleteManager()

    class Meta:
        ordering = ['organization']
        verbose_name = _(u"Дилер")
        verbose_name_plural = _(u"Дилеры")
        permissions = (
            ("dealer_view", _(u"Просмотр")),
        )

    def __unicode__(self):
        return unicode(self.organization)

    def delete(self):
        if not self.deleted:
            self.deleted = True
            self.save()
            return
        super(Dealer, self).delete()


class DealerPay(models.Model):
    dealer = models.ForeignKey('billservice.Dealer', on_delete=models.CASCADE)
    pay = models.FloatField()
    salecard = models.ForeignKey(
        'billservice.SaleCard',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    created = models.DateTimeField()

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Платёж дилера")
        verbose_name_plural = _(u"Платежи дилера")
        permissions = (
            ("dealerpay_view", _(u"Просмотр")),
        )
