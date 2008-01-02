#-*-coding=utf-8-*-
from django.db import models
from mikrobill.nas.models import Nas, TrafficClass, IPAddressPool
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
        return self.name
    
    class Admin:
        pass
    
    class Meta:
        pass

class TimePeriod(models.Model):
    name= models.CharField(max_length=255, verbose_name=u'Название группы временных периодов')
    time_period_nodes = models.ManyToManyField(to=TimePeriodNode, verbose_name=u'Группа временных периодов')

    def in_period(self):
        for time_period_node in self.time_period_nodes:
            if time_period_node.in_period()==True:
                return True
        return False
    
    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        pass


    
class SettlementPeriod(models.Model):
    """
    Расчётный период
    """
    name = models.CharField(max_length=255, verbose_name=u'Название расчётного периода')
    time_start = models.DateTimeField(verbose_name=u'Дата и время начала периода')
    length = models.IntegerField(verbose_name=u'Период действия в секундах')
    length_in = models.CharField(max_length=255, choices=PERIOD_CHOISES, blank=True, null=True, verbose_name=u'Повторять через промежуток')
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
        pass

    class Meta:
        pass

class PeriodicalService(models.Model):
    """
    Справочник периодических услуг
    TO-DO: Сделать справочники валют
    """
    name              = models.CharField(max_length=255, verbose_name=u'Название услуги')
#    settlement_period = models.ForeignKey(to=SettlementPeriod, verbose_name=u'Период')
    cost              = models.FloatField(verbose_name=u'Стоимость услуги', null=True, blank=True)
    cash_method       = models.CharField(verbose_name=u'Способ снятия', max_length=255, choices=CASH_METHODS)
    cash_times        = models.IntegerField(verbose_name=u'Количество снятий', blank=True, null=True)
    
    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        pass

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
        pass

    class Meta:
        pass

class TimeAccessNode(models.Model):
    """
    Нода тарификации по времени
    """
    name              = models.CharField(max_length=255, verbose_name=u'Название промежутка')
    time_period       = models.ForeignKey(to=TimePeriod, verbose_name=u'Промежуток')
    cost              = models.FloatField(verbose_name=u'Стоимость за секунду в указанном промежутке')

    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        pass
    
class TimeAccessService(models.Model):
    """
    Доступ с тарификацией по времени
    """
    name              = models.CharField(max_length=255, verbose_name=u'Название промежутка')
    time_periods      = models.ManyToManyField(to=TimeAccessNode, verbose_name=u'Промежутки')
    prepaid_time      = models.IntegerField(verbose_name=u'Предоплаченное время')

    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        pass
    
class AccessParameters(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название вида доступа')
    access_type       = models.CharField(max_length=255, choices=ACCESS_TYPE_METHODS, verbose_name=u'Вид доступа')
    ip_address_pool   = models.ForeignKey(to=IPAddressPool, verbose_name=u'Пул адресов', blank=True, null=True)
    nas               = models.ManyToManyField(to=Nas, blank=True, null=True, verbose_name=u'Сервер доступа')

    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        pass
    
class PrepaidTraffic(models.Model):
    traffic_class    = models.ForeignKey(to=TrafficClass, verbose_name=u'Класс трафика')
    size             = models.FloatField(verbose_name=u'Размер')
    
    def __unicode__(self):
        return "%s %s" % (self.traffic_class, self.size)

    class Admin:
        pass

    class Meta:
        pass
    
class TrafficTransmitNodes(models.Model):
    traffic_class     = models.ForeignKey(to=TrafficClass, verbose_name=u'Класс трафика')
    time_period       = models.ManyToManyField(to=TimePeriod, verbose_name=u'Промежуток времени', blank=True, null=True)
    cost              = models.FloatField(verbose_name=u'Цена трафика')
    edge_start        = models.FloatField(verbose_name=u'Начальная граница')
    edge_end          = models.FloatField(verbose_name=u'Конечная граница')

    def __unicode__(self):
        return u"%s %s" % (self.traffic_class, self.cost)

    class Admin:
        pass

    class Meta:
        pass

class TrafficTransmitService(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название услуги')
    traffic_nodes     = models.ManyToManyField(to=TrafficTransmitNodes, verbose_name=u'Цены за трафик')
    prepaid_traffic   = models.ManyToManyField(to=PrepaidTraffic, verbose_name=u'Предоплаченный трафик', blank=True, null=True)
    
    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        pass
    
class Tariff(models.Model):
    name              = models.CharField(max_length=255, verbose_name=u'Название тарифного плана')
    access_type       = models.ForeignKey(to=AccessParameters, verbose_name=u'Параметры доступа')
    periodical_services = models.ManyToManyField(to=PeriodicalService, verbose_name=u'периодические услуги', blank=True, null=True)
    onetime_servies     = models.ManyToManyField(to=OneTimeService, verbose_name=u'Разовые услуги', blank=True, null=True)
    time_access_service = models.ForeignKey(to=TimeAccessService, verbose_name=u'Доступ с учётом времени', blank=True, null=True)
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService, verbose_name=u'Доступ с учётом трафика', blank=True, null=True)
    cost              = models.FloatField(verbose_name=u'Стоимость активации тарифного плана', default=0.000 ,help_text=u"Если не указана-предоплаченный трафик и время не учитываются")
    settlement_period       = models.ForeignKey(to=SettlementPeriod, verbose_name=u'Расчётный период')
    access_time       = models.ForeignKey(to=TimePeriod, verbose_name=u'Разрешённое время доступа')
    reset_time        = models.BooleanField(verbose_name=u'Сбрасывать в конце периода предоплаченное время')
    reset_traffic        = models.BooleanField(verbose_name=u'Сбрасывать в конце периода предоплаченный трафик')
    
    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        pass

class Account(models.Model):
    user=models.ForeignKey(User,verbose_name='Системный пользователь', related_name='user_account2')
    username=models.CharField(verbose_name='Имя пользователя',max_length=200,unique=True)
    password=models.CharField(verbose_name='Пароль',max_length=200)
    firstname=models.CharField(verbose_name='Имя',max_length=200)
    lastname=models.CharField(verbose_name='Фамилия',max_length=200)
    address=models.TextField(verbose_name='Домашний адрес')
    tarif=models.ForeignKey(Tariff,verbose_name='Тарифный план')
    ipaddress=models.IPAddressField(u'IP адрес')
    status=models.CharField(verbose_name='Статус пользователя',max_length=200, choices=ACTIVITY_CHOISES,radio_admin=True, default='Enabled')
    banned=models.CharField(verbose_name='Бан?',max_length=200, choices=ACTIVITY_CHOISES,radio_admin=True, default='Enabled')
    created=models.DateTimeField(verbose_name='Создан',auto_now_add=True)
    ballance=models.FloatField('Балланс', blank=True)



    class Admin:
        ordering = ['user']
        list_display = ('user','username','status','banned','ballance','firstname','lastname','ipaddress','tarif','tarif', 'created')
        #list_filter = ('username')

    def __str__(self):
        return u'%s' % self.username
