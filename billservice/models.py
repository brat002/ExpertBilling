#-*-coding=utf-8-*-
from django.db import models
from mikrobill.nas.models import Nas, TrafficClass

# Create your models here.
PERIOD_CHOISES=(
                ('DAY','День'),
                ('WEEKDAY','Неделя'),
                ('MONTH','Месяц'),
                ('QUARTER','Квартал'),
                ('HALF_YEAR','Полугодие'),
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
                
class TimePeriodNode(models.Model):
    """
    Диапазон времени ( с 15 00 до 18 00 каждую вторник-пятницу,утро, ночь, сутки, месяц, год и т.д.)
    """
    name = models.CharField(max_length=255, verbose_name=u'Название периода')
    time_start = models.DateTimeField(verbose_name=u'Дата и время начала периода')
    length = models.IntegerField(verbose_name=u'Период в секундах')
    repeat_after = models.CharField(max_length=255, choices=PERIOD_CHOISES, verbose_name=u'Повторять через промежуток')
    
    def __unicode__(self):
        return self.name
    
    class Admin:
        pass
    
    class Meta:
        pass

class TimePeriod(models.Model):
    name= models.CharField(max_length=255, verbose_name=u'Название группы временных периодов')
    time_period_nodes = models.ManyToManyField(to=TimePeriodNode, verbose_name=u'Группа временных периодов')

    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        pass

class IPAddressPool(models.Model):
    name     = models.CharField(max_length=255, verbose_name=u'Имя пула')
    start_IP = models.IPAddressField(verbose_name=u'Начальный адрес')
    end_IP   = models.IPAddressField(verbose_name=u'Конечный адрес')

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
    access_time       = models.ManyToManyField(to=TimePeriod, verbose_name=u'Разрешённое время доступа')

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
        return "%s %s" % (self.traffic_class, self.cost)

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
    
    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        pass