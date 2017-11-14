# -*- coding: utf-8 -*-

from django.apps import apps
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from billservice.models.constants import STATUS_CLASS
from billservice.models.managers import SoftDeletedDateManager


class Tariff(models.Model):
    name = models.CharField(
        max_length=255, verbose_name=_(u'Название'), unique=True)
    description = models.TextField(
        verbose_name=_(u'Описание тарифного плана'), blank=True, default='')
    access_parameters = models.ForeignKey(
        to='billservice.AccessParameters',
        verbose_name=_(u'Параметры доступа'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    contracttemplate = models.ForeignKey(
        "ContractTemplate",
        verbose_name=_(u"Шаблон номера договора"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    time_access_service = models.ForeignKey(
        to='billservice.TimeAccessService',
        verbose_name=_(u'Доступ с учётом времени'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    traffic_transmit_service = models.ForeignKey(
        to='billservice.TrafficTransmitService',
        verbose_name=_(u'Доступ с учётом трафика'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    radius_traffic_transmit_service = models.ForeignKey(
        to="RadiusTraffic",
        verbose_name=_(u'RADIUS тарификация трафика'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    cost = models.FloatField(
        verbose_name=_(u'Стоимость пакета'),
        default=0,
        help_text=_(u"Стоимость активации тарифного плана. Целесообразно "
                    u"указать с расчётным периодом. Если не указана - "
                    u"предоплаченный трафик и время не учитываются")
    )
    reset_tarif_cost = models.BooleanField(
        verbose_name=_(u'Производить доснятие'),
        blank=True,
        default=False,
        help_text=_(u'Производить доснятие суммы до стоимости тарифного '
                    u'плана в конце расчётного периода')
    )
    settlement_period = models.ForeignKey(
        to='billservice.SettlementPeriod',
        blank=True,
        null=True,
        verbose_name=_(u'Расчётный период'),
        on_delete=models.CASCADE
    )
    ps_null_ballance_checkout = models.BooleanField(
        verbose_name=_(u'Производить снятие денег  при нулевом баллансе'),
        help_text=_(u"Производить ли списывание денег по периодическим "
                    u"услугам при достижении нулевого балланса или исчерпании "
                    u"кредита?"),
        blank=True,
        default=False
    )
    active = models.BooleanField(
        verbose_name=_(u"Активен"), default=False, blank=True)
    deleted = models.DateTimeField(_(u'Удален'), null=False, blank=True)
    allow_express_pay = models.BooleanField(
        verbose_name=_(u'Оплата экспресс картами'), blank=True, default=False)
    require_tarif_cost = models.BooleanField(
        verbose_name=_(u"Требовать наличия стоимости пакета"),
        default=False,
        blank=True
    )
    allow_userblock = models.BooleanField(
        verbose_name=_(u"Разрешить пользовательскую блокировку"),
        blank=True,
        default=False
    )
    userblock_cost = models.DecimalField(
        verbose_name=_(u"Стоимость блокировки"),
        decimal_places=2,
        max_digits=30,
        blank=True,
        default=0
    )
    userblock_max_days = models.IntegerField(
        verbose_name=_(u"MAX длительность блокировки"), blank=True, default=0)
    userblock_require_balance = models.DecimalField(
        verbose_name=_(u"Минимальный баланс для блокировки"),
        decimal_places=2,
        max_digits=10,
        blank=True,
        default=0
    )
    allow_ballance_transfer = models.BooleanField(
        verbose_name=_(u"Разрешить услугу перевода баланса"),
        blank=True,
        default=False
    )
    vpn_ippool = models.ForeignKey(
        'billservice.IPPool',
        verbose_name=_(u"VPN IP пул"),
        blank=True,
        null=True,
        related_name='tariff_vpn_ippool_set',
        on_delete=models.SET_NULL
    )
    vpn_guest_ippool = models.ForeignKey(
        'billservice.IPPool',
        verbose_name=_(u"Гостевой VPN IP пул"),
        blank=True,
        null=True,
        related_name='tariff_guest_vpn_ippool_set',
        on_delete=models.SET_NULL
    )

    objects = SoftDeletedDateManager()

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = (
            'name',
            'access_parameters',
            'time_access_service',
            'traffic_transmit_service',
            'cost',
            'settlement_period',
            'ps_null_ballance_checkout'
        )

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Тариф")
        verbose_name_plural = _(u"Тарифы")
        permissions = (
            ("tariff_view", _(u"Просмотр")),
        )

    def delete(self):
        if not self.deleted:
            self.deleted = True
            self.save()
            return
        super(Tariff, self).delete()

    def get_row_class(self):
        return STATUS_CLASS.get(self.active)

    def get_hide_url(self):
        return "%s?id=%s" % (reverse('tariff_hide'), self.id)

    def get_addon_services(self):
        return (apps.get_model('billservice.AddonServiceTarif').objects
                .filter(tarif=self, type=0))


class NotificationsSettings(models.Model):
    tariffs = models.ManyToManyField('billservice.Tariff')
    payment_notifications = models.BooleanField(
        default=False,
        verbose_name=_(u'Уведомления при пополнении баланса')
    )
    payment_notifications_template = models.TextField(
        verbose_name=_(u'Шаблон уведомления о платеже'),
        # TODO: fix typo
        help_text=_(u'Можно использовать переменные account, transaction. '
                    u'Для рендеринга используоется Django Template Engine.'),
        default=''
    )
    balance_notifications = models.BooleanField(
        default=False,
        verbose_name=_(u'Уведомления о недостатке баланса')
    )
    balance_edge = models.FloatField(
        verbose_name=_(u'Граница баланса'),
        help_text=_(u'Граница, с которой слать уведомления  о недостатке '
                    u'баланса'),
        default=0
    )
    balance_notifications_each = models.IntegerField(
        verbose_name=_(u'Периодичность между уведомлениями о балансе'),
        help_text=_(u'В днях'),
        default=1
    )
    balance_notifications_limit = models.IntegerField(
        verbose_name=_(u'Количество уведомлений о балансе'),
        help_text=_(u'Не слать более уведомлений о балансе при исчерпании '
                    u'указанного количества'),
        default=1
    )
    balance_notifications_template = models.TextField(
        verbose_name=_(u'Шаблон уведомления о недостатке денег'),
        help_text=_(u'Можно использовать переменные account. Для рендеринга '
                    u'используется Django Template Engine.'),
        default=''
    )
    notification_type = models.CharField(
        max_length=64, choices=(
            ('SMS', 'SMS'),
            ('EMAIL', 'EMAIL')
        ),
        default='SMS'
    )
    backend = models.CharField(
        max_length=64, blank=True, choices=settings.SENDSMS_BACKENDS)

    def get_remove_url(self):
        return '{}?id={}'.format(reverse('notificationssettings_delete'),
                                 self.id)


class TPChangeRule(models.Model):
    from_tariff = models.ForeignKey(
        'billservice.Tariff',
        verbose_name=_(u'С тарифного плана'),
        related_name="from_tariff"
    )
    to_tariff = models.ForeignKey(
        'billservice.Tariff',
        verbose_name=_(u'На тарифный план'),
        related_name="to_tariff"
    )
    disabled = models.BooleanField(
        verbose_name=_(u'Временно запретить'), blank=True, default=False)
    cost = models.FloatField(verbose_name=_(u'Стоимость перехода'))
    ballance_min = models.FloatField(verbose_name=_(u'Минимальный баланс'))
    on_next_sp = models.BooleanField(
        verbose_name=_(u'Со следующего расчётного периода'),
        blank=True,
        default=False
    )
    settlement_period = models.ForeignKey(
        'billservice.SettlementPeriod',
        verbose_name=_(u'Расчётный период'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('tpchangerule_delete'), self.id)

    class Meta:
        ordering = ['from_tariff', 'to_tariff']
        unique_together = (("from_tariff", "to_tariff"),)
        verbose_name = _(u"Правило смены тарифов")
        verbose_name_plural = _(u"Правила смены тарифов")
        permissions = (
            ("tpchangerule_view", _(u"Просмотр")),
        )
