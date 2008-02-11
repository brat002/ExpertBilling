#-*-coding=utf-8-*-
from django.db import models
from mikrobill.nas.models import Nas, TrafficClass, IPAddressPool, TrafficClass
from django.contrib.auth.models import User
import datetime, time


# Create your models here.
PERIOD_CHOISES=(
                ('NOT_REPEAT', 'Не повторять'),
                ('DAY','День'),
                ('WEEK','Неделя'),
                ('MONTH','Месяц'),
                ('QUARTER','Квартал'), # Не реализовано
                ('HALF_YEAR','Полугодие'), # Не реализовано
                ('YEAR','Год'),
                )

CASH_METHODS=(
                ('AT_START','В начале периода'),
                ('AT_END','В конце периода'),
                ('GRADUAL','В течении периода'),
                )

ACCESS_TYPE_METHODS=(
                ('IPN','IPN'),
                ('PPTP','PPTP'),
                ('PPPOE','PPPOE'),
                )

ACTIVITY_CHOISES=(
        ("Enabled","Enabled"),
        ("Disabled","Disabled"),
        )
        
class TimePeriodNode(models.Model):
    """
    Диапазон времени ( с 15 00 до 18 00 каждую вторник-пятницу,утро, ночь, сутки, месяц, год и т.д.)
    """
    name = models.CharField(max_length=255, verbose_name=u'Название периода')
    time_start = models.DateTimeField(verbose_name=u'Дата и время начала периода')
    length = models.IntegerField(verbose_name=u'Период в секундах')
    repeat_after = models.CharField(max_length=255, choices=PERIOD_CHOISES, verbose_name=u'Повторять через промежуток')
    
    def in_period(self):
        """
        Если повторение-год = проверяем месяц, число, время
        Если повтроение - полугодие = текущий месяц-начальный месяц по-модулю равно 6, совпадает число, время
        Если повтроение - квартал   = (текущий месяц - начальный месяц по модулю)/3=1, совпадает число, время
        Если повторение месяц - смотрим совпадает ли дата, время
        Если повторение неделя - смотрим совпадает ли день недели, время
        если повторение день - смотрим совпадает ли время
        =
        а=Текущее время - начальное время
        текущее_начальное_время_нач=начальное время+таймдельта(а[год],а[месяц],a[день])
        текущее_конечное_время =текущее_начальное_время_нач+таймдельта(self.length)
        если текущее время >текущее_начальное_время_нач И текущее время < текущее_конечное_время
             ок
        иначе
             вышел за рамки
        
        """
        now=datetime.datetime.now()

        if self.repeat_after=='DAY':
            delta_days=now - self.time_start
            #Когда будет начало в текущем периоде. 
            nums,ost= divmod(delta_days.seconds, 86400)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=self.length)
            if now>=tnc and now<=tkc:
                return True
            return False
        elif self.repeat_after=='WEEK':
            delta_days=now - self.time_start
            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.seconds, 604800)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=self.length)
            if now>=tnc and now<=tkc:
                return True
            return False
        elif self.repeat_after=='MONTH':
            #Февраль!
            tnc=datetime.datetime(now.year, now.month, self.time_start.day,self.time_start.hour,self.time_start.minute, self.time_start.second)
            tkc=tnc+datetime.timedelta(seconds=self.length)
            if now>=tnc and now<=tkc:
                return True
            return False
        elif self.repeat_after=='YEAR':
            #Февраль!
            tnc=datetime.datetime(now.year, self.time_start.month, self.time_start.day,self.time_start.hour,self.time_start.minute, self.time_start.second)
            tkc=tnc+datetime.timedelta(seconds=self.length)
            if now>=tnc and now<=tkc:
                return True
            return False
        
    def __unicode__(self):
        return u"%s" % self.name
    
    class Admin:
        ordering = ['name']
        list_display = ('name','time_start','length','repeat_after')

    
    class Meta:
        verbose_name = "Нода временного периода"
        verbose_name_plural = "Ноды временных периодов"


class TimePeriod(models.Model):
    name= models.CharField(max_length=255, verbose_name=u'Название группы временных периодов')
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
        verbose_name = "Временной период"
        verbose_name_plural = "Временные периоды"


    
class SettlementPeriod(models.Model):
    """
    Расчётный период
    """
    name = models.CharField(max_length=255, verbose_name=u'Название расчётного периода')
    time_start = models.DateTimeField(verbose_name=u'Дата и время начала периода')
    length = models.IntegerField(blank=True, default=0,verbose_name=u'Период действия в секундах')
    length_in = models.CharField(max_length=255, choices=PERIOD_CHOISES, blank=True, null=True, verbose_name=u'Длина промежутка')
    autostart = models.BooleanField(verbose_name=u'Начинать при активации', default=False)
    next_settlementtime = models.ForeignKey('SettlementPeriod', verbose_name=u'Следующий расчётный период', blank=True, null=True)

    """
    TO-DO: Сделать предустановленные пириоды :
    год (с учётом високосного)
    квартал
    месяц (с учётом 30,31,29 дней в феврале)
    неделя
    день
    """
    def __unicode__(self):
        return self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','time_start','length','length_in','autostart')


    class Meta:
        verbose_name = "Расчётный период"
        verbose_name_plural = "Расчётные периоды"

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
        return self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','settlement_period','cost','cash_method')


    class Meta:
        verbose_name = "Периодическая услуга"
        verbose_name_plural = "Периодические услуги"

class PeriodicalServiceHistory(models.Model):
    service = models.ForeignKey(to=PeriodicalService)
    #tarif   = models.ForeignKey(to='Tariff')
    transaction = models.ForeignKey(to='Transaction')
    #account = models.ForeignKey(to='Account')
    #summ    = models.FloatField()
    datetime  = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s" % (self.service)

    class Admin:
        ordering = ['-datetime']
        list_display = ('service','transaction','datetime')


    class Meta:
        verbose_name = "История проводок по периодическим услугам"
        verbose_name_plural = "История проводок по периодическим услугам"
    
class OneTimeService(models.Model):
    """
    Справочник разовых услуг
    TO-DO: Сделать справочники валют
    """
    name              = models.CharField(max_length=255, verbose_name=u'Название разовой услуги')
    cost              = models.FloatField(verbose_name=u'Стоимость разовой услуги', null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','cost')


    class Meta:
        verbose_name = "Разовый платеж"
        verbose_name_plural = "Разовые платежи"

    
class TimeAccessNode(models.Model):
    """
    Нода тарификации по времени
    """
    name              = models.CharField(max_length=255, verbose_name=u'Название промежутка')
    time_period       = models.ForeignKey(to=TimePeriod, verbose_name=u'Промежуток')
    cost              = models.FloatField(verbose_name=u'Стоимость за минуту в указанном промежутке')

    def __unicode__(self):
        return self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','time_period','cost')


    class Meta:
        verbose_name = "Период доступа"
        verbose_name_plural = "Периоды доступа"
    
class TimeAccessService(models.Model):
    """
    Доступ с тарификацией по времени
    """
    name              = models.CharField(max_length=255, verbose_name=u'Название услуги')
    time_periods      = models.ManyToManyField(to=TimeAccessNode, verbose_name=u'Промежутки')
    prepaid_time      = models.IntegerField(verbose_name=u'Предоплаченное время')

    def __unicode__(self):
        return self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','prepaid_time')


    class Meta:
        verbose_name = "Доступ с учётом времени"
        verbose_name_plural = "Доступ с учётом времени"
    
class AccessParameters(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название вида доступа')
    access_type       = models.CharField(max_length=255, choices=ACCESS_TYPE_METHODS, verbose_name=u'Вид доступа')
    ip_address_pool   = models.ForeignKey(to=IPAddressPool, verbose_name=u'Пул адресов', blank=True, null=True)
    nas               = models.ManyToManyField(to=Nas, blank=True, null=True, verbose_name=u'Сервер доступа')

    def __unicode__(self):
        return self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','access_type','ip_address_pool')


    class Meta:
        verbose_name = "Параметры доступа"
        verbose_name_plural = "Параметры доступа"
    
class PrepaidTraffic(models.Model):
    traffic_class    = models.ForeignKey(to=TrafficClass, verbose_name=u'Класс трафика')
    size             = models.FloatField(verbose_name=u'Размер')
    
    def __unicode__(self):
        return u"%s %s" % (self.traffic_class, self.size)

    class Admin:
        ordering = ['traffic_class']
        list_display = ('traffic_class','size')


    class Meta:
        verbose_name = "Предоплаченный трафик"
        verbose_name_plural = "Предоплаченный трафик"
    
class TrafficTransmitNodes(models.Model):
    traffic_class     = models.ForeignKey(to=TrafficClass, verbose_name=u'Класс трафика')
    time_period       = models.ManyToManyField(to=TimePeriod, verbose_name=u'Промежуток времени', blank=True, null=True)
    cost              = models.FloatField(verbose_name=u'Цена трафика')
    edge_start        = models.FloatField(verbose_name=u'Начальная граница')
    edge_end          = models.FloatField(verbose_name=u'Конечная граница')

    def __unicode__(self):
        return u"%s %s" % (self.traffic_class, self.cost)

    class Admin:
        ordering = ['traffic_class']
        list_display = ('traffic_class','cost','edge_start','edge_end')


    class Meta:
        pass

class TrafficTransmitService(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название услуги')
    traffic_nodes     = models.ManyToManyField(to=TrafficTransmitNodes, verbose_name=u'Цены за трафик')
    prepaid_traffic   = models.ManyToManyField(to=PrepaidTraffic, verbose_name=u'Предоплаченный трафик', blank=True, null=True)
    
    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name',)


    class Meta:
        verbose_name = "Доступ с учётом трафика"
        verbose_name_plural = "Доступ с учётом трафика"
    
class Tariff(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название тарифного плана')
    description          = models.TextField(verbose_name=u'Описание тарифного плана')
    access_type       = models.ForeignKey(to=AccessParameters, verbose_name=u'Параметры доступа')
    periodical_services = models.ManyToManyField(to=PeriodicalService, verbose_name=u'периодические услуги', blank=True, null=True)
    onetime_services     = models.ManyToManyField(to=OneTimeService, verbose_name=u'Разовые услуги', blank=True, null=True)
    time_access_service = models.ForeignKey(to=TimeAccessService, verbose_name=u'Доступ с учётом времени', blank=True, null=True)
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService, verbose_name=u'Доступ с учётом трафика', blank=True, null=True)
    cost              = models.FloatField(verbose_name=u'Стоимость активации тарифного плана', default=0.000 ,help_text=u"Если не указана-предоплаченный трафик и время не учитываются")
    settlement_period       = models.ForeignKey(to=SettlementPeriod, blank=True, null=True, verbose_name=u'Расчётный период')
    access_time       = models.ForeignKey(to=TimePeriod, verbose_name=u'Разрешённое время доступа')
    reset_time        = models.BooleanField(verbose_name=u'Сбрасывать в конце периода предоплаченное время')
    reset_traffic        = models.BooleanField(verbose_name=u'Сбрасывать в конце периода предоплаченный трафик')
    ps_null_ballance_checkout  = models.BooleanField(verbose_name=u'Производить снятие денег  при нулевом баллансе', help_text =u"Производить ли списывание денег по периодическим услугам при достижении нулевого балланса или исчерпании кредита?", blank=True, null=True, default=False )

    
    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        ordering = ['name']
        list_display = ('name','access_type','time_access_service','traffic_transmit_service','cost','settlement_period', 'access_time', 'ps_null_ballance_checkout')


    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"


class Account(models.Model):
    user=models.ForeignKey(User,verbose_name=u'Системный пользователь', related_name='user_account2')
    username=models.CharField(verbose_name=u'Имя пользователя',max_length=200,unique=True)
    password=models.CharField(verbose_name=u'Пароль',max_length=200)
    firstname=models.CharField(verbose_name=u'Имя',max_length=200)
    lastname=models.CharField(verbose_name=u'Фамилия',max_length=200)
    address=models.TextField(verbose_name=u'Домашний адрес')
#    tarif=models.ForeignKey(Tariff,verbose_name=u'Тарифный план')
    ipaddress=models.IPAddressField(u'IP адрес')
    status=models.CharField(verbose_name=u'Статус пользователя',max_length=200, choices=ACTIVITY_CHOISES,radio_admin=True, default='Enabled')
    suspended = models.BooleanField(verbose_name=u'Усыплён', help_text=u'Не производить списывание денег по периодическим услугам', default=False)
    #banned=models.CharField(verbose_name=u'Бан?',max_length=200, choices=ACTIVITY_CHOISES,radio_admin=True, default='Enabled')
    created=models.DateTimeField(verbose_name=u'Создан',auto_now_add=True)
    ballance=models.FloatField(u'Балланс', blank=True)
    credit = models.FloatField(verbose_name=u'Размер кредита', help_text=u'Сумма, на которую данному пользователю можно работать в кредит', blank=True, null=True, default=0)


    class Admin:
        ordering = ['user']
        list_display = ('user','username','status','credit','ballance','firstname','lastname','ipaddress', 'created')
        #list_filter = ('username')

    def __str__(self):
        return u'%s' % self.username
    
    class Meta:
        verbose_name = u"Аккаунт"
        verbose_name_plural = u"Аккаунты"
        
    def save(self):
        id=self.id
        super(Account, self).save()
        if id==None and self.status=='Active':
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


class Transaction(models.Model):
    account=models.ForeignKey(Account)
    approved = models.BooleanField(default=True)
    tarif=models.ForeignKey(Tariff)
    summ=models.FloatField(blank=True)
    description = models.TextField()
    created=models.DateTimeField(auto_now_add=True)

    class Admin:
        list_display=('account', 'tarif', 'summ', 'description','created')

    class Meta:
        pass

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
    account   = models.ForeignKey(to=Account, edit_inline=models.STACKED, num_in_admin=1)
    tarif     = models.ForeignKey(to=Tariff, verbose_name=u'Тарифный план', core=True)
    datetime  = models.DateTimeField()
    
    class Admin:
        ordering = ['-datetime']
        list_display = ('account','tarif','datetime')


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
        pass
    
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
    start = models.IntegerField()
    #sysuptime flow send
    finish = models.IntegerField()
    src_port = models.IntegerField()
    dst_port = models.IntegerField()
    tcp_flags = models.IntegerField()
    protocol = models.IntegerField()
    tos = models.IntegerField()
    source_as = models.IntegerField()
    dst_as =  models.IntegerField()
    src_netmask_length = models.IntegerField()
    dst_netmask_length = models.IntegerField()
    fetched=models.BooleanField(blank=True, null=True, default=False)



    class Admin:
          ordering = ['-date_start']
          list_display = ('nas', 'traffic_class','date_start','src_addr','dst_addr','next_hop','src_port','dst_port','octets','groups')

    class Meta:
        verbose_name = "Сырая NetFlow статистика"
        verbose_name_plural = "Сырая NetFlow статистика"

class NetFlowStream(models.Model):
    nas = models.ForeignKey(Nas, blank=True, null=True)
    account=models.ForeignKey(Account, related_name='account_netflow')
    tarif = models.ForeignKey(Tariff, related_name='tarif_netflow')
    date_start = models.DateTimeField(auto_now_add=True)
    src_addr = models.IPAddressField()
    traffic_class = models.ForeignKey(to=TrafficClass, related_name='netflow_class', verbose_name=u'Класс трафика', blank=True, null=True)
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
        verbose_name = "NetFlow статистика"
        verbose_name_plural = "NetFlow статистика"

