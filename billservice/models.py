#-*-coding=utf-8-*-
from django.db import models
from mikrobill.nas.models import Nas, TrafficClass, IPAddressPool, TrafficClass, IPAddressPool
from django.contrib.auth.models import User
import datetime, time


# Create your models here.
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

ACTIVITY_CHOISES=(
        (u"Enabled",u"Активен"),
        (u"Disabled",u"Неактивен"),
        )

CHOISE_METHODS=(
        (u"MAX",u"Наибольший"),
        (u"SUMM",u"Сумма всех"),
        )

COUNT_METHODS=(
        (u"INPUT",u"Входящий"),
        (u"OUTPUT",u"Исходящий"),
        (u"SUM",u"Входящий+Исходящий"),
        )


CHECK_PERIODS=(
        (u"SP_START",u"С начала расчётного периода"),
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

class TimePeriodNode(models.Model):
    """
    Диапазон времени ( с 15 00 до 18 00 каждую вторник-пятницу,утро, ночь, сутки, месяц, год и т.д.)
    """
    name = models.CharField(max_length=255, verbose_name=u'Название периода')
    time_start = models.DateTimeField(verbose_name=u'Дата и время начала периода')
    length = models.IntegerField(verbose_name=u'Период в секундах')
    repeat_after = models.CharField(max_length=255, choices=PERIOD_CHOISES, verbose_name=u'Повторять через промежуток')

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
    time_period_nodes = models.ManyToManyField(to=TimePeriodNode, filter_interface=models.HORIZONTAL, verbose_name=u'Группа временных периодов')

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
    name = models.CharField(max_length=255, verbose_name=u'Название расчётного периода')
    time_start = models.DateTimeField(verbose_name=u'Дата и время начала периода')
    length = models.IntegerField(blank=True, default=0,verbose_name=u'Период действия в секундах')
    length_in = models.CharField(max_length=255, choices=PERIOD_CHOISES, blank=True, null=True, verbose_name=u'Длина промежутка')
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
    name              = models.CharField(max_length=255, verbose_name=u'Название услуги')
    settlement_period = models.ForeignKey(to=SettlementPeriod, verbose_name=u'Период')
    cost              = models.FloatField(verbose_name=u'Стоимость услуги', null=True, blank=True)
    cash_method       = models.CharField(verbose_name=u'Способ снятия', max_length=255, choices=CASH_METHODS)
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
    name              = models.CharField(max_length=255, verbose_name=u'Название разовой услуги')
    cost              = models.FloatField(verbose_name=u'Стоимость разовой услуги', null=True, blank=True)

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
    name              = models.CharField(max_length=255, verbose_name=u'Название услуги')
    prepaid_time      = models.IntegerField(verbose_name=u'Предоплаченное время')
    reset_time        = models.BooleanField(verbose_name=u'Сбрасывать в конце периода предоплаченное время', blank=True, default=False)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','prepaid_time')


    class Meta:
        verbose_name = u"Доступ с учётом времени"
        verbose_name_plural = u"Доступ с учётом времени"

class TimeAccessNode(models.Model):
    """
    Нода тарификации по времени
    """
    time_access_service = models.ForeignKey(to=TimeAccessService, edit_inline=True, related_name="time_access_nodes")
    time_period         = models.ForeignKey(to=TimePeriodNode, verbose_name=u'Промежуток', core=True)
    cost                = models.FloatField(verbose_name=u'Стоимость за минуту в указанном промежутке', core=True)

    def __unicode__(self):
        return u"%s %s" % (self.time_period, self.cost)

    class Admin:
        ordering = ['name']
        list_display = ('time_period', 'cost')


    class Meta:
        verbose_name = u"Период доступа"
        verbose_name_plural = u"Периоды доступа"

class AccessParameters(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название вида доступа')
    access_type       = models.CharField(max_length=255, choices=ACCESS_TYPE_METHODS, verbose_name=u'Вид доступа')
    access_time       = models.ForeignKey(to=TimePeriod, verbose_name=u'Разрешённое время доступа')
    ip_address_pool   = models.ForeignKey(to=IPAddressPool, verbose_name=u'Пул адресов', blank=True, null=True)
    max_limit_in      = models.CharField(verbose_name=u"MAX IN (kbps)", max_length=64, blank=True, default=0)
    max_limit_out     = models.CharField(verbose_name=u"MAX OUT (kbps)", max_length=64, blank=True, default=0)
    min_limit_in      = models.CharField(verbose_name=u"MIN IN (kbps)", max_length=64, blank=True, default=0)
    min_limit_out     = models.CharField(verbose_name=u"MIN OUT (kbps)", max_length=64, blank=True, default=0)
    burst_limit_in    = models.CharField(verbose_name=u"Burst IN (kbps)", max_length=64, blank=True, default=0)
    burst_limit_out   = models.CharField(verbose_name=u"Burst OUT (kbps)", max_length=64, blank=True, default=0)
    burst_treshold_in    = models.CharField(verbose_name=u"Burst treshold IN (kbps)", max_length=64, blank=True, default=0)
    burst_treshold_out   = models.CharField(verbose_name=u"Burst treshold OUT (kbps)", max_length=64, blank=True, default=0)
    burst_time_in        = models.IntegerField(verbose_name=u"Burst Time in", blank=True, default=0)
    burst_time_out       = models.IntegerField(verbose_name=u"Burst Time out", blank=True, default=0)
    #от 1 до 8
    priority             = models.IntegerField(verbose_name=u"Приоритет", blank=True, default=8)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','access_type','ip_address_pool')


    class Meta:
        verbose_name = u"Параметры доступа"
        verbose_name_plural = u"Параметры доступа"

class TimeSpeed(models.Model):
    """
    Настройки скорости в интервал времени
    """
    access_parameters = models.ForeignKey(to=AccessParameters, edit_inline=True, related_name="access_speed")
    time = models.ForeignKey(TimePeriodNode, core=True)
    max_limit_in      = models.CharField(verbose_name=u"MAX IN (kbps)", max_length=64, blank=True, default=0)
    max_limit_out     = models.CharField(verbose_name=u"MAX OUT (kbps)", max_length=64, blank=True, default=0)
    min_limit_in      = models.CharField(verbose_name=u"MIN IN (kbps)", max_length=64, blank=True, default=0)
    min_limit_out     = models.CharField(verbose_name=u"MIN OUT (kbps)", max_length=64, blank=True, default=0)
    burst_limit_in    = models.CharField(verbose_name=u"Burst IN (kbps)", max_length=64, blank=True, default=0)
    burst_limit_out   = models.CharField(verbose_name=u"Burst OUT (kbps)", max_length=64, blank=True, default=0)
    burst_treshold_in    = models.CharField(verbose_name=u"Burst treshold IN (kbps)", max_length=64, blank=True, default=0)
    burst_treshold_out   = models.CharField(verbose_name=u"Burst treshold OUT (kbps)", max_length=64, blank=True, default=0)
    burst_time_in        = models.IntegerField(verbose_name=u"Burst Time in", blank=True, default=0)
    burst_time_out       = models.IntegerField(verbose_name=u"Burst Time out", blank=True, default=0)
    #от 1 до 8
    priority             = models.IntegerField(verbose_name=u"Приоритет", blank=True, default=8)

    def __unicode__(self):
        return u"%s %s/%s %s/%s %s/%s" % (self.time, self.max_limit_in, self.max_limit_out, self.min_limit_in, self.min_limit_out, self.burst_limit_in, self.burst_limit_out)

    class Admin:
        pass

    class Meta:
         verbose_name = u"настройка скорости"
         verbose_name_plural = u"Настройки скорости"

class PrepaidTraffic(models.Model):
    """
    Настройки предоплаченного трафика для тарифного плана
    """
    traffic_transmit_service = models.ForeignKey(to="TrafficTransmitService", edit_inline=True, verbose_name=u"Услуга доступа по трафику", related_name="prepaid_traffic")
    traffic_class    = models.ManyToManyField(to=TrafficClass, verbose_name=u'Класс трафика')
    size             = models.FloatField(verbose_name=u'Размер в байтах', core=True)

    def __unicode__(self):
        return u"%s %s" % (self.traffic_class, self.size)

    class Admin:
        ordering = ['traffic_class']
        list_display = ('size',)


    class Meta:
        verbose_name = u"Предоплаченный трафик"
        verbose_name_plural = u"Предоплаченный трафик"


class TrafficTransmitService(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название услуги')
    reset_traffic     = models.BooleanField(verbose_name=u'Сбрасывать в конце периода предоплаченный трафик')
    cash_method       = models.CharField(verbose_name=u"Списывать за класс трафика", max_length=32,choices=CHOISE_METHODS, default=u'SUMM', editable=False)
    period_check      = models.CharField(verbose_name=u"Проверять на наибольший ", max_length=32,choices=CHECK_PERIODS, default=u'SP_START', editable=False)
    count_method      = models.CharField(verbose_name=u"Снимать за", choices=COUNT_METHODS, max_length=32, default='SUM')


    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name',)


    class Meta:
        verbose_name = u"Доступ с учётом трафика"
        verbose_name_plural = u"Доступ с учётом трафика"

class TrafficTransmitNodes(models.Model):
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService, edit_inline=True, verbose_name=u"Услуга доступа по трафику", related_name="traffic_transmit_nodes")
    traffic_class     = models.ManyToManyField(to=TrafficClass, filter_interface=models.HORIZONTAL, verbose_name=u'Классы трафика')
    time_nodes        = models.ManyToManyField(to=TimePeriodNode, filter_interface=models.HORIZONTAL, verbose_name=u'Промежуток времени')
    cost              = models.FloatField(default=0, core=True, verbose_name=u'Цена трафика')
    edge_start        = models.FloatField(default=0,verbose_name=u'Начальная граница', help_text=u'Цена актуальна, если пользователь в текущем расчётном периоде наработал больше указанного количество байт')
    edge_end          = models.FloatField(default=0,verbose_name=u'Конечная граница', help_text=u'Цена актуальна, если пользователь в текущем расчётном периоде наработал меньше указанного количество байт')
    in_direction      = models.BooleanField()
    out_direction      = models.BooleanField()
    transit_direction      = models.BooleanField()
    
    def __unicode__(self):
        return u"%s" % (self.cost)

    class Admin:
        ordering = ['traffic_class']
        list_display = ('cost','edge_start','edge_end')


    class Meta:
        verbose_name = u"цена за направление"
        verbose_name_plural = u"Цены за направления трафика"


class AccountPrepays(models.Model):
    """
    При подключении пользователю тарифного плана, у которого есть предоплаченный трафик
    в таблице должны создаваться записи
    В начале каждого расчётного периода пользователю должен заново начисляться трафик
    """
    account_tarif = models.ForeignKey(to="AccountTarif")
    prepaid_traffic = models.ForeignKey(to=PrepaidTraffic)
    size = models.FloatField(blank=True, default=0.000)
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s-%s" % (self.account, self.prepaid_traffic)

    class Admin:
        pass

    class Meta:
        verbose_name = u"Предоплаченый трафик пользователя"
        verbose_name_plural = u"Предоплаченный трафик пользователя"

class AccountPrepaysTime(models.Model):
    account_tarif = models.ForeignKey(to="AccountTarif")
    prepaid_time_service = models.ForeignKey(to=TimeAccessService)
    size = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)

    class Admin:
        pass

    class Meta:
        verbose_name = u"Предоплаченное время пользователя"
        verbose_name_plural = u"Предоплаченное время пользователей"

class TrafficLimit(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название лимита')
    settlement_period = models.ForeignKey(to=SettlementPeriod, verbose_name=u'Период', blank=True, null=True, help_text=u"Если период не указан-берётся период тарифного плана. Если установлен автостарт-началом периода будет считаться день привязки тарифного плана пользователю. Если не установлен-старт берётся из расчётного периода")
    traffic_class     = models.ManyToManyField(to=TrafficClass, filter_interface=models.HORIZONTAL, verbose_name=u'Лимит на класс', blank=True, null=True)
    size              = models.IntegerField(verbose_name=u'Размер в килобайтах', default=0)
    mode              = models.BooleanField(verbose_name=u'За последнюю длинну расчётного периода', help_text=u'Если флаг установлен-то количество трафика считается за последние N секунд, указанные в расчётном периоде')

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name', 'settlement_period')


    class Meta:
        verbose_name = u"лимит трафика"
        verbose_name_plural = u"Лимиты трафика"

class Tariff(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название тарифного плана')
    description       = models.TextField(verbose_name=u'Описание тарифного плана')
    access_parameters = models.ForeignKey(to=AccessParameters, verbose_name=u'Параметры доступа')
    traffic_limit     = models.ManyToManyField(to=TrafficLimit, filter_interface=models.HORIZONTAL,verbose_name=u'Лимиты трафика', blank=True, null=True, help_text=u"Примеры: 200 мегабайт в расчётный период, 50 мегабайт за последнюю неделю")
    periodical_services = models.ManyToManyField(to=PeriodicalService, filter_interface=models.HORIZONTAL, verbose_name=u'периодические услуги', blank=True, null=True)
    onetime_services  = models.ManyToManyField(to=OneTimeService, filter_interface=models.HORIZONTAL,verbose_name=u'Разовые услуги', blank=True, null=True)
    time_access_service = models.ForeignKey(to=TimeAccessService, verbose_name=u'Доступ с учётом времени', blank=True, null=True)
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService, verbose_name=u'Доступ с учётом трафика', blank=True, null=True)
    cost              = models.FloatField(verbose_name=u'Стоимость пакета', default=0.000 ,help_text=u"Стоимость активации тарифного плана. Целесообразно указать с расчётным периодом. Если не указана-предоплаченный трафик и время не учитываются")
    reset_tarif_cost  = models.BooleanField(verbose_name=u'Производить доснятие', blank=True, null=True, default=False, help_text=u'Производить доснятие суммы до стоимости тарифного плана в конце расчётного периода')
    settlement_period = models.ForeignKey(to=SettlementPeriod, blank=True, null=True, verbose_name=u'Расчётный период')
    ps_null_ballance_checkout = models.BooleanField(verbose_name=u'Производить снятие денег  при нулевом баллансе', help_text =u"Производить ли списывание денег по периодическим услугам при достижении нулевого балланса или исчерпании кредита?", blank=True, null=True, default=False )


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
    user = models.ForeignKey(User,verbose_name=u'Системный пользователь', related_name='user_account2')
    username = models.CharField(verbose_name=u'Имя пользователя',max_length=200,unique=True)
    password = models.CharField(verbose_name=u'Пароль',max_length=200)
    firstname = models.CharField(verbose_name=u'Имя', blank=True, default='', max_length=200)
    lastname = models.CharField(verbose_name=u'Фамилия', blank=True, default='',max_length=200)
    address = models.TextField(verbose_name=u'Домашний адрес', blank=True, default='')
    assign_vpn_ip_from_dhcp = models.BooleanField(default=False)
    nas = models.ForeignKey(to=Nas, blank=True, null=True, verbose_name=u'Сервер доступа')
    vpn_pool = models.ForeignKey(to=IPAddressPool, related_name='virtual_pool', blank=True, null=True)
    vpn_ip_address = models.IPAddressField(u'Статический IP VPN адрес', help_text=u'Если не назначен-выбрать из пула, указанного в тарифном плане', blank=True, null=True)
    assign_ipn_ip_from_dhcp = models.BooleanField(blank=True, default=False)
    ipn_pool = models.ForeignKey(to=IPAddressPool, related_name='ipn_pool', blank=True, null=True)
    ipn_ip_address = models.IPAddressField(u'IP адрес клиента', help_text=u'Для IPN тарифных планов', blank=True, null=True)
    ipn_mac_address = models.CharField(u'MAC адрес клиента', max_length=32, help_text=u'Для IPN тарифных планов', blank=True, null=True)
    ipn_status = models.BooleanField(verbose_name=u"Статус на сервере доступа", default=False, blank=True)
    status=models.BooleanField(verbose_name=u'Статус пользователя', radio_admin=True, default=False)
    suspended = models.BooleanField(verbose_name=u'Списывать периодическое услуги', help_text=u'Производить списывание денег по периодическим услугам', default=True)
    created=models.DateTimeField(verbose_name=u'Создан',auto_now_add=True)
    ballance=models.FloatField(u'Балланс', blank=True)
    credit = models.FloatField(verbose_name=u'Размер кредита', help_text=u'Сумма, на которую данному пользователю можно работать в кредит', blank=True, null=True, default=0)
    disabled_by_limit = models.BooleanField(blank=True, default=False, editable=False)




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
        list_display = ('user', 'vpn_ip_address', 'ipn_ip_address', 'username', 'status', 'credit', 'ballance', 'firstname', 'lastname', 'created')
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


class TransactionType(models.Model):
    name = models.CharField(max_length=255)
    internal_name = models.CharField(max_length=32, unique=True)

    def __unicode__(self):
        return u"%s %s" % (self.name, self.internal_name)

    class Admin:
        pass

    class Meta:
        verbose_name = u"тип проводки"
        verbose_name_plural = u"Типы проводок"
#===============================================================================


class Transaction(models.Model):
    account=models.ForeignKey(Account)
    type = models.ForeignKey(to=TransactionType, to_field='internal_name')
    approved = models.BooleanField(default=True)
    tarif=models.ForeignKey(Tariff)
    summ=models.FloatField(blank=True)
    description = models.TextField()
    created=models.DateTimeField(auto_now_add=True)


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
    account   = models.ForeignKey(verbose_name=u'Пользователь', to=Account, blank=True, null=True, edit_inline=models.STACKED, num_in_admin=1)
    tarif     = models.ForeignKey(to=Tariff, verbose_name=u'Тарифный план', core=True)
    datetime  = models.DateTimeField()

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
      speed   = models.CharField(max_length=32)
      state   = models.BooleanField(blank=True, default=False)
      static  = models.BooleanField(verbose_name=u"Статическая скорость", help_text=u"Пока опция установлена, биллинг не будет менять для этого клиента скорость", blank=True, null=True)
      datetime  = models.DateTimeField()

      def __unicode__(self):
          return u"%s %s" % (self.account, self.speed)

      class Admin:
          pass

      class Meta:
        verbose_name = u"скорости IPN клиентов"
        verbose_name_plural = u"Скорости IPN клиентов"


class SummaryTrafic(models.Model):
    """
    Класс предназначен для ведения статистики по трафику, потреблённому пользователями
    """

    account = models.ForeignKey('Account', blank=True, null=True, related_name='account_trafic')
    incomming_bytes = models.PositiveIntegerField(blank=True, null=True)
    outgoing_bytes = models.PositiveIntegerField(blank=True, null=True)
    radius_session = models.CharField(max_length=32)
    nas_id = models.IPAddressField()
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(blank=True, null=True)

    class Admin:
        ordering = ['-date_end']
        list_display = ('account',  'incomming_bytes',  'outgoing_bytes', 'date_start', 'date_end')

    class Meta:
        verbose_name = u"Общий трафик по RADIUS сессиям"
        verbose_name_plural = u"Общий трафик по RADIUS сессиям"

    def __unicode__(self):
        return u'%s' % self.account


class RawNetFlowStream(models.Model):
    nas = models.ForeignKey(Nas, blank=True, null=True)
    date_start = models.DateTimeField(auto_now_add=True)
    groups = models.IntegerField(default=0, null=True, blank=True)
    src_addr = models.IPAddressField()
    traffic_class = models.ForeignKey(to=TrafficClass, related_name='rawnetflow_class', verbose_name=u'Класс трафика', blank=True, null=True)
    dst_addr = models.IPAddressField()
    next_hop = models.IPAddressField()
    in_index = models.IntegerField()
    out_index = models.IntegerField()
    packets = models.IntegerField()
    octets = models.IntegerField()
    #sysuptime start flow aggregate
    start = models.PositiveIntegerField()
    #sysuptime flow send
    finish = models.PositiveIntegerField()
    src_port = models.IntegerField()
    dst_port = models.IntegerField()
    tcp_flags = models.IntegerField()
    protocol = models.IntegerField()
    tos = models.IntegerField()
    source_as = models.IntegerField()
    dst_as =  models.IntegerField()
    src_netmask_length = models.IntegerField()
    dst_netmask_length = models.IntegerField()
    fetched=models.BooleanField(blank=True, default=False)

    class Admin:
          ordering = ['-date_start']
          list_display = ('nas', 'traffic_class','date_start','src_addr','dst_addr','next_hop','src_port','dst_port','octets','groups')

    class Meta:
        verbose_name = u"Сырая NetFlow статистика"
        verbose_name_plural = u"Сырая NetFlow статистика"

    def __unicode__(self):
        return u"%s" % self.nas

class NetFlowStream(models.Model):
    nas = models.ForeignKey(Nas, blank=True, null=True)
    account=models.ForeignKey(Account, related_name='account_netflow')
    tarif = models.ForeignKey(Tariff, related_name='tarif_netflow')
    date_start = models.DateTimeField(auto_now_add=True)
    src_addr = models.IPAddressField()
    traffic_class = models.ForeignKey(to=TrafficClass, related_name='netflow_class', verbose_name=u'Класс трафика', blank=True, null=True)
    traffic_transmit_node = models.ForeignKey(to=TrafficTransmitNodes, blank=True, null=True, editable=False)
    dst_addr = models.IPAddressField()
    octets = models.IntegerField()
    src_port = models.IntegerField()
    dst_port = models.IntegerField()
    protocol = models.IntegerField()
    checkouted = models.BooleanField(blank=True, null=True, default=False)
    for_checkout = models.BooleanField(blank=True, null=True, default=False)


    class Admin:
          ordering = ['-date_start']
          list_display = ('nas', 'account', 'tarif','traffic_class','date_start','src_addr','dst_addr','src_port','dst_port','octets')

    class Meta:
        verbose_name = u"NetFlow статистика"
        verbose_name_plural = u"NetFlow статистика"

    def __unicode__(self):
        return u"%s" % self.nas

class SheduleLog(models.Model):
    account = models.ForeignKey(to=Account, unique=True)
    ballance_checkout = models.DateTimeField(blank=True, null=True)
    prepaid_traffic_reset = models.DateTimeField(blank=True, null=True)
    prepaid_time_reset = models.DateTimeField(blank=True, null=True)

    class Admin:
        pass

    class Meta:
        verbose_name = u"Периодическая операция"
        verbose_name_plural = u"Периодиеские операции"

