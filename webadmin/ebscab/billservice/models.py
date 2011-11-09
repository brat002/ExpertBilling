#-*-coding=utf-8-*-
from django.db import models
from ebscab.nas.models import Nas, TrafficClass, TrafficClass
from django.contrib.auth.models import User

import datetime, time
from django.contrib.contenttypes.models import ContentType

# Create your models here.
# choiCe

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
                (u'IPN',u'IPN'),
                (u'PPTP',u'PPTP'),
                (u'PPPOE',u'PPPOE'),
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


class TimePeriodNode(models.Model):
    """
    Диапазон времени ( с 15 00 до 18 00 каждую вторник-пятницу,утро, ночь, сутки, месяц, год и т.д.)
    """
    name = models.CharField(max_length=255, verbose_name=u'Название периода', default='', blank=True)
    time_start = models.DateTimeField(verbose_name=u'Дата и время начала периода', default='', blank=True)
    length = models.IntegerField(verbose_name=u'Период в секундах', default=0, blank=True)
    repeat_after = models.CharField(max_length=255, choices=PERIOD_CHOISES, verbose_name=u'Повторять через', default='MONTH', blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','time_start','length','repeat_after')

    class Meta:
        verbose_name = u"Нода временного периода"
        verbose_name_plural = u"Ноды временных периодов"


class TimePeriod(models.Model):
    name = models.CharField(max_length=255, verbose_name=u'Название группы временных периодов', unique=True)
    time_period_nodes = models.ManyToManyField(to=TimePeriodNode, verbose_name=u'Группа временных периодов')

    def in_period(self):
        for time_period_node in self.time_period_nodes:
            if time_period_node.in_period()==True:
                return True
        return False

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name',)


    class Meta:
        verbose_name = u"Временной период"
        verbose_name_plural = u"Временные периоды"



class SettlementPeriod(models.Model):
    """
    Расчётный период
    """
    name = models.CharField(max_length=255, verbose_name=u'Название расчётного периода', unique=True)
    time_start = models.DateTimeField(verbose_name=u'Дата и время начала периода')
    length = models.IntegerField(blank=True, default=0,verbose_name=u'Период действия в секундах')
    length_in = models.CharField(max_length=255, choices=PERIOD_CHOISES, blank=True, default='', verbose_name=u'Длина промежутка')
    autostart = models.BooleanField(verbose_name=u'Начинать при активации', default=False)

    def __unicode__(self):
        return u"%s, Автостарт %s" % (self.name, self.autostart)

    class Admin:
        ordering = ['name']
        list_display = ('name','time_start','length','length_in','autostart')


    class Meta:
        verbose_name = u"Расчётный период"
        verbose_name_plural = u"Расчётные периоды"

class PeriodicalService(models.Model):
    """
    Справочник периодических услуг
    TO-DO: Сделать справочники валют
    """
    tarif             = models.ForeignKey('Tariff')
    name              = models.CharField(max_length=255, verbose_name=u'Название услуги')
    settlement_period = models.ForeignKey(to=SettlementPeriod, verbose_name=u'Период')
    cost              = models.FloatField(verbose_name=u'Стоимость услуги', default=0, blank=True)
    cash_method       = models.CharField(verbose_name=u'Способ снятия', max_length=255, choices=CASH_METHODS, default='AT_START', blank=True)
    condition         = models.IntegerField() # 0 - Всегда. 1- Только при положительном балансе. 2 - только при орицательном балансе

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','settlement_period','cost','cash_method')


    class Meta:
        verbose_name = u"Периодическая услуга"
        verbose_name_plural = u"Периодические услуги"

class PeriodicalServiceHistory(models.Model):
    service = models.ForeignKey(to=PeriodicalService)
    #transaction = models.ForeignKey(to='Transaction')
    accounttarif = models.ForeignKey(to='AccountTarif')
    datetime  = models.DateTimeField(auto_now_add=True)
    summ = models.FloatField()
    account = models.ForeignKey('Account')
    type_id   = models.CharField(max_length=32, default='')

    def __unicode__(self):
        return u"%s" % (self.service)

    class Admin:
        ordering = ['-datetime']
        list_display = ('service','transaction','datetime')


    class Meta:
        verbose_name = u"История по пер. услугам"
        verbose_name_plural = u"История по пер. услугам"

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
        verbose_name = u"Разовый платеж"
        verbose_name_plural = u"Разовые платежи"
        
class OneTimeServiceHistory(models.Model):
    onetimeservice = models.ForeignKey(OneTimeService)
    datetime  = models.DateTimeField(auto_now_add=True)
    summ = models.IntegerField()
    account=models.ForeignKey('Account')
    accounttarif = models.ForeignKey('AccountTarif')
    transaction = models.ForeignKey('Transaction')


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
        return u"%s" % self.name

    class Admin:
        #ordering = ['name']
        list_display = ('prepaid_time',)


    class Meta:
        verbose_name = u"Доступ с учётом времени"
        verbose_name_plural = u"Доступ с учётом времени"

class TimeAccessNode(models.Model):
    """
    Нода тарификации по времени
    """
    time_access_service = models.ForeignKey(to=TimeAccessService, related_name="time_access_nodes")
    time_period         = models.ForeignKey(to=TimePeriod, verbose_name=u'Промежуток')
    cost                = models.FloatField(verbose_name=u'Стоимость за минуту', default=0)

    def __unicode__(self):
        return u"%s %s" % (self.time_period, self.cost)

    class Admin:
        ordering = ['name']
        list_display = ('time_period', 'cost')


    class Meta:
        verbose_name = u"Период доступа"
        verbose_name_plural = u"Периоды доступа"

class AccessParameters(models.Model):
    #name              = models.CharField(max_length=255, verbose_name=u'Название вида доступа')
    access_type       = models.CharField(max_length=255, choices=ACCESS_TYPE_METHODS, default='PPTP', blank=True, verbose_name=u'Вид доступа')
    access_time       = models.ForeignKey(to=TimePeriod, verbose_name=u'Разрешённое время доступа')
    #ip_address_pool   = models.ForeignKey(to=IPAddressPool, verbose_name=u'Пул адресов', blank=True, null=True)
    max_limit      = models.CharField(verbose_name=u"MAX (kbps)", max_length=64, blank=True, default="")
    min_limit      = models.CharField(verbose_name=u"MIN (kbps)", max_length=64, blank=True, default="")
    burst_limit    = models.CharField(verbose_name=u"Burst", max_length=64, blank=True, default="")
    burst_treshold = models.CharField(verbose_name=u"Burst treshold (kbps)", max_length=64, blank=True, default="")
    burst_time     = models.CharField(verbose_name=u"Burst Time", blank=True, max_length=64, default="")
    #от 1 до 8
    priority             = models.IntegerField(verbose_name=u"Приоритет", blank=True, default=8)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        #ordering = ['name']
        list_display = ('access_type',)


    class Meta:
        verbose_name = u"Параметры доступа"
        verbose_name_plural = u"Параметры доступа"

class TimeSpeed(models.Model):
    """
    Настройки скорости в интервал времени
    """
    access_parameters = models.ForeignKey(to=AccessParameters, related_name="access_speed")
    time = models.ForeignKey(TimePeriod)
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
        verbose_name = u"настройка скорости"
        verbose_name_plural = u"Настройки скорости"

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

class TrafficTransmitNodes(models.Model):
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService, verbose_name=u"Услуга доступа по трафику", related_name="traffic_transmit_nodes")
    traffic_class     = models.ManyToManyField(to=TrafficClass, verbose_name=u'Классы трафика')
    time_nodes        = models.ManyToManyField(to=TimePeriod, verbose_name=u'Промежуток времени')
    cost              = models.FloatField(default=0, verbose_name=u'Цена трафика')
    edge_start        = models.FloatField(default=0,verbose_name=u'Начальная граница', help_text=u'Цена актуальна, если пользователь в текущем расчётном периоде наработал больше указанного количество байт')
    edge_end          = models.FloatField(default=0,verbose_name=u'Конечная граница', help_text=u'Цена актуальна, если пользователь в текущем расчётном периоде наработал меньше указанного количество байт')
    in_direction      = models.BooleanField(default=True, blank=True)
    out_direction      = models.BooleanField(default=True, blank=True)
    #transit_direction      = models.BooleanField()
    
    def __unicode__(self):
        return u"%s" % (self.cost)

    class Admin:
        ordering = ['traffic_class']
        list_display = ('cost','edge_start','edge_end')


    class Meta:
        verbose_name = u"цена за направление"
        verbose_name_plural = u"Цены за направления трафика"


class AccountPrepaysTrafic(models.Model):
    """
    При подключении пользователю тарифного плана, у которого есть предоплаченный трафик
    в таблице должны создаваться записи
    В начале каждого расчётного периода пользователю должен заново начисляться трафик
    """
    account_tarif = models.ForeignKey(to="AccountTarif")
    prepaid_traffic = models.ForeignKey(to=PrepaidTraffic)
    size = models.FloatField(blank=True, default=0)
    datetime = models.DateTimeField(auto_now_add=True, default='')
    current=models.BooleanField(default=False)
    reseted=models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s" % (self.prepaid_traffic)

    class Admin:
        pass

    class Meta:
        verbose_name = u"Предоплаченый трафик"
        verbose_name_plural = u"Предоплаченный трафик"

class AccountPrepaysRadiusTrafic(models.Model):
    """
    При подключении пользователю тарифного плана, у которого есть предоплаченный трафик
    в таблице должны создаваться записи
    В начале каждого расчётного периода пользователю должен заново начисляться трафик
    """
    account_tarif = models.ForeignKey(to="AccountTarif")
    prepaid_traffic = models.ForeignKey(to='RadiusTraffic')
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
        verbose_name = u"Предоплаченый radius трафик "
        verbose_name_plural = u"Предоплаченный radius трафик"




class AccountPrepaysTime(models.Model):
    account_tarif = models.ForeignKey(to="AccountTarif")
    prepaid_time_service = models.ForeignKey(to=TimeAccessService)
    size = models.IntegerField(default=0, blank=True)
    datetime = models.DateTimeField(auto_now_add=True, default='')
    current=models.BooleanField(default=False)
    reseted=models.BooleanField(default=False)

    class Admin:
        pass

    class Meta:
        verbose_name = u"Предоплаченное время пользователя"
        verbose_name_plural = u"Предоплаченное время пользователей"

class TrafficLimit(models.Model):
    tarif             = models.ForeignKey('Tariff')
    name              = models.CharField(max_length=255, verbose_name=u'Название лимита')
    settlement_period = models.ForeignKey(to=SettlementPeriod, verbose_name=u'Период', blank=True, null=True, help_text=u"Если период не указан-берётся период тарифного плана. Если установлен автостарт-началом периода будет считаться день привязки тарифного плана пользователю. Если не установлен-старт берётся из расчётного периода")
    size              = models.IntegerField(verbose_name=u'Размер в килобайтах', default=0)
    group             = models.ForeignKey("Group")
    mode              = models.BooleanField(default=False, blank=True, verbose_name=u'За длинну расчётного периода', help_text=u'Если флаг установлен-то количество трафика считается за последние N секунд, указанные в расчётном периоде')
    #action            = models.IntegerField()
    
    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name', 'settlement_period')


    class Meta:
        verbose_name = u"лимит трафика"
        verbose_name_plural = u"Лимиты трафика"

class Tariff(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название тарифного плана', unique = True)
    description       = models.TextField(verbose_name=u'Описание тарифного плана', blank=True, default='')
    access_parameters = models.ForeignKey(to=AccessParameters, verbose_name=u'Параметры доступа')
    #traffic_limit     = models.ManyToManyField(to=TrafficLimit, verbose_name=u'Лимиты трафика', blank=True, null=True, help_text=u"Примеры: 200 мегабайт в расчётный период, 50 мегабайт за последнюю неделю")
    #periodical_services = models.ManyToManyField(to=PeriodicalService, verbose_name=u'периодические услуги', blank=True, null=True)
    #onetime_services  = models.ManyToManyField(to=OneTimeService, verbose_name=u'Разовые услуги', blank=True, null=True)
    time_access_service = models.ForeignKey(to=TimeAccessService, verbose_name=u'Доступ с учётом времени', blank=True, null=True)
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService, verbose_name=u'Доступ с учётом трафика', blank=True, null=True)
    cost              = models.FloatField(verbose_name=u'Стоимость пакета', default=0 ,help_text=u"Стоимость активации тарифного плана. Целесообразно указать с расчётным периодом. Если не указана-предоплаченный трафик и время не учитываются")
    reset_tarif_cost  = models.BooleanField(verbose_name=u'Производить доснятие', blank=True, default=False, help_text=u'Производить доснятие суммы до стоимости тарифного плана в конце расчётного периода')
    settlement_period = models.ForeignKey(to=SettlementPeriod, blank=True, null=True, verbose_name=u'Расчётный период')
    ps_null_ballance_checkout = models.BooleanField(verbose_name=u'Производить снятие денег  при нулевом баллансе', help_text =u"Производить ли списывание денег по периодическим услугам при достижении нулевого балланса или исчерпании кредита?", blank=True, default=False )
    active            = models.BooleanField(default=False, blank=True)
    deleted           = models.BooleanField(default=False, blank=True)
    allow_express_pay = models.BooleanField(verbose_name=u'Оплата экспресс картами', blank=True, default=False)
    require_tarif_cost = models.BooleanField(default=False, blank=True)
    allow_userblock   =models.BooleanField(default=False)
    userblock_cost = models.DecimalField(decimal_places=10, max_digits=60)  
    userblock_max_days = models.IntegerField()
    userblock_require_balance = models.DecimalField(decimal_places=10, max_digits=60)  
    allow_ballance_transfer = models.BooleanField()
    
    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','access_parameters','time_access_service','traffic_transmit_service','cost','settlement_period', 'ps_null_ballance_checkout')


    class Meta:
        verbose_name = u"Тариф"
        verbose_name_plural = u"Тарифы"

ACTIVE = 1
NOT_ACTIVE_NOT_WRITING_OFF  = 2
NOT_ACTIVE_WRITING_OFF = 3 

ACCOUNT_STATUS = (
                  (ACTIVE, u'Активен'),
                  (NOT_ACTIVE_NOT_WRITING_OFF, u'Неактивен, не списывать периодические услуги'),
                  (NOT_ACTIVE_WRITING_OFF, u'Неактивен, списывать периодические услуги'),
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
    email = models.CharField(verbose_name=u'Фамилия', blank=True, default='',max_length=200)
    #phone = models.CharField(max_length=255)
    #cellphone = models.CharField(max_length=255)
    #passport_n = models.CharField(max_length=255)
    #passport_give = models.CharField(max_length=255)
    #passport_date = models.DateField()
    
    address = models.TextField(verbose_name=u'Домашний адрес', blank=True, default='')
    city = models.ForeignKey('City', blank=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255)
    street = models.ForeignKey('Street', blank=True)
    house = models.ForeignKey('House', blank=True)
    house_bulk = models.CharField(blank=True, max_length=255)
    entrance = models.CharField(blank=True, max_length=255)
    room = models.CharField(blank=True, max_length=255)
    
    #assign_vpn_ip_from_dhcp = models.BooleanField(blank=True, default=False)
    nas = models.ForeignKey(to=Nas, blank=True,null=True, verbose_name=u'Сервер доступа')
    #vpn_pool = models.ForeignKey(to=IPAddressPool, related_name='virtual_pool', blank=True, null=True)
    #vpn_ip_address = models.IPAddressField(u'Статический IP VPN адрес', help_text=u'Если не назначен-выбрать из пула, указанного в тарифном плане', blank=True, default='0.0.0.0')
    #assign_ipn_ip_from_dhcp = models.BooleanField(blank=True, default=False)
    #ipn_pool = models.ForeignKey(to=IPAddressPool, related_name='ipn_pool', blank=True, null=True)
    #ipn_ip_address = models.IPAddressField(u'IP адрес клиента', help_text=u'Для IPN тарифных планов', blank=True, default='0.0.0.0')
    #ipn_mac_address = models.CharField(u'MAC адрес клиента', max_length=32, help_text=u'Для IPN тарифных планов', blank=True, default='')
    ipn_status = models.BooleanField(verbose_name=u"Статус на сервере доступа", default=False, blank=True)
    status=models.IntegerField(verbose_name=u'Статус пользователя', default=1)
    suspended = models.BooleanField(verbose_name=u'Списывать периодическое услуги', help_text=u'Производить списывание денег по периодическим услугам', default=True)
    created=models.DateTimeField(verbose_name=u'Создан',auto_now_add=True, blank=True,null=True,default='')
    #NOTE: baLance
    ballance=models.DecimalField(u'Баланс', blank=True, default=0,decimal_places=10,max_digits=20)
    credit = models.DecimalField(verbose_name=u'Размер кредита',decimal_places=10,max_digits=20, help_text=u'Сумма, на которую данному пользователю можно работать в кредит', blank=True, default=0)
    disabled_by_limit = models.BooleanField(blank=True, default=False, editable=False)
    balance_blocked = models.BooleanField(blank=True, default=False)
    #ipn_speed = models.CharField(max_length=96, blank=True, default="")
    #vpn_speed = models.CharField(max_length=96, blank=True, default="")
    #netmask = models.IPAddressField(blank=True, default='0.0.0.0')
    #vlan = models.IntegerField()
    allow_webcab = models.BooleanField()
    allow_expresscards = models.BooleanField()
    #assign_dhcp_null = models.BooleanField()
    #assign_dhcp_block = models.BooleanField()
    #allow_vpn_null = models.BooleanField()
    #allow_vpn_block = models.BooleanField()
    passport = models.CharField(blank=True, max_length=64)
    passport_given = models.CharField(blank=True, max_length=64)
    phone_h = models.CharField(blank=True, max_length=64)
    phone_m = models.CharField(blank=True, max_length=64)
    contactperson_phone = models.CharField(blank=True, max_length=64)
    comment = models.TextField(blank=True)
    row = models.CharField(blank=True, max_length=6)
    elevator_direction = models.CharField(blank=True, max_length=128)
    contactperson = models.CharField(blank=True, max_length=256)
    passport_given = models.CharField(blank=True, null=True, max_length=128)
    contract = models.TextField(blank=True)
    systemuser = models.ForeignKey('SystemUser',blank=True,null=True)
    last_balance_null = models.DateTimeField(blank=True)
    entrance_code = models.CharField(blank=True, max_length=256)
    private_passport_number = models.CharField(blank=True, max_length=128)
    allow_ipn_with_null = models.BooleanField()
    allow_ipn_with_minus = models.BooleanField()
    allow_ipn_with_block = models.BooleanField()
    




    """
    assign_ip_from_dhcp - если стоит галочка-добавить в таблицу nas_ipleases свободную
    запись без времени старта из пула pool и выдавать ему адрес по DHCP. Время конца аренды прописано в пуле.

    Если выбран пул и указан IP - считать запись статической.
    Если выбран пул и не указан IP - назначать IP адрес из пула динамически

    После первой выдачи IP адреса клиенту - поставить дату старта.
    Для virtual_pool предлагать только пулы с service=vpn
    Для ipn_pool предлагать только пулы с service=ipn
    """

    def get_actual_ballance(self):
        return self.ballance+self.credit
    
    def ballance_isnt_good(self):
        if self.ballance+self.credit<=0:
            return True
        else:
            return False
    
    def account_status(self):
        if self.status==1:
            return True
        else: 
            return False    
    
    class Admin:
        ordering = ['user']
        #list_display = ('user', 'vpn_ip_address', 'ipn_ip_address', 'username', 'status', 'credit', 'ballance', 'firstname', 'lastname', 'created')
        #list_filter = ('username')

    def __str__(self):
        return '%s' % self.username

    class Meta:
        verbose_name = u"Аккаунт"
        verbose_name_plural = u"Аккаунты"
        
    @models.permalink
    def change_password_url_ajax(self):
        return ('billservice.views.change_password', (), {})

    def is_authenticated(self):
        """Always return True. This is a way to tell if the user has been authenticated in templates.
        """
        return True
    
    def get_account_tariff(self):
        tariff = Tariff.objects.extra(where=['id=get_tarif(%s)'], params=[self.id])[:1]
        return tariff[0]
    
    def get_account_tariff_info(self):
        tariff_info = Tariff.objects.extra(where=['id=get_tarif(%s)'], params=[self.id])[:1]
        for tariff in tariff_info:
            return [tariff.id, tariff.name,]
        
    def get_status(self):
        return dict(ACCOUNT_STATUS)[int(self.status)]


class Organization(models.Model):
    account = models.ForeignKey(Account)
    name = models.CharField(max_length=255)
    #rs = models.CharField(max_length=255)
    uraddress = models.CharField(max_length=255)
    okpo = models.CharField(max_length=255)
    unp = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    fax = models.CharField(max_length=255)
    bank = models.ForeignKey("BankData")


class TransactionType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    internal_name = models.CharField(max_length=32, unique=True)

    def __unicode__(self):
        return u"%s %s" % (self.name, self.internal_name)

    class Admin:
        pass

    class Meta:
        verbose_name = u"Тип проводки"
        verbose_name_plural = u"Типы проводок"
#===============================================================================


class Transaction(models.Model):
    bill = models.CharField(blank=True, default = "", max_length=255)
    account=models.ForeignKey(Account)
    type = models.ForeignKey(to=TransactionType, to_field='internal_name')
    
    approved = models.BooleanField(default=True)
    tarif=models.ForeignKey(Tariff, blank=True, null=True)
    summ=models.FloatField(default=0, blank=True)
    description = models.TextField(default='', blank=True)
    created=models.DateTimeField(auto_now_add=True, default='')
    promise=models.BooleanField(default=False) 
    end_promise=models.DateTimeField(auto_now_add=True, default='')
    promise_expired = models.BooleanField(default=False)
    systemuser=models.ForeignKey(to='SystemUser')


    class Admin:
        list_display=('account',  'tarif', 'summ', 'description', 'created')

    class Meta:
        verbose_name = u"Проводка"
        verbose_name_plural = u"Проводки"

    def human_sum(self):
        return self.summ*(-1)
    def __unicode__(self):
        return u"%s, %s, %s" % (self.account, self.tarif, self.created)

class AccountTarif(models.Model):
    account   = models.ForeignKey(verbose_name=u'Пользователь', to=Account, related_name='related_accounttarif')
    tarif     = models.ForeignKey(to=Tariff, verbose_name=u'Тарифный план', related_name="account_tarif")
    datetime  = models.DateTimeField(default='', blank=True)

    class Admin:
        ordering = ['-datetime']
        list_display = ('account','tarif','datetime')

    def __unicode__(self):
        return u"%s, %s" % (self.account, self.tarif)

    class Meta:
        verbose_name = u"привязка"
        verbose_name_plural = u"Привязки аккаунтов к тарифам"

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
        verbose_name = u"скорости IPN клиентов"
        verbose_name_plural = u"Скорости IPN клиентов"


#===============================================================================
# class RawNetFlowStream(models.Model):
#    nas = models.ForeignKey(Nas)
#    date_start = models.DateTimeField(auto_now_add=True, default='')
#    src_addr = models.IPAddressField()
#    traffic_class = models.ForeignKey(to=TrafficClass, related_name='rawnetflow_class', verbose_name=u'Направление трафика', blank=True, null=True)
#    direction = models.CharField(verbose_name=u"Тип трафика", choices=DIRECTIONS_LIST, max_length=32)
#    dst_addr = models.IPAddressField()
#    next_hop = models.IPAddressField()
#    in_index = models.IntegerField()
#    out_index = models.IntegerField()
#    packets = models.IntegerField()
#    octets = models.IntegerField()
#    src_port = models.IntegerField()
#    dst_port = models.IntegerField()
#    tcp_flags = models.IntegerField()
#    protocol = models.IntegerField()
#    tos = models.IntegerField()
#    source_as = models.IntegerField()
#    dst_as =  models.IntegerField()
#    src_netmask_length = models.IntegerField()
#    dst_netmask_length = models.IntegerField()
#    fetched=models.BooleanField(blank=True, default=False)
# 
#    class Admin:
#        ordering = ['-date_start']
#        list_display = ('nas', 'traffic_class','date_start','src_addr','dst_addr','next_hop','src_port','dst_port','octets')
# 
#    class Meta:
#        verbose_name = u"Сырая NetFlow статистика"
#        verbose_name_plural = u"Сырая NetFlow статистика"
# 
#    def __unicode__(self):
#        return u"%s" % self.nas
#    
#    def get_protocol(self):
#        print 
#===============================================================================

class NetFlowStream(models.Model):
    nas = models.ForeignKey(Nas, blank=True, null=True)
    account=models.ForeignKey(Account, related_name='account_netflow')
    tarif = models.ForeignKey(Tariff, related_name='tarif_netflow')
    date_start = models.DateTimeField(auto_now_add=True)
    src_addr = models.IPAddressField()
    traffic_class = models.ForeignKey(to=TrafficClass, related_name='netflow_class', verbose_name=u'Класс трафика', blank=True, null=True)
    direction = models.CharField(verbose_name=u"Направление трафика", choices=DIRECTIONS_LIST, max_length=32)
    traffic_transmit_node = models.ForeignKey(to=TrafficTransmitNodes, blank=True, null=True, editable=False)
    dst_addr = models.IPAddressField()
    octets = models.IntegerField()
    src_port = models.IntegerField()
    dst_port = models.IntegerField()
    protocol = models.IntegerField()
    checkouted = models.BooleanField(blank=True, default=False)
    for_checkout = models.BooleanField(blank=True, default=False)


    class Admin:
        ordering = ['-date_start']
        list_display = ('nas', 'account', 'tarif','traffic_class','date_start','src_addr','dst_addr','src_port','dst_port','octets')

    class Meta:
        verbose_name = u"NetFlow статистика"
        verbose_name_plural = u"NetFlow статистика"

    def __unicode__(self):
        return u"%s" % self.nas
    
    def get_protocol(self): 
        return PROTOCOLS[str(self.protocol)] 

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
        verbose_name = u"Периодическая операция"
        verbose_name_plural = u"Периодиеские операции"

class OneTimeServiceHistory(models.Model):
    accounttarif = models.ForeignKey(AccountTarif)
    onetimeservice = models.ForeignKey(OneTimeService)
    datetime = models.DateTimeField()
    
    class Admin:
        pass
    
    
"""
    Для SystemGroup есть 3 предопределенные группы
    ADMINISTRATORS - высший приоритет, видит тикеты суппорта и техников
    SUPPORT - средний преоритет, видит тикеты техников
    TECHNICS - минимальный приоритет, видит только свои тикеты
"""

class SystemGroup(models.Model):
    
    name = models.CharField(max_length=255)
    system = models.BooleanField(blank=True, default=False)
    system_name = models.CharField(max_length=255, blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' %self.name
    
    def get_users(self):
        return SystemUser.objects.filter(group=self)
    
    def get_tickets(self):
        from helpdesk.models import Ticket
        ctype = ContentType.objects.get_for_model(self)
        return Ticket.objects.filter(content_type=ctype, object_id=self.id, archived=False)
    
class SystemUser(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, default='')
    email = models.CharField(verbose_name=u'Фамилия', blank=True, default='',max_length=200)
    fullname = models.TextField()
    last_ip  = models.CharField(max_length=64, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, default='')
    created = models.DateTimeField(blank=True, null=True, default='')
    status = models.BooleanField(default=False)
    host = models.CharField(max_length=255, blank=True, null=True, default="0.0.0.0/0")
    group = models.ManyToManyField(SystemGroup)
    role = models.IntegerField()
    text_password = models.CharField(max_length=255)
    email = models.EmailField()

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

class Ports(models.Model):
    port = models.IntegerField()
    protocol = models.IntegerField()
    name = models.CharField(max_length=64, default='')
    description = models.CharField(max_length=255, default='')

class DocumentType(models.Model):
    name = models.CharField(max_length=255)
    
class TemplateType(models.Model):
    name = models.TextField()
        
class Template(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(DocumentType)
    body = models.TextField()    

class Card(models.Model):
    series = models.IntegerField()
    pin = models.CharField(max_length=255)
    sold = models.DateTimeField(blank=True, default=False)
    nominal = models.FloatField(default=0)
    activated = models.DateTimeField(blank=True, default=False)
    activated_by = models.ForeignKey(Account, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, default='')
    end_date = models.DateTimeField(blank=True, default='')
    disabled= models.BooleanField(default=False, blank=True)
    created = models.DateTimeField()
    template = models.ForeignKey(Template)
  
  
class BankData(models.Model):
    bank = models.CharField(max_length=255)
    bankcode = models.CharField(max_length=40)
    rs = models.CharField(max_length=60)
    currency = models.CharField(max_length=40)

    
class Operator(models.Model):
    organization = models.CharField(max_length=255)
    unp = models.CharField(max_length=40)
    okpo = models.CharField(max_length=40)
    contactperson = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    phone = models.CharField(max_length=40)
    fax = models.CharField(max_length=40)
    postaddress = models.CharField(max_length=255)
    uraddress = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    bank = models.ForeignKey(BankData)
    

class Dealer(models.Model):
    organization = models.CharField(max_length = 400)
    unp  = models.CharField(max_length = 255)
    okpo  = models.CharField(max_length = 255)
    contactperson  = models.CharField(max_length = 255)
    director  = models.CharField(max_length = 255)
    phone  = models.CharField(max_length = 255)
    fax  = models.CharField(max_length = 255)
    postaddress  = models.CharField(max_length = 400)
    uraddress  = models.CharField(max_length = 400)
    email = models.EmailField(max_length=255)
    prepayment = models.FloatField()
    paydeffer = models.IntegerField()
    discount = models.FloatField()
    always_sell_cards = models.BooleanField()
    
    bank = models.ForeignKey(BankData)
    deleted = models.BooleanField()
    

class SaleCard(models.Model):
    dealer = models.ForeignKey(Dealer)
    #pay = models.FloatField()
    sum_for_pay = models.FloatField()
    paydeffer = models.IntegerField()
    discount = models.FloatField()
    discount_sum = models.FloatField()
    prepayment = models.FloatField()
    cards = models.ManyToManyField(Card)
    created = models.DateTimeField()
    
class DealerPay(models.Model):
    dealer = models.ForeignKey(Dealer)
    pay = models.FloatField()
    salecard = models.ForeignKey(SaleCard, blank=True, null=True)
    created = models.DateTimeField()

    
class Document(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True)
    type = models.ForeignKey(DocumentType)
    body = models.TextField()

class SuspendedPeriod(models.Model):
    account = models.ForeignKey(Account)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    activated_by_account = models.BooleanField()
    
class Group(models.Model):
    #make it an array
    name = models.CharField(max_length=255)
    trafficclass = models.ManyToManyField(TrafficClass)
    #1 - in, 2-out, 3 - sum, 4-max
    direction = models.IntegerField()
    # 1 -sum, 2-max
    type = models.IntegerField()
    
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
    max_tx = models.IntegerField()
    max_rx = models.IntegerField()
    burst_tx = models.IntegerField()
    burst_rx = models.IntegerField()
    burst_treshold_tx = models.IntegerField()
    burst_treshold_rx = models.IntegerField()
    burst_time_tx = models.IntegerField()
    burst_time_rx = models.IntegerField()
    min_tx = models.IntegerField()
    min_rx = models.IntegerField()
    priority = models.IntegerField()
    
class AccountSpeedLimit(models.Model):
    account = models.ForeignKey(Account)
    speedlimit = models.ForeignKey(SpeedLimit)

class IPPool(models.Model):
    name = models.CharField(max_length=255)
    #0 - VPN, 1-IPN
    type = models.IntegerField()
    start_ip = models.IPAddressField()
    end_ip = models.IPAddressField()
    
class IPInUse(models.Model):
    pool = models.ForeignKey(IPPool)
    ip = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    

class TrafficTransaction(models.Model):
    traffictransmitservice = models.ForeignKey(TrafficTransmitService) # ON DELETE SET NULL
    account = models.ForeignKey(Account)
    summ = models.FloatField()
    datetime = models.DateTimeField()
    account = models.ForeignKey(Account)
    accounttarif = models.ForeignKey(AccountTarif)
    
    
class TPChangeRule(models.Model):
    from_tariff = models.ForeignKey(Tariff, related_name="from_tariff")
    to_tariff = models.ForeignKey(Tariff, related_name="to_tariff")
    disabled = models.BooleanField()
    cost = models.FloatField()
    ballance_min = models.FloatField()
    settlement_period = models.ForeignKey(SettlementPeriod, null=True)
    on_next_sp = models.BooleanField(default=False)
    
class RadiusAttrs(models.Model):
    tarif = models.ForeignKey(Tariff)
    vendor = models.IntegerField()
    attrid = models.IntegerField()
    value = models.CharField(max_length = 255)
    
class x8021(models.Model):    
    account = models.ForeignKey(Account, blank = True)    
    nas = models.ForeignKey(Nas)    
    port = models.SmallIntegerField()    
    typeauth = models.CharField(verbose_name=u"Способ авторизации", choices=AUTH_TYPES, max_length=32)    
    vlan_accept = models.IntegerField()    
    vlan_reject = models.IntegerField()    
    simpleauth = models.BooleanField()    

class AddonService(models.Model):    
    name = models.CharField(max_length=255)    
    comment = models.CharField(max_length=255, default='')
    allow_activation = models.BooleanField(default = False)    
    service_type = models.CharField(max_length=32, choices=((u"Разовая услуга","onetime"),(u"Периодическая услуга","periodical",),))    
    sp_type = models.CharField(max_length=32, choices=((u"В начале расчётного периода","AT_START"),(u"В конце расчётного периода","AT_END"),(u"На протяжении расчётного периода","GRADUAL"),))    
    sp_period = models.ForeignKey(SettlementPeriod, related_name="addonservice_spperiod")    
    timeperiod = models.ForeignKey(TimePeriod)    
    cost = models.DecimalField(decimal_places=10, max_digits=60)    
    cancel_subscription = models.BooleanField(default = True)    
    wyte_period = models.ForeignKey(SettlementPeriod, related_name="addonservice_wyteperiod")    
    wyte_cost = models.DecimalField(decimal_places=10, max_digits=60)    
    action = models.BooleanField()    
    nas = models.ForeignKey(Nas)    
    service_activation_action = models.CharField(max_length = 8000)    
    service_deactivation_action = models.CharField(max_length = 8000)    
    deactivate_service_for_blocked_account = models.BooleanField()    
    change_speed = models.BooleanField()    
    change_speed_type = models.CharField(max_length=32, choices=(("Add","add",), ("abs","abs",),))    
    speed_units = models.CharField(max_length = 32,choices=(("Kbps","Kbps",), ("Mbps","Mbps",),("%", "%",)))    
    max_tx = models.IntegerField()    
    max_rx = models.IntegerField()    
    burst_tx = models.IntegerField()    
    burst_rx = models.IntegerField()    
    burst_treshold_tx = models.IntegerField()    
    burst_treshold_rx = models.IntegerField()    
    burst_time_tx = models.IntegerField()    
    burst_time_rx = models.IntegerField()    
    min_tx = models.IntegerField()    
    min_rx = models.IntegerField()    
    priority = models.IntegerField()    

class AddonServiceTarif(models.Model):    
    tarif = models.ForeignKey(Tariff)    
    service = models.ForeignKey(AddonService)    
    activation_count = models.IntegerField()    
    activation_count_period = models.ForeignKey(SettlementPeriod)    
    type=models.IntegerField(default=0)# 0-Account, 1-Subaccount
    
class AccountAddonService(models.Model):    
    service = models.ForeignKey(AddonService)    
    account = models.ForeignKey(Account)   
    subaccount = models.ForeignKey('SubAccount',null=True) 
    activated = models.DateTimeField()    
    deactivated = models.DateTimeField()    
    action_status = models.BooleanField()    
    speed_status = models.BooleanField()        

class AddonServiceTransaction(models.Model):
    service = models.ForeignKey(AddonService)
    service_type = models.CharField(max_length=32)#onetime, periodical   
    account = models.ForeignKey(Account)
    accountaddonservice = models.ForeignKey(AccountAddonService)
    accounttarif = models.ForeignKey(AccountTarif)
    type = models.ForeignKey(TransactionType)
    summ = models.IntegerField()
    created = models.DateTimeField()
    
class AccountAttributes(models.Model):
    name = models.CharField(max_length=100)
    internal_name = models.SlugField(max_length=32 )
    type = models.CharField(max_length=20)#date, text, int, bool
    ordering = models.IntegerField()
    user_created = models.BooleanField()
    
class AccountAttributesData(models.Model):
    account = models.ForeignKey(Account)
    attribute = models.ForeignKey(AccountAttributes)
    value = models.CharField(max_length=1024)
    
class News(models.Model):
    body = models.TextField(u'Заголовок новости')
    age = models.DateTimeField()
    public = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    agent = models.BooleanField(default=False)
    created = models.DateTimeField()
    
class AccountViewedNews(models.Model):
    news = models.ForeignKey(News)
    account = models.ForeignKey(Account)
    viewed = models.BooleanField(default=False)
    
    
class Log(models.Model):
    systemuser = models.ForeignKey(SystemUser)
    text = models.TextField()
    created = models.DateTimeField()
    
class SubAccount(models.Model):
    account = models.ForeignKey(Account, related_name='subaccounts')
    username = models.CharField(max_length=512)
    password = models.CharField(max_length=512)
    ipn_ip_address = models.IPAddressField()
    ipn_mac_address = models.CharField(max_length=16)
    vpn_ip_address = models.IPAddressField()
    allow_mac_update = models.BooleanField(default=False)
    
class BalanceHistory(models.Model):
    account=models.ForeignKey(Account)
    balance = models.DecimalField(max_digits=30, decimal_places=20)
    datetime = models.DateTimeField()
    
class City(models.Model):
    name = models.CharField(max_length=320)

    def __unicode__(self):
        return u"%s" % self.name
class Street(models.Model):
    name = models.CharField(max_length=320)
    city= models.ForeignKey(City)
    def __unicode__(self):
        return u"%s" % self.name

class House(models.Model):
    name = models.CharField(max_length=320)
    street = models.ForeignKey(Street)
    def __unicode__(self):
        return u"%s" % self.name
    
class RadiusTraffic(models.Model):
    direction = models.IntegerField()
    tarification_step = models.IntegerField()
    rounding = models.IntegerField()
    prepaid_direction = models.IntegerField()
    prepaid_value = models.IntegerField()
    created = models.DateTimeField()
    deleted = models.DateTimeField()
    
class RadiusTrafficNode(models.Model):
    radiustraffic = models.ForeignKey(RadiusTraffic)
    value = models.DecimalField(max_digits=30, decimal_places=20)
    timeperiod = models.ForeignKey(TimePeriod)
    cost = models.DecimalField(max_digits=30, decimal_places=20)

class ContractTemplate(models.Model):
    template = models.TextField()

class Manufacturer(models.Model):
    name = models.TextField()

class Model(models.Model):
    name = models.TextField()

    
class Hardware(models.Model):
    manufacturer = models.ForeignKey(Manufacturer)
    model = models.ForeignKey(Model)
    name = models.CharField(max_length=500)
    sn = models.CharField(max_length=500)
    comment = models.TextField()#
    ipaddress = models.IPAddressField()
    macaddress = models.CharField(max_length=32)

class AccountHardware(models.Model):
    account=models.ForeignKey(Account)
    hardware = models.ForeignKey(Hardware)
    datetime = models.DateTimeField()
    returned = models.DateTimeField()
    comment = models.TextField()
    