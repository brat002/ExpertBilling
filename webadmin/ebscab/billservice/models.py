#-*- coding=utf-8 -*-
from django.db import models
from ebscab.nas.models import Nas, TrafficClass, TrafficClass
from django.contrib.auth.models import User
from django.db.models import F
import datetime, time
from django.core.urlresolvers import reverse
from django.db import connection
from annoying.fields import JSONField

connection.features.can_return_id_from_insert = False
# Create your models here.
# choiCe
import IPy
from lib.fields import IPNetworkField, EncryptedTextField
from dynamicmodel.models import DynamicModel, DynamicSchema
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ValidationError
import re
from django.core.cache import cache
from django.db.models import Q

def validate_phone(value):
    if value and not re.match(r'''\+\d{1,25}$''', value):
        raise ValidationError(_(u'Некорректный формат номера. Используйте международный формат +71923453333'))

#===============================================================================
# def _(s):
#	return unicode(s)
#===============================================================================

PROTOCOLS = {'0': '-all-',
             '37': 'ddp',
             '98': 'encap',
             '3': 'ggp',
             '47': 'gre',
             '20': 'hmp',
             '1': 'icmp',
             '38': 'idpr-cmtp',
             '2': 'igmp',
             '4': 'ipencap',
             '94': 'ipip',
             '89': 'ospf',
             '27': 'rdp',
             '6': 'tcp',
             '17': 'udp'
}

PERIOD_CHOISES = (
    ('DONT_REPEAT', _(u'Не повторять')),
    ('DAY', _(u'День')),
    ('WEEK', _(u'Неделя')),
    ('MONTH', _(u'Месяц')),
    ('YEAR', _(u'Год')),
)

CASH_METHODS = (
    ('AT_START', _(u'В начале периода')),
    ('AT_END', _(u'В конце периода')),
    ('GRADUAL', _(u'В течении периода')),
)

ACCESS_TYPE_METHODS = (
    ("PPTP", "PPTP" ),
    ("PPPOE", "PPPOE"),
    ("IPN", "IPN"),
    ("HotSpot", "HotSpot"),
    ('HotSpotIp+Mac', 'HotSpotIp+Mac'),
    ('HotSpotIp+Password', 'HotSpotIp+Password'),
    ('HotSpotMac', 'HotSpotMac'),
    ('HotSpotMac+Password', 'HotSpotMac+Password'),
    ('lISG', 'lISG'),
    ("DHCP", "DHCP")
)
# choiCe
ACTIVITY_CHOISES = (
    ("Enabled", _(u"Активен")),
    ("Disabled", _(u"Неактивен")),
)
# choiCe
CHOISE_METHODS = (
    ("MAX", _(u"Наибольший")),
    ("SUMM", _(u"Сумма всех")),
)

CHECK_PERIODS = (
    ("period_checkSP_START", _(u"С начала расчётного периода")),
    ("AG_START", _(u"С начала интервала агрегации")),
)

STATISTIC_MODE = (
    ('NETFLOW', _(u'NetFlow')),
    ('ACCOUNTING', _(u'RADIUS Accounting')),
)

PRIORITIES = (
    ('1', _(u'1')),
    ('2', _(u'2')),
    ('3', _(u'3')),
    ('4', _(u'4')),
    ('5', _(u'5')),
    ('6', _(u'6')),
    ('7', _(u'7')),
    ('8', _(u'8')),
)

DIRECTIONS_LIST = (
    ('INPUT', _(u'Входящий на абонента')),
    ('OUTPUT', _(u'Исходящий от абонента')),
    ('TRANSIT', _(u'Межабонентский')),
)

AUTH_TYPES = (
    ('BY_LOGIN', 'BY_LOGIN'),
    ('BY_MAC', 'BY_MAC'),
)

STATUS_CLASS = {
    1: '',
    2: 'inactive-light',
    3: 'inactive',
    4: 'info',
    False: 'inactive',
}

PORT_OPER_STATUS = (
    (1, 'up'),
    (2, 'down'),
    (3, 'testing'),
    (4, 'unknown'),
    (5, 'dormant'),
    (6, 'notPresent'),
    (7, 'lowerLayerDown')
)

ADMIN_OPER_STATUS = (
    (1, 'up'),
    (2, 'down'),
    (3, 'testing'),
)


class SoftDeleteManager(models.Manager):
    ''' Use this manager to get objects that have a deleted field '''

    def get_query_set(self):
        return super(SoftDeleteManager, self).get_query_set().filter(deleted=False)

    def all_with_deleted(self):
        return super(SoftDeleteManager, self).get_query_set()

    def deleted_set(self):
        return super(SoftDeleteManager, self).get_query_set().filter(deleted=True)


class SoftDeletedDateManager(models.Manager):
    ''' Use this manager to get objects that have a deleted field '''

    def get_query_set(self):
        return super(SoftDeletedDateManager, self).get_query_set().filter(deleted__isnull=True)

    def all_with_deleted(self):
        return super(SoftDeletedDateManager, self).get_query_set()

    def deleted_set(self):
        return super(SoftDeletedDateManager, self).get_query_set().filter(deleted__isnull=False)


class TimePeriod(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u'Название группы временных периодов'), unique=True)
    #time_period_nodes = models.ManyToManyField(to=TimePeriodNode, blank=True, null=True, verbose_name=_(u'Группа временных периодов')

    def in_period(self):
        for time_period_node in self.time_period_nodes:
            if time_period_node.in_period() == True:
                return True
        return False

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name',)


    class Meta:
        ordering = ['name']
        verbose_name = _(u"Временной период")
        verbose_name_plural = _(u"Временные периоды")
        permissions = (
            ("timeperiod_view", _(u"Просмотр временных периодов")),
        )


class TimePeriodNode(models.Model):
    """
    Диапазон времени ( с 15 00 до 18 00 каждую вторник-пятницу,утро, ночь, сутки, месяц, год и т.д.)
    """
    time_period = models.ForeignKey(TimePeriod, verbose_name=_(u"Период времени"))
    name = models.CharField(max_length=255, verbose_name=_(u'Название подпериода'), default='', blank=True)
    time_start = models.DateTimeField(verbose_name=_(u'Дата и время начала'), default='', blank=True)
    length = models.IntegerField(verbose_name=_(u'Длительность в секундах'), default=0, blank=True)
    repeat_after = models.CharField(max_length=255, choices=PERIOD_CHOISES, verbose_name=_(u'Повторять через'),
                                    default='DAY', blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u"Нода временного периода")
        verbose_name_plural = _(u"Ноды временных периодов")
        permissions = (
            ("timeperiodnode_view", _(u"Просмотр нод временных периодов")),
        )


class SettlementPeriod(models.Model):
    """
    Расчётный период
    """
    name = models.CharField(max_length=255, verbose_name=_(u'Название'), unique=True)
    time_start = models.DateTimeField(verbose_name=_(u'Начало периода'))
    length = models.IntegerField(blank=True, null=True, default=0, verbose_name=_(u'Период действия в секундах'))
    length_in = models.CharField(max_length=255, choices=PERIOD_CHOISES, null=True, blank=True, default='',
                                 verbose_name=_(u'Длина промежутка'))
    autostart = models.BooleanField(verbose_name=_(u'Начинать при активации'), default=False)

    def __unicode__(self):
        return u"%s%s" % ("+" if self.autostart else '', self.name, )

    class Admin:
        list_display = ('name', 'time_start', 'length', 'length_in', 'autostart')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('settlementperiod_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Расчетный период")
        verbose_name_plural = _(u"Расчетные периоды")
        permissions = (
            ("settlementperiod_view", _(u"Просмотр расчётных периодов")),
        )


class PeriodicalService(models.Model):
    """
    Справочник периодических услуг
    TO-DO: Сделать справочники валют
    """
    ps_condition = (
        (0, _(u'При любом балансе')),
        (1, _(u'Меньше')),
        (2, _(u'Меньше или равно')),
        (3, _(u'Равно')),
        (4, _(u'Больше или равно')),
        (5, _(u'Больше')),
    )
    tarif = models.ForeignKey('Tariff')
    name = models.CharField(max_length=255, verbose_name=_(u'Название'))
    settlement_period = models.ForeignKey(to=SettlementPeriod, verbose_name=_(u'Период'), null=True,
                                          on_delete=models.SET_NULL)
    cost = models.DecimalField(verbose_name=_(u'Стоимость'), default=0, blank=True, decimal_places=2, max_digits=30)
    cash_method = models.CharField(verbose_name=_(u'Способ списания'), max_length=255, choices=CASH_METHODS,
                                   default='AT_START', blank=True)
    tpd = models.SmallIntegerField(verbose_name=_(u'Кол-во списаний в сутки'), default=1, blank=True, null=True)
    #condition         = models.IntegerField(verbose_name=_(u"Условие", default = 0, choices=((0, _(u"Списывать при любом балансе"),(1, _(u"Списывать при полождительном балансе"),(2, _(u"Списывать при отрицательном балансе"),(2, _(u"Списывать при нулевом и положительном балансе"))) # 0 - Всегда. 1- Только при положительном балансе. 2 - только при орицательном балансе
    ps_condition = models.IntegerField(verbose_name=_(u"Условие списания"), default=0, choices=ps_condition)
    condition_summ = models.DecimalField(verbose_name=_(u'Сумма для условия'), default=0, blank=True, decimal_places=2,
                                         max_digits=30)

    deactivated = models.DateTimeField(verbose_name=_(u"Отключить"), blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"Активировать"), help_text=_(
        u'Не указывайте, если списания должны начаться с начала расчётного периода'), blank=True, null=True)
    deleted = models.BooleanField(blank=True, default=False, db_index=True)


    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name', 'settlement_period', 'cost', 'cash_method')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('periodicalservice_delete'), self.id)


    class Meta:
        ordering = ['name']
        verbose_name = _(u"Периодическая услуга")
        verbose_name_plural = _(u"Периодические услуги")
        permissions = (
            ("periodicalservice_view", _(u"Просмотр периодических услуг")),
        )


class PeriodicalServiceHistory(models.Model):
    service = models.ForeignKey(to=PeriodicalService, blank=True, null=True, on_delete=models.SET_NULL)
    #transaction = models.ForeignKey(to='Transaction')
    accounttarif = models.ForeignKey(to='AccountTarif', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    summ = models.DecimalField(decimal_places=5, max_digits=20)
    prev_balance = models.DecimalField(verbose_name=(u'Предыдущий баланс'), decimal_places=5, max_digits=20, blank=True,
                                       default=0)
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    type = models.ForeignKey('TransactionType', to_field='internal_name', null=True, on_delete=models.SET_NULL)
    real_created = models.DateTimeField(verbose_name=u'Реальная дата списания', auto_now_add=True)

    def __unicode__(self):
        return u"%s" % (self.service)

    class Admin:
        list_display = ('service', 'transaction', 'datetime')


    class Meta:
        ordering = ['-created']
        verbose_name = _(u"История по пер. услугам")
        verbose_name_plural = _(u"История по пер. услугам")
        permissions = (
            ("periodicalservicehistory_view", _(u"Просмотр списаний")),
        )


class OneTimeService(models.Model):
    """
    Справочник разовых услуг
    TO-DO: Сделать справочники валют
    """
    tarif = models.ForeignKey('Tariff')
    name = models.CharField(max_length=255, verbose_name=_(u'Название разовой услуги'), default='', blank=True)
    cost = models.FloatField(verbose_name=_(u'Стоимость разовой услуги'), default=0, blank=True)

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
    onetimeservice = models.ForeignKey(OneTimeService, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    summ = models.IntegerField()
    prev_balance = models.DecimalField(verbose_name=(u'Предыдущий баланс'), decimal_places=5, max_digits=20, blank=True,
                                       default=0)
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    accounttarif = models.ForeignKey('AccountTarif', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Списание по разовым услугам")
        verbose_name_plural = _(u"Списания по разовым услугам")
        permissions = (
            ("onetimeservicehistory_view", _(u"Просмотр услуг")),
        )


class TimeAccessService(models.Model):
    """
    Доступ с тарификацией по времени
    """
    #name              = models.CharField(max_length=255, verbose_name=_(u'Название услуги', unuque=True)
    prepaid_time = models.IntegerField(verbose_name=_(u'Предоплаченное время'), default=0, blank=True)
    reset_time = models.BooleanField(verbose_name=_(u'Сбрасывать  предоплаченное время'), blank=True, default=False)
    tarification_step = models.IntegerField(verbose_name=_(u"Тарифицировать по, c."), blank=True, default=60)
    rounding = models.IntegerField(verbose_name=_(u"Округлять"), default=0, blank=True,
                                   choices=((0, _(u"Не округлять")), (1, _(u"В большую сторону")),))


    def __unicode__(self):
        return u"%s" % self.id

    class Admin:
        #ordering = ['name']
        list_display = ('prepaid_time',)


    class Meta:
        verbose_name = _(u"Доступ с учётом времени")
        verbose_name_plural = _(u"Доступ с учётом времени")
        permissions = (
            ("timeaccessservice_view", _(u"Просмотр услуг доступа по времени")),
        )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('tariff_timeaccessservice_delete'), self.id)


class TimeAccessNode(models.Model):
    """
    Нода тарификации по времени
    """
    time_access_service = models.ForeignKey(to=TimeAccessService, related_name="time_access_nodes")
    time_period = models.ForeignKey(to=TimePeriod, verbose_name=_(u'Промежуток'), null=True, on_delete=models.SET_NULL)
    cost = models.FloatField(verbose_name=_(u'Стоимость за минуту'), default=0)

    def __unicode__(self):
        return u"%s %s" % (self.time_period, self.cost)

    class Admin:
        ordering = ['name']
        list_display = ('time_period', 'cost')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('timeaccessnode_delete'), self.id)

    class Meta:
        verbose_name = _(u"Период доступа")
        verbose_name_plural = _(u"Периоды доступа")
        permissions = (
            ("timeacessnode_view", _(u"Просмотр")),
        )


class AccessParameters(models.Model):
    #name              = models.CharField(max_length=255, verbose_name=_(u'Название вида доступа')
    access_type = models.CharField(max_length=255, choices=ACCESS_TYPE_METHODS, default='PPTP', blank=True,
                                   verbose_name=_(u'Способ доступа'))
    access_time = models.ForeignKey(to=TimePeriod, verbose_name=_(u'Доступ разрешён'), null=True, db_index=True,
                                    on_delete=models.SET_NULL)
    #ip_address_pool   = models.ForeignKey(to=IPAddressPool, verbose_name=_(u'Пул адресов', blank=True, null=True)
    ipn_for_vpn = models.BooleanField(verbose_name=_(u'Выполнять IPN действия'), blank=True, default=False)
    #max_limit      = models.CharField(verbose_name=_(u"MAX (kbps)", max_length=64, blank=True, default="")
    #min_limit      = models.CharField(verbose_name=_(u"MIN (kbps)", max_length=64, blank=True, default="")
    #burst_limit    = models.CharField(verbose_name=_(u"Burst", max_length=64, blank=True, default="")
    #burst_treshold = models.CharField(verbose_name=_(u"Burst treshold (kbps)", max_length=64, blank=True, default="")
    #burst_time     = models.CharField(verbose_name=_(u"Burst Time", blank=True, max_length=64, default="")

    max_tx = models.CharField(verbose_name=_(u"MAX tx (kbps)"), max_length=64, blank=True, default="")
    max_rx = models.CharField(verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")
    burst_tx = models.CharField(verbose_name=_(u"Burst tx (kbps)"), max_length=64, blank=True, default="")
    burst_rx = models.CharField(verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")
    burst_treshold_tx = models.CharField(verbose_name=_(u"Burst treshold tx (kbps)"), max_length=64, blank=True,
                                         default="")
    burst_treshold_rx = models.CharField(verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")
    burst_time_tx = models.CharField(verbose_name=_(u"Burst time tx (s)"), max_length=64, blank=True, default="")
    burst_time_rx = models.CharField(verbose_name=_(u"rx (s)"), max_length=64, blank=True, default="")
    min_tx = models.CharField(verbose_name=_(u"Min tx (kbps)"), max_length=64, blank=True, default="")
    min_rx = models.CharField(verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")



    #от 1 до 8
    priority = models.IntegerField(verbose_name=_(u"Приоритет"), blank=True, default=8)
    sessionscount = models.IntegerField(verbose_name=_(u"Одноверменных RADIUS сессий на субаккаунт"), blank=True,
                                        default=0)

    def __unicode__(self):
        return u"%s" % self.id

    class Admin:
        #ordering = ['name']
        list_display = ('access_type',)


    class Meta:
        verbose_name = _(u"Параметры доступа")
        verbose_name_plural = _(u"Параметры доступа")
        permissions = (
            ("accessparameters_view", _(u"Просмотр параметров доступа")),
        )


class TimeSpeed(models.Model):
    """
    Настройки скорости в интервал времени
    """
    access_parameters = models.ForeignKey(to=AccessParameters, related_name="access_speed")
    time = models.ForeignKey(TimePeriod, on_delete=models.CASCADE)
    #max_limit      = models.CharField(verbose_name=_(u"MAX (kbps)", max_length=64, blank=True, default="")
    #min_limit      = models.CharField(verbose_name=_(u"MIN (kbps)", max_length=64, blank=True, default="")
    #burst_limit    = models.CharField(verbose_name=_(u"Burst", max_length=64, blank=True, default="")
    #burst_treshold = models.CharField(verbose_name=_(u"Burst treshold (kbps)", max_length=64, blank=True, default="")
    #burst_time     = models.CharField(verbose_name=_(u"Burst Time", blank=True, max_length=64, default="")
    #от 1 до 8
    priority = models.IntegerField(verbose_name=_(u"Приоритет"), blank=True, default=8)

    max_tx = models.CharField(verbose_name=_(u"MAX tx (kbps)"), max_length=64, blank=True, default="")
    max_rx = models.CharField(verbose_name=_(u"rx"), max_length=64, blank=True, default="")
    burst_tx = models.CharField(verbose_name=_(u"Burst tx (kbps)"), max_length=64, blank=True, default="")
    burst_rx = models.CharField(verbose_name=_(u"rx"), max_length=64, blank=True, default="")
    burst_treshold_tx = models.CharField(verbose_name=_(u"Burst treshold tx (kbps)"), max_length=64, blank=True,
                                         default="")
    burst_treshold_rx = models.CharField(verbose_name=_(u"rx"), max_length=64, blank=True, default="")
    burst_time_tx = models.CharField(verbose_name=_(u"Burst time tx (s)"), max_length=64, blank=True, default="")
    burst_time_rx = models.CharField(verbose_name=_(u"rx"), max_length=64, blank=True, default="")
    min_tx = models.CharField(verbose_name=_(u"Min tx (kbps)"), max_length=64, blank=True, default="")
    min_rx = models.CharField(verbose_name=_(u"tx"), max_length=64, blank=True, default="")


    def __unicode__(self):
        return u"%s" % self.time

    class Admin:
        pass

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('tariff_timespeed_delete'), self.id)

    class Meta:
        verbose_name = _(u"Настройка скорости")
        verbose_name_plural = _(u"Настройки скорости")
        permissions = (
            ("timespeed_view", _(u"Просмотр")),
        )


class PrepaidTraffic(models.Model):
    """
    Настройки предоплаченного трафика для тарифного плана
    """
    traffic_transmit_service = models.ForeignKey(to="TrafficTransmitService",
                                                 verbose_name=_(u"Услуга доступа по трафику"),
                                                 related_name="prepaid_traffic")
    size = models.FloatField(verbose_name=_(u'Размер в байтах'), default=0, blank=True)
    group = models.ForeignKey("Group")

    def __unicode__(self):
        return u"%s" % self.size

    class Admin:
        ordering = ['traffic_class']
        list_display = ('size',)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('prepaidtraffic_delete'), self.id)

    class Meta:
        verbose_name = _(u"Предоплаченный трафик")
        verbose_name_plural = _(u"Предоплаченный трафик")
        permissions = (
            ("prepaidtraffic_view", _(u"Просмотр")),
        )


class TrafficTransmitService(models.Model):
    #name              = models.CharField(max_length=255, default='', blank=True)
    reset_traffic = models.BooleanField(verbose_name=_(u'Сбрасывать предоплаченный трафик'), blank=True, default=False)
    #Не реализовано в GUI
    #cash_method       = models.CharField(verbose_name=_(u"Списывать за класс трафика", max_length=32,choices=CHOISE_METHODS, blank=True, default=_(u'SUMM', editable=False)
    #Не реализовано в GUI
    #period_check      = models.CharField(verbose_name=_(u"Проверять на наибольший ", max_length=32,choices=CHECK_PERIODS, blank=True, default=_(u'SP_START', editable=False)


    def get_remove_url(self):
        return "%s?id=%s" % (reverse('traffictransmitservice_delete'), self.id)

    class Meta:
        verbose_name = _(u"Доступ с учётом трафика")
        verbose_name_plural = _(u"Доступ с учётом трафика")
        permissions = (
            ("traffictransmitservice_view", _(u"Просмотр")),
        )


class TrafficTransmitNodes(models.Model):
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService,
                                                 verbose_name=_(u"Услуга доступа по трафику"),
                                                 related_name="traffic_transmit_nodes")
    #traffic_class     = models.ManyToManyField(to=TrafficClass, verbose_name=_(u'Классы трафика')
    timeperiod = models.ForeignKey(to=TimePeriod, verbose_name=_(u'Промежуток времени'), null=True,
                                   on_delete=models.SET_NULL)
    group = models.ForeignKey(to='Group', verbose_name=_(u'Группа трафика'), null=True, on_delete=models.SET_NULL)
    cost = models.FloatField(default=0, verbose_name=_(u'Цена за мб.'))
    #edge_start        = models.FloatField(default=0,blank=True, null=True, verbose_name=_(u'Начальная граница', help_text=_(u'Цена актуальна, если пользователь в текущем расчётном периоде наработал больше указанного количество байт')
    #edge_end          = models.FloatField(default=0, blank=True, null=True, verbose_name=_(u'Конечная граница', help_text=_(u'Цена актуальна, если пользователь в текущем расчётном периоде наработал меньше указанного количество байт')
    #in_direction      = models.BooleanField(default=True, blank=True)
    #out_direction      = models.BooleanField(default=True, blank=True)
    #transit_direction      = models.BooleanField()

    def __unicode__(self):
        return u"%s" % (self.cost)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('traffictransmitnode_delete'), self.id)

    class Meta:
        ordering = ['timeperiod', 'group']
        verbose_name = _(u"Цена за направление")
        verbose_name_plural = _(u"Цены за направления трафика")
        permissions = (
            ("traffictransmitnodes_view", _(u"Просмотр")),
        )


class AccountPrepaysTrafic(models.Model):
    """
    При подключении пользователю тарифного плана, у которого есть предоплаченный трафик
    в таблице должны создаваться записи
    В начале каждого расчётного периода пользователю должен заново начисляться трафик
    """
    account_tarif = models.ForeignKey(to="AccountTarif", on_delete=models.CASCADE)
    prepaid_traffic = models.ForeignKey(to=PrepaidTraffic, null=True, on_delete=models.CASCADE)
    size = models.FloatField(blank=True, default=0, verbose_name=_(u'Остаток'))
    datetime = models.DateTimeField(auto_now_add=True, default='', verbose_name=_(u'Начислен'))
    current = models.BooleanField(default=False, verbose_name=_(u'Текущий'))
    reseted = models.BooleanField(default=False, verbose_name=_(u'Сброшен'))

    def __unicode__(self):
        return u"%s" % (self.prepaid_traffic)

    class Admin:
        pass

    def in_percents(self):
        a = self.size * 100 / self.prepaid_traffic.size
        return a

    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"Предоплаченый трафик")
        verbose_name_plural = _(u"Предоплаченный трафик")
        permissions = (
            ("account_prepaystraffic_view", _(u"Просмотр")),
        )


class AccountPrepaysRadiusTrafic(models.Model):
    """
    При подключении пользователю тарифного плана, у которого есть предоплаченный трафик
    в таблице должны создаваться записи
    В начале каждого расчётного периода пользователю должен заново начисляться трафик
    """
    account_tarif = models.ForeignKey(to="AccountTarif", on_delete=models.CASCADE)
    prepaid_traffic = models.ForeignKey(to='RadiusTraffic', null=True, on_delete=models.SET_NULL)
    size = models.FloatField(blank=True, default=0)
    direction = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True, default='')
    current = models.BooleanField(default=False)
    reseted = models.BooleanField(default=False)


    def __unicode__(self):
        return u"%s" % (self.prepaid_traffic)

    class Admin:
        pass

    def in_percents(self):
        a = self.size * 100 / self.prepaid_traffic.size
        return a

    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"Предоплаченый radius трафик ")
        verbose_name_plural = _(u"Предоплаченный radius трафик")

        permissions = (
            ("accountprepaysradiustraffic_view", _(u"Просмотр")),
        )


class AccountPrepaysTime(models.Model):
    account_tarif = models.ForeignKey(to="AccountTarif", on_delete=models.CASCADE)
    prepaid_time_service = models.ForeignKey(to=TimeAccessService, null=True, on_delete=models.SET_NULL)
    size = models.IntegerField(default=0, blank=True)
    datetime = models.DateTimeField(auto_now_add=True, default='')
    current = models.BooleanField(default=False)
    reseted = models.BooleanField(default=False)

    def in_percents(self):
        a = self.size * 100 / self.prepaid_time_service.prepaid_time
        return a

    class Admin:
        pass

    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"Предоплаченное время пользователя")
        verbose_name_plural = _(u"Предоплаченное время пользователей")
        permissions = (
            ("accountprepaystime_view", _(u"Просмотр")),
        )


class TrafficLimit(models.Model):
    tarif = models.ForeignKey('Tariff')
    name = models.CharField(max_length=255, verbose_name=_(u'Название'))
    settlement_period = models.ForeignKey(to=SettlementPeriod, verbose_name=_(u'Период'), blank=True, null=True,
                                          on_delete=models.SET_NULL, help_text=_(
            u"Если период не указан-берётся период тарифного плана. Если установлен автостарт-началом периода будет считаться день привязки тарифного плана пользователю. Если не установлен-старт берётся из расчётного периода"))
    size = models.IntegerField(verbose_name=_(u'Размер в килобайтах'), default=0)
    group = models.ForeignKey("Group", verbose_name=_(u"Группа"))
    mode = models.BooleanField(default=False, blank=True, verbose_name=_(u'За длинну расчётного периода'), help_text=_(
        u'Если флаг установлен-то количество трафика считается за последние N секунд, указанные в расчётном периоде'))
    action = models.IntegerField(verbose_name=_(u"Действие"), blank=True, default=0,
                                 choices=((0, _(u"Заблокировать пользователя")), (1, _(u"Изменить скорость"))))
    speedlimit = models.ForeignKey("SpeedLimit", verbose_name=_(u"Изменить скорость"), blank=True, null=True,
                                   on_delete=models.SET_NULL)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name', 'settlement_period')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('trafficlimit_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Лимит трафика")
        verbose_name_plural = _(u"Лимиты трафика")
        permissions = (
            ("trafficlimit_view", _(u"Просмотр")),
        )


class Tariff(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u'Название'), unique=True)
    description = models.TextField(verbose_name=_(u'Описание тарифного плана'), blank=True, default='')
    access_parameters = models.ForeignKey(to=AccessParameters, verbose_name=_(u'Параметры доступа'), null=True,
                                          blank=True, on_delete=models.SET_NULL)
    contracttemplate = models.ForeignKey("ContractTemplate", verbose_name=_(u"Шаблон номера договора"), blank=True,
                                         null=True, on_delete=models.SET_NULL)
    #traffic_limit     = models.ManyToManyField(to=TrafficLimit, verbose_name=_(u'Лимиты трафика', blank=True, null=True, help_text=_(u"Примеры: 200 мегабайт в расчётный период, 50 мегабайт за последнюю неделю")
    #periodical_services = models.ManyToManyField(to=PeriodicalService, verbose_name=_(u'периодические услуги', blank=True, null=True)
    #onetime_services  = models.ManyToManyField(to=OneTimeService, verbose_name=_(u'Разовые услуги', blank=True, null=True)
    time_access_service = models.ForeignKey(to=TimeAccessService, verbose_name=_(u'Доступ с учётом времени'),
                                            blank=True, null=True, on_delete=models.SET_NULL)
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService, verbose_name=_(u'Доступ с учётом трафика'),
                                                 blank=True, null=True, on_delete=models.SET_NULL)
    radius_traffic_transmit_service = models.ForeignKey(to="RadiusTraffic",
                                                        verbose_name=_(u'RADIUS тарификация трафика'), blank=True,
                                                        null=True, on_delete=models.SET_NULL)
    cost = models.FloatField(verbose_name=_(u'Стоимость пакета'), default=0, help_text=_(
        u"Стоимость активации тарифного плана. Целесообразно указать с расчётным периодом. Если не указана-предоплаченный трафик и время не учитываются"))
    reset_tarif_cost = models.BooleanField(verbose_name=_(u'Производить доснятие'), blank=True, default=False,
                                           help_text=_(
                                               u'Производить доснятие суммы до стоимости тарифного плана в конце расчётного периода'))
    settlement_period = models.ForeignKey(to=SettlementPeriod, blank=True, null=True,
                                          verbose_name=_(u'Расчётный период'))
    ps_null_ballance_checkout = models.BooleanField(verbose_name=_(u'Производить снятие денег  при нулевом баллансе'),
                                                    help_text=_(
                                                        u"Производить ли списывание денег по периодическим услугам при достижении нулевого балланса или исчерпании кредита?"),
                                                    blank=True, default=False)
    active = models.BooleanField(verbose_name=_(u"Активен"), default=False, blank=True)
    deleted = models.BooleanField(default=False, blank=True)
    allow_express_pay = models.BooleanField(verbose_name=_(u'Оплата экспресс картами'), blank=True, default=False)
    require_tarif_cost = models.BooleanField(verbose_name=_(u"Требовать наличия стоимости пакета"), default=False,
                                             blank=True)
    allow_userblock = models.BooleanField(verbose_name=_(u"Разрешить пользовательскую блокировку"), blank=True,
                                          default=False)
    userblock_cost = models.DecimalField(verbose_name=_(u"Стоимость блокировки"), decimal_places=2, max_digits=30,
                                         blank=True, default=0)
    userblock_max_days = models.IntegerField(verbose_name=_(u"MAX длительность блокировки"), blank=True, default=0)
    userblock_require_balance = models.DecimalField(verbose_name=_(u"Минимальный баланс для блокировки"),
                                                    decimal_places=2, max_digits=10, blank=True, default=0)
    allow_ballance_transfer = models.BooleanField(verbose_name=_(u"Разрешить услугу перевода баланса"), blank=True,
                                                  default=False)
    vpn_ippool = models.ForeignKey("IPPool", verbose_name=_(u"VPN IP пул"), blank=True, null=True,
                                   related_name='tariff_vpn_ippool_set', on_delete=models.SET_NULL)
    vpn_guest_ippool = models.ForeignKey("IPPool", verbose_name=_(u"Гостевой VPN IP пул"), blank=True, null=True,
                                         related_name='tariff_guest_vpn_ippool_set', on_delete=models.SET_NULL)
    objects = SoftDeleteManager()

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = (
            'name', 'access_parameters', 'time_access_service', 'traffic_transmit_service', 'cost', 'settlement_period',
            'ps_null_ballance_checkout')


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


ACTIVE = 1
NOT_ACTIVE_NOT_WRITING_OFF = 2
NOT_ACTIVE_WRITING_OFF = 3

ACCOUNT_STATUS = (
    (ACTIVE, _(u'Активен')),
    (NOT_ACTIVE_NOT_WRITING_OFF, _(u'Неактивен, не списывать периодические услуги')),
    (NOT_ACTIVE_WRITING_OFF, _(u'Неактивен, списывать периодические услуги')),
)


class AccountGroup(models.Model):
    name = models.CharField(max_length=512)

    def __unicode__(self):
        return u"%s" % self.name

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accountgroup_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Группа абонентов")
        verbose_name_plural = _(u"Группы абонентов")
        permissions = (
            ("accountgroup_view", _(u"Просмотр")),
        )


class Account(DynamicModel):
    """
    Если стоят галочки assign_vpn_ip_from_dhcp или assign_ipn_ip_from_dhcp,
    значит каждый раз при RADIUS запросе будет провереряться есть ли аренда и не истекла ли она.
    Если аренды нет или она истекла, то создаётся новая и пользователю назначается новый IP адрес.
    """
    #user = models.ForeignKey(User,verbose_name=_(u'Системный пользователь', related_name='user_account2')
    username = models.CharField(verbose_name=_(u'Логин'), max_length=200, unique=True)
    password = EncryptedTextField(verbose_name=_(u'Пароль'), blank=True, default='')
    fullname = models.CharField(verbose_name=_(u'ФИО'), blank=True, default='', max_length=200)
    email = models.CharField(verbose_name=_(u'E-mail'), blank=True, default='', max_length=200)

    address = models.TextField(verbose_name=_(u'Адрес'), blank=True, default='')
    city = models.ForeignKey('City', verbose_name=_(u'Город'), blank=True, null=True, on_delete=models.SET_NULL)
    postcode = models.CharField(verbose_name=_(u'Индекс'), max_length=255, blank=True, null=True)
    region = models.CharField(blank=True, verbose_name=_(u'Район'), max_length=255, default='')
    street = models.CharField(max_length=255, verbose_name=_(u'Улица'), blank=True, null=True)
    house = models.CharField(max_length=255, verbose_name=_(u'Дом'), blank=True, null=True)
    house_bulk = models.CharField(verbose_name=_(u'Корпус'), blank=True, max_length=255)
    entrance = models.CharField(verbose_name=_(u'Подъезд'), blank=True, max_length=255)
    room = models.CharField(verbose_name=_(u'Квартира'), blank=True, max_length=255)


    #nas = models.ForeignKey(to=Nas, blank=True,null=True, verbose_name=_(u'Сервер доступа', on_delete = models.SET_NULL)

    #ipn_added = models.BooleanField(verbose_name=_(u"Добавлен на сервере доступа", default=False, blank=True)
    #ipn_status = models.BooleanField(verbose_name=_(u"Статус на сервере доступа", default=False, blank=True)
    status = models.IntegerField(verbose_name=_(u'Статус'), default=1, choices=(
        (1, _(u"Активен")), (2, _(u"Не активен, списывать периодические услуги")),
        (3, _(u"Не активен, не списывать периодические услуги")), (4, _(u"Пользовательская блокировка")),
        (5, _(u"Системная блокировка"))))
    created = models.DateTimeField(verbose_name=_(u'Создан'), help_text=_(u'Начало оказания услуг'), default='')
    #NOTE: baLance
    ballance = models.DecimalField(_(u'Баланс'), blank=True, default=0, decimal_places=2, max_digits=20)
    bonus_ballance = models.DecimalField(_(u'Бонусный баланс'), blank=True, default=0, decimal_places=2, max_digits=20)
    credit = models.DecimalField(verbose_name=_(u'Кредит'), decimal_places=2, max_digits=20, default=0)
    disabled_by_limit = models.BooleanField(blank=True, default=False, editable=False)
    balance_blocked = models.BooleanField(blank=True, default=False)

    allow_webcab = models.BooleanField(verbose_name=_(u"Разрешить пользоваться веб-кабинетом"), blank=True,
                                       default=True)
    allow_expresscards = models.BooleanField(verbose_name=_(u"Разрешить активацию карт экспресс-оплаты"), blank=True,
                                             default=True)

    passport = models.CharField(verbose_name=_(u'№ паспорта'), blank=True, max_length=64)
    passport_date = models.CharField(verbose_name=_(u'Выдан'), blank=True, max_length=64)
    passportdislocate = models.CharField(verbose_name=_(u'Адрес регистрации'), blank=True, max_length=1024)
    phone_h = models.CharField(validators=[validate_phone], verbose_name=_(u'Дом. телефон'), blank=True, max_length=64)
    phone_m = models.CharField(validators=[validate_phone], verbose_name=_(u'Моб. телефон'),
                               help_text=_(u'В международном формате +71923453333'), blank=True, max_length=64)
    contactperson_phone = models.CharField(validators=[validate_phone], verbose_name=_(u'Тел. контактного лица'),
                                           blank=True, max_length=64)
    comment = models.TextField(blank=True)
    row = models.CharField(verbose_name=_(u'Этаж'), blank=True, max_length=6)
    elevator_direction = models.CharField(verbose_name=_(u'Направление от лифта'), blank=True, null=True,
                                          max_length=128)
    contactperson = models.CharField(verbose_name=_(u'Контактное лицо'), blank=True, max_length=256)
    passport_given = models.CharField(verbose_name=_(u'Кем выдан'), blank=True, null=True, max_length=128)
    contract = models.TextField(verbose_name=_(u'№ договора'), blank=True)
    systemuser = models.ForeignKey('SystemUser', verbose_name=_(u'Менеджер'), blank=True, null=True,
                                   on_delete=models.SET_NULL)
    entrance_code = models.CharField(verbose_name=_(u'Код домофона'), blank=True, max_length=256)
    private_passport_number = models.CharField(verbose_name=_(u'Идент. номер'), blank=True, max_length=128)

    birthday = models.DateField(verbose_name=_(u'День рождения'), blank=True, null=True)
    #allow_ipn_with_null = models.BooleanField()
    #allow_ipn_with_minus = models.BooleanField()
    #allow_ipn_with_block = models.BooleanField()
    deleted = models.DateTimeField(blank=True, null=True, db_index=True)
    promise_summ = models.IntegerField(_(u'Максимальный обещанный платёж'), blank=True, default=0)
    promise_min_ballance = models.IntegerField(_(u'Минимальный баланс для обещанного платежа'), blank=True, default=0)
    promise_days = models.IntegerField(_(u'Длительность обещанного платежа, дней'), blank=True, default=1)
    #allow_block_after_summ = models.BooleanField(_(u'Разрешить блокировку списаний'), blank=True, default=False, help_text= _(u"Разрешить приостановку списаний по периодическим и подключаемым услугам при достижении указанного баланса"))
    #block_after_summ = models.IntegerField(_(u'Блокировка списаний после суммы'), blank=True, default=0)
    account_group = models.ForeignKey(AccountGroup, verbose_name=_(u'Группа'), blank=True, null=True,
                                      on_delete=models.SET_NULL)
    objects = SoftDeletedDateManager()


    def get_actual_ballance(self):
        return self.ballance + self.credit

    def ballance_isnt_good(self):
        if self.ballance + self.credit <= 0:
            return True
        else:
            return False

    def delete(self):
        if not self.deleted:
            self.deleted = datetime.datetime.now()
            self.status = 3 #set suspendedperiod by trigger in db
            self.save()
            return
        super(Account, self).delete()


    def account_status(self):
        if self.status == 1:
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        try:
            user = User.objects.get(username=self.username)
        except:
            user = User()
            user.username = self.username
            user.set_password(self.password)
        user.is_staff = False
        user.is_active = self.deleted is not None
        user.first_name = self.fullname
        user.save()

        super(Account, self).save(*args, **kwargs)

    def get_last_promises_count(self):
        return Transaction.objects.filter(account=self, promise_expired=False,
                                          type=TransactionType.objects.get(internal_name='PROMISE_PAYMENT')).count()


    class Admin:
        ordering = ['user']
        #list_display = ('user', 'vpn_ip_address', 'ipn_ip_address', 'username', 'status', 'credit', 'ballance', 'firstname', 'lastname', 'created')
        #list_filter = ('username')

    def __unicode__(self):
        return '%s' % self.username


    def get_row_class(self):
        return STATUS_CLASS.get(self.status)

    class Meta:
        ordering = ['username']
        verbose_name = _(u"Аккаунт")
        verbose_name_plural = _(u"Аккаунты")
        permissions = (
            ("account_view", _(u"Просмотр")),
            ("get_tariff", _(u"Получить тариф для аккаунта")),
            ("cashier_view", _(u"Список аккаунтов для кассира"))
        )

    @property
    def ips(self):
        vpn_ips = []
        ipn_ips = []
        macs = []
        sas = SubAccount.objects.filter(account=self)
        for sa in sas:
            if sa.vpn_ip_address:
                vpn_ips.append(sa.vpn_ip_address)
            if sa.ipn_ip_address:
                ipn_ips.append(str(sa.ipn_ip_address))
            if sa.ipn_mac_address:
                macs.append(sa.ipn_mac_address)

        return '%s %s %s' % ( ', '.join(vpn_ips), ', '.join(ipn_ips), ', '.join(macs),)

    @models.permalink
    def change_password_url_ajax(self):
        return ('billservice.views.change_password', (), {})

    def is_authenticated(self):
        """Always return True. This is a way to tell if the user has been authenticated in templates.
        """
        return True

    def get_account_tariff(self):
        tariff = Tariff.objects.extra(where=['id=get_tarif(%s)'], params=[self.id])[:1]
        if tariff:
            return tariff[0]

    def get_accounttariff(self):
        accounttarif = AccountTarif.objects.filter(account=self, datetime__lte=datetime.datetime.now()).order_by(
            "-datetime")
        return accounttarif[0] if accounttarif else None

    def get_account_tariff_info(self):
        tariff_info = Tariff.objects.extra(where=['id=get_tarif(%s)'], params=[self.id])[:1]
        for tariff in tariff_info:
            return [tariff.id, tariff.name, ]
        return '', ''

    @property
    def tariff(self):
        try:
            name = Tariff.objects.extra(where=['id=get_tarif(%s)'], params=[self.id])[0].name
        except:
            name = _(u'Не назначен')
        return name

    def get_status(self):
        return dict(ACCOUNT_STATUS)[int(self.status)]

    def get_absolute_url(self):
        return "%s?id=%s" % (reverse('account_edit'), self.id)


class Organization(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_(u"Название организации"))
    #rs = models.CharField(max_length=255)
    uraddress = models.CharField(max_length=255, blank=True, null=True, verbose_name=_(u"Юр. адрес"))
    okpo = models.CharField(max_length=255, blank=True, null=True, verbose_name=_(u"ОКПО"))
    kpp = models.CharField(max_length=255, blank=True, null=True, verbose_name=_(u"КПП"))
    kor_s = models.CharField(max_length=255, blank=True, null=True, verbose_name=_(u"Корреспонденский счёт"))
    unp = models.CharField(max_length=255, blank=True, null=True, verbose_name=_(u"УНП"))
    phone = models.CharField(validators=[validate_phone], max_length=255, blank=True, null=True,
                             verbose_name=_(u"Телефон"))
    fax = models.CharField(max_length=255, blank=True, null=True, verbose_name=_(u"Факс"))
    bank = models.ForeignKey("BankData", blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_(u"Банк"))

    def __unicode__(self):
        return u"%s" % (self.name, )

    class Meta:
        permissions = (
            ("organization_view", _(u"Просмотр организации")),
        )


class TransactionType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    internal_name = models.CharField(max_length=32, unique=True)
    is_deletable = models.BooleanField(verbose_name=_(u'Может быть удалён'), blank=True, default=True)
    allowed_systemusers = models.ManyToManyField("SystemUser", verbose_name=u'Разрешено выполнять', blank=True,
                                                 null=True)
    is_bonus = models.BooleanField(verbose_name=u'Является бонусной', blank=True, default=False)
    #content_type = models.ForeignKey(ContentType)
    #object_id = models.PositiveIntegerField()
    #content_object = generic.GenericForeignKey('content_type', 'object_id')
    def __unicode__(self):
        return u"%s" % (self.name,)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('transactiontype_delete'), self.id)

    class Admin:
        pass

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Тип проводки")
        verbose_name_plural = _(u"Типы проводок")
        permissions = (
            ("transactiontype_view", _(u"Просмотр")),
        )

#===============================================================================


class Transaction(models.Model):
    bill = models.CharField(blank=True, default="", max_length=255, verbose_name=_(u"Платёжный документ"))
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_(u"Аккаунт"))
    accounttarif = models.ForeignKey('AccountTarif', blank=True, null=True, on_delete=models.CASCADE)
    type = models.ForeignKey(to=TransactionType, null=True, to_field='internal_name', verbose_name=_(u"Тип"),
                             on_delete=models.SET_NULL)

    is_bonus = models.BooleanField(default=False, blank=True, verbose_name=u'Бонус')
    approved = models.BooleanField(default=True)
    tarif = models.ForeignKey(Tariff, blank=True, null=True, on_delete=models.SET_NULL)
    summ = models.DecimalField(default=0, blank=True, verbose_name=_(u"Сумма"), decimal_places=10, max_digits=20)
    prev_balance = models.DecimalField(verbose_name=(u'Предыдущий баланс'), decimal_places=5, max_digits=20, blank=True,
                                       default=0)
    description = models.TextField(default='', blank=True, verbose_name=_(u"Комментарий"))
    created = models.DateTimeField(verbose_name=_(u"Дата"))
    #promise=models.BooleanField(default=False, verbose_name=_(u"Обещанный платёж"))
    end_promise = models.DateTimeField(blank=True, null=True, verbose_name=_(u"Закрыть ОП"))
    promise_expired = models.BooleanField(default=False, verbose_name=_(u"ОП истек"))
    systemuser = models.ForeignKey(to='SystemUser', null=True, on_delete=models.SET_NULL, verbose_name=_(u"Выполнил"))

    #def update_ballance(self):
    #    Account.objects.filter(id=self.account_id).update(ballance=F('ballance')+self.summ)

    def save(self, *args, **kwargs):
        from django.db import connection
        connection.features.can_return_id_from_insert = False
        super(Transaction, self).save(*args, **kwargs)

    class Admin:
        list_display = ('account', 'tarif', 'summ', 'description', 'created')

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Проводка")
        verbose_name_plural = _(u"Проводки")
        permissions = (
            ("transaction_view", _(u"Просмотр")),
        )

    @staticmethod
    def create_payment(account, summ, created, bill, trtype):
        tr = Transaction()
        tr.account = account
        tr.bill = bill
        tr.summ = summ
        tr.created = created
        tr.type = TransactionType.objects.get(internal_name=trtype)
        tr.save()

    def human_sum(self):
        return self.summ

    def __unicode__(self):
        return u"%s, %s, %s" % (self.account, self.summ, self.created)


class AccountTarif(models.Model):
    account = models.ForeignKey(verbose_name=_(u'Пользователь'), to=Account, related_name='related_accounttarif')
    prev_tarif = models.ForeignKey(to=Tariff, verbose_name=_(u'Предыдущий тарифный план'), blank=True, null=True, related_name="account_prev_tarif")
    tarif = models.ForeignKey(to=Tariff, verbose_name=_(u'Тарифный план'), related_name="account_tarif")
    datetime = models.DateTimeField(verbose_name=_(u'C даты'), default='', blank=True)
    periodical_billed = models.BooleanField(blank=True)

    class Admin:
        ordering = ['-datetime']
        list_display = ('account', 'tarif', 'datetime')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accounttariff_delete'), self.id)

    def __unicode__(self):
        return u"%s, %s" % (self.account, self.tarif)

    def save(self, *args, **kwargs):
       # custom save method #pdb.set_trace() 


        if not self.id:
            at = AccountTarif.objects.filter(account=self.account).order_by('-id')
            if at:
                print at[0]
                self.prev_tarif = at[0].tarif
        super(AccountTarif, self).save(*args, **kwargs)
    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"Тариф аккаунта")
        verbose_name_plural = _(u"Тариф аккаунта")
        permissions = (
            ("accounttarif_view", _(u"Просмотр")),
        )


class AccountIPNSpeed(models.Model):
    """
    Класс описывает настройки скорости для пользователей с тарифными планами IPN
    После создания пользователя должна создваться запись в этой таблице
    """
    account = models.ForeignKey(to=Account)
    speed = models.CharField(max_length=32, default='')
    state = models.BooleanField(blank=True, default=False)
    static = models.BooleanField(verbose_name=_(u"Статическая скорость"), help_text=_(
        u"Пока опция установлена, биллинг не будет менять для этого клиента скорость"), blank=True, default=False)
    datetime = models.DateTimeField(default='')

    def __unicode__(self):
        return u"%s %s" % (self.account, self.speed)

    class Admin:
        pass

    class Meta:
        verbose_name = _(u"Скорость IPN клиента")
        verbose_name_plural = _(u"Скорости IPN клиентов")


class SheduleLog(models.Model):
    account = models.ForeignKey(to=Account, unique=True)
    accounttarif = models.ForeignKey(to=AccountTarif, blank=True, null=True)
    ballance_checkout = models.DateTimeField(blank=True, null=True)
    prepaid_traffic_reset = models.DateTimeField(blank=True, null=True)
    prepaid_traffic_accrued = models.DateTimeField(blank=True, null=True)
    prepaid_time_reset = models.DateTimeField(blank=True, null=True)
    prepaid_time_accrued = models.DateTimeField(blank=True, null=True)
    balance_blocked = models.DateTimeField(blank=True, null=True)

    class Admin:
        pass

    class Meta:
        verbose_name = _(u"История периодических операций")
        verbose_name_plural = _(u"История периодических операций")


    def __unicode__(self):
        return u'%s' % self.account.username


class SystemUser(models.Model):
    username = models.CharField(max_length=255, unique=True)
    #password = models.CharField(max_length=255, default='')
    email = models.CharField(verbose_name=_(u'E-mail'), blank=True, default='', max_length=200)
    fullname = models.CharField(verbose_name=_(u'ФИО'), max_length=512, blank=True, default='')
    home_phone = models.CharField(validators=[validate_phone], verbose_name=_(u'Дом. телефон'), max_length=512,
                                  blank=True, default='')
    mobile_phone = models.CharField(validators=[validate_phone], verbose_name=_(u'Моб. телефон'),
                                    help_text=_(u'В международном формате +71231231212'), max_length=512, blank=True,
                                    default='')
    address = models.CharField(verbose_name=_(u'Адрес'), max_length=512, blank=True, default='')
    job = models.CharField(verbose_name=_(u'Должность'), max_length=256, blank=True, default='')
    last_ip = models.CharField(verbose_name=_(u'Последний IP'), max_length=64, blank=True, null=True)
    last_login = models.DateTimeField(verbose_name=_(u'Последний логин'), blank=True, null=True)
    description = models.TextField(verbose_name=_(u'Комментарий'), blank=True, default='')
    created = models.DateTimeField(verbose_name=_(u'Создан'), blank=True, null=True, auto_now_add=True)
    status = models.BooleanField(verbose_name=_(u'Статус'), default=False)
    host = models.CharField(verbose_name=_(u'Разрешённые IP'), max_length=255, blank=True, null=True,
                            default="0.0.0.0/0")
    #group = models.ManyToManyField(SystemGroup)
    text_password = EncryptedTextField(verbose_name=_(u'Пароль'), blank=True, default='')
    passport = EncryptedTextField(verbose_name=_(u'№ паспорта'), max_length=512, blank=True, default='')
    passport_details = models.CharField(verbose_name=_(u'Паспорт выдан'), max_length=512, blank=True, default='')
    passport_number = models.CharField(verbose_name=_(u'Личный номер'), max_length=512, blank=True, default='')
    unp = models.CharField(verbose_name=_(u'УНП'), max_length=1024, blank=True, default='')
    im = models.CharField(verbose_name=_(u'ICQ/Skype'), max_length=512, blank=True, default='')
    permissiongroup = models.ForeignKey("PermissionGroup", blank=True, null=True, verbose_name=_(u"Группа доступа"))
    is_superuser = models.BooleanField(verbose_name=_(u"Суперадминистратор"))

    permcache = {}

    def __str__(self):
        return '%s' % self.username

    def __unicode__(self):
        return u'%s' % self.username

    def is_authenticated(self):
        """Always return True. This is a way to tell if the user has been authenticated in templates.
        """
        return True

    def get_absolute_url(self):
        return "%s?id=%s" % (reverse('systemuser_edit'), self.id)

    def save(self, *args, **kwargs):
        try:
            user = User.objects.get(username=self.username)
        except:
            user = User()
            user.username = self.username
            user.set_password(self.text_password)
        user.is_staff = True
        user.is_active = self.status
        user.first_name = self.fullname
        user.is_superuser = self.is_superuser
        user.save()
        super(SystemUser, self).save(*args, **kwargs)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('systemuser_delete'), self.id)

    def has_perm(self, perm):
        app, internal_name = perm.split('.')
        #if perm in self.permcache:
        #    return self.permcache[perm]
        #print app, internal_name, self.permissiongroup.permissions.filter(app=app, internal_name=internal_name) if self.permissiongroup else ''
        r = self.status and (self.is_superuser or (self.permissiongroup.permissions.filter(app=app,
                                                                                           internal_name=internal_name).exists() if self.permissiongroup else False))
        #self.permcache[perm]=r
        return r

    def delete(self):
        return

    class Meta:
        ordering = ['username']
        verbose_name = _(u"Пользователь системы")
        verbose_name_plural = _(u"Пользователи системы")
        permissions = (
            ("systemuser_view", _(u"Просмотр администраторов")),
            ("get_model", _(u"Получение любой модели методом get_model")),
            ("actions_set", _(u"Установка IPN статуса на сервере доступаl")),
            ("documentrender", _(u"Серверный рендеринг документов")),
            ("testcredentials", _(u"Тестирование данных для сервера доступа")),
            ("getportsstatus", _(u"Получение статуса портов коммутатора")),
            ("setportsstatus", _(u"Установка статуса портов коммутатора")),
            ("list_log_files", _(u"Список лог-файлов биллинга")),
            ("view_log_files", _(u"Просмотр лог-файлов биллинга")),
            ("transactions_delete", _(u"Удаление проводок")),
            ("sp_info", _(u"Метод sp_info")),
            ("auth_groups", _(u"Просмотр груп доступа")),
            ("rawsqlexecution", _(u"Выполнение любого sql запроса"))

        )


class DocumentType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']


class TemplateType(models.Model):
    name = models.TextField(verbose_name=_(u"Название типа шаблона"))

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        ordering = ['id']
        verbose_name = _(u"Тип шаблона")
        verbose_name_plural = _(u"Типы шаблонов")
        permissions = (
            ("templatetype_view", _(u"Просмотр")),
        )


class Template(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(TemplateType)
    body = models.TextField()

    def __unicode__(self):
        return u"%s" % (self.name)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('template_delete'), self.id)

    class Meta:
        ordering = ['type']
        verbose_name = _(u"Шаблон")
        verbose_name_plural = _(u"Шаблоны")
        permissions = (
            ("template_view", _(u"Просмотр")),
        )


class Card(models.Model):
    series = models.CharField(max_length=32, verbose_name=_(u"Серия"))
    pin = models.CharField(max_length=255, verbose_name=_(u"Пин"))
    login = models.CharField(max_length=255, blank=True, default='', verbose_name=_(u"Логин"))
    #sold = models.DateTimeField(blank=True, null=True, verbose_name=_(u"Продана")
    nominal = models.FloatField(default=0, verbose_name=_(u"Номинал"))
    activated = models.DateTimeField(blank=True, null=True, verbose_name=_(u"Актив-на"))
    activated_by = models.ForeignKey(Account, blank=True, null=True, verbose_name=_(u"Аккаунт"))
    start_date = models.DateTimeField(blank=True, default='', verbose_name=_(u"Актив-ть с"))
    end_date = models.DateTimeField(blank=True, default='', verbose_name=_(u"по"))
    disabled = models.BooleanField(verbose_name=_(u"Неактивна"), default=False, blank=True)
    created = models.DateTimeField(verbose_name=_(u"Создана"))
    #template = models.ForeignKey(Template, verbose_name=_(u"Шаблон")
    type = models.IntegerField(verbose_name=_(u"Тип"), choices=(
        (0, _(u"Экспресс-оплаты"), ), (1, _(u'Хотспот')), (2, _(u'VPN доступ')), (3, _(u'Телефония')),))
    tarif = models.ForeignKey(Tariff, blank=True, null=True, verbose_name=_(u"Тариф"))
    nas = models.ForeignKey(Nas, blank=True, null=True)
    ip = models.CharField(max_length=20, blank=True, default='')
    ipinuse = models.ForeignKey("IPInUse", blank=True, null=True)
    ippool = models.ForeignKey("IPPool", verbose_name=_(u"Пул"), blank=True, null=True)
    ext_id = models.CharField(max_length=512, blank=True, null=True)
    salecard = models.ForeignKey("SaleCard", verbose_name=_(u"Продана"), blank=True, null=True,
                                 on_delete=models.SET_NULL)

    def get_row_class(self):
        return 'error' if self.disabled else ''

    class Meta:
        ordering = ['-series', '-created', 'activated']
        verbose_name = _(u"Карта")
        verbose_name_plural = _(u"Карты")
        permissions = (
            ("card_view", _(u"Просмотр карт")),
        )


class BankData(models.Model):
    bank = models.CharField(max_length=255, verbose_name=_(u"Название банка"))
    bankcode = models.CharField(blank=True, default='', max_length=40, verbose_name=_(u"Код банка"))
    rs = models.CharField(blank=True, default='', max_length=60, verbose_name=_(u"Расчётный счёт"))
    currency = models.CharField(blank=True, default='', max_length=40, verbose_name=_(u"Валюта расчётов"))

    def __unicode__(self):
        return u"%s" % self.id

    class Meta:
        ordering = ['bank']
        verbose_name = _(u"Банк")
        verbose_name_plural = _(u"Банки")
        permissions = (
            ("view", _(u"Просмотр банков")),
        )


class Operator(models.Model):
    organization = models.CharField(verbose_name=_(u'Название'), max_length=255)
    unp = models.CharField(verbose_name=_(u'УНП'), max_length=40, blank=True, default='')
    okpo = models.CharField(verbose_name=_(u'ОКПО'), max_length=40, blank=True, default='')
    contactperson = models.CharField(verbose_name=_(u'Контактное лицо'), max_length=255, blank=True, default='')
    director = models.CharField(verbose_name=_(u'Директор'), max_length=255, blank=True, default='')
    phone = models.CharField(verbose_name=_(u'Телефон'), max_length=40, blank=True, default='')
    fax = models.CharField(verbose_name=_(u'Факс'), max_length=40, blank=True, default='')
    postaddress = models.CharField(verbose_name=_(u'Почтовый адрес'), max_length=255, blank=True, default='')
    uraddress = models.CharField(verbose_name=_(u'Юр. адрес'), max_length=255, blank=True, default='')
    email = models.EmailField(verbose_name=_(u'E-mail'), max_length=255, blank=True, default='')
    #bank = models.ForeignKey(BankData, blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.organization

    class Meta:
        verbose_name = _(u"Информация о провайдере")
        verbose_name_plural = _(u"Информация о провайдере")
        permissions = (
            ("operator_view", _(u"Просмотр")),
        )


class Dealer(models.Model):
    organization = models.CharField(max_length=400, verbose_name=_(u"Организация"))
    unp = models.CharField(max_length=255, blank=True, default='', verbose_name=_(u"УНП"))
    okpo = models.CharField(max_length=255, blank=True, default='', verbose_name=_(u"ОКПО"))
    contactperson = models.CharField(max_length=255, blank=True, default='', verbose_name=_(u"Контактное лицо"))
    director = models.CharField(max_length=255, blank=True, default='', verbose_name=_(u"Директор"))
    phone = models.CharField(max_length=255, blank=True, default='', verbose_name=_(u"Телефон"))
    fax = models.CharField(max_length=255, blank=True, default='', verbose_name=_(u"Факс"))
    postaddress = models.CharField(max_length=400, blank=True, default='', verbose_name=_(u"Почтовый адрес"))
    uraddress = models.CharField(max_length=400, blank=True, default='', verbose_name=_(u"Юр. адрес"))
    email = models.EmailField(verbose_name=_(u'E-mail'), max_length=255, blank=True, null=True)
    prepayment = models.FloatField(blank=True, default=0, verbose_name=_(u"% предоплаты"))
    paydeffer = models.IntegerField(blank=True, default=0, verbose_name=_(u"Отсрочка платежа"))
    discount = models.FloatField(blank=True, default=0, verbose_name=_(u"Скидка"))
    always_sell_cards = models.BooleanField(default=False)

    bank = models.ForeignKey(BankData, blank=True, null=True, on_delete=models.SET_NULL)
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


class SaleCard(models.Model):
    dealer = models.ForeignKey(Dealer)
    #pay = models.FloatField()
    sum_for_pay = models.FloatField(blank=True, verbose_name=_(u"Сумма к оплате"), default=0)
    paydeffer = models.IntegerField(blank=True, verbose_name=_(u"Отсрочка платежа, дн."), default=0)
    discount = models.FloatField(blank=True, verbose_name=_(u"Сидка, %"), default=0)
    discount_sum = models.FloatField(blank=True, verbose_name=_(u"Сумма скидки"), default=0)
    prepayment = models.FloatField(blank=True, verbose_name=_(u"% предоплаты"), default=0)
    #cards = models.ManyToManyField(Card, blank=True, null=True)
    created = models.DateTimeField(verbose_name=_(u"Создана"), auto_now_add=True, blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Накладная на карты")
        verbose_name_plural = _(u"накладные на карты")
        permissions = (
            ("salecard_view", _(u"Просмотр")),
        )


class DealerPay(models.Model):
    dealer = models.ForeignKey(Dealer)
    pay = models.FloatField()
    salecard = models.ForeignKey(SaleCard, blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Платёж дилера")
        verbose_name_plural = _(u"Платежи дилера")
        permissions = (
            ("dealerpay_view", _(u"Просмотр")),
        )


class Document(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True)
    type = models.ForeignKey(Template, blank=True, null=True)
    body = models.TextField()
    contractnumber = models.CharField(max_length=1024)
    date_start = models.DateTimeField(blank=True)
    date_end = models.DateTimeField(blank=True, null=True)


    def __unicode__(self):
        return u"%s %s" % (self.type, self.date_start)


class SuspendedPeriod(models.Model):
    account = models.ForeignKey(Account)
    start_date = models.DateTimeField(verbose_name=_(u"Дата начала"))
    end_date = models.DateTimeField(verbose_name=_(u"Дата конца"), blank=True, null=True)
    activated_by_account = models.BooleanField(verbose_name=_(u"Активировано аккаунтом"), blank=True, default=False)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('suspendedperiod_delete'), self.id)

    class Meta:
        ordering = ['-start_date']
        verbose_name = _(u"Период без списаний")
        verbose_name_plural = _(u"Периоды без списаний")
        permissions = (
            ("suspendedperiod_view", _(u"Просмотр")),
        )


class Group(models.Model):
    #make it an array
    name = models.CharField(verbose_name=_(u'Название'), max_length=255)
    trafficclass = models.ManyToManyField(TrafficClass, verbose_name=_(u'Классы трафика'))
    #1 - in, 2-out, 3 - sum, 4-max
    direction = models.IntegerField(verbose_name=_(u'Направление'),
                                    choices=((0, _(u"Входящий")), (1, _(u"Исходящий")), (2, _(u"Вх.+Исх.")),))
    # 1 -sum, 2-max
    type = models.IntegerField(verbose_name=_(u'Тип'),
                               choices=((1, _(u"Сумма классов")), (2, _(u"Максимальный класс"))))

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('group_delete'), self.id)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Группа трафика")
        verbose_name_plural = _(u"Группы трафика")
        permissions = (
            ("group_view", _(u"Просмотр")),
        )


"""class GroupTrafficClass(models.Model):
    group = models.ForeignKey(Group)
    trafficclass = models.ForeignKey(TrafficClass)
    
    
    class Meta:
        db_table = "billservice_group_trafficclass"
"""


class GroupStat(models.Model):
    group = models.ForeignKey(Group)
    account = models.ForeignKey(Account)
    bytes = models.IntegerField()
    datetime = models.DateTimeField()


class GlobalStat(models.Model):
    account = models.ForeignKey(Account)
    bytes_in = models.BigIntegerField()
    bytes_out = models.BigIntegerField()
    datetime = models.DateTimeField()

    #trafficclass = models.ForeignKey(TrafficClass, blank=True, null=True)


#class GroupStatAll(models.Model):
#    account = models.ForeignKey(Account)

class SpeedLimit(models.Model):
    change_speed_type = models.CharField(verbose_name=_(u"Способ изменения скорости"), max_length=32,
                                         choices=(("add", "Добавить к текущей"), ("abs", "Абсолютное значение",),),
                                         blank=True, null=True)
    speed_units = models.CharField(verbose_name=_(u"Единицы"), max_length=32,
                                   choices=(("Kbps", "Kbps",), ("Mbps", "Mbps",), ("%", "%",)), blank=True, null=True)
    max_tx = models.IntegerField(verbose_name=_(u"MAX tx (kbps)"), default=0, blank=True)
    max_rx = models.IntegerField(verbose_name=_(u"rx"), default=0, blank=True)
    burst_tx = models.IntegerField(verbose_name=_(u"Burst tx (kbps)"), default=0, blank=True)
    burst_rx = models.IntegerField(verbose_name=_(u"rx"), blank=True, default=0)
    burst_treshold_tx = models.IntegerField(verbose_name=_(u"Burst treshold tx (kbps)"), default=0, blank=True)
    burst_treshold_rx = models.IntegerField(verbose_name=_(u"rx"), default=0, blank=True)
    burst_time_tx = models.IntegerField(verbose_name=_(u"Burst time tx (kbps)"), default=0, blank=True)
    burst_time_rx = models.IntegerField(verbose_name=_(u"rx"), default=0, blank=True)
    min_tx = models.IntegerField(verbose_name=_(u"Min tx (kbps)"), default=0, blank=True)
    min_rx = models.IntegerField(verbose_name=_(u"tx"), default=0, blank=True)
    priority = models.IntegerField(default=0, blank=True)

    def __unicode__(self):
        return "%s/%s %s/%s %s/%s %s/%s %s/%s %s" % (
            self.max_tx, self.max_rx, self.burst_tx, self.burst_rx, self.burst_treshold_tx, self.burst_treshold_rx,
            self.burst_time_tx, self.burst_time_rx, self.min_tx, self.min_rx, self.priority)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('speedlimit_delete'), self.id)


class AccountSpeedLimit(models.Model):
    account = models.ForeignKey(Account)
    speedlimit = models.ForeignKey(SpeedLimit)


class IPPool(models.Model):
    name = models.CharField(verbose_name=_(u'Название'), max_length=255)
    #0 - VPN, 1-IPN
    type = models.IntegerField(verbose_name=_(u'Тип'), choices=(
        (0, _(u"IPv4 VPN")), (1, _(u"IPv4 IPN")), (2, _(u"IPv6 VPN")), (3, _(u"IPv6 IPN")),))
    start_ip = models.GenericIPAddressField(verbose_name=_(u'C IP'))
    end_ip = models.GenericIPAddressField(verbose_name=_(u'По IP'))
    next_ippool = models.ForeignKey("IPPool", verbose_name=_(u'Следующий пул'), blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"IP пул")
        verbose_name_plural = _(u"IP пулы")
        permissions = (
            ("ippool_view", _(u"Просмотр")),
        )

    def __unicode__(self):
        return u"%s" % self.name

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('ippool_delete'), self.id)

    def get_pool_size(self):
        return IPy.IP(self.end_ip).int() - IPy.IP(self.start_ip).int()

    def get_used_ip_count(self):
        return self.ipinuse_set.filter(Q(dynamic=True, last_update__gte=datetime.datetime.now()-datetime.timedelta(minutes=15)) | Q(dynamic=False, disabled__isnull=True)).count()


class IPInUse(models.Model):
    pool = models.ForeignKey(IPPool, verbose_name=_(u'IP пул'))
    ip = models.CharField(max_length=255, verbose_name=_(u'IP адрес'))
    datetime = models.DateTimeField(verbose_name=_(u'Дата выдачи'))
    disabled = models.DateTimeField(blank=True, null=True, verbose_name=_(u'Дата освобождения'))
    dynamic = models.BooleanField(default=False, verbose_name=_(u'Выдан динамически'))
    ack = models.BooleanField(default=False, blank=True, verbose_name=_(u'Подтверждён'))
    last_update = models.DateTimeField(blank=True, null=True, verbose_name=_(u'Последнее обновление'), help_text=_(u'Для динамической выдачи'))

    class Meta:
        ordering = ['ip']
        verbose_name = _(u"Занятый IP адрес")
        verbose_name_plural = _(u"Занятые IP адреса")
        permissions = (
            ("ipinuse_view", _(u"Просмотр")),
        )

    def __unicode__(self):
        return u"%s" % self.ip


class TrafficTransaction(models.Model):
    traffictransmitservice = models.ForeignKey(TrafficTransmitService, null=True,
                                               on_delete=models.SET_NULL) # ON DELETE SET NULL
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    summ = models.FloatField()
    prev_balance = models.DecimalField(verbose_name=(u'Предыдущий баланс'), decimal_places=5, max_digits=20, blank=True,
                                       default=0)
    created = models.DateTimeField()
    accounttarif = models.ForeignKey(AccountTarif, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Списание за трафик")
        verbose_name_plural = _(u"Списания за трафик")
        permissions = (
            ("traffictransaction_view", _(u"Просмотр")),
        )


class TimeTransaction(models.Model):
    timeaccessservice = models.ForeignKey(TimeAccessService, null=True, on_delete=models.SET_NULL) # ON DELETE SET NULL
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    summ = models.FloatField()
    prev_balance = models.DecimalField(verbose_name=(u'Предыдущий баланс'), decimal_places=5, max_digits=20, blank=True,
                                       default=0)
    created = models.DateTimeField()
    accounttarif = models.ForeignKey(AccountTarif, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Списание за время")
        verbose_name_plural = _(u"Списания за время")
        permissions = (
            ("transaction_view", _(u"Просмотр")),
        )


class TPChangeRule(models.Model):
    from_tariff = models.ForeignKey(Tariff, verbose_name=_(u'С тарифного плана'), related_name="from_tariff")
    to_tariff = models.ForeignKey(Tariff, verbose_name=_(u'На тарифный план'), related_name="to_tariff")
    disabled = models.BooleanField(verbose_name=_(u'Временно запретить'), blank=True, default=False)
    cost = models.FloatField(verbose_name=_(u'Стоимость перехода'))
    ballance_min = models.FloatField(verbose_name=_(u'Минимальный баланс'))
    on_next_sp = models.BooleanField(verbose_name=_(u'Со следующего расчётного периода'), blank=True, default=False)
    settlement_period = models.ForeignKey(SettlementPeriod, verbose_name=_(u'Расчётный период'), blank=True, null=True,
                                          on_delete=models.SET_NULL)


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


class RadiusAttrs(models.Model):
    tarif = models.ForeignKey(Tariff, blank=True, null=True)
    nas = models.ForeignKey(Nas, blank=True, null=True)
    vendor = models.IntegerField(blank=True, default=0)
    attrid = models.IntegerField()
    value = models.CharField(max_length=255)

    account_status = models.IntegerField(choices=((0, _(u'Всегда')), (1, _(u'Активен')), (2, _(u'Не активен')),),
                                         default=0, verbose_name=_(u'Статус аккаунта'),
                                         help_text=_(u'Добавлять атрибут в Access Accept, если срабатывает условие'))

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('radiusattr_delete'), self.id)

    class Meta:
        ordering = ['vendor', 'attrid']
        verbose_name = _(u"Custom RADIUS атрибут")
        verbose_name_plural = _(u"Custom RADIUS атрибуты")
        permissions = (
            ("radiusattrs_view", _(u"Просмотр")),
        )


class AddonService(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u'Название'))
    comment = models.TextField(blank=True, default='', verbose_name=_(u'Комментарий'))
    allow_activation = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разешить активацию"),
                                           help_text=_(u'Разрешить активацию при нулевом балансе и блокировках'))
    service_type = models.CharField(verbose_name=_(u"Тип услуги"), max_length=32, choices=(
        ("onetime", _(u"Разовая услуга")), ("periodical", _(u"Периодическая услуга")),))
    sp_type = models.CharField(verbose_name=_(u"Способ списания"), max_length=32, choices=(
        ("AT_START", _(u"В начале расчётного периода")), ("AT_END", _(u"В конце расчётного периода") ),
        ("GRADUAL", _(u"На протяжении расчётного периода")),))
    tpd = models.SmallIntegerField(verbose_name=_(u'Кол-во списаний в сутки'), default=1, blank=True, null=True)
    sp_period = models.ForeignKey(SettlementPeriod, verbose_name=_(u"Расчётный период"),
                                  help_text=_(u"Период, в течении которого будет списываться стоимость услуги"),
                                  related_name="addonservice_spperiod", blank=True, null=True,
                                  on_delete=models.SET_NULL)
    timeperiod = models.ForeignKey(TimePeriod, verbose_name=_(u"Время активации"),
                                   help_text=_(u"Время, когда услуга будет активирована"), null=True,
                                   on_delete=models.SET_NULL)
    cost = models.DecimalField(verbose_name=_(u"Стоимость услуги"), decimal_places=2, max_digits=10, blank=True,
                               default=0)
    cancel_subscription = models.BooleanField(verbose_name=_(u"Разрешить отключение"),
                                              help_text=_(u"Разрешить самостоятельное отключение услуги"), default=True)
    wyte_period = models.ForeignKey(SettlementPeriod, verbose_name=_(u"Штрафуемый период"), help_text=_(
        u"Списывать сумму штрафа при досрочном отключении услуги пользователем"),
                                    related_name="addonservice_wyteperiod", blank=True, null=True,
                                    on_delete=models.SET_NULL)
    wyte_cost = models.DecimalField(verbose_name=_(u"Сумма штрафа"), decimal_places=2, max_digits=10, blank=True,
                                    default=0)
    action = models.BooleanField(verbose_name=_(u"Выполнить действие"), blank=True, default=False)
    nas = models.ForeignKey(Nas, verbose_name=_(u"Сервер доступа"),
                            help_text=_(u"Сервер доступа, на котором будут производиться действия"), blank=True,
                            null=True, on_delete=models.SET_NULL)
    service_activation_action = models.TextField(verbose_name=_(u"Действие для активации услуги"), blank=True,
                                                 default='')
    service_deactivation_action = models.TextField(verbose_name=_(u"Действие для отключения услуги"), blank=True,
                                                   default='')
    deactivate_service_for_blocked_account = models.BooleanField(
        verbose_name=_(u"Отключать услугу при бловировке аккаунта"),
        help_text=_(u"Отключать услугу при достижении нулевого баланса или блокировках"), blank=True, default=False)
    change_speed = models.BooleanField(verbose_name=_(u"Изменить скорость"),
                                       help_text=_(u"Изменить параметры скорости при активации аккаунта"), blank=True,
                                       default=False)
    change_speed_type = models.CharField(verbose_name=_(u"Способ изменения скорости"), max_length=32, choices=(
        ("add", _(u"Добавить к текущей")), ("abs", _(u"Абсолютное значение"))), blank=True, null=True)
    speed_units = models.CharField(verbose_name=_(u"Единицы скорости"), max_length=32,
                                   choices=(("Kbps", "Kbps",), ("Mbps", "Mbps",), ("%", "%",)), blank=True, null=True)
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
    priority = models.IntegerField(blank=True, default=0)


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
    tarif = models.ForeignKey(Tariff)
    service = models.ForeignKey(AddonService, verbose_name=_(u"Услуга"))
    activation_count = models.IntegerField(verbose_name=_(u"Активаций за расчётный период"), blank=True, default=0)
    activation_count_period = models.ForeignKey(SettlementPeriod, verbose_name=_(u"Расчётный период"), blank=True,
                                                null=True)
    type = models.IntegerField(verbose_name=_(u"Тип активации"),
                               choices=((0, _(u"На аккаунт")), (1, _(u"На субаккаунт")), ),
                               default=0)# 0-Account, 1-Subaccount

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


class AccountAddonService(models.Model):
    service = models.ForeignKey(AddonService, null=True, verbose_name=_(u'Услуга'), on_delete=models.CASCADE)
    account = models.ForeignKey(Account, verbose_name=_(u'Аккаунт'), blank=True, null=True, on_delete=models.CASCADE)
    subaccount = models.ForeignKey('SubAccount', verbose_name=_(u'Субаккаунт'), blank=True, null=True,
                                   on_delete=models.CASCADE)
    cost = models.DecimalField(verbose_name=u'Стоимость',
                               help_text=u'Укажите, если хотите задать цену, отличную от указанной в услуге',
                               decimal_places=2, max_digits=15, blank=True, null=True)
    activated = models.DateTimeField(verbose_name=_(u'Активирована'))
    deactivated = models.DateTimeField(verbose_name=_(u'Отключена'), blank=True, null=True)
    action_status = models.BooleanField()
    speed_status = models.BooleanField()
    temporary_blocked = models.DateTimeField(verbose_name=_(u'Пауза до'), blank=True, null=True)
    last_checkout = models.DateTimeField(verbose_name=_(u'Последнее списание'), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.activated)

    class Meta:
        ordering = ['-activated', '-deactivated']
        verbose_name = _(u"Подключённая услуга")
        verbose_name_plural = _(u"Подключённые услуги")
        permissions = (
            ("accountaddonservice_view", _(u"Просмотр")),
        )


class AddonServiceTransaction(models.Model):
    service = models.ForeignKey(AddonService)
    service_type = models.CharField(max_length=32)#onetime, periodical   
    account = models.ForeignKey(Account)
    accountaddonservice = models.ForeignKey(AccountAddonService)
    accounttarif = models.ForeignKey(AccountTarif)
    type = models.ForeignKey(to=TransactionType, null=True, to_field='internal_name', verbose_name=_(u"Тип операции"),
                             on_delete=models.SET_NULL)
    summ = models.DecimalField(decimal_places=5, max_digits=60)
    prev_balance = models.DecimalField(verbose_name=(u'Предыдущий баланс'), decimal_places=5, max_digits=20, blank=True,
                                       default=0)
    created = models.DateTimeField()

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Списание по подключаемой услуге")
        verbose_name_plural = _(u"Списания по подключаемым услугам")
        permissions = (
            ("accountaddonservicetransaction_view", _(u"Просмотр")),
        )


class News(models.Model):
    body = models.TextField(verbose_name=_(u'Заголовок новости'))
    age = models.DateTimeField(verbose_name=_(u'Актуальна до'),
                               help_text=_(u'Не указывайте ничего, если новость должна отображаться всегда'),
                               blank=True, null=True)
    public = models.BooleanField(verbose_name=_(u'Публичная'),
                                 help_text=_(u'Отображать в публичной части веб-кабинета'), default=False)
    private = models.BooleanField(verbose_name=_(u'Приватная'),
                                  help_text=_(u'Отображать в приватной части веб-кабинета'), default=False)
    agent = models.BooleanField(verbose_name=_(u'Показать через агент'), default=False)
    created = models.DateTimeField(verbose_name=_(u'Актуальна с'), blank=True)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('news_delete'), self.id)

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Новость")
        verbose_name_plural = _(u"Новости")
        permissions = (
            ("news_view", _(u"Просмотр")),
        )


class AccountViewedNews(models.Model):
    news = models.ForeignKey(News)
    account = models.ForeignKey(Account)
    viewed = models.BooleanField(default=False)


class SubAccount(models.Model):
    account = models.ForeignKey(Account, related_name='subaccounts')
    username = models.CharField(verbose_name=_(u'Логин'), max_length=512, blank=True)
    password = EncryptedTextField(verbose_name=_(u'Пароль'), blank=True, default='')
    ipn_ip_address = IPNetworkField(blank=True, null=True, default='0.0.0.0')
    ipn_mac_address = models.CharField(blank=True, max_length=17, default='')
    vpn_ip_address = models.IPAddressField(blank=True, null=True, default='0.0.0.0')
    allow_mac_update = models.BooleanField(default=False)
    nas = models.ForeignKey(Nas, blank=True, null=True, on_delete=models.SET_NULL)
    ipn_added = models.BooleanField(verbose_name=_(u'Добавлен на NAS'))
    ipn_enabled = models.BooleanField(verbose_name=_(u'Включен на NAS'))
    ipn_sleep = models.BooleanField(verbose_name=_(u'Не менять IPN статус'))
    ipn_queued = models.DateTimeField(blank=True, null=True,
                                      verbose_name=_(u'Поставлен в очередь на изменение статуса'))
    need_resync = models.BooleanField()
    speed = models.TextField(blank=True)
    switch = models.ForeignKey("Switch", blank=True, null=True, on_delete=models.SET_NULL)
    switch_port = models.IntegerField(blank=True, null=True)
    allow_dhcp = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать получать IP адреса по DHCP"))
    allow_dhcp_with_null = models.BooleanField(blank=True, default=False, verbose_name=_(
        u"Разрешать получать IP адреса по DHCP при нулевом балансе"))
    allow_dhcp_with_minus = models.BooleanField(blank=True, default=False, verbose_name=_(
        u"Разрешать получать IP адреса по DHCP при отрицатеьлном балансе"))
    allow_dhcp_with_block = models.BooleanField(blank=True, default=False, verbose_name=_(
        u"Разрешать получать IP адреса по DHCP при наличии блокировок по лимитам или балансу"))
    allow_vpn_with_null = models.BooleanField(blank=True, default=False,
                                              verbose_name=_(u"Разрешать RADIUS авторизацию при нулевом балансе"))
    allow_vpn_with_minus = models.BooleanField(blank=True, default=False, verbose_name=_(
        u"Разрешать RADIUS авторизацию при отрицательном балансе балансе"))
    allow_vpn_with_block = models.BooleanField(blank=True, default=False, verbose_name=_(
        u"Разрешать RADIUS авторизацию при наличии блокировок по лимитам или балансу"))
    allow_ipn_with_null = models.BooleanField(blank=True, default=False,
                                              verbose_name=_(u"Разрешать IPN авторизацию при нулевом балансе"))
    allow_ipn_with_minus = models.BooleanField(blank=True, default=False,
                                               verbose_name=_(u"Разрешать IPN авторизацию при отрицательном балансе"))
    allow_ipn_with_block = models.BooleanField(blank=True, default=False, verbose_name=_(
        u"Разрешать IPN авторизацию при наличии блокировок по лимитам или балансу"))
    associate_pptp_ipn_ip = models.BooleanField(blank=True, default=False,
                                                verbose_name=_(u"Привязать PPTP/L2TP авторизацию к IPN IP"))
    associate_pppoe_ipn_mac = models.BooleanField(blank=True, default=False,
                                                  verbose_name=_(u"Привязать PPPOE авторизацию к IPN MAC"))

    ipn_speed = models.TextField(blank=True, help_text=_(u"Не менять указанные настройки скорости"))
    vpn_speed = models.TextField(blank=True, help_text=_(u"Не менять указанные настройки скорости"))
    allow_addonservice = models.BooleanField(blank=True, default=False, verbose_name=_(
        u"Разрешить самостоятельную активацию подключаемых услуг на этот субаккаунт"))
    vpn_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_vpn_ipinuse_set',
                                    on_delete=models.SET_NULL)
    ipn_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_ipn_ipinuse_set',
                                    on_delete=models.SET_NULL)
    vpn_ipv6_ip_address = models.GenericIPAddressField(blank=True, null=True)
    vpn_ipv6_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_vpn_ipv6_ipinuse_set',
                                         on_delete=models.SET_NULL)
    #ipn_ipv6_ip_address = models.TextField(blank=True, null=True)
    vlan = models.IntegerField(blank=True, null=True)
    allow_mac_update = models.BooleanField(blank=True, default=False, verbose_name=_(
        u"Разрешить самостоятельно обновлять MAC адрес через веб-кабинет"))
    ipv4_ipn_pool = models.ForeignKey(IPPool, blank=True, default=None, null=True,
                                      related_name='subaccount_ipn_ippool_set', on_delete=models.SET_NULL)
    ipv4_vpn_pool = models.ForeignKey(IPPool, blank=True, default=None, null=True,
                                      related_name='subaccount_vpn_ippool_set', on_delete=models.SET_NULL)
    ipv6_vpn_pool = models.ForeignKey(IPPool, blank=True, default=None, null=True,
                                      related_name='subaccount_ipv6_vpn_ippool_set', on_delete=models.SET_NULL)
    sessionscount = models.IntegerField(verbose_name=_(u"Одноверменных RADIUS сессий на субаккаунт"), blank=True,
                                        default=0)

    def __unicode__(self):
        return u"%s" % self.username

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('subaccount_delete'), self.id)

    class Meta:
        ordering = ['-username']
        verbose_name = _(u"Субаккаунт")
        verbose_name_plural = _(u"Субаккаунт")
        permissions = (
            ("subaccount_view", _(u"Просмотр")),
            ("getmacforip", _(u"Получение mac адреса по IP")),
        )

    def save(self, *args, **kwargs):

        if self.vpn_ipinuse:

            #vpn_pool = IPPool.objects.get(id=ipv4_vpn_pool)

            if str(self.vpn_ip_address) not in ['0.0.0.0', '0.0.0.0/32', '', None]:
                if self.ipv4_vpn_pool:


                    if str(self.vpn_ipinuse.ip) != str(self.vpn_ip_address):
                        obj = IPInUse.objects.get(id=self.vpn_ipinuse.id)
                        obj.disabled = datetime.datetime.now()
                        obj.save()

                        obj = IPInUse(pool=self.ipv4_vpn_pool, ip=self.vpn_ip_address, datetime=datetime.datetime.now())
                        obj.save()
                        self.vpn_ipinuse = obj


                else:
                    obj = self.vpn_ipinuse
                    obj.disabled = datetime.datetime.now()
                    obj.save()
                    self.vpn_ipinuse = None




            elif str(self.vpn_ip_address) in ['', '0.0.0.0', '0.0.0.0/32', '', None]:
                obj = self.vpn_ipinuse
                obj.disabled = datetime.datetime.now()
                obj.save()

                self.vpn_ipinuse = None
        elif str(self.vpn_ip_address) not in ['', '0.0.0.0', '0.0.0.0/32', '', None] and self.ipv4_vpn_pool:

            ip = IPInUse(pool=self.ipv4_vpn_pool, ip=self.vpn_ip_address, datetime=datetime.datetime.now())
            ip.save()
            self.vpn_ipinuse = ip

            #print '1111111', subaccount, vpn_ipinuse, ipn_ipinuse, subaccount.ipv4_vpn_pool
        if self.vpn_ipv6_ipinuse:

            #vpn_pool = IPPool.objects.get(id=ipv4_vpn_pool)
            #print 222
            if str(self.vpn_ipv6_ip_address) not in ['', '::', ':::', None]:
                if self.ipv6_vpn_pool:

                    if str(self.vpn_ipv6_ipinuse.ip) != str(self.vpn_ipv6_ip_address):
                        obj = IPInUse.objects.get(id=self.vpn_ipv6_ipinuse.id)
                        obj.disabled = datetime.datetime.now()
                        obj.save()
                        #print 444
                        obj = IPInUse.objects.create(pool=self.ipv6_vpn_pool, ip=self.vpn_ipv6_ip_address,
                                                     datetime=datetime.datetime.now())
                        obj.save()
                        self.vpn_ipv6_ipinuse = obj
                else:
                    obj = self.vpn_ipv6_ipinuse
                    obj.disabled = datetime.datetime.now()
                    obj.save()
                    self.vpn_ipv6_ipinuse = None



            elif str(self.vpn_ipv6_ip_address) in ['', '::', ':::', None]:
                #print 666
                obj = self.vpn_ipv6_ipinuse
                obj.disabled = datetime.datetime.now()
                obj.save()

                self.vpn_ipv6_ipinuse = None
        elif str(self.vpn_ipv6_ip_address) not in ['', '::', ':::', None] and self.ipv6_vpn_pool:

            ip = IPInUse(pool=self.ipv6_vpn_pool, ip=self.vpn_ipv6_ip_address, datetime=datetime.datetime.now())
            ip.save()

            self.vpn_ipv6_ipinuse = ip

        if self.ipn_ipinuse:


            if str(self.ipn_ip_address) not in ['0.0.0.0', '0.0.0.0/32', '', None]:
                if self.ipv4_ipn_pool:

                    if str(self.ipn_ipinuse.ip) != str(self.ipn_ip_address):
                        obj = IPInUse.objects.get(id=self.ipn_ipinuse.id)
                        obj.disabled = datetime.datetime.now()
                        obj.save()

                        obj = IPInUse(pool=self.ipv4_ipn_pool, ip=self.ipn_ip_address, datetime=datetime.datetime.now())
                        obj.save()
                        self.ipn_ipinuse = obj
                else:
                    obj = self.ipn_ipinuse
                    obj.disabled = datetime.datetime.now()
                    obj.save()
                    self.ipn_ipinuse = None



            elif str(self.ipn_ip_address) in ['', '0.0.0.0', '0.0.0.0/32', '', None]:

                obj = IPInUse.objects.get(id=self.ipn_ipinuse.id)
                obj.disabled = datetime.datetime.now()
                obj.save()
                self.ipn_ipinuse = None
        elif str(self.ipn_ip_address) not in ['', '0.0.0.0', '0.0.0.0/32', '', None] and self.ipv4_ipn_pool:


            ip = IPInUse(pool=self.ipv4_ipn_pool, ip=self.ipn_ip_address, datetime=datetime.datetime.now())
            ip.save()
            self.ipn_ipinuse = ip
        self.ipn_ip_address = self.ipn_ip_address or '0.0.0.0'
        self.vpn_ip_address = self.vpn_ip_address or '0.0.0.0'

        super(SubAccount, self).save(*args, **kwargs)


class BalanceHistory(models.Model):
    account = models.ForeignKey(Account, verbose_name=_(u"Аккаунт"))
    balance = models.DecimalField(max_digits=30, decimal_places=20, verbose_name=_(u"Баланс"))
    summ = models.DecimalField(max_digits=30, default=0, decimal_places=6, verbose_name=_(u"Сумма"))
    datetime = models.DateTimeField()

    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"История изменения баланса")
        verbose_name_plural = _(u"История изменения баланса")
        permissions = (
            ("balancehistory_view", "Просмотр"),
        )


class City(models.Model):
    name = models.CharField(max_length=320)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Город")
        verbose_name_plural = _(u"Города")
        permissions = (
            ("city_view", _(u"Просмотр")),
        )


class Street(models.Model):
    name = models.CharField(max_length=320)
    city = models.ForeignKey(City)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Улица")
        verbose_name_plural = _(u"Улицы")
        permissions = (
            ("street_view", _(u"Просмотр")),
        )


class House(models.Model):
    name = models.CharField(max_length=320)
    street = models.ForeignKey(Street)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Дом")
        verbose_name_plural = _(u"Дома")
        permissions = (
            ("house_view", _(u"Просмотр")),
        )


class RadiusTraffic(models.Model):
    direction = models.IntegerField(verbose_name=_(u"Направление"), blank=True, default=2, choices=(
        (0, _(u"Входящий")), (1, _(u"Исходящий")), (2, _(u"Сумма")), (3, _(u"Максимум"))))
    tarification_step = models.IntegerField(verbose_name=_(u"Единица тарификации, кб."), blank=True, default=1024)
    rounding = models.IntegerField(verbose_name=_(u"Округление"), default=0, blank=True,
                                   choices=((0, _(u"Не округлять")), (1, _(u"В большую сторону")),))
    prepaid_direction = models.IntegerField(blank=True, default=2, verbose_name=_(u"Предоплаченное направление"),
                                            choices=((0, _(u"Входящий")), (1, _(u"Исходящий")), (2, _(u"Сумма")),
                                                     (3, _(u"Максимум"))))
    prepaid_value = models.IntegerField(verbose_name=_(u"Объём, мб."), blank=True, default=0)
    reset_prepaid_traffic = models.BooleanField(verbose_name=_(u"Сбрасывать предоплаченный трафик"), blank=True,
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
    radiustraffic = models.ForeignKey(RadiusTraffic)
    value = models.BigIntegerField(verbose_name=_(u"Объём"), help_text=_(u"Объём, с которого действует указаная цена"),
                                   default=0)
    timeperiod = models.ForeignKey(TimePeriod, verbose_name=_(u"Период тарификации"))
    cost = models.DecimalField(verbose_name=_(u"Цена"), help_text=_(u"Цена за единицу тарификации"), default=0,
                               max_digits=30, decimal_places=3)

    class Meta:
        ordering = ['value']
        verbose_name = _(u"Настройка тарификации RADIUS трафика")
        verbose_name_plural = _(u"Настройка тарификации RADIUS трафика")
        permissions = (
            ("radiustrafficnode_view", _(u"Просмотр")),
        )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('radiustrafficnode_delete'), self.id)


class ContractTemplate(models.Model):
    template = models.CharField(max_length=128, verbose_name=u'Шаблон', help_text=u'''%(contract_num)i - номер заключаемого договора этого типа
%(account_id)i - идентификатор аккаунта
%(day)i,%(month)i,%(year)i,%(hour)i,%(minute)i,%(second)i - дата подключения на тариф''')
    counter = models.IntegerField()

    class Meta:
        ordering = ['template']
        verbose_name = _(u"Шаблон номера договора")
        verbose_name_plural = _(u"Шаблоны номеров договоров")
        permissions = (
            ("contracttemplate_view", _(u"Просмотр")),
        )

    def __unicode__(self):
        return unicode(self.template)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('contracttemplate_delete'), self.id)


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


class Model(models.Model):
    name = models.TextField(verbose_name=_(u"Модель"))
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=_(u"Производитель"))
    hardwaretype = models.ForeignKey(HardwareType, verbose_name=_(u"Тип оборудования"))

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
    #manufacturer = models.ForeignKey(Manufacturer)
    model = models.ForeignKey(Model, verbose_name=_(u"Модель"))
    name = models.CharField(max_length=500, blank=True, default='', verbose_name=_(u"Название"))
    sn = models.CharField(max_length=500, blank=True, default='', verbose_name=_(u"Серийный номер"))
    ipaddress = models.IPAddressField(blank=True, verbose_name=_(u"IP адрес"))
    macaddress = models.CharField(blank=True, default='', max_length=32, verbose_name=_(u"MAC адрес"))
    comment = models.TextField(blank=True, default='', verbose_name=_(u"Комментарий"))#

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


class AccountHardware(models.Model):
    account = models.ForeignKey(Account)
    hardware = models.ForeignKey(Hardware, verbose_name=_(u"Устройство"))
    datetime = models.DateTimeField(blank=True, verbose_name=_(u"Дата выдачи"))
    returned = models.DateTimeField(blank=True, verbose_name=_(u"Дата возврата"))
    comment = models.TextField(blank=True, default="", verbose_name=_(u"Комментарий"))

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accounthardware_delete'), self.id)

    def __unicode__(self):
        return u'%s-%s %s' % (self.id, self.account, self.hardware)

    class Meta:
        ordering = ['datetime']
        verbose_name = _(u"Устройство у абонента")
        verbose_name_plural = _(u"Устройства у абонентов")
        permissions = (
            ("accounthardware_view", _(u"Просмотр")),
        )


class TotalTransactionReport(models.Model):
    service_id = models.IntegerField()
    table = models.CharField(max_length=128)
    created = models.DateTimeField()
    tariff = models.ForeignKey(Tariff, blank=True, null=True)
    summ = models.DecimalField(decimal_places=10, max_digits=30)
    prev_balance = models.DecimalField(verbose_name=(u'Предыдущий баланс'), decimal_places=5, max_digits=20, blank=True,
                                       default=0)
    account = models.ForeignKey(Account)
    type = models.ForeignKey(TransactionType, to_field='internal_name')
    is_bonus = models.BooleanField(blank=True, default=False, verbose_name=u'Бонус')
    systemuser = models.ForeignKey(SystemUser, blank=True, null=True)
    bill = models.TextField()
    description = models.TextField()
    end_promise = models.DateTimeField()
    promise_expired = models.BooleanField()

    def get_remove_url(self):
        return "%s?type=%s&id=%s" % (reverse('totaltransaction_delete'), (self.table, self.id))

    class Meta:
        managed = False
        abstract = False
        ordering = ['-created']


class PeriodicalServiceLog(models.Model):
    service = models.ForeignKey(PeriodicalService, verbose_name=_(u'Услуга'))
    accounttarif = models.ForeignKey(AccountTarif, verbose_name=_(u'Тариф аккаунта'))
    datetime = models.DateTimeField(verbose_name=_(u'Последнее списание'))

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('periodicalservicelog_delete'), self.id)

    class Meta:
        ordering = ['-datetime']


class Switch(models.Model):
    manufacturer = models.ForeignKey(to=Manufacturer, verbose_name=_(u"Производитель"), max_length=250, blank=True,
                                     null=True, default='', on_delete=models.SET_NULL)
    model = models.ForeignKey(to=Model, verbose_name=_(u"Модель"), max_length=250, blank=True, null=True, default='',
                              on_delete=models.SET_NULL)
    name = models.CharField(max_length=500, verbose_name=_(u"Название"), blank=True, default='')
    sn = models.CharField(max_length=500, verbose_name=_(u"Серийный номер"), blank=True, default='')
    city = models.ForeignKey(to=City, verbose_name=_(u"Город"), blank=True, null=True, default='',
                             on_delete=models.SET_NULL)
    street = models.CharField(verbose_name=_(u"Улица"), max_length=250, blank=True, default='')
    house = models.CharField(verbose_name=_(u"Дом"), max_length=250, blank=True, default='')
    place = models.TextField(blank=True, verbose_name=_(u"Место размещения"), default='')#место установки
    comment = models.TextField(blank=True, verbose_name=_(u"Комментарий"), default='')#
    ports_count = models.IntegerField(blank=True, verbose_name=_(u"Количество портов"), default=0)
    broken_ports = models.TextField(blank=True, verbose_name=_(u"Битые порты"), default='')#через запятую
    uplink_ports = models.TextField(blank=True, verbose_name=_(u"Аплинк-порты"), default='')#через запятую
    protected_ports = models.TextField(blank=True, verbose_name=_(u"Порты с грозозащитой"), default='')#через запятую
    monitored_ports = models.TextField(blank=True, verbose_name=_(u"Порты с мониторингом"), default='')
    disabled_ports = models.TextField(blank=True, verbose_name=_(u"Отключенные порты"), default='')
    snmp_support = models.BooleanField(default=False, verbose_name=_(u"Поддержка SNMP"))
    snmp_version = models.CharField(max_length=10, choices=(('1', "v1",), ('2c', "v2c",)),
                                    verbose_name=_(u"Версия SNMP"), blank=True, default='v1')#version
    snmp_community = models.CharField(max_length=128, verbose_name=_(u"SNMP компьюнити"), blank=True, default='')#
    ipaddress = models.IPAddressField(blank=True, verbose_name=_(u"IP адрес"), default=None)
    macaddress = models.CharField(max_length=32, verbose_name=_(u"MAC адрес"), blank=True, default='')
    management_method = models.IntegerField(verbose_name=_(u"Метод SNMP управления"), choices=(
        (0, _(u"Не управлять")), (1, _(u"SSH")), (2, _(u"SNMP")), (3, _(u"Telnet")), (4, _(u"localhost"))), blank=True,
                                            default=1)
    option82 = models.BooleanField(verbose_name=_(u"Опция 82"), default=False)
    option82_auth_type = models.IntegerField(verbose_name=_(u"Тип авторизации по Option82"),
                                             choices=((0, _(u"Порт"),), (1, _(u"Порт+MAC"),), (2, _(u"MAC"),)),
                                             blank=True, null=True)#1-port, 2 - mac+port, 3-mac
    secret = models.CharField(verbose_name=_(u"RADIUS secret"), max_length=128, blank=True, default='')
    identify = models.CharField(verbose_name=_(u"RADIUS identify"), max_length=128, blank=True, default='')
    username = models.CharField(verbose_name=_(u"Имя пользователя"), max_length=256, blank=True, default='')
    password = models.CharField(verbose_name=_(u"Пароль пользователя"), max_length=256, blank=True, default='')
    enable_port = models.TextField(verbose_name=_(u"Команда включения порта"), blank=True, default='')
    disable_port = models.TextField(verbose_name=_(u"Команда отключения порта"), blank=True, default='')
    option82_template = models.CharField(verbose_name=_(u"Шаблон option82"), choices=(("dlink-32xx", 'dlink-32xx'),),
                                         blank=True, max_length=256, default='')
    remote_id = models.CharField(verbose_name=_(u"remote_id"), blank=True, max_length=256, default='')

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _(u"Коммутатор")
        verbose_name_plural = _(u"Коммутаторы")
        permissions = (
            ("switch_view", _(u"Просмотр")),
        )


class SwitchPort(models.Model):
    switch = models.ForeignKey(Switch)
    port = models.IntegerField(db_index=True)
    comment = models.CharField(blank=True, default='', max_length=1024)
    oper_status = models.IntegerField(choices=PORT_OPER_STATUS, default=4)
    admin_status = models.IntegerField(choices=ADMIN_OPER_STATUS)
    uplink = models.BooleanField(default=False)
    broken = models.BooleanField(default=False)
    protection = models.ForeignKey(Hardware, blank=True, null=True, on_delete=models.SET_NULL)


class SwitchPortStat(models.Model):
    switchport = models.ForeignKey(SwitchPort)
    oper_status = models.IntegerField(choices=PORT_OPER_STATUS, default=4)
    admin_status = models.IntegerField(choices=ADMIN_OPER_STATUS)
    out_bytes = models.IntegerField()
    in_errors = models.IntegerField()
    out_errors = models.IntegerField()
    datetime = models.DateTimeField()


class Permission(models.Model):
    name = models.CharField(max_length=500, verbose_name=_(u"Название"))
    app = models.CharField(max_length=500, verbose_name=_(u"Приложение"))
    internal_name = models.CharField(max_length=500, verbose_name=_(u"Внутреннее имя"))
    ordering = models.IntegerField()

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _(u"Право доступа")
        verbose_name_plural = _(u"Права доступа")


class PermissionGroup(models.Model):
    name = models.CharField(max_length=128, verbose_name=_(u"Название"))
    permissions = models.ManyToManyField(Permission, verbose_name=_(u"Права"))
    deletable = models.BooleanField(default=False, blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _(u"Группа доступа")
        verbose_name_plural = _(u"Группы доступа")

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('permissiongroup_delete'), self.id)

#===============================================================================
# class Message(models.Model):
#    type = models.CharField(max_length=32, choices=(('email', 'email'),('sms', 'sms'),), default='email')
#    message = models.TextField()
#    accounts = JSONField()
#    
#===============================================================================

class NotificationsSettings(models.Model):
    #account = models.ForeignKey(Account)
    payment_notifications = models.BooleanField() #Transaction
    payment_notifications_template = models.TextField(verbose_name=u'Шаблон уведомления о платеже', default='')
    tariff_cost_notifications = models.BooleanField(verbose_name=u'Уведомления о недостатке денег для продления тарифа')
    tariff_cost_notifications_template = models.TextField(
        verbose_name=u'Шаблон уведомления о недостатке денег для тарифа', default='')
    balance_notifications = models.BooleanField(verbose_name=u'Уведомления о недостатке баланса')
    balance_edge = models.FloatField(verbose_name=u'Граница баланса',
                                     help_text=u'Граница, с которой слать уведомления  о недостатке баланса')
    balance_notifications_each = models.IntegerField(verbose_name=u'Периодичность между уведомлениями о балансе',
                                                     help_text=u'В днях')
    balance_notifications_limit = models.IntegerField(verbose_name=u'Количество уведомлений о балансе',
                                                      help_text=u'Не слать более уведомлений о балансе при исчерпании указанного количества')
    balance_notifications_template = models.TextField(verbose_name=u'Шаблон уведомления о недостатке денег', default='')
    send_email = models.BooleanField(blank=True, default=True)
    send_sms = models.BooleanField(blank=True, default=True)


#===============================================================================
# class Monitoring(models.Model):
#    account =models.ForeignKey(Account)
#    subaccount = models.ForeignKey(SubAccount)
#    ip_ip_address_ping = models.TextField()
#    vpn_ip_address_ping = models.TextField()
#    subaccount_vpn_active = models.DateTimeField(blank=True, null=True)
#===============================================================================

class AccountSuppAgreement(models.Model):
    suppagreement = models.ForeignKey('SuppAgreement', verbose_name=_(u"Дополнительное соглашение"))
    account = models.ForeignKey('Account', verbose_name=_(u"Аккаунт"))
    contract = models.CharField(_(u"Номер"), max_length=128)
    accounthardware = models.ForeignKey('AccountHardware', blank=True, null=True,
                                        verbose_name=_(u"Связанное оборудование"))
    created = models.DateTimeField(_(u"Создано"))
    closed = models.DateTimeField(_(u"Закрыто"), blank=True, null=True)

    def __unicode__(self):
        return u"%s %s" % (self.suppagreement, self.account)

    class Meta:
        verbose_name = _(u"Дополнительное соглашение")
        verbose_name_plural = _(u"Дополнительные соглашения")

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accountsuppagreement_delete'), self.id)
    

class SuppAgreement(models.Model):
    name = models.CharField(max_length=128, verbose_name=_(u"Название"))
    description = models.TextField(verbose_name=_(u'Комментарий'), blank=True, default='')
    body = models.TextField(verbose_name=_(u'Текст шаблона'), blank=True, default='')
    length = models.IntegerField(verbose_name=_(u"Длительность в днях"), blank=True, null=True)
    disable_tarff_change = models.BooleanField(verbose_name=_(u"Запретить смену тарифного плана"), blank=True,
                                               default=False)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u"Вид доп. соглашения")
        verbose_name_plural = _(u"Виды доп. соглашения")

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('suppagreement_delete'), self.id)


        #===========================================================================
        # def get_remove_url(self):
        #    return "%s?id=%s" % (reverse('permissiongroup_delete'), self.id)
        #===========================================================================
    