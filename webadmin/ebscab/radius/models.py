# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _

from billservice.models import Account, SubAccount, IPInUse
from ebscab.utils.decorators import to_partition
from nas.models import Nas


SERVICE_TYPES = (
    (u"PPTP/L2TP", u"PPTP"),
    (u"PPPOE", u"PPPOE"),
    (u"DHCP", u"DHCP"),
    (u"HotSpot", u"HOTSPOT"),
)

LOG_ITEM_TYPES = (
    ("AHTH_OK", _(u"Авторизация разрешена")),
    ("AUTH_ACCOUNT_DISABLED", _(u"Аккаунт неактивен")),
    ("AUTH_RADIUS_ONLY_ONE", _(u"Вторая сессия на указанном сервере доступа")),
    ("AUTH_BAD_PASSWORD", _(u"Неверный пароль")),
    ("AUTH_WRONG_ACCESS_TYPE",
     _(u"Способ доступа %s не совпадает с разрешённым в параметрах "
       u"тарифнго плана.")),
    ("AUTH_SUBACC_NOT_FOUND", _(u"Субаккаунт с таким логином не найден")),
    ("AUTH_ACC_FOR_SUBACC_NOT_FOUND", _(u"Аккаунт для субаккаунта не найден")),
    ("AUTH_BAD_TIME", _(u"В данный момент запрещено устанавливать соединение")),
    ("AUTH_BAD_NAS", _(u"Запрещено подключаться к данному серверу доступа")),
    ("AUTH_8021x_NAS",
     _(u"Для 802.1x авторизации должен быть указан коммутатор")),
    ("AUTH_NAS_NOT_FOUND",
     _(u"Запрещено подключаться к данному серверу доступа")),
    ("AUTH_VPN_IPN_IP_LINK_ERROR",
     _(u"Соединение установлено с запрещённого IPN IP")),
    ("AUTH_PPPOE_IPN_MAC_LINK_ERROR",
     _(u"Соединение установлено с запрещённого IPN MAC")),
    ("AUTH_VPN_BALLANCE_ERROR",
     _(u"Запрещена VPN авторизация с нулевым балансом"))
)
SESSION_STATUS = (
    (u"ACTIVE", _(u"Активна")),
    (u"NACK", _(u"Не сброшена")),
    (u"ACK", _(u"Cброшена"))
)

STATUS_CLASS = {
    "ACTIVE": '',
    "NACK": 'error',
    "ACK": ''
}


class ActiveSession(models.Model):
    account = models.ForeignKey(Account, verbose_name=_(u'Аккаунт'))
    subaccount = models.ForeignKey(SubAccount, verbose_name=_(u'Субаккаунт'))
    # Атрибут радиуса Acct-Session-Id
    sessionid = models.CharField(
        max_length=255, blank=True, verbose_name=_(u'ID'))
    # Время последнего обновления
    interrim_update = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True,
        verbose_name=_(u'Последнее обновление')
    )
    # Время старта сессии
    date_start = models.DateTimeField(
        blank=True, null=True, verbose_name=_(u'Начало'))
    # Время конца сессии
    date_end = models.DateTimeField(
        null=True, blank=True, verbose_name=_(u'Конец'))
    # Атрибут радиуса Calling-Station-Id. IP адрес или мак-адрес
    caller_id = models.CharField(
        max_length=255, blank=True, verbose_name=u'Caller ID')
    # Атрибут радиуса Called-Station-Id (IP адрес или имя сервиса для PPPOE)
    called_id = models.CharField(
        max_length=255, blank=True, verbose_name=u'Called ID')
    framed_ip_address = models.CharField(
        max_length=255, blank=True, default='', verbose_name=_(u'IP'))
    # Атрибут радиуса NAS-IP-Address
    nas_id = models.CharField(
        max_length=255, blank=True, verbose_name=_(u'Nas ID'))
    nas_int = models.ForeignKey(
        Nas, blank=True, null=True, verbose_name=_(u'NAS'))
    # Атрибут радиуса Acct-Session-Time
    session_time = models.IntegerField(
        default=0, null=True, blank=True, verbose_name=_(u'Время'))
    # Нужно определить каким образом клиент подключился к серверу
    framed_protocol = models.CharField(
        max_length=32, choices=SERVICE_TYPES, verbose_name=_(u'Протокол'))
    # Атрибут радиуса Acct-Input-Octets
    bytes_in = models.IntegerField(
        null=True, blank=True, verbose_name=_(u'IN'))
    # Атрибут радиуса Acct-Output-Octets
    bytes_out = models.IntegerField(
        null=True, blank=True, verbose_name=_(u'OUT'))
    # Выставляется в случае, если был произведён платёж
    session_status = models.CharField(
        max_length=32,
        choices=SESSION_STATUS,
        null=True,
        blank=True,
        verbose_name=_(u'Статус')
    )
    speed_string = models.CharField(max_length=255, blank=True, null=True)
    acct_terminate_cause = models.CharField(
        verbose_name=_(u'Причина разрыва'),
        max_length=128,
        blank=True,
        default=''
    )
    ipinuse = models.ForeignKey(
        IPInUse, blank=True, null=True, on_delete=models.SET_NULL)

    class Admin:
        ordering = ['-id']
        list_display = ('account', 'bytes_in', 'bytes_out', 'sessionid',
                        'date_start', 'interrim_update', 'date_end',
                        'caller_id', 'called_id', 'session_time',
                        'session_status')

    class Meta:
        verbose_name = _(u"RADIUS сессия")
        verbose_name_plural = _(u"RADIUS сессии")
        permissions = (
           ("activesession_view", _(u"Просмотр")),
        )

    def get_row_class(self):
        return STATUS_CLASS.get(self.session_status)

    def __unicode__(self):
        return u"%s" % self.sessionid

    @property
    def bytes_sum(self):
        return self.bytes_in + self.bytes_out

    @to_partition
    def save(self, *args, **kwargs):
        super(ActiveSession, self).save(*args, **kwargs)


class AuthLog(models.Model):
    account = models.ForeignKey(
        Account, blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=100)
    service = models.CharField(max_length=40)
    subaccount = models.ForeignKey(
        SubAccount, blank=True, null=True, on_delete=models.SET_NULL)
    nas = models.ForeignKey(
        Nas,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    cause = models.TextField()
    datetime = models.DateTimeField()

    class Meta:
        verbose_name = _(u'RADIUS авторизации')
        ordering = ['-datetime']

    def get_row_class(self):
        if self.type not in ['AUTH_OK', 'DHCP_AUTH_OK']:
            return 'inactive'
        elif self.type in ['AUTH_OK', 'DHCP_AUTH_OK']:
            return 'success'
        return ''


class RadiusStat(models.Model):
    nas = models.ForeignKey(
        Nas,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    start = models.PositiveIntegerField(blank=True, default=0)
    alive = models.PositiveIntegerField(blank=True, default=0)
    end = models.PositiveIntegerField(blank=True, default=0)
    active = models.PositiveIntegerField(blank=True, default=0)
    datetime = models.DateTimeField(db_index=True)
