#-*-coding=utf-8-*-
from django.db import models
from mikrobill.nas.models import Nas, TrafficClass, TrafficClass
from django.contrib.auth.models import User
import datetime, time


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

class TimePeriodNode(models.Model):
    """
    Диапазон времени ( с 15 00 до 18 00 каждую вторник-пятницу,утро, ночь, сутки, месяц, год и т.д.)
    """
    name = models.CharField(max_length=255, verbose_name=u'Название периода', default='', blank=True)
    time_start = models.DateTimeField(verbose_name=u'Дата и время начала периода', default='', blank=True)
    length = models.IntegerField(verbose_name=u'Период в секундах', default=0, blank=True)
    repeat_after = models.CharField(max_length=255, choices=PERIOD_CHOISES, verbose_name=u'Повторять через промежуток', default='MONTH', blank=True)

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
#    cash_times        = models.IntegerField(verbose_name=u'Количество снятий', blank=True, null=True)

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
    transaction = models.ForeignKey(to='Transaction')
    accounttarif = models.ForeignKey(to='AccountTarif')
    datetime  = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s" % (self.service)

    class Admin:
        ordering = ['-datetime']
        list_display = ('service','transaction','datetime')


    class Meta:
        verbose_name = u"История проводок по пер. услугам"
        verbose_name_plural = u"История проводок по пер. услугам"

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


class TimeAccessService(models.Model):
    """
    Доступ с тарификацией по времени
    """
    #name              = models.CharField(max_length=255, verbose_name=u'Название услуги', unuque=True)
    prepaid_time      = models.IntegerField(verbose_name=u'Предоплаченное время', default=0, blank=True)
    reset_time        = models.BooleanField(verbose_name=u'Сбрасывать в конце периода предоплаченное время', blank=True, default=False)

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
    cost                = models.FloatField(verbose_name=u'Стоимость за минуту в указанном промежутке', default=0)

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
    traffic_class    = models.ManyToManyField(to=TrafficClass, verbose_name=u'Класс трафика')
    in_direction     = models.BooleanField(default=True, blank=True)
    out_direction    = models.BooleanField(default=True, blank=True)
    transit_direction= models.BooleanField(default=True, blank=True)
    size             = models.FloatField(verbose_name=u'Размер в байтах', default=0,blank=True)

    def __unicode__(self):
        return u"%s %s" % (self.traffic_class, self.size)

    class Admin:
        ordering = ['traffic_class']
        list_display = ('size',)


    class Meta:
        verbose_name = u"Предоплаченный трафик"
        verbose_name_plural = u"Предоплаченный трафик"


class TrafficTransmitService(models.Model):
    #name              = models.CharField(max_length=255, default='', blank=True)
    reset_traffic     = models.BooleanField(verbose_name=u'Сбрасывать в конце периода предоплаченный трафик', blank=True, default=False)
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

    def __unicode__(self):
        return u"%s" % (self.prepaid_traffic)

    class Admin:
        pass

    class Meta:
        verbose_name = u"Предоплаченый трафик пользователя"
        verbose_name_plural = u"Предоплаченный трафик пользователя"

class AccountPrepaysTime(models.Model):
    account_tarif = models.ForeignKey(to="AccountTarif")
    prepaid_time_service = models.ForeignKey(to=TimeAccessService)
    size = models.IntegerField(default=0, blank=True)
    datetime = models.DateTimeField(auto_now_add=True, default='')

    class Admin:
        pass

    class Meta:
        verbose_name = u"Предоплаченное время пользователя"
        verbose_name_plural = u"Предоплаченное время пользователей"

class TrafficLimit(models.Model):
    tarif             = models.ForeignKey('Tariff')
    name              = models.CharField(max_length=255, verbose_name=u'Название лимита')
    settlement_period = models.ForeignKey(to=SettlementPeriod, verbose_name=u'Период', blank=True, null=True, help_text=u"Если период не указан-берётся период тарифного плана. Если установлен автостарт-началом периода будет считаться день привязки тарифного плана пользователю. Если не установлен-старт берётся из расчётного периода")
    #traffic_class     = models.ManyToManyField(to=TrafficClass, verbose_name=u'Лимит на класс', blank=True, null=True)
    size              = models.IntegerField(verbose_name=u'Размер в килобайтах', default=0)
    #in_direction      = models.BooleanField(default=True, blank=True)
    #out_direction     = models.BooleanField(default=True, blank=True)
    group             = models.ForeignKey("Group")
    mode              = models.BooleanField(default=False, blank=True, verbose_name=u'За последнюю длинну расчётного периода', help_text=u'Если флаг установлен-то количество трафика считается за последние N секунд, указанные в расчётном периоде')

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
    allow_express_pay = models.BooleanField(verbose_name=u'Оплата экспресс картами', blank=True, null=True, default=False)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','access_parameters','time_access_service','traffic_transmit_service','cost','settlement_period', 'ps_null_ballance_checkout')


    class Meta:
        verbose_name = u"Тариф"
        verbose_name_plural = u"Тарифы"

class Account(models.Model):
    """
    Если стоят галочки assign_vpn_ip_from_dhcp или assign_ipn_ip_from_dhcp,
    значит каждый раз при RADIUS запросе будет провереряться есть ли аренда и не истекла ли она.
    Если аренды нет или она истекла, то создаётся новая и пользователю назначается новый IP адрес.
    """
    #user = models.ForeignKey(User,verbose_name=u'Системный пользователь', related_name='user_account2')
    #agreement = models.ForeignKey('Document', blank=True, null=True)
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
    city = models.CharField(max_length=255)
    postcode = models.IntegerField()
    region = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=255)
    house_bulk = models.CharField(max_length=255)
    entrance = models.CharField(max_length=255)
    room = models.CharField(max_length=255)
    
    #assign_vpn_ip_from_dhcp = models.BooleanField(blank=True, default=False)
    nas = models.ForeignKey(to=Nas, blank=True, verbose_name=u'Сервер доступа')
    #vpn_pool = models.ForeignKey(to=IPAddressPool, related_name='virtual_pool', blank=True, null=True)
    vpn_ip_address = models.IPAddressField(u'Статический IP VPN адрес', help_text=u'Если не назначен-выбрать из пула, указанного в тарифном плане', blank=True, default='0.0.0.0')
    assign_ipn_ip_from_dhcp = models.BooleanField(blank=True, default=False)
    #ipn_pool = models.ForeignKey(to=IPAddressPool, related_name='ipn_pool', blank=True, null=True)
    ipn_ip_address = models.IPAddressField(u'IP адрес клиента', help_text=u'Для IPN тарифных планов', blank=True, default='0.0.0.0')
    ipn_mac_address = models.CharField(u'MAC адрес клиента', max_length=32, help_text=u'Для IPN тарифных планов', blank=True, default='')
    ipn_status = models.BooleanField(verbose_name=u"Статус на сервере доступа", default=False, blank=True)
    status=models.BooleanField(verbose_name=u'Статус пользователя', default=False)
    suspended = models.BooleanField(verbose_name=u'Списывать периодическое услуги', help_text=u'Производить списывание денег по периодическим услугам', default=True)
    created=models.DateTimeField(verbose_name=u'Создан',auto_now_add=True, default='')
    #NOTE: baLance
    ballance=models.FloatField(u'Баланс', blank=True, default=0)
    credit = models.FloatField(verbose_name=u'Размер кредита', help_text=u'Сумма, на которую данному пользователю можно работать в кредит', blank=True, default=0)
    disabled_by_limit = models.BooleanField(blank=True, default=False, editable=False)
    balance_blocked = models.BooleanField(blank=True, default=False)
    ipn_speed = models.CharField(max_length=96, blank=True, default="")
    vpn_speed = models.CharField(max_length=96, blank=True, default="")
    netmask = models.IPAddressField(blank=True, default='0.0.0.0')
    vlan = models.IntegerField()
    allow_webcab = models.BooleanField()
    allow_expresscards = models.BooleanField()
    assign_dhcp_null = models.BooleanField()
    assign_dhcp_block = models.BooleanField()
    allow_vpn_null = models.BooleanField()
    allow_vpn_block = models.BooleanField()
    




    """
    assign_ip_from_dhcp - если стоит галочка-добавить в таблицу nas_ipleases свободную
    запись без времени старта из пула pool и выдавать ему адрес по DHCP. Время конца аренды прописано в пуле.

    Если выбран пул и указан IP - считать запись статической.
    Если выбран пул и не указан IP - назначать IP адрес из пула динамически

    После первой выдачи IP адреса клиенту - поставить дату старта.
    Для virtual_pool предлагать только пулы с service=vpn
    Для ipn_pool предлагать только пулы с service=ipn
    """

    class Admin:
        ordering = ['user']
        #list_display = ('user', 'vpn_ip_address', 'ipn_ip_address', 'username', 'status', 'credit', 'ballance', 'firstname', 'lastname', 'created')
        #list_filter = ('username')

    def __str__(self):
        return '%s' % self.username

    class Meta:
        verbose_name = u"Аккаунт"
        verbose_name_plural = u"Аккаунты"

    def save(self):
        id=self.id
        #if self.assign_ip_from_dhcp and ipn_ip_address!='':

        super(Account, self).save()
        if not id and self.status=='Active':
            cost=0
            for ots in self.tarif.onetime_servies.all():
                cost+=ots.cost
            transaction=Transaction()
            transaction.approved=True
            transaction.account=self
            transaction.tarif=self.select_related().filter(accounttarif__account=self.id, accounttarif__datetimelte=datetime.datetime.now())[:1]
            transaction.summ = cost
            transaction.description = u'Снятие за первоначальную услугу'
            transaction.save()


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


    class Admin:
        list_display=('account',  'tarif', 'summ', 'description', 'created')

    class Meta:
        verbose_name = u"Проводка"
        verbose_name_plural = u"Проводки"

    def save(self):
        if self.approved!=False:
           self.account.ballance-=self.summ
           self.account.save()
           super(Transaction, self).save()

    def delete(self):
        self.account.ballance+=self.summ
        self.account.save()
        super(Transaction, self).delete()

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
    
class SystemUser(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, default='')
    last_ip  = models.CharField(max_length=64, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, default='')
    created = models.DateTimeField(blank=True, null=True, default='')
    status = models.BooleanField(default=False)
    host = models.CharField(max_length=255, blank=True, null=True, default="0.0.0.0/0")
    
class Ports(models.Model):
    port = models.IntegerField()
    protocol = models.IntegerField()
    name = models.CharField(max_length=64, default='')
    description = models.CharField(max_length=255, default='')
    

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
    template = models.CharField(max_length=255)
  
  
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


class DocumentType(models.Model):
    name = models.CharField(max_length=255)
    
class Template(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(DocumentType)
    body = models.TextField()
    
class Document(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True)
    type = models.ForeignKey(DocumentType)
    body = models.TextField()

class SuspendedPeriod(models.Model):
    account = models.ForeignKey(Account)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
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
    trafficclass = models.ForeignKey(TrafficClass, blank=True, null=True)
    
    
class GroupStatAll(models.Model):
    account = models.ForeignKey(Account)
    
[cl[[123][13123]],c2[[12]][2323]]

    
