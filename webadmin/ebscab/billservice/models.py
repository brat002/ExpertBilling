#-*-coding=utf-8-*-
from django.db import models
from ebscab.nas.models import Nas, TrafficClass, TrafficClass, Switch
from django.contrib.auth.models import User
from django.db.models import F
import datetime, time
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
# Create your models here.
# choiCe
from lib.fields import IPNetworkField
PROTOCOLS = {'0':'-all-',
           '37':'ddp',
           '98':'encap', 
           '3':'ggp', 
           '47':'gre', 
           '20':'hmp', 
           '1':'icmp', 
           '38':'idpr-cmtp', 
           '2':'igmp', 
           '4':'ipencap', 
           '94':'ipip',  
           '89':'ospf', 
           '27':'rdp', 
           '6':'tcp', 
           '17':'udp'
           }

PERIOD_CHOISES=(
                (u'DONT_REPEAT', u'Не повторять'),
                (u'DAY',u'День'),
                (u'WEEK',u'Неделя'),
                (u'MONTH',u'Месяц'),
                (u'YEAR',u'Год'),
                )

CASH_METHODS=(
                (u'AT_START',u'В начале периода'),
                (u'AT_END',u'В конце периода'),
                (u'GRADUAL',u'В течении периода'),
                )

ACCESS_TYPE_METHODS=(
                      ("PPTP", "PPTP" ),
                      ("PPPOE", "PPPOE"),
                      ("IPN", "IPN"),
                      ("HotSpot","HotSpot"),
                      ('HotSpotIp+Mac', 'HotSpotIp+Mac'),
                      ('HotSpotIp+Password', 'HotSpotIp+Password'),
                      ('HotSpotMac','HotSpotMac'),
                      ('HotSpotMac+Password','HotSpotMac+Password'),
                      ('lISG', 'lISG'),
                      ("DHCP", "DHCP")
                )
# choiCe
ACTIVITY_CHOISES=(
        (u"Enabled",u"Активен"),
        (u"Disabled",u"Неактивен"),
        )
# choiCe
CHOISE_METHODS=(
        (u"MAX",u"Наибольший"),
        (u"SUMM",u"Сумма всех"),
        )


CHECK_PERIODS=(
        (u"period_checkSP_START",u"С начала расчётного периода"),
        (u"AG_START",u"С начала интервала агрегации"),
        )

STATISTIC_MODE=(
                (u'NETFLOW',u'NetFlow'),
                (u'ACCOUNTING',u'RADIUS Accounting'),
                )

PRIORITIES=(
                (u'1',u'1'),
                (u'2',u'2'),
                (u'3',u'3'),
                (u'4',u'4'),
                (u'5',u'5'),
                (u'6',u'6'),
                (u'7',u'7'),
                (u'8',u'8'),
                )

DIRECTIONS_LIST=(
                (u'INPUT', u'Входящий на абонента'),
                (u'OUTPUT',u'Исходящий от абонента'),
                (u'TRANSIT',u'Межабонентский'),
                )

AUTH_TYPES=(
              ('BY_LOGIN', 'BY_LOGIN'),
              ('BY_MAC', 'BY_MAC'),
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
    name = models.CharField(max_length=255, verbose_name=u'Название группы временных периодов', unique=True)
    #time_period_nodes = models.ManyToManyField(to=TimePeriodNode, blank=True, null=True, verbose_name=u'Группа временных периодов')

    def in_period(self):
        for time_period_node in self.time_period_nodes:
            if time_period_node.in_period()==True:
                return True
        return False

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name',)


    class Meta:
        ordering = ['name']
        verbose_name = u"Временной период"
        verbose_name_plural = u"Временные периоды"
        permissions = (
            ("timeperiod_view", u"Просмотр временных периодов"),
            )

class TimePeriodNode(models.Model):
    """
    Диапазон времени ( с 15 00 до 18 00 каждую вторник-пятницу,утро, ночь, сутки, месяц, год и т.д.)
    """
    time_period = models.ForeignKey(TimePeriod, verbose_name=u"Период времени")
    name = models.CharField(max_length=255, verbose_name=u'Название подпериода', default='', blank=True)
    time_start = models.DateTimeField(verbose_name=u'Дата и время начала', default='', blank=True)
    length = models.IntegerField(verbose_name=u'Длительность в секундах', default=0, blank=True)
    repeat_after = models.CharField(max_length=255, choices=PERIOD_CHOISES, verbose_name=u'Повторять через', default='DAY', blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name',]
        verbose_name = u"Нода временного периода"
        verbose_name_plural = u"Ноды временных периодов"
        permissions = (
            ("timeperiodnode_view", u"Просмотр нод временных периодов"),
            )
        
class SettlementPeriod(models.Model):
    """
    Расчётный период
    """
    name = models.CharField(max_length=255, verbose_name=u'Название', unique=True)
    time_start = models.DateTimeField(verbose_name=u'Начало периода')
    length = models.IntegerField(blank=True, null=True, default=0,verbose_name=u'Период действия в секундах')
    length_in = models.CharField(max_length=255, choices=PERIOD_CHOISES, null=True, blank=True, default='', verbose_name=u'Длина промежутка')
    autostart = models.BooleanField(verbose_name=u'Начинать при активации', default=False)

    def __unicode__(self):
        return u"%s, Автостарт %s" % (self.name, self.autostart)

    class Admin:
        
        list_display = ('name','time_start','length','length_in','autostart')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('settlementperiod_delete'), self.id)
    
    class Meta:
        ordering = ['name']
        verbose_name = u"Расчетный период"
        verbose_name_plural = u"Расчетные периоды"
        permissions = (
            ("settlementperiod_view", u"Просмотр расчётных периодов"),
            )
        
class PeriodicalService(models.Model):
    """
    Справочник периодических услуг
    TO-DO: Сделать справочники валют
    """
    tarif             = models.ForeignKey('Tariff')
    name              = models.CharField(max_length=255, verbose_name=u'Название услуги')
    settlement_period = models.ForeignKey(to=SettlementPeriod, verbose_name=u'Период', null=True, on_delete=models.SET_NULL)
    cost              = models.DecimalField(verbose_name=u'Стоимость услуги', default=0, blank=True, decimal_places=10, max_digits=30)
    cash_method       = models.CharField(verbose_name=u'Способ снятия', max_length=255, choices=CASH_METHODS, default='AT_START', blank=True)
    condition         = models.IntegerField(default = 0) # 0 - Всегда. 1- Только при положительном балансе. 2 - только при орицательном балансе
    deactivated     = models.DateTimeField(blank=True, null=True)
    created     = models.DateTimeField(blank=True, null=True)
    deleted     = models.BooleanField(blank=True, default=False)
    
    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        
        list_display = ('name','settlement_period','cost','cash_method')


    class Meta:
        ordering = ['name']
        verbose_name = u"Периодическая услуга"
        verbose_name_plural = u"Периодические услуги"
        permissions = (
            ("periodicalservice_view", u"Просмотр периодических услуг"),
            )
        
class PeriodicalServiceHistory(models.Model):
    service = models.ForeignKey(to=PeriodicalService,  blank=True, null=True, on_delete=models.SET_NULL)
    #transaction = models.ForeignKey(to='Transaction')
    accounttarif = models.ForeignKey(to='AccountTarif', on_delete=models.CASCADE)
    created  = models.DateTimeField(auto_now_add=True)
    summ = models.DecimalField(decimal_places=10, max_digits=30)
    account = models.ForeignKey('Account',on_delete = models.CASCADE)
    type   = models.ForeignKey('TransactionType', to_field='internal_name', null=True, on_delete = models.SET_NULL)

    def __unicode__(self):
        return u"%s" % (self.service)

    class Admin:
        
        list_display = ('service','transaction','datetime')


    class Meta:
        ordering = ['-created']
        verbose_name = u"История по пер. услугам"
        verbose_name_plural = u"История по пер. услугам"
        permissions = (
            ("periodicalservicehistory_view", u"Просмотр списаний"),
            )
        
class OneTimeService(models.Model):
    """
    Справочник разовых услуг
    TO-DO: Сделать справочники валют
    """
    tarif             = models.ForeignKey('Tariff')
    name              = models.CharField(max_length=255, verbose_name=u'Название разовой услуги', default='', blank=True)
    cost              = models.FloatField(verbose_name=u'Стоимость разовой услуги', default=0, blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','cost')


    class Meta:
        ordering = ['name']
        verbose_name = u"Разовая услуга"
        verbose_name_plural = u"Разовые услуги"
        permissions = (
            ("onetimeservice_view", u"Просмотр услуг"),
            )
class OneTimeServiceHistory(models.Model):
    onetimeservice = models.ForeignKey(OneTimeService, null=True, on_delete=models.SET_NULL)
    created  = models.DateTimeField(auto_now_add=True)
    summ = models.IntegerField()
    account=models.ForeignKey('Account', on_delete=models.CASCADE)
    accounttarif = models.ForeignKey('AccountTarif', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created']
        verbose_name = u"Списание по разовым услугам"
        verbose_name_plural = u"Списания по разовым услугам"
        permissions = (
            ("onetimeservicehistory_view", u"Просмотр услуг"),
            )
        
class TimeAccessService(models.Model):
    """
    Доступ с тарификацией по времени
    """
    #name              = models.CharField(max_length=255, verbose_name=u'Название услуги', unuque=True)
    prepaid_time      = models.IntegerField(verbose_name=u'Предоплаченное время', default=0, blank=True)
    reset_time        = models.BooleanField(verbose_name=u'Сбрасывать  предоплаченное время', blank=True, default=False)
    rounding = models.IntegerField()
    tarification_step = models.IntegerField()
    
    def __unicode__(self):
        return u"%s" % self.id

    class Admin:
        #ordering = ['name']
        list_display = ('prepaid_time',)


    class Meta:
        verbose_name = u"Доступ с учётом времени"
        verbose_name_plural = u"Доступ с учётом времени"
        permissions = (
            ("timeaccessservice_view", u"Просмотр услуг доступа по времени"),
            )
        
class TimeAccessNode(models.Model):
    """
    Нода тарификации по времени
    """
    time_access_service = models.ForeignKey(to=TimeAccessService, related_name="time_access_nodes")
    time_period         = models.ForeignKey(to=TimePeriod, verbose_name=u'Промежуток', null=True, on_delete = models.SET_NULL)
    cost                = models.FloatField(verbose_name=u'Стоимость за минуту', default=0)

    def __unicode__(self):
        return u"%s %s" % (self.time_period, self.cost)

    class Admin:
        ordering = ['name']
        list_display = ('time_period', 'cost')


    class Meta:
        verbose_name = u"Период доступа"
        verbose_name_plural = u"Периоды доступа"
        permissions = (
            ("timeacessnode_view", u"Просмотр"),
            )
        
class AccessParameters(models.Model):
    #name              = models.CharField(max_length=255, verbose_name=u'Название вида доступа')
    access_type       = models.CharField(max_length=255, choices=ACCESS_TYPE_METHODS, default='PPTP', blank=True, verbose_name=u'Вид доступа')
    access_time       = models.ForeignKey(to=TimePeriod, verbose_name=u'Разрешённое время доступа', null=True, on_delete = models.SET_NULL)
    #ip_address_pool   = models.ForeignKey(to=IPAddressPool, verbose_name=u'Пул адресов', blank=True, null=True)
    ipn_for_vpn     = models.BooleanField(blank=True, default=False)
    max_limit      = models.CharField(verbose_name=u"MAX (kbps)", max_length=64, blank=True, default="")
    min_limit      = models.CharField(verbose_name=u"MIN (kbps)", max_length=64, blank=True, default="")
    burst_limit    = models.CharField(verbose_name=u"Burst", max_length=64, blank=True, default="")
    burst_treshold = models.CharField(verbose_name=u"Burst treshold (kbps)", max_length=64, blank=True, default="")
    burst_time     = models.CharField(verbose_name=u"Burst Time", blank=True, max_length=64, default="")
    #от 1 до 8
    priority             = models.IntegerField(verbose_name=u"Приоритет", blank=True, default=8)
    sessionscount = models.IntegerField(verbose_name=u"Одноверменных RADIUS сессий на субаккаунт", blank=True, default=0)
    
    def __unicode__(self):
        return u"%s" % self.id

    class Admin:
        #ordering = ['name']
        list_display = ('access_type',)


    class Meta:
        verbose_name = u"Параметры доступа"
        verbose_name_plural = u"Параметры доступа"
        permissions = (
            ("accessparameters_view", u"Просмотр параметров доступа"),
            )
        
class TimeSpeed(models.Model):
    """
    Настройки скорости в интервал времени
    """
    access_parameters = models.ForeignKey(to=AccessParameters, related_name="access_speed")
    time = models.ForeignKey(TimePeriod, on_delete = models.CASCADE)
    max_limit      = models.CharField(verbose_name=u"MAX (kbps)", max_length=64, blank=True, default="")
    min_limit      = models.CharField(verbose_name=u"MIN (kbps)", max_length=64, blank=True, default="")
    burst_limit    = models.CharField(verbose_name=u"Burst", max_length=64, blank=True, default="")
    burst_treshold = models.CharField(verbose_name=u"Burst treshold (kbps)", max_length=64, blank=True, default="")
    burst_time     = models.CharField(verbose_name=u"Burst Time", blank=True, max_length=64, default="")
    #от 1 до 8
    priority       = models.IntegerField(verbose_name=u"Приоритет", blank=True, default=8)

    def __unicode__(self):
        return u"%s" % self.time

    class Admin:
        pass

    class Meta:
        verbose_name = u"Настройка скорости"
        verbose_name_plural = u"Настройки скорости"
        permissions = (
            ("timespeed_view", u"Просмотр"),
            )
        
class PrepaidTraffic(models.Model):
    """
    Настройки предоплаченного трафика для тарифного плана
    """
    traffic_transmit_service = models.ForeignKey(to="TrafficTransmitService", verbose_name=u"Услуга доступа по трафику", related_name="prepaid_traffic")
    size             = models.FloatField(verbose_name=u'Размер в байтах', default=0,blank=True)
    group             = models.ForeignKey("Group")

    def __unicode__(self):
        return u"%s" %self.size

    class Admin:
        ordering = ['traffic_class']
        list_display = ('size',)


    class Meta:
        verbose_name = u"Предоплаченный трафик"
        verbose_name_plural = u"Предоплаченный трафик"
        permissions = (
            ("prepaidtraffic_view", u"Просмотр"),
            )

class TrafficTransmitService(models.Model):
    #name              = models.CharField(max_length=255, default='', blank=True)
    reset_traffic     = models.BooleanField(verbose_name=u'Сбрасывать предоплаченный трафик', blank=True, default=False)
    #Не реализовано в GUI
    cash_method       = models.CharField(verbose_name=u"Списывать за класс трафика", max_length=32,choices=CHOISE_METHODS, blank=True, default=u'SUMM', editable=False)
    #Не реализовано в GUI
    period_check      = models.CharField(verbose_name=u"Проверять на наибольший ", max_length=32,choices=CHECK_PERIODS, blank=True, default=u'SP_START', editable=False)


    class Admin:
        #ordering = ['name']
        #list_display = ('name',)
        pass


    class Meta:
        verbose_name = u"Доступ с учётом трафика"
        verbose_name_plural = u"Доступ с учётом трафика"
        permissions = (
            ("traffictransmitservice_view", u"Просмотр"),
            )
        
class TrafficTransmitNodes(models.Model):
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService, verbose_name=u"Услуга доступа по трафику", related_name="traffic_transmit_nodes")
    #traffic_class     = models.ManyToManyField(to=TrafficClass, verbose_name=u'Классы трафика')
    timeperiod        = models.ForeignKey(to=TimePeriod, verbose_name=u'Промежуток времени', null=True, on_delete = models.SET_NULL)
    group        = models.ForeignKey(to='Group', verbose_name=u'Группа трафика', null=True, on_delete = models.SET_NULL)
    cost              = models.FloatField(default=0, verbose_name=u'Цена трафика')
    edge_start        = models.FloatField(default=0,blank=True, null=True, verbose_name=u'Начальная граница', help_text=u'Цена актуальна, если пользователь в текущем расчётном периоде наработал больше указанного количество байт')
    edge_end          = models.FloatField(default=0, blank=True, null=True, verbose_name=u'Конечная граница', help_text=u'Цена актуальна, если пользователь в текущем расчётном периоде наработал меньше указанного количество байт')
    #in_direction      = models.BooleanField(default=True, blank=True)
    #out_direction      = models.BooleanField(default=True, blank=True)
    #transit_direction      = models.BooleanField()
    
    def __unicode__(self):
        return u"%s" % (self.cost)

    class Admin:
        list_display = ('cost','edge_start','edge_end')


    class Meta:
        verbose_name = u"Цена за направление"
        verbose_name_plural = u"Цены за направления трафика"
        permissions = (
           ("traffictransmitnodes_view", u"Просмотр"),
            )

class AccountPrepaysTrafic(models.Model):
    """
    При подключении пользователю тарифного плана, у которого есть предоплаченный трафик
    в таблице должны создаваться записи
    В начале каждого расчётного периода пользователю должен заново начисляться трафик
    """
    account_tarif = models.ForeignKey(to="AccountTarif", on_delete = models.CASCADE)
    prepaid_traffic = models.ForeignKey(to=PrepaidTraffic, null=True, on_delete = models.SET_NULL)
    size = models.FloatField(blank=True, default=0)
    datetime = models.DateTimeField(auto_now_add=True, default='')
    current=models.BooleanField(default=False)
    reseted=models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s" % (self.prepaid_traffic)

    class Admin:
        pass

    class Meta:
        ordering = ['-datetime']
        verbose_name = u"Предоплаченый трафик"
        verbose_name_plural = u"Предоплаченный трафик"
        permissions = (
           ("account_prepaystraffic_view", u"Просмотр"),
            )
        
class AccountPrepaysRadiusTrafic(models.Model):
    """
    При подключении пользователю тарифного плана, у которого есть предоплаченный трафик
    в таблице должны создаваться записи
    В начале каждого расчётного периода пользователю должен заново начисляться трафик
    """
    account_tarif = models.ForeignKey(to="AccountTarif", on_delete = models.CASCADE)
    prepaid_traffic = models.ForeignKey(to='RadiusTraffic', null=True, on_delete = models.SET_NULL)
    size = models.FloatField(blank=True, default=0)
    direction = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True, default='')
    current=models.BooleanField(default=False)
    reseted=models.BooleanField(default=False)


    def __unicode__(self):
        return u"%s" % (self.prepaid_traffic)

    class Admin:
        pass

    class Meta:
        ordering = ['-datetime']
        verbose_name = u"Предоплаченый radius трафик "
        verbose_name_plural = u"Предоплаченный radius трафик"

        permissions = (
           ("accountprepaysradiustraffic_view", u"Просмотр"),
            )


class AccountPrepaysTime(models.Model):
    account_tarif = models.ForeignKey(to="AccountTarif", on_delete = models.CASCADE)
    prepaid_time_service = models.ForeignKey(to=TimeAccessService, null=True, on_delete = models.SET_NULL)
    size = models.IntegerField(default=0, blank=True)
    datetime = models.DateTimeField(auto_now_add=True, default='')
    current=models.BooleanField(default=False)
    reseted=models.BooleanField(default=False)

    class Admin:
        pass

    class Meta:
        ordering = ['-datetime']
        verbose_name = u"Предоплаченное время пользователя"
        verbose_name_plural = u"Предоплаченное время пользователей"
        permissions = (
           ("accountprepaystime_view", u"Просмотр"),
            )
        
class TrafficLimit(models.Model):
    tarif             = models.ForeignKey('Tariff')
    name              = models.CharField(max_length=255, verbose_name=u'Название лимита')
    settlement_period = models.ForeignKey(to=SettlementPeriod, verbose_name=u'Период', blank=True, null=True, on_delete = models.SET_NULL, help_text=u"Если период не указан-берётся период тарифного плана. Если установлен автостарт-началом периода будет считаться день привязки тарифного плана пользователю. Если не установлен-старт берётся из расчётного периода")
    size              = models.IntegerField(verbose_name=u'Размер в килобайтах', default=0)
    group             = models.ForeignKey("Group")
    mode              = models.BooleanField(default=False, blank=True, verbose_name=u'За длинну расчётного периода', help_text=u'Если флаг установлен-то количество трафика считается за последние N секунд, указанные в расчётном периоде')
    action            = models.IntegerField()
    
    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name', 'settlement_period')


    class Meta:
        ordering = ['name']
        verbose_name = u"Лимит трафика"
        verbose_name_plural = u"Лимиты трафика"
        permissions = (
           ("trafficlimit_view", u"Просмотр"),
            )
        
class Tariff(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название тарифного плана', unique = True)
    description       = models.TextField(verbose_name=u'Описание тарифного плана', blank=True, default='')
    access_parameters = models.ForeignKey(to=AccessParameters, verbose_name=u'Параметры доступа', null=True, on_delete = models.SET_NULL)
    contracttemplate  = models.ForeignKey("ContractTemplate", blank=True, null=True, on_delete = models.SET_NULL)
    #traffic_limit     = models.ManyToManyField(to=TrafficLimit, verbose_name=u'Лимиты трафика', blank=True, null=True, help_text=u"Примеры: 200 мегабайт в расчётный период, 50 мегабайт за последнюю неделю")
    #periodical_services = models.ManyToManyField(to=PeriodicalService, verbose_name=u'периодические услуги', blank=True, null=True)
    #onetime_services  = models.ManyToManyField(to=OneTimeService, verbose_name=u'Разовые услуги', blank=True, null=True)
    time_access_service = models.ForeignKey(to=TimeAccessService, verbose_name=u'Доступ с учётом времени', blank=True, null=True, on_delete = models.SET_NULL)
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService, verbose_name=u'Доступ с учётом трафика', blank=True, null=True, on_delete = models.SET_NULL)
    radius_traffic_transmit_service = models.ForeignKey(to="RadiusTraffic", verbose_name=u'RADIUS тарификация трафика', blank=True, null=True, on_delete = models.SET_NULL)
    cost              = models.FloatField(verbose_name=u'Стоимость пакета', default=0 ,help_text=u"Стоимость активации тарифного плана. Целесообразно указать с расчётным периодом. Если не указана-предоплаченный трафик и время не учитываются")
    reset_tarif_cost  = models.BooleanField(verbose_name=u'Производить доснятие', blank=True, default=False, help_text=u'Производить доснятие суммы до стоимости тарифного плана в конце расчётного периода')
    settlement_period = models.ForeignKey(to=SettlementPeriod, blank=True, null=True, verbose_name=u'Расчётный период')
    ps_null_ballance_checkout = models.BooleanField(verbose_name=u'Производить снятие денег  при нулевом баллансе', help_text =u"Производить ли списывание денег по периодическим услугам при достижении нулевого балланса или исчерпании кредита?", blank=True, default=False )
    active            = models.BooleanField(default=False, blank=True)
    deleted           = models.BooleanField(default=False, blank=True)
    allow_express_pay = models.BooleanField(verbose_name=u'Оплата экспресс картами', blank=True, default=False)
    require_tarif_cost = models.BooleanField(default=False, blank=True)
    allow_userblock   =models.BooleanField(blank=True, default=False)
    userblock_cost = models.DecimalField(decimal_places=10, max_digits=30, blank=True, default=0)  
    userblock_max_days = models.IntegerField(blank=True, default=0)
    userblock_require_balance = models.DecimalField(decimal_places=10, max_digits=60, blank=True, default=0)  
    allow_ballance_transfer = models.BooleanField(blank=True, default=False)
    vpn_ippool = models.ForeignKey("IPPool", blank=True, null=True, related_name='tariff_vpn_ippool_set', on_delete = models.SET_NULL)
    vpn_guest_ippool = models.ForeignKey("IPPool", blank=True, null=True, related_name='tariff_guest_vpn_ippool_set', on_delete = models.SET_NULL)
    objects = SoftDeleteManager()
    
    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name','access_parameters','time_access_service','traffic_transmit_service','cost','settlement_period', 'ps_null_ballance_checkout')


    class Meta:
        ordering = ['name']
        verbose_name = u"Тариф"
        verbose_name_plural = u"Тарифы"
        permissions = (
           ("tariff_view", u"Просмотр"),
            )
        
    def delete(self):
        if not self.deleted:
            self.deleted = True
            self.save()
            return
        super(Tariff, self).delete()
        
ACTIVE = 1
NOT_ACTIVE_NOT_WRITING_OFF  = 2
NOT_ACTIVE_WRITING_OFF = 3 

ACCOUNT_STATUS = (
                  (ACTIVE, u'Активен'),
                  (NOT_ACTIVE_NOT_WRITING_OFF, u'Неактивен, не списывать периодические услуги'),
                  (NOT_ACTIVE_WRITING_OFF, u'Неактивен, списывать периодические услуги'),
                  )

class AccountGroup(models.Model):
    name = models.CharField(max_length=512)
    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name']
        verbose_name = u"Группа абонентов"
        verbose_name_plural = u"Группы абонентов"
        permissions = (
           ("accountgroup_view", u"Просмотр"),
            )
        
class Account(models.Model):
    """
    Если стоят галочки assign_vpn_ip_from_dhcp или assign_ipn_ip_from_dhcp,
    значит каждый раз при RADIUS запросе будет провереряться есть ли аренда и не истекла ли она.
    Если аренды нет или она истекла, то создаётся новая и пользователю назначается новый IP адрес.
    """
    #user = models.ForeignKey(User,verbose_name=u'Системный пользователь', related_name='user_account2')
    username = models.CharField(verbose_name=u'Имя пользователя',max_length=200,unique=True)
    password = models.CharField(verbose_name=u'Пароль',max_length=200, blank=True, default='')
    fullname = models.CharField(verbose_name=u'Имя', blank=True, default='', max_length=200)
    email = models.CharField(verbose_name=u'E-mail', blank=True, default='',max_length=200)

    
    address = models.TextField(verbose_name=u'Домашний адрес', blank=True, default='')
    city = models.ForeignKey('City', verbose_name=u'Город', blank=True, null=True, on_delete = models.SET_NULL)
    postcode = models.CharField(verbose_name=u'Индекс', max_length=255, blank=True, null=True)
    region = models.CharField( blank=True, verbose_name=u'Район', max_length=255, default='')
    street = models.CharField(max_length=255, verbose_name=u'Улица', blank=True, null=True)
    house = models.CharField(max_length=255, verbose_name=u'Дом', blank=True, null=True)
    house_bulk = models.CharField(verbose_name=u'Корпус', blank=True, max_length=255)
    entrance = models.CharField(verbose_name=u'Подъезд', blank=True, max_length=255)
    room = models.CharField(verbose_name=u'Квартира', blank=True, max_length=255)
    

    nas = models.ForeignKey(to=Nas, blank=True,null=True, verbose_name=u'Сервер доступа', on_delete = models.SET_NULL)

    ipn_added = models.BooleanField(verbose_name=u"Добавлен на сервере доступа", default=False, blank=True)
    ipn_status = models.BooleanField(verbose_name=u"Статус на сервере доступа", default=False, blank=True)
    status=models.IntegerField(verbose_name=u'Статус', default=1, choices=((1, u"Активен"), (2, u"Не активен, списывать периодические услуги"), (3, u"Не активен, не списывать периодические услуги"), (4, u"Пользовательская блокировка"),))
    created=models.DateTimeField(verbose_name=u'Создан', default='')
    #NOTE: baLance
    ballance=models.DecimalField(u'Баланс', blank=True, default=0,decimal_places=10,max_digits=20)
    credit = models.DecimalField(verbose_name=u'Размер кредита', decimal_places=2,max_digits=20, blank=True, default=0)
    disabled_by_limit = models.BooleanField(blank=True, default=False, editable=False)
    balance_blocked = models.BooleanField(blank=True, default=False)

    allow_webcab = models.BooleanField(verbose_name=u"Разрешить пользоваться веб-кабинетом", blank=True, default=True)
    allow_expresscards = models.BooleanField(verbose_name=u"Разрешить активацию карт экспресс-оплаты", blank=True, default=True)

    passport = models.CharField(verbose_name=u'№ паспорта', blank=True, max_length=64)
    passport_date = models.CharField(verbose_name=u'Выдан', blank=True, max_length=64)
    phone_h = models.CharField(verbose_name=u'Дом. телефон' ,blank=True, max_length=64)
    phone_m = models.CharField(verbose_name=u'Моб. телефон', blank=True, max_length=64)
    contactperson_phone = models.CharField(verbose_name=u'Тел. контактного лица', blank=True, max_length=64)
    comment = models.TextField(blank=True)
    row = models.CharField(verbose_name=u'Этаж', blank=True, max_length=6)
    elevator_direction = models.CharField(verbose_name=u'Направление от лифта', blank=True, max_length=128)
    contactperson = models.CharField(verbose_name=u'Контактное лицо', blank=True, max_length=256)
    passport_given = models.CharField(verbose_name=u'Кем выдан', blank=True, null=True, max_length=128)
    contract = models.TextField(verbose_name=u'№ договора', blank=True)
    systemuser = models.ForeignKey('SystemUser',verbose_name=u'Менеджер', blank=True,null=True, on_delete = models.SET_NULL)
    entrance_code = models.CharField(verbose_name=u'Код домофона', blank=True, max_length=256)
    private_passport_number = models.CharField(verbose_name=u'Идент. номер', blank=True, max_length=128)
    allow_ipn_with_null = models.BooleanField()
    allow_ipn_with_minus = models.BooleanField()
    allow_ipn_with_block = models.BooleanField()
    deleted = models.DateTimeField(blank=True, null=True)
    promise_summ = models.IntegerField(u'Максимальный обещанный платёж', blank=True, default=0)
    promise_min_ballance = models.IntegerField(u'Минимальный баланс для обещанного платежа', blank=True, default=0)
    promise_days = models.IntegerField(u'Длительность обещанного платежа, дней', blank=True, default=1)
    allow_block_after_summ = models.BooleanField(u'Разрешить блокировку списаний', blank=True, default=False, help_text= u"Разрешить приостановку списаний по периодическим и подключаемым услугам при достижении указанного баланса")
    block_after_summ = models.IntegerField(u'Блокировка списаний после суммы', blank=True, default=0)
    account_group = models.ForeignKey(AccountGroup, verbose_name=u'Группа', blank=True, null=True, on_delete=models.SET_NULL)
    objects = SoftDeletedDateManager()
    

    def get_actual_ballance(self):
        return self.ballance+self.credit
    
    def ballance_isnt_good(self):
        if self.ballance+self.credit<=0:
            return True
        else:
            return False
    
    def delete(self):
        if not self.deleted:
            self.deleted = datetime.datetime.now()
            self.save()
            return
        super(Account, self).delete()
        
    def account_status(self):
        if self.status==1:
            return True
        else: 
            return False    
    
    class Admin:
        ordering = ['user']
        #list_display = ('user', 'vpn_ip_address', 'ipn_ip_address', 'username', 'status', 'credit', 'ballance', 'firstname', 'lastname', 'created')
        #list_filter = ('username')

    def __unicode__(self):
        return '%s' % self.username

    class Meta:
        ordering = ['username']
        verbose_name = u"Аккаунт"
        verbose_name_plural = u"Аккаунты"
        permissions = (
           ("account_view", u"Просмотр"),
           ("get_tariff", u"Получить тариф для аккаунта"),
           ("cashier_view", u"Список аккаунтов для кассира")
            )
        
    def _ips(self):
        vpn_ips=[]
        ipn_ips=[]
        macs = []
        sas = SubAccount.objects.filter(account = self)
        for sa in sas:
            if sa.vpn_ip_address:
                vpn_ips.append(sa.vpn_ip_address)  
            if sa.ipn_ip_address:
                ipn_ips.append(sa.ipn_ip_address)  
            if sa.ipn_mac_address:
                macs.append(sa.ipn_mac_address)  
        return ', '.join(vpn_ips), ', '.join(ipn_ips), ', '.join(macs), 
    
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
        accounttarif = AccountTarif.objects.filter(account=self, datetime__lte=datetime.datetime.now()).order_by("-datetime")
        return accounttarif[0] if accounttarif else None
    
    def get_account_tariff_info(self):
        tariff_info = Tariff.objects.extra(where=['id=get_tarif(%s)'], params=[self.id])[:1]
        for tariff in tariff_info:
            return [tariff.id, tariff.name,]

    @property
    def tariff(self):
        try:
            name = Tariff.objects.extra(where=['id=get_tarif(%s)'], params=[self.id])[0].name
        except:
            name=u'Не назначен'
        return name
           
    def get_status(self):
        return dict(ACCOUNT_STATUS)[int(self.status)]



class Organization(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Название организации")
    #rs = models.CharField(max_length=255)
    uraddress = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Юр. адрес")
    okpo = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"ОКПО")
    kpp = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"КПП")
    kor_s = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Корреспонденский счёт")
    unp = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"УНП")
    phone = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Телефон")
    fax = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Факс")
    bank = models.ForeignKey("BankData", blank=True, null=True, on_delete = models.SET_NULL, verbose_name=u"Банк")

    def __unicode__(self):
        return u"%s" % (self.name, )
    
    class Meta:
        permissions = (
           ("organization_view", u"Просмотр организации"),
            )

class TransactionType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    internal_name = models.CharField(max_length=32, unique=True)
    #content_type = models.ForeignKey(ContentType)
    #object_id = models.PositiveIntegerField()
    #content_object = generic.GenericForeignKey('content_type', 'object_id')
    def __unicode__(self):
        return u"%s %s" % (self.name, self.internal_name)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('transactiontype_delete'), self.id)
    
    class Admin:
        pass

    class Meta:
        ordering = ['name']
        verbose_name = u"Тип проводки"
        verbose_name_plural = u"Типы проводок"
        permissions = (
           ("transactiontype_view", u"Просмотр"),
            )
#===============================================================================


class Transaction(models.Model):
    bill = models.CharField(blank=True, default = "", max_length=255, verbose_name=u"Платёжный документ")
    account=models.ForeignKey(Account, on_delete = models.CASCADE, verbose_name=u"Аккаунт")
    accounttarif=models.ForeignKey('AccountTarif', blank=True, null=True, on_delete = models.CASCADE)
    type = models.ForeignKey(to=TransactionType, null=True, to_field='internal_name', verbose_name=u"Тип операции", on_delete = models.SET_NULL)
    
    approved = models.BooleanField(default=True)
    tarif=models.ForeignKey(Tariff, blank=True, null=True, on_delete = models.SET_NULL)
    summ=models.DecimalField(default=0, blank=True, verbose_name=u"Сумма", decimal_places=10,max_digits=20)
    description = models.TextField(default='', blank=True, verbose_name=u"Комментарий")
    created=models.DateTimeField(verbose_name=u"Дата")
    promise=models.BooleanField(default=False, verbose_name=u"Обещанный платёж") 
    end_promise=models.DateTimeField(blank=True, null=True, verbose_name=u"Окончание обещанного платежа")
    promise_expired = models.BooleanField(default=False, verbose_name=u"Обещанный платёж истек")
    systemuser=models.ForeignKey(to='SystemUser', null=True, on_delete = models.SET_NULL, verbose_name=u"Администратор" )

    #def update_ballance(self):
    #    Account.objects.filter(id=self.account_id).update(ballance=F('ballance')+self.summ)
        

    class Admin:
        list_display=('account',  'tarif', 'summ', 'description', 'created')

    class Meta:
        ordering = ['-created']
        verbose_name = u"Проводка"
        verbose_name_plural = u"Проводки"
        permissions = (
           ("transaction_view", u"Просмотр"),
            )
        
    def human_sum(self):
        return self.summ*(-1)
    def __unicode__(self):
        return u"%s, %s, %s" % (self.account, self.summ, self.created)

class AccountTarif(models.Model):
    account   = models.ForeignKey(verbose_name=u'Пользователь', to=Account, related_name='related_accounttarif')
    tarif     = models.ForeignKey(to=Tariff, verbose_name=u'Тарифный план', related_name="account_tarif")
    datetime  = models.DateTimeField(default='', blank=True)
    periodical_billed = models.BooleanField(blank=True)

    class Admin:
        ordering = ['-datetime']
        list_display = ('account','tarif','datetime')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accounttariff_delete'), self.id)
    
    def __unicode__(self):
        return u"%s, %s" % (self.account, self.tarif)

    class Meta:
        ordering = ['-datetime']
        verbose_name = u"Тариф аккаунта"
        verbose_name_plural = u"Тариф аккаунта"
        permissions = (
           ("accounttarif_view", u"Просмотр"),
            )
        
class AccountIPNSpeed(models.Model):
      """
      Класс описывает настройки скорости для пользователей с тарифными планами IPN
      После создания пользователя должна создваться запись в этой таблице
      """
      account = models.ForeignKey(to=Account)
      speed   = models.CharField(max_length=32, default='')
      state   = models.BooleanField(blank=True, default=False)
      static  = models.BooleanField(verbose_name=u"Статическая скорость", help_text=u"Пока опция установлена, биллинг не будет менять для этого клиента скорость", blank=True, default=False)
      datetime  = models.DateTimeField(default='')

      def __unicode__(self):
          return u"%s %s" % (self.account, self.speed)

      class Admin:
          pass

      class Meta:
        verbose_name = u"Скорость IPN клиента"
        verbose_name_plural = u"Скорости IPN клиентов"


class SheduleLog(models.Model):
    account = models.ForeignKey(to=Account, unique=True)
    accounttarif = models.ForeignKey(to=AccountTarif, unique=True)
    ballance_checkout = models.DateTimeField(blank=True, null=True)
    prepaid_traffic_reset = models.DateTimeField(blank=True, null=True)
    prepaid_traffic_accrued = models.DateTimeField(blank=True, null=True)
    prepaid_time_reset = models.DateTimeField(blank=True, null=True)
    prepaid_time_accrued = models.DateTimeField(blank=True, null=True)
    balance_blocked = models.DateTimeField(blank=True, null=True)
    class Admin:
        pass

    class Meta:
        verbose_name = u"История периодических операций"
        verbose_name_plural = u"История периодических операций"


    def __unicode__(self):
        return u'%s' % self.account.username
    
class SystemUser(models.Model):
    username = models.CharField(max_length=255, unique=True)
    #password = models.CharField(max_length=255, default='')
    email = models.CharField(verbose_name=u'Фамилия', blank=True, default='',max_length=200)
    fullname = models.CharField(max_length=512, blank=True, default='')
    home_phone  = models.CharField(max_length=512, blank=True, default ='')
    mobile_phone  = models.CharField(max_length=512, blank=True, default ='')
    address = models.CharField(max_length=512, blank=True, default='')
    job = models.CharField(max_length=256, blank=True, default='')
    last_ip  = models.CharField(max_length=64, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, default='')
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    status = models.BooleanField(default=False)
    host = models.CharField(max_length=255, blank=True, null=True, default="0.0.0.0/0")
    #group = models.ManyToManyField(SystemGroup)
    text_password = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    passport  = models.CharField(max_length=512, blank=True, default ='')
    passport_details  = models.CharField(max_length=512, blank=True, default ='')
    passport_number  = models.CharField(max_length=512, blank=True, default ='')
    unp  = models.CharField(max_length=1024, blank=True, default ='')
    im  = models.CharField(max_length=512, blank=True, default ='')
    
    def __str__(self):
        return '%s' % self.username
    
    def __unicode__(self):
        return u'%s' %self.username
            
    def is_authenticated(self):
        """Always return True. This is a way to tell if the user has been authenticated in templates.
        """
        return True
    is_staff = True
    is_superuser = True    

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('systemuser_delete'), self.id)
        
    class Meta:
        ordering = ['username']
        verbose_name = u"Пользователь системы"
        verbose_name_plural = u"Пользователи системы"
        permissions = (
           ("systemuser_view", u"Просмотр администраторов"),
            ("get_model", "Получение любой модели методом get_model"),
            ("actions_set", "Установка IPN статуса на сервере доступаl"),
            ("documentrender", "Серверный рендеринг документов"),
            ("testcredentials",  "Тестирование данных для сервера доступа"),
            ("getportsstatus","Получение статуса портов коммутатора"),
            ("setportsstatus","Установка статуса портов коммутатора"),
            ("list_log_files","Список лог-файлов биллинга"),
            ("view_log_files","Просмотр лог-файлов биллинга"),
            ("transactions_delete","Удаление проводок"),
            ("sp_info","Метод sp_info"),
            ("auth_groups", "Просмотр груп доступа"),
            ("rawsqlexecution", "Выполнение любого sql запроса")
            
            )

class DocumentType(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        ordering = ['name']
        
class TemplateType(models.Model):
    name = models.TextField()
    
    def __unicode__(self):
        return u"%s" % (self.name)
    
    class Meta:
        ordering = ['id']
        verbose_name = u"Тип шаблона"
        verbose_name_plural = u"Типы шаблонов"
        permissions = (
           ("templatetype_view", u"Просмотр"),
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
        verbose_name = u"Шаблон"
        verbose_name_plural = u"Шаблоны"
        permissions = (
           ("template_view", u"Просмотр"),
           )
class Card(models.Model):
    series = models.IntegerField()
    pin = models.CharField(max_length=255)
    login = models.CharField(max_length=255, blank=True, default='')
    sold = models.DateTimeField(blank=True, default=False)
    nominal = models.FloatField(default=0)
    activated = models.DateTimeField(blank=True, default=False)
    activated_by = models.ForeignKey(Account, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, default='')
    end_date = models.DateTimeField(blank=True, default='')
    disabled= models.BooleanField(default=False, blank=True)
    created = models.DateTimeField()
    template = models.ForeignKey(Template)
    type = models.IntegerField()
    tarif = models.ForeignKey(Tariff, blank=True, null=True)
    nas = models.ForeignKey(Nas, blank=True, null=True)
    ip = models.CharField(max_length=20,blank=True, default='')
    ipinuse = models.ForeignKey("IPInUse", blank=True, null=True)
    ippool = models.ForeignKey("IPPool", blank=True, null=True)
    ext_id = models.CharField(max_length=512,  blank=True, null=True)
    
    class Meta:
        ordering = ['-series', '-created', 'activated']
        verbose_name = u"Карта"
        verbose_name_plural = u"Карты"
        permissions = (
           ("card_view", u"Просмотр карт"),
           )
class BankData(models.Model):
    bank = models.CharField(max_length=255)
    bankcode = models.CharField(blank=True, default='', max_length=40)
    rs = models.CharField(blank=True, default='', max_length=60)
    currency = models.CharField(blank=True, default='', max_length=40)

    def __unicode__(self):
        return u"%s" % self.id
    
    class Meta:
        ordering = ['bank']
        verbose_name = u"Банк"
        verbose_name_plural = u"Банки"
        permissions = (
           ("view", u"Просмотр банков"),
           )
        
class Operator(models.Model):
    organization = models.CharField(max_length=255)
    unp = models.CharField(max_length=40, blank=True, default='')
    okpo = models.CharField(max_length=40, blank=True, default='')
    contactperson = models.CharField(max_length=255, blank=True, default='')
    director = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=40, blank=True, default='')
    fax = models.CharField(max_length=40, blank=True, default='')
    postaddress = models.CharField(max_length=255, blank=True, default='')
    uraddress = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(max_length=255, blank=True, default='')
    bank = models.ForeignKey(BankData, blank=True, null=True)

    class Meta:
        ordering = ['bank']
        verbose_name = u"Информация о провайдере"
        verbose_name_plural = u"Информация о провайдере"
        permissions = (
           ("operator_view", u"Просмотр"),
           )

class Dealer(models.Model):
    organization = models.CharField(max_length = 400)
    unp  = models.CharField(max_length = 255, blank=True, default='')
    okpo  = models.CharField(max_length = 255, blank=True, default='')
    contactperson  = models.CharField(max_length = 255, blank=True, default='')
    director  = models.CharField(max_length = 255, blank=True, default='')
    phone  = models.CharField(max_length = 255, blank=True, default='')
    fax  = models.CharField(max_length = 255, blank=True, default='')
    postaddress  = models.CharField(max_length = 400, blank=True, default='')
    uraddress  = models.CharField(max_length = 400, blank=True, default='')
    email = models.EmailField(max_length=255, blank=True, null=True)
    prepayment = models.FloatField(blank=True, default=0)
    paydeffer = models.IntegerField(blank=True, default=0)
    discount = models.FloatField(blank=True, default=0)
    always_sell_cards = models.BooleanField(default=False)
    
    bank = models.ForeignKey(BankData, blank=True, null=True, on_delete=models.SET_NULL)
    deleted = models.BooleanField(blank=True, default=False)
    objects = SoftDeleteManager()
    
    class Meta:
        ordering = ['organization']
        verbose_name = u"Дилер"
        verbose_name_plural = u"Дилеры"
        permissions = (
           ("dealer_view", u"Просмотр"),
           )
        
    def delete(self):
        if not self.deleted:
            self.deleted=True
            self.save()
            return
        super(Dealer, self).delete()
        
class SaleCard(models.Model):
    dealer = models.ForeignKey(Dealer)
    #pay = models.FloatField()
    sum_for_pay = models.FloatField(blank=True, default=0)
    paydeffer = models.IntegerField(blank=True, default=0)
    discount = models.FloatField(blank=True, default=0)
    discount_sum = models.FloatField(blank=True, default=0)
    prepayment = models.FloatField(blank=True, default=0)
    cards = models.ManyToManyField(Card, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    
    class Meta:
        ordering = ['-created']
        verbose_name = u"Накладная на карты"
        verbose_name_plural = u"накладные на карты"
        permissions = (
           ("salecard_view", u"Просмотр"),
           )
        
class DealerPay(models.Model):
    dealer = models.ForeignKey(Dealer)
    pay = models.FloatField()
    salecard = models.ForeignKey(SaleCard, blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        ordering = ['-created']
        verbose_name = u"Платёж дилера"
        verbose_name_plural = u"Платежи дилера"
        permissions = (
           ("dealerpay_view", u"Просмотр"),
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
    start_date = models.DateTimeField(verbose_name=u"Дата начала")
    end_date = models.DateTimeField(verbose_name=u"Дата конца", blank=True, null=True)
    activated_by_account = models.BooleanField(verbose_name=u"Активировано аккаунтом", blank=True, default=False)
    
    def get_remove_url(self):
        return "%s?id=%s" % (reverse('suspendedperiod_delete'), self.id)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = u"Период без списаний"
        verbose_name_plural = u"Периоды без списаний"
        permissions = (
           ("suspendedperiod_view", u"Просмотр"),
           )
class Group(models.Model):
    #make it an array
    name = models.CharField(max_length=255)
    #trafficclass = models.ManyToManyField(TrafficClass)
    #1 - in, 2-out, 3 - sum, 4-max
    direction = models.IntegerField()
    # 1 -sum, 2-max
    type = models.IntegerField()
    
    
    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name']
        verbose_name = u"Группа трафика"
        verbose_name_plural = u"Группы трафика"
        permissions = (
           ("group_view", u"Просмотр"),
           )
        
class GroupTrafficClass(models.Model):
    group = models.ForeignKey(Group)
    trafficclass = models.ForeignKey(TrafficClass)
    
    
    class Meta:
        db_table = "billservice_group_trafficclass"
        
class GroupStat(models.Model):
    group = models.ForeignKey(Group)
    account = models.ForeignKey(Account)
    bytes = models.IntegerField()
    datetime = models.DateTimeField()
    #trafficclass = models.ForeignKey(TrafficClass, blank=True, null=True)
    
    
#class GroupStatAll(models.Model):
#    account = models.ForeignKey(Account)
    
class SpeedLimit(models.Model):
    limit = models.ForeignKey(TrafficLimit)
    speed_units = models.CharField(max_length=10, blank=True)
    change_speed_type = models.CharField(max_length=10, blank=True)
    max_tx = models.IntegerField(blank=True)
    max_rx = models.IntegerField(blank=True)
    burst_tx = models.IntegerField(blank=True)
    burst_rx = models.IntegerField(blank=True)
    burst_treshold_tx = models.IntegerField(blank=True)
    burst_treshold_rx = models.IntegerField(blank=True)
    burst_time_tx = models.IntegerField(blank=True)
    burst_time_rx = models.IntegerField(blank=True)
    min_tx = models.IntegerField(blank=True)
    min_rx = models.IntegerField(blank=True)
    priority = models.IntegerField(blank=True)
    

class AccountSpeedLimit(models.Model):
    account = models.ForeignKey(Account)
    speedlimit = models.ForeignKey(SpeedLimit)

class IPPool(models.Model):
    name = models.CharField(max_length=255)
    #0 - VPN, 1-IPN
    type = models.IntegerField(choices=((0, u"IPv4 VPN"),(1, u"IPv4 IPN"),(2, u"IPv6 VPN"),(3, u"IPv6 IPN"),))
    start_ip = models.IPAddressField()
    end_ip = models.IPAddressField()
    next_ippool = models.ForeignKey("IPPool", blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = u"IP пул"
        verbose_name_plural = u"IP пулы"
        permissions = (
           ("ippool_view", u"Просмотр"),
           )
    def __unicode__(self):
        return u"%s-%s" % (self.start_ip, self.end_ip)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('ippool_delete'), self.id)




class IPInUse(models.Model):
    pool = models.ForeignKey(IPPool, verbose_name=u'IP пул')
    ip = models.CharField(max_length=255, verbose_name=u'IP адрес')
    datetime = models.DateTimeField(verbose_name=u'Дата выдачи')
    disabled = models.DateTimeField(blank=True, null=True, verbose_name=u'Дата освобождения')
    dynamic = models.BooleanField(default=False, verbose_name=u'Выдан динамически')

    class Meta:
        ordering = ['ip']
        verbose_name = u"Занятый IP адрес"
        verbose_name_plural =  u"Занятые IP адреса"
        permissions = (
           ("ipinuse_view", u"Просмотр"),
           )
    def __unicode__(self):
        return u"%s" % self.ip

class TrafficTransaction(models.Model):
    traffictransmitservice = models.ForeignKey(TrafficTransmitService, null=True, on_delete=models.SET_NULL) # ON DELETE SET NULL
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    summ = models.FloatField()
    created = models.DateTimeField()
    accounttarif = models.ForeignKey(AccountTarif, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created']
        verbose_name = u"Списание за трафик"
        verbose_name_plural = u"Списания за трафик"
        permissions = (
           ("traffictransaction_view", u"Просмотр"),
           )

class TPChangeRule(models.Model):
    from_tariff = models.ForeignKey(Tariff, related_name="from_tariff")
    to_tariff = models.ForeignKey(Tariff, related_name="to_tariff")
    disabled = models.BooleanField()
    cost = models.FloatField()
    ballance_min = models.FloatField()
    settlement_period = models.ForeignKey(SettlementPeriod, blank=True, null=True, on_delete=models.SET_NULL)
    on_next_sp = models.BooleanField( blank=True, default=False)
    
    class Meta:
        ordering = ['from_tariff', 'to_tariff']
        verbose_name = u"Правило смены тарифов"
        verbose_name_plural = u"Правила смены тарифов"
        permissions = (
           ("tpchangerule_view", u"Просмотр"),
           )
        
class RadiusAttrs(models.Model):
    tarif = models.ForeignKey(Tariff, blank=True, null=True)
    nas = models.ForeignKey(Nas, blank=True, null=True)
    vendor = models.IntegerField(blank=True, default=0)
    attrid = models.IntegerField()
    value = models.CharField(max_length = 255)
     
    class Meta:
        ordering = ['vendor', 'attrid']
        verbose_name = u"Custom RADIUS атрибут"
        verbose_name_plural = u"Custom RADIUS атрибуты"
        permissions = (
           ("radiusattrs_view", u"Просмотр"),
           )
        
class AddonService(models.Model):    
    name = models.CharField(max_length=255 , verbose_name=u'Название')    
    comment = models.TextField(blank=True, default='', verbose_name=u'Комментарий')
    allow_activation = models.BooleanField(blank=True, default = False, verbose_name=u"Разешить активацию", help_text=u'Разрешить активацию при нулевом балансе и блокировках')    
    service_type = models.CharField(verbose_name=u"Тип услуги",max_length=32, choices=(("onetime", u"Разовая услуга"),("periodical", u"Периодическая услуга"),))    
    sp_type = models.CharField(verbose_name=u"Способ списания",max_length=32, choices=(("AT_START",u"В начале расчётного периода"),("AT_END", u"В конце расчётного периода" ),("GRADUAL", u"На протяжении расчётного периода"),))    
    sp_period = models.ForeignKey(SettlementPeriod, verbose_name=u"Расчётный период", help_text=u"Период, в течении которого будет списываться стоимость услуги", related_name="addonservice_spperiod", blank=True, null=True, on_delete=models.SET_NULL)    
    timeperiod = models.ForeignKey(TimePeriod, verbose_name=u"Время активации", help_text=u"Время, когда возможна активация услуги",null=True, on_delete=models.SET_NULL)    
    cost = models.DecimalField(verbose_name=u"Стоимость услуги", decimal_places=10, max_digits=30, blank=True, default=0)    
    cancel_subscription = models.BooleanField(verbose_name=u"Разрешить отключение", help_text=u"Разрешить самостоятельное отключение услуги", default = True)    
    wyte_period = models.ForeignKey(SettlementPeriod, verbose_name=u"Штрафуемый период", help_text=u"Списывать сумму штрафа при досрочном отключении услуги пользователем",  related_name="addonservice_wyteperiod", blank=True, null=True, on_delete=models.SET_NULL)    
    wyte_cost = models.DecimalField(verbose_name=u"Сумма штрафа", decimal_places=10, max_digits=60, blank=True, default=0)    
    action = models.BooleanField(verbose_name=u"Выполнить действие", blank=True, default=False)    
    nas = models.ForeignKey(Nas, verbose_name=u"Сервер доступа", help_text=u"Сервер доступа, на котором будут производиться действия",  blank=True, null=True, on_delete=models.SET_NULL)    
    service_activation_action = models.TextField(verbose_name=u"Действие для активации услуги", blank=True, default='')    
    service_deactivation_action = models.TextField(verbose_name=u"Действие для отключения услуги", blank=True, default='')    
    deactivate_service_for_blocked_account = models.BooleanField(verbose_name=u"Отключать услугу при бловировке аккаунта", help_text=u"Отключать услугу при достижении нулевого баланса или блокировках", blank=True, default=False)    
    change_speed = models.BooleanField(verbose_name=u"Изменить скорость", help_text=u"Изменить параметры скорости при активации аккаунта", blank=True, default=False)    
    change_speed_type = models.CharField(verbose_name=u"Способ изменения скорости", max_length=32, choices=(("add", "Добавить к текущей"), ("abs","Абсолютное значение",),), blank=True, null=True)    
    speed_units = models.CharField(verbose_name=u"Единицы скорости", max_length = 32,choices=(("Kbps","Kbps",), ("Mbps","Mbps",),("%", "%",)), blank=True, null=True)    
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
        verbose_name = u"Подключаемая услуга"
        verbose_name_plural = u"Подключаемые услуги"
        permissions = (
           ("addonservice_view", u"Просмотр"),
           )
        
class AddonServiceTarif(models.Model):    
    tarif = models.ForeignKey(Tariff)    
    service = models.ForeignKey(AddonService)    
    activation_count = models.IntegerField(blank=True, default=0)    
    activation_count_period = models.ForeignKey(SettlementPeriod, blank=True, null=True)    
    type=models.IntegerField(default=0)# 0-Account, 1-Subaccount

    class Meta:
        ordering = ['id']
        verbose_name = u"Разрешённая подключаемая услуга"
        verbose_name_plural = u"Разрешённые подключаемые услуги"
        permissions = (
           ("addonservicetarif_view", u"Просмотр"),
           )

class AccountAddonService(models.Model):    
    service = models.ForeignKey(AddonService, null=True, on_delete = models.CASCADE)    
    account = models.ForeignKey(Account, blank=True, null=True)   
    subaccount = models.ForeignKey('SubAccount', blank=True, null=True) 
    activated = models.DateTimeField()    
    deactivated = models.DateTimeField(blank=True, null=True)    
    action_status = models.BooleanField()    
    speed_status = models.BooleanField()
    temporary_blocked = models.DateTimeField(blank=True, null=True)
    last_checkout = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-activated', '-deactivated']
        verbose_name = u"Подключённая услуга"
        verbose_name_plural = u"Подключённые услуги"
        permissions = (
           ("accountaddonservice_view", u"Просмотр"),
           )
        
class AddonServiceTransaction(models.Model):
    service = models.ForeignKey(AddonService)
    service_type = models.CharField(max_length=32)#onetime, periodical   
    account = models.ForeignKey(Account)
    accountaddonservice = models.ForeignKey(AccountAddonService)
    accounttarif = models.ForeignKey(AccountTarif)
    type = models.ForeignKey(to=TransactionType, null=True, to_field='internal_name', verbose_name=u"Тип операции", on_delete = models.SET_NULL)
    summ = models.DecimalField(decimal_places=5, max_digits=60)
    created = models.DateTimeField()
    
    class Meta:
        ordering = ['-created']
        verbose_name = u"Списание по подключаемой услуге"
        verbose_name_plural = u"Списания по подключаемым услугам"
        permissions = (
           ("accountaddonservicetransaction_view", u"Просмотр"),
           )

    
class News(models.Model):
    body = models.TextField(u'Заголовок новости')
    age = models.DateTimeField(blank=True, null=True)
    public = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    agent = models.BooleanField(default=False)
    created = models.DateTimeField(blank=True, auto_now_add=True)
    
    class Meta:
        ordering = ['-created']
        verbose_name = u"Новость"
        verbose_name_plural = u"Новости"
        permissions = (
           ("news_view", u"Просмотр"),
           )
        
class AccountViewedNews(models.Model):
    news = models.ForeignKey(News)
    account = models.ForeignKey(Account)
    viewed = models.BooleanField(default=False)

        
    
       
class SubAccount(models.Model):
    account = models.ForeignKey(Account, related_name='subaccounts')
    username = models.CharField(max_length=512, blank=True)
    password = models.CharField(max_length=512, blank=True)
    ipn_ip_address = IPNetworkField(blank=True,null=True, default='0.0.0.0')
    ipn_mac_address = models.CharField(blank=True, max_length=17, default='')
    vpn_ip_address = models.IPAddressField(blank=True,null=True,  default='0.0.0.0')
    allow_mac_update = models.BooleanField(default=False)
    nas = models.ForeignKey(Nas, blank=True, null=True, on_delete = models.SET_NULL)
    ipn_added = models.BooleanField()
    ipn_enabled = models.BooleanField()
    ipn_sleep = models.BooleanField()
    need_resync = models.BooleanField()
    speed = models.TextField(blank=True)
    switch = models.ForeignKey(Switch, blank=True, null=True, on_delete = models.SET_NULL)
    switch_port = models.IntegerField(blank=True, null=True)
    allow_dhcp = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешать получать IP адреса по DHCP")
    allow_dhcp_with_null = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешать получать IP адреса по DHCP при нулевом балансе")    
    allow_dhcp_with_minus = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешать получать IP адреса по DHCP при отрицатеьлном балансе")    
    allow_dhcp_with_block = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешать получать IP адреса по DHCP при наличии блокировок по лимитам или балансу")    
    allow_vpn_with_null = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешать RADIUS авторизацию при нулевом балансе")    
    allow_vpn_with_minus = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешать RADIUS авторизацию при отрицательном балансе балансе")    
    allow_vpn_with_block = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешать RADIUS авторизацию при наличии блокировок по лимитам или балансу")   
    allow_ipn_with_null = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешать IPN авторизацию при нулевом балансе")
    allow_ipn_with_minus = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешать IPN авторизацию при отрицательном балансе")
    allow_ipn_with_block = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешать IPN авторизацию при нулевом балансе")  
    associate_pptp_ipn_ip = models.BooleanField(blank=True, default=False, verbose_name=u"Привязать PPTP/L2TP авторизацию к IPN IP")  
    associate_pppoe_ipn_mac = models.BooleanField(blank=True, default=False, verbose_name=u"Привязать PPPOE авторизацию к IPN MAC")  
    ipn_speed = models.TextField(blank=True, help_text=u"Не менять указанные настройки скорости")
    vpn_speed = models.TextField(blank=True, help_text=u"Не менять указанные настройки скорости")
    allow_addonservice = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешить самостоятельную активацию подключаемых услуг на этот субаккаунт")  
    vpn_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_vpn_ipinuse_set', on_delete=models.SET_NULL)
    ipn_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_ipn_ipinuse_set', on_delete=models.SET_NULL)
    vpn_ipv6_ip_address = models.CharField(blank=True, null=True, max_length=128, default='::')
    vpn_ipv6_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_vpn_ipv6_ipinuse_set', on_delete=models.SET_NULL)
    #ipn_ipv6_ip_address = models.TextField(blank=True, null=True)
    vlan = models.IntegerField(blank=True, null=True)
    allow_mac_update = models.BooleanField(blank=True, default=False, verbose_name=u"Разрешить самостоятельно обновлять MAC адрес через веб-кабинет")  
    ipv4_ipn_pool = models.ForeignKey(IPPool, blank=True, default=None, null=True, related_name='subaccount_ipn_ippool_set', on_delete=models.SET_NULL)
    ipv4_vpn_pool = models.ForeignKey(IPPool, blank=True, default=None, null=True, related_name='subaccount_vpn_ippool_set', on_delete=models.SET_NULL)
  
    def __unicode__(self):
        return u"%s" % self.username

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('subaccount_delete'), self.id)
    
    class Meta:
        ordering = ['-username']
        verbose_name = u"Субаккаунт"
        verbose_name_plural = u"Субаккаунт"
        permissions = (
            ("subaccount_view", "Просмотр"),
            ("getmacforip", "Получение mac адреса по IP"),
            )
        
class BalanceHistory(models.Model):
    account=models.ForeignKey(Account)
    balance = models.DecimalField(max_digits=30, decimal_places=20)
    datetime = models.DateTimeField()
    
    class Meta:
        ordering = ['-datetime']
        verbose_name = u"История изменения баланса"
        verbose_name_plural =  u"История изменения баланса"
        permissions = (
            ("balancehistory_view", "Просмотр"),
            )
    
class City(models.Model):
    name = models.CharField(max_length=320)

    def __unicode__(self):
        return u"%s" % self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = u"Город"
        verbose_name_plural =  u"Города"
        permissions = (
           ("city_view", u"Просмотр"),
           )
        
class Street(models.Model):
    name = models.CharField(max_length=320)
    city= models.ForeignKey(City)
    
    def __unicode__(self):
        return u"%s" % self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = u"Улица"
        verbose_name_plural =  u"Улицы"
        permissions = (
           ("street_view", u"Просмотр"),
           )
        
class House(models.Model):
    name = models.CharField(max_length=320)
    street = models.ForeignKey(Street)
    def __unicode__(self):
        return u"%s" % self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = u"Дом"
        verbose_name_plural =  u"Дома"
        permissions = (
           ("house_view", u"Просмотр"),
           )
        
class RadiusTraffic(models.Model):
    direction = models.IntegerField()
    tarification_step = models.IntegerField()
    rounding = models.IntegerField()
    prepaid_direction = models.IntegerField()
    prepaid_value = models.IntegerField()
    reset_prepaid_traffic = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = u"Услуга тарификации RADIUS трафика"
        verbose_name_plural = u"Услуги тарификации RADIUS трафика"
        permissions = (
           ("radiustraffic_view", u"Просмотр"),
           )
        
class RadiusTrafficNode(models.Model):
    radiustraffic = models.ForeignKey(RadiusTraffic)
    value = models.DecimalField(max_digits=30, decimal_places=20)
    timeperiod = models.ForeignKey(TimePeriod)
    cost = models.DecimalField(max_digits=30, decimal_places=20)
    class Meta:
        ordering = ['value']
        verbose_name = u"Настройка тарификации RADIUS трафика"
        verbose_name_plural = u"Настройка тарификации RADIUS трафика"
        permissions = (
           ("radiustrafficnode_view", u"Просмотр"),
           )
        
class ContractTemplate(models.Model):
    template = models.TextField()
    counter = models.IntegerField()
    class Meta:
        ordering = ['template']
        verbose_name =u"Шаблон номера договора"
        verbose_name_plural =u"Шаблоны номеров договоров"
        permissions = (
           ("contracttemplate_view", u"Просмотр"),
           )
    def __unicode__(self):
        return unicode(self.template)
    
class Manufacturer(models.Model):
    name = models.TextField()

    def __unicode__(self):
        return u'%s' % self.name
    
    class Meta:
        ordering = ['name']
        verbose_name =u"Производитель"
        verbose_name_plural =u"Производители"
        permissions = (
           ("manufacturer_view", u"Просмотр"),
           )
        
class HardwareType(models.Model):
    name = models.TextField()
    
    def __unicode__(self):
        return u'%s' % self.name
    class Meta:
        ordering = ['name']
        verbose_name =u"Тип оборудования"
        verbose_name_plural =u"Типы оборудования"
        permissions = (
           ("hardwaretype_view", u"Просмотр"),
           )
        
class Model(models.Model):
    name = models.TextField()
    manufacturer = models.ForeignKey(Manufacturer)
    hardwaretype = models.ForeignKey(HardwareType)

    def __unicode__(self):
        return u'%s/%s/%s' % (self.hardwaretype, self.manufacturer, self.name)
    class Meta:
        ordering = ['name']
        verbose_name =u"Модель оборудования"
        verbose_name_plural =u"Модель оборудования"
        permissions = (
           ("model_view", u"Просмотр"),
           )
        
class Hardware(models.Model):
    #manufacturer = models.ForeignKey(Manufacturer)
    model = models.ForeignKey(Model)
    name = models.CharField(max_length=500, blank=True, default='',)
    sn = models.CharField(max_length=500, blank=True, default='',)
    comment = models.TextField(blank=True, default='')#
    ipaddress = models.IPAddressField(blank=True)
    macaddress = models.CharField(blank=True, default='', max_length=32)

    @property
    def manufacturer(self):
        return "%s" % self.model.manufacturer
    
    def __unicode__(self):
        return u'%s' % self.name
    class Meta:
        ordering = ['name']
        verbose_name =u"Устройство"
        verbose_name_plural =u"Устройства"
        permissions = (
           ("hardware_view", u"Просмотр"),
           )
        
class AccountHardware(models.Model):
    account=models.ForeignKey(Account)
    hardware = models.ForeignKey(Hardware)
    datetime = models.DateTimeField()
    returned = models.DateTimeField()
    comment = models.TextField()

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accounthardware_delete'), self.id)
    
    class Meta:
        ordering = ['datetime']
        verbose_name =u"Устройство у абонента"
        verbose_name_plural =u"Устройства у абонентов"
        permissions = (
           ("accounthardware_view", u"Просмотр"),
           )

class TotalTransactionReport(models.Model):
    service_id = models.IntegerField()
    service_name = models.CharField(max_length=128)
    table = models.CharField(max_length=128)
    created = models.DateTimeField()
    tariff = models.ForeignKey(Tariff)
    summ = models.DecimalField(decimal_places=10, max_digits=30)
    account = models.ForeignKey(Account)
    type = models.ForeignKey(TransactionType, to_field='internal_name')
    systemuser = models.ForeignKey(SystemUser)
    bill = models.TextField()
    description = models.TextField()
    end_promise = models.DateTimeField()
    promise_expired = models.BooleanField()

    class Meta:
        managed = False
        ordering = ['-created']
        
class PeriodicalServiceLog(models.Model):
    service = models.ForeignKey(PeriodicalService)
    accounttarif = models.ForeignKey(AccountTarif)
    datetime = models.DateTimeField()
      
    class Meta:
        ordering = ['-datetime']
