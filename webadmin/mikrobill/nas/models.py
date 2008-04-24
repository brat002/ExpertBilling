#-*-coding=utf-8-*-

from django.db import models
#from mikrobill.billservice.models import Account, Tariff

# Create your models here.

NAS_LIST=(
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9',u'MikroTik 2.9'),
                (u'mikrotik3',u'Mikrotik 3'),
                (u'windows2000s',u'Windows 2000 Server'),
                (u'common_radius',u'Общий RADIUS интерфейс'),
                (u'common_ssh',u'common_ssh'),
                )

DIRECTIONS_LIST=(
                (u'INPUT', u'Входящий на абонента'),
                (u'OUTPUT',u'Исходящий от абонента'),
                (u'BOTH',u'Межабонентский'),
                )

SERVICE_LIST=(
              ('Virtual', 'VPN'),
              ('IPN', 'IPN'),
              )

class Nas(models.Model):
    """
    /ip firewall address-list add address=$ipaddress list=allow_ip comment=$user_id
    /ip firewall address-list remove $user_id
    """
    type = models.CharField(choices=NAS_LIST, max_length=32, default='mikrotik3')
    name = models.CharField(verbose_name=u'Идентификатор сервера доступа', help_text=u"Используется дли идентификации сервера доступа. Смотрите настройки /system identity print", max_length=255, unique=True)
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
    support_netflow = models.BooleanField(verbose_name=u'Сервер поддерживает экспорт NetFlow', help_text=u"Сервер доступа поддерживает экспорт статистики через NetFlow", blank=True, null=True, default=True)
    netflow_version = models.SmallIntegerField(verbose_name=u'Версия NetFlow', editable=False, blank=True, null=True, default=5)
    support_coa = models.BooleanField(verbose_name=u'Сервер поддерживает CoA', help_text=u"Технология, позволяющая менять клиенту скорость или другие параметры без обрыва сессии. Подробно описана в RFC 3576", blank=True, null=True, default=True)
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
        verbose_name = u"Сервер доступа"
        verbose_name_plural = u"Сервера доступа"
    
    def __unicode__(self):
        return u"%s" % self.name

    
class TrafficNode(models.Model):
    """
    Направления трафика. Внутри одного класса не должно быть пересекающихся направлений
    """
    name = models.CharField(verbose_name=u'Название направления', max_length=255)
    src_ip  = models.IPAddressField(verbose_name=u'Cеть источника', default='0.0.0.0')
    src_mask  = models.IPAddressField(verbose_name=u'Маска сети источника', default='0.0.0.0')
    src_port  = models.IntegerField(verbose_name=u'Порт источника', default=0)
    
    dst_ip = models.IPAddressField(verbose_name=u'Сеть получателя', default='0.0.0.0')
    dst_mask = models.IPAddressField(verbose_name=u'Маска сети получателя', default='0.0.0.0')
    dst_port  = models.IntegerField(verbose_name=u'Порт получетеля', default=0)
    
    next_hop = models.IPAddressField(verbose_name=u'Направление пакета (IP address)', default='0.0.0.0')
    
    def __unicode__(self):
        return u"%s" % self.name
        
    class Admin:
        pass

    class Meta:
        verbose_name = u"Направление трафика"
        verbose_name_plural = u"Направления трафика"
        
class TrafficClass(models.Model):
    """
    Классы трафика не должны пересекаться, ноды внутри одного класса не должны указывать сразу входящие 
    и исходящие направления. Правило: Один класс на одно направление (вх/исх/межабонентский) 
    """
    name = models.CharField(verbose_name=u'Навзание класса', max_length=255)
    weight = models.IntegerField(verbose_name=u'Вес класа в цепочке классов', unique=True)
    color = models.CharField(verbose_name=u'Цвет на графиках', max_length=16, blank=True, null=True)
    direction = models.CharField(verbose_name=u"Направление трафика", choices=DIRECTIONS_LIST, max_length=32)
    store    = models.BooleanField(verbose_name=u"Хранить всю статистику по классу", help_text=u"Хранить статистику, если она поступила от сервера доступа но под неё не попал ни один пользователь в базе", blank=True, default=True)
    trafficnode=models.ManyToManyField(verbose_name=u'Направления трафика', to=TrafficNode)

    
    def __unicode__(self):
        return u"%s" % self.name
        
    class Admin:
        pass

    class Meta:
        verbose_name = u"Класс трафика"
        verbose_name_plural = u"Классы трафика"
        
class IPAddressPool(models.Model):
    name     = models.CharField(max_length=255, verbose_name=u'Имя пула')
    start_IP = models.IPAddressField(verbose_name=u'Начальный адрес')
    end_IP   = models.IPAddressField(verbose_name=u'Конечный адрес')
    lease_length = models.PositiveIntegerField(verbose_name=u'Время аренды')
    service    = models.CharField(max_length=32, choices=SERVICE_LIST)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        pass

    class Meta:
        verbose_name = u"Пул IP адресов"
        verbose_name_plural = u"Пулы IP адресов"

class IPLeases(models.Model):
    from billservice.models import Account
    pool = models.ForeignKey(to=IPAddressPool)
    ip_address = models.IPAddressField()
    account = models.ForeignKey(to=Account)
    mac_address = models.CharField(max_length=22)
    lease_start = models.DateTimeField()
    
    
    def __unicode__(self):
        return u"%s" % (self.ip_address)
    
    class Admin:
        pass

    class Meta:
        verbose_name = u"Использемый адрес пула"
        verbose_name_plural = u"Использемые адреса пулов"
            
    