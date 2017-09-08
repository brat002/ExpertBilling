# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class OneTimeService(models.Model):
    """
    Справочник разовых услуг
    TODO: Сделать справочники валют
    """
    tarif = models.ForeignKey('billservice.Tariff', on_delete=models.CASCADE)
    name = models.CharField(
        max_length=255,
        verbose_name=_(u'Название разовой услуги'),
        default='',
        blank=True
    )
    cost = models.FloatField(
        verbose_name=_(u'Стоимость разовой услуги'),
        default=0,
        blank=True
    )

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name', 'cost')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('onetimeservice_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Разовая услуга")
        verbose_name_plural = _(u"Разовые услуги")
        permissions = (
            ("onetimeservice_view", _(u"Просмотр услуг")),
        )


class OneTimeServiceHistory(models.Model):
    onetimeservice = models.ForeignKey(
        'billservice.OneTimeService', null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    summ = models.IntegerField()
    prev_balance = models.DecimalField(
        verbose_name=_(u'Предыдущий баланс'),
        decimal_places=5,
        max_digits=20,
        blank=True,
        default=0
    )
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE)
    accounttarif = models.ForeignKey(
        'billservice.AccountTarif', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Списание по разовым услугам")
        verbose_name_plural = _(u"Списания по разовым услугам")
        permissions = (
            ("onetimeservicehistory_view", _(u"Просмотр услуг")),
        )
