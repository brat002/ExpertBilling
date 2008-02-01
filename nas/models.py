#-*-coding=utf-8-*-

from django.db import models
#import mikrobill.billservice.models

# Create your models here.

class Nas(models.Model):
    name = models.CharField(verbose_name=u'Имя сервера доступа', help_text=u"Используется дли идентификации сервера доступа. Смотрите настройки /system identity print", max_length=255, unique=True)
    ipaddress = models.CharField(verbose_name=u'IP адрес сервера доступа', max_length=255)
    secret = models.CharField(verbose_name=u'Секретная фраза', help_text=u"Смотрите вывод команды /radius print", max_length=255)
    login = models.CharField(verbose_name=u'Имя для доступа к серверу по SSH', max_length=255)
    password = models.CharField(verbose_name=u'Пароль для доступа к серверу по SSH', max_length=255)
    description = models.TextField(verbose_name=u'Описание', blank=True, null=True)
    allow_pptp = models.BooleanField(verbose_name=u'Разрешить серверу работать с PPTP', default=True)
    allow_pppoe = models.BooleanField(verbose_name=u'Разрешить серверу работать с PPPOE', default=True)
    allow_ipn = models.BooleanField(verbose_name=u'Сервер поддерживает IPN', help_text=u"IPN - технология, которая позволяет предоставлять доступ в интернет без установления VPN соединения с сервером доступа", blank=True, null=True, default=True)
    user_add_action = models.TextField(verbose_name=u'Действие при создании пользователя',blank=True, null=True)
    user_enable_action = models.TextField(verbose_name=u'Действие при разрешении работы пользователя',blank=True, null=True)
    user_disable_action = models.TextField(verbose_name=u'Действие при запрещении работы пользователя',blank=True, null=True)
    user_delete_action = models.TextField(verbose_name=u'Действие при удалении пользователя',blank=True, null=True)
    support_pod = models.BooleanField(verbose_name=u'Сервер поддерживает PoD', help_text=u"Технология, позволяющая сбрасывать пользователя с линии средствами RADIUS. Подробно описана в RFC 3576", blank=True, null=True, default=True)
    suport_cao = models.BooleanField(verbose_name=u'Сервер поддерживает CoA', help_text=u"Технология, позволяющая менять клиенту скорость или другие параметры без обрыва сессии. Подробно описана в RFC 3576", blank=True, null=True, default=True)
    configure_nas = models.BooleanField(verbose_name=u'Произвести начальное конфигурирование сервера доступа?',help_text=u"На сервере доступа будет настроен RADIUS клиент, включен PPTP")


    def save(self):
        if self.configure_nas==True:
            self.configure_nas=False
            pass
        super(Nas, self).save()
    class Admin:
          ordering = ['-name']
          list_display = ('name','ipaddress','description')

    class Meta:
        verbose_name = "Сервер доступа"
        verbose_name_plural = "Сервера доступа"
    
    def __str__(self):
        return self.name

class Collector(models.Model):
    name=models.CharField(max_length=255)
    ipaddress = models.IPAddressField(verbose_name=u'IP адресов коллектора')
    description = models.TextField(verbose_name=u'Описание', blank=True)
    version=models.IntegerField(verbose_name=u'Версия протокола NetFLow')
    
    class Admin:
          ordering = ['-name']
          list_display = ('name','ipaddress','description')

    class Meta:
        verbose_name = "NetFlow коллектор"
        verbose_name_plural = "NetFlow коллекторы"
    
class NetFlowStream(models.Model):
    collector = models.ForeignKey(Collector)
    date_start = models.DateTimeField(auto_now_add=True)
    groups = models.IntegerField(default=0, null=True, blank=True)
    src_addr = models.IPAddressField()
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

        
    
    class Admin:
          ordering = ['-date_start']
          list_display = ('collector','date_start','src_addr','dst_addr','next_hop','src_port','dst_port','octets','groups')

    class Meta:
        verbose_name = "Поток NetFlow"
        verbose_name_plural = "Собранная NetFlow статистика"
        
class TrafficNode(models.Model):
    name = models.CharField(verbose_name=u'Название класса', max_length=255)
    src_ip_from  = models.IPAddressField(verbose_name=u'От адреса источника', default='0.0.0.0')
    src_ip_to  = models.IPAddressField(verbose_name=u'До адреса источника', default='0.0.0.0')
    src_port  = models.IntegerField(verbose_name=u'Порт источника', default=0)
    
    dst_ip_from = models.IPAddressField(verbose_name=u'От адреса получателя', default='0.0.0.0')
    dst_ip_to = models.IPAddressField(verbose_name=u'До адреса получателя', default='0.0.0.0')
    dst_port  = models.IntegerField(verbose_name=u'Порт получетеля', default=0)
    
    next_hop = models.IPAddressField(verbose_name=u'Направление пакета (IP address)', default='0.0.0.0')
    
    def __unicode__(self):
        return u"%s" % self.name
        
    class Admin:
        pass

    class Meta:
        verbose_name = "Направление трафика"
        verbose_name_plural = "Направления трафика"
        
class TrafficClass(models.Model):
    name = models.CharField(verbose_name=u'Навзание класса', max_length=255)
    weight = models.IntegerField(verbose_name=u'Вес класа в цепочке классов', unique=True)
    color = models.IntegerField(verbose_name=u'Цвет на графиках', blank=True, null=True)
    trafficnode=models.ManyToManyField(verbose_name=u'Направления трафика', to=TrafficNode)
    
    def __unicode__(self):
        return u"%s" % self.name
        
    class Admin:
        pass

    class Meta:
        verbose_name = "Класс трафика"
        verbose_name_plural = "Классы трафика"
        
class IPAddressPool(models.Model):
    name     = models.CharField(max_length=255, verbose_name=u'Имя пула')
    start_IP = models.IPAddressField(verbose_name=u'Начальный адрес')
    end_IP   = models.IPAddressField(verbose_name=u'Конечный адрес')

    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        verbose_name = "Пул IP адресов"
        verbose_name_plural = "Пулы IP адресов"
