# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from billservice.models.constants import ADMIN_OPER_STATUS, PORT_OPER_STATUS


class Switch(models.Model):
    manufacturer = models.ForeignKey(
        to='billservice.Manufacturer',
        verbose_name=_(u"Производитель"),
        max_length=250,
        blank=True,
        null=True,
        default='',
        on_delete=models.SET_NULL
    )
    model = models.ForeignKey(
        to='billservice.Model',
        verbose_name=_(u"Модель"),
        max_length=250,
        blank=True,
        null=True,
        default='',
        on_delete=models.SET_NULL
    )
    name = models.CharField(
        max_length=500,
        verbose_name=_(u"Название"),
        blank=True,
        default=''
    )
    sn = models.CharField(
        max_length=500,
        verbose_name=_(u"Серийный номер"),
        blank=True,
        default=''
    )
    city = models.ForeignKey(
        to='billservice.City',
        verbose_name=_(u"Город"),
        blank=True,
        null=True,
        default='',
        on_delete=models.SET_NULL
    )
    street = models.CharField(
        verbose_name=_(u"Улица"),
        max_length=250,
        blank=True,
        default=''
    )
    house = models.CharField(
        verbose_name=_(u"Дом"), max_length=250, blank=True, default='')
    place = models.TextField(
        blank=True, verbose_name=_(u"Место размещения"), default='')  # место установки
    comment = models.TextField(
        blank=True, verbose_name=_(u"Комментарий"), default='')
    ports_count = models.IntegerField(
        blank=True, verbose_name=_(u"Количество портов"), default=0)
    broken_ports = models.TextField(
        blank=True, verbose_name=_(u"Битые порты"), default='')  # через запятую
    uplink_ports = models.TextField(
        blank=True, verbose_name=_(u"Аплинк-порты"), default='')  # через запятую
    protected_ports = models.TextField(
        blank=True, verbose_name=_(u"Порты с грозозащитой"), default='')  # через запятую
    monitored_ports = models.TextField(
        blank=True, verbose_name=_(u"Порты с мониторингом"), default='')
    disabled_ports = models.TextField(
        blank=True, verbose_name=_(u"Отключенные порты"), default='')
    snmp_support = models.BooleanField(
        default=False, verbose_name=_(u"Поддержка SNMP"))
    snmp_version = models.CharField(
        max_length=10,
        choices=(
            ('1', "v1"),
            ('2c', "v2c")
        ),
        verbose_name=_(u"Версия SNMP"),
        blank=True,
        default='v1'
    )
    snmp_community = models.CharField(
        max_length=128,
        verbose_name=_(u"SNMP компьюнити"),
        blank=True,
        default=''
    )
    ipaddress = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_(u"IP адрес"),
        default=None
    )
    macaddress = models.CharField(
        max_length=32, verbose_name=_(u"MAC адрес"), blank=True, default='')
    management_method = models.IntegerField(
        verbose_name=_(u"Метод SNMP управления"),
        choices=(
            (0, _(u"Не управлять")),
            (1, _(u"SSH")),
            (2, _(u"SNMP")),
            (3, _(u"Telnet")),
            (4, _(u"localhost"))
        ),
        blank=True,
        default=1
    )
    option82 = models.BooleanField(verbose_name=_(u"Опция 82"), default=False)
    option82_auth_type = models.IntegerField(
        verbose_name=_(u"Тип авторизации по Option82"),
        # 1-port, 2 - mac+port, 3-mac
        choices=(
            (0, _(u"Порт")),
            (1, _(u"Порт+MAC")),
            (2, _(u"MAC"))
        ),
        blank=True,
        null=True
    )
    secret = models.CharField(
        verbose_name=_(u"RADIUS secret"),
        max_length=128,
        blank=True,
        default=''
    )
    identify = models.CharField(
        verbose_name=_(u"RADIUS identify"),
        max_length=128,
        blank=True,
        default=''
    )
    username = models.CharField(
        verbose_name=_(u"Имя пользователя"),
        max_length=256,
        blank=True,
        default=''
    )
    password = models.CharField(
        verbose_name=_(u"Пароль пользователя"),
        max_length=256,
        blank=True,
        default=''
    )
    enable_port = models.TextField(
        verbose_name=_(u"Команда включения порта"), blank=True, default='')
    disable_port = models.TextField(
        verbose_name=_(u"Команда отключения порта"), blank=True, default='')
    option82_template = models.CharField(
        verbose_name=_(u"Шаблон option82"),
        choices=(
            ("dlink-32xx", 'dlink-32xx'),
        ),
        blank=True,
        max_length=256,
        default=''
    )
    remote_id = models.CharField(
        verbose_name=_(u"remote_id"), blank=True, max_length=256, default='')

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _(u"Коммутатор")
        verbose_name_plural = _(u"Коммутаторы")
        permissions = (
            ("switch_view", _(u"Просмотр")),
        )


class SwitchPort(models.Model):
    switch = models.ForeignKey('billservice.Switch')
    port = models.IntegerField(db_index=True)
    comment = models.CharField(blank=True, default='', max_length=1024)
    oper_status = models.IntegerField(choices=PORT_OPER_STATUS, default=4)
    admin_status = models.IntegerField(choices=ADMIN_OPER_STATUS)
    uplink = models.BooleanField(default=False)
    broken = models.BooleanField(default=False)
    protection = models.ForeignKey(
        'billservice.Hardware',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )


class SwitchPortStat(models.Model):
    switchport = models.ForeignKey(SwitchPort, on_delete=models.CASCADE)
    oper_status = models.IntegerField(choices=PORT_OPER_STATUS, default=4)
    admin_status = models.IntegerField(choices=ADMIN_OPER_STATUS)
    out_bytes = models.IntegerField()
    in_errors = models.IntegerField()
    out_errors = models.IntegerField()
    datetime = models.DateTimeField()
