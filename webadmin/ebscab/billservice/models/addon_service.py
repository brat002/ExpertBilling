# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from nas.models import Nas


class AddonService(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u'Название'))
    comment = models.TextField(
        blank=True, default='', verbose_name=_(u'Комментарий'))
    allow_activation = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разешить активацию"),
        help_text=_(u'Разрешить активацию при нулевом балансе и блокировках')
    )
    service_type = models.CharField(
        verbose_name=_(u"Тип услуги"),
        max_length=32,
        choices=(
            ("onetime", _(u"Разовая услуга")),
            ("periodical", _(u"Периодическая услуга"))
        )
    )
    sp_type = models.CharField(
        verbose_name=_(u"Способ списания"),
        max_length=32,
        choices=(
            ("AT_START", _(u"В начале расчётного периода")),
            ("AT_END", _(u"В конце расчётного периода")),
            ("GRADUAL", _(u"На протяжении расчётного периода"))
        )
    )
    tpd = models.SmallIntegerField(
        verbose_name=_(u'Кол-во списаний в сутки'),
        default=1,
        blank=True,
        null=True
    )
    sp_period = models.ForeignKey(
        'billservice.SettlementPeriod',
        verbose_name=_(u"Расчётный период"),
        help_text=_(u"Период, в течении которого будет списываться стоимость "
                    u"услуги"),
        related_name="addonservice_spperiod",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    timeperiod = models.ForeignKey(
        'billservice.TimePeriod',
        verbose_name=_(u"Время активации"),
        help_text=_(u"Время, когда услуга будет активирована"),
        null=True,
        on_delete=models.SET_NULL
    )
    cost = models.DecimalField(
        verbose_name=_(u"Стоимость услуги"),
        decimal_places=2,
        max_digits=10,
        blank=True,
        default=0
    )
    cancel_subscription = models.BooleanField(
        verbose_name=_(u"Разрешить отключение"),
        help_text=_(u"Разрешить самостоятельное отключение услуги"),
        default=True
    )
    wyte_period = models.ForeignKey(
        'billservice.SettlementPeriod',
        verbose_name=_(u"Штрафуемый период"),
        help_text=_(u"Списывать сумму штрафа при досрочном отключении услуги "
                    u"пользователем"),
        related_name="addonservice_wyteperiod",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    wyte_cost = models.DecimalField(
        verbose_name=_(u"Сумма штрафа"),
        decimal_places=2,
        max_digits=10,
        blank=True,
        default=0
    )
    action = models.BooleanField(
        verbose_name=_(u"Выполнить действие"), blank=True, default=False)
    nas = models.ForeignKey(
        Nas,
        verbose_name=_(u"Сервер доступа"),
        help_text=_(u"Сервер доступа, на котором будут производиться "
                    u"действия"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    service_activation_action = models.TextField(
        verbose_name=_(u"Действие для активации услуги"),
        blank=True,
        default=''
    )
    service_deactivation_action = models.TextField(
        verbose_name=_(u"Действие для отключения услуги"),
        blank=True,
        default=''
    )
    deactivate_service_for_blocked_account = models.BooleanField(
        verbose_name=_(u"Отключать услугу при бловировке аккаунта"),
        help_text=_(u"Отключать услугу при достижении нулевого баланса "
                    u"или блокировках"),
        blank=True,
        default=False
    )
    change_speed = models.BooleanField(
        verbose_name=_(u"Изменить скорость"),
        help_text=_(u"Изменить параметры скорости при активации аккаунта"),
        blank=True,
        default=False
    )
    change_speed_type = models.CharField(
        verbose_name=_(u"Способ изменения скорости"),
        max_length=32,
        choices=(
            ("add", _(u"Добавить к текущей")),
            ("abs", _(u"Абсолютное значение"))
        ),
        blank=True,
        null=True
    )
    speed_units = models.CharField(
        verbose_name=_(u'Единицы измерения скорости'),
        max_length=32,
        choices=(
            ('Kbps', 'Kbps'),
            ('Mbps', 'Mbps'),
            ('%', '%')
        ),
        blank=True,
        null=True
    )

    max_tx = models.IntegerField(blank=True, default=0)
    max_rx = models.IntegerField(blank=True, default=0)
    burst_tx = models.IntegerField(blank=True, default=0)
    burst_rx = models.IntegerField(blank=True, default=0)
    burst_treshold_tx = models.IntegerField(blank=True, default=0)
    burst_treshold_rx = models.IntegerField(blank=True, default=0)
    burst_time_tx = models.IntegerField(blank=True, default=0)
    burst_time_rx = models.IntegerField(blank=True, default=0)
    min_tx = models.IntegerField(blank=True, default=0)
    min_rx = models.IntegerField(blank=True, default=0)
    priority = models.IntegerField(
        verbose_name=_(u'Приоритет'), blank=True, default=0)

    def __unicode__(self):
        return u"%s" % self.name

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('addonservice_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Подключаемая услуга")
        verbose_name_plural = _(u"Подключаемые услуги")
        permissions = (
            ("addonservice_view", _(u"Просмотр")),
        )


class AddonServiceTarif(models.Model):
    tarif = models.ForeignKey('billservice.Tariff', on_delete=models.CASCADE)
    service = models.ForeignKey(
        AddonService, verbose_name=_(u"Услуга"), on_delete=models.CASCADE)
    activation_count = models.IntegerField(
        verbose_name=_(u"Активаций за расчётный период"),
        blank=True,
        default=0
    )
    activation_count_period = models.ForeignKey(
        'billservice.SettlementPeriod',
        verbose_name=_(u"Расчётный период"),
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    type = models.IntegerField(
        verbose_name=_(u"Тип активации"),
        # 0-Account, 1-Subaccount
        choices=(
            (0, _(u"На аккаунт")),
            (1, _(u"На субаккаунт"))
        ),
        default=0
    )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('addonservicetariff_delete'), self.id)

    def __unicode__(self):
        return u"%s %s" % (self.service, self.tarif.name)

    class Meta:
        ordering = ['id']
        verbose_name = _(u"Разрешённая подключаемая услуга")
        verbose_name_plural = _(u"Разрешённые подключаемые услуги")
        permissions = (
            ("addonservicetarif_view", _(u"Просмотр")),
        )


class AddonServiceTransaction(models.Model):
    service = models.ForeignKey(AddonService)
    service_type = models.CharField(max_length=32)  # onetime, periodical
    account = models.ForeignKey('billservice.Account')
    accountaddonservice = models.ForeignKey('billservice.AccountAddonService')
    accounttarif = models.ForeignKey('billservice.AccountTarif')
    type = models.ForeignKey(
        to='billservice.TransactionType',
        null=True,
        to_field='internal_name',
        verbose_name=_(u"Тип операции"),
        on_delete=models.SET_NULL
    )
    summ = models.DecimalField(decimal_places=5, max_digits=60)
    prev_balance = models.DecimalField(
        verbose_name=_(u'Предыдущий баланс'),
        decimal_places=5,
        max_digits=20,
        blank=True,
        default=0
    )
    created = models.DateTimeField()

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Списание по подключаемой услуге")
        verbose_name_plural = _(u"Списания по подключаемым услугам")
        permissions = (
            ("accountaddonservicetransaction_view", _(u"Просмотр")),
        )
