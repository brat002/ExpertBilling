#-*-coding=utf-8-*-

from django.db import models
#from ebscab.billservice.models import Account, Tariff

# Create your models here.

NAS_LIST=(
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9',u'MikroTik 2.9'),
                (u'mikrotik3',u'Mikrotik 3'),
                (u'mikrotik4',u'Mikrotik 4'),
                (u'mikrotik5',u'Mikrotik 5'),
                (u'common_radius',u'Общий RADIUS интерфейс'),
                (u'common_ssh',u'common_ssh'),
                )

DIRECTIONS_LIST=(
                (u'INPUT', u'Входящий на абонента'),
                (u'OUTPUT',u'Исходящий от абонента'),
                (u'TRANSIT',u'Межабонентский'),
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
    identify = models.CharField(verbose_name=u'RADIUS идентификатор сервера доступа', max_length=255)
    name = models.CharField(verbose_name=u'Идентификатор сервера доступа', help_text=u"Используется дли идентификации сервера доступа. Смотрите настройки /system identity print", max_length=255, unique=True)
    ipaddress = models.CharField(verbose_name=u'IP адрес сервера доступа', max_length=255)
    secret = models.CharField(verbose_name=u'Секретная фраза', help_text=u"Смотрите вывод команды /radius print", max_length=255)
    login = models.CharField(verbose_name=u'Имя для доступа к серверу по SSH', max_length=255, blank=True, default='admin')
    password = models.CharField(verbose_name=u'Пароль для доступа к серверу по SSH', max_length=255, blank=True, default='')
    #description = models.TextField(verbose_name=u'Описание', blank=True, default='')
    allow_pptp = models.BooleanField(verbose_name=u'Разрешить серверу работать с PPTP', default=True)
    allow_pppoe = models.BooleanField(verbose_name=u'Разрешить серверу работать с PPPOE', default=True)
    allow_ipn = models.BooleanField(verbose_name=u'Сервер поддерживает IPN', help_text=u"IPN - технология, которая позволяет предоставлять доступ в интернет без установления VPN соединения с сервером доступа", default=True)
    user_add_action = models.TextField(verbose_name=u'Действие при создании пользователя',blank=True, null=True)
    user_enable_action = models.TextField(verbose_name=u'Действие при разрешении работы пользователя',blank=True, null=True)
    user_disable_action = models.TextField(verbose_name=u'Действие при запрещении работы пользователя',blank=True, null=True)
    user_delete_action = models.TextField(verbose_name=u'Действие при удалении пользователя',blank=True, null=True)
    vpn_speed_action = models.TextField(max_length=255, blank=True, default="")
    ipn_speed_action = models.TextField(max_length=255, blank=True, default="")
    reset_action = models.TextField(max_length=255, blank=True, default="")
    confstring = models.TextField(verbose_name="Конфигурация по запросу", blank=True, default='')
    subacc_disable_action = models.TextField(blank=True, default="")
    subacc_enable_action = models.TextField(blank=True, default="")
    subacc_add_action = models.TextField(blank=True, default="")
    subacc_delete_action = models.TextField(blank=True, default="")
    subacc_ipn_speed_action = models.TextField(blank=True, default="")
    snmp_version = models.CharField(verbose_name=u'Версия SNMP', max_length=10, blank=True, null=True)
    speed_vendor_1 = models.TextField(blank=True, default="")
    speed_vendor_2 = models.TextField(blank=True, default="")
    speed_attr_id1 = models.TextField(blank=True, default="")
    speed_attr_id2 = models.TextField(blank=True, default="")
    speed_value1 = models.TextField(blank=True, default="")
    speed_value2 = models.TextField(blank=True, default="")
    acct_interim_interval = models.IntegerField(default=60, blank=True, null=True)
    

    class Admin:
          ordering = ['-name']
          list_display = ('name','ipaddress')

    class Meta:
        verbose_name = u"Сервер доступа"
        verbose_name_plural = u"Сервера доступа"

    def __unicode__(self):
        return u"%s" % self.name


class TrafficClass(models.Model):
    """
    Классы трафика не должны пересекаться, ноды внутри одного класса не должны указывать сразу входящие
    и исходящие направления. Правило: Один класс на одно направление (вх/исх/межабонентский)
    """
    name = models.CharField(verbose_name=u'Навзание класса', max_length=255, unique=True)
    weight = models.IntegerField(verbose_name=u'Вес класа в цепочке классов', unique=True)
    color = models.CharField(verbose_name=u'Цвет на графиках', max_length=16, blank=True, default='#FFFFFF')
    store    = models.BooleanField(verbose_name=u"Хранить всю статистику по классу", help_text=u"Хранить статистику, если она поступила от сервера доступа но под неё не попал ни один пользователь в базе", blank=True, default=True)
    passthrough = models.BooleanField(blank=True, default=True)
    
    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        pass

    class Meta:
        verbose_name = u"Класс трафика"
        verbose_name_plural = u"Классы трафика"

class TrafficNode(models.Model):
    """
    Направления трафика. Внутри одного класса не должно быть пересекающихся направлений
    """
    traffic_class = models.ForeignKey(TrafficClass)
    name = models.CharField(verbose_name=u'Название направления', max_length=255)
    direction = models.CharField(verbose_name=u"Направление трафика", choices=DIRECTIONS_LIST, max_length=32)
    protocol = models.CharField(max_length=10, blank=True, default='')

    src_ip  = models.IPAddressField(verbose_name=u'Cеть источника', default='0.0.0.0')
#    src_mask  = models.IPAddressField(verbose_name=u'Маска сети источника', default='0.0.0.0')
    src_port  = models.IntegerField(verbose_name=u'Порт источника', default=0)

    dst_ip = models.IPAddressField(verbose_name=u'Сеть получателя', default='0.0.0.0')
#    dst_mask = models.IPAddressField(verbose_name=u'Маска сети получателя', default='0.0.0.0')
    dst_port  = models.IntegerField(verbose_name=u'Порт получетеля', default=0)

    next_hop = models.IPAddressField(verbose_name=u'Направление пакета (IP address)', default='0.0.0.0')

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        pass

    class Meta:
        verbose_name = u"Направление трафика"
        verbose_name_plural = u"Направления трафика"
        
class Switch(models.Model):
    manufacturer = models.CharField(max_length=250)
    model = models.CharField(max_length=500)
    name = models.CharField(max_length=500)
    sn = models.CharField(max_length=500)
    city = models.IntegerField(db_column='city_id')
    street = models.IntegerField(db_column='street_id')
    house = models.IntegerField(db_column='house_id')
    place = models.TextField()#место установки
    comment = models.TextField()#
    ports_count = models.IntegerField()
    broken_ports = models.TextField()#через запятую
    uplink_ports = models.TextField()#через запятую
    protected_ports = models.TextField()#через запятую
    monitored_ports = models.TextField()
    disabled_ports = models.TextField()
    snmp_support = models.BooleanField(default=False)
    snmp_version = models.CharField(max_length=10)#version
    snmp_community = models.CharField(max_length=128)#
    ipaddress = models.IPAddressField()
    macaddress = models.CharField(max_length=32)
    management_method = models.CharField(max_length=32)
    option82 = models.BooleanField(default=False)
    option82_auth_type = models.IntegerField()#1-port, 2 - mac+port, 3-mac
    secret = models.CharField(max_length=128)
    identify = models.CharField(max_length=128)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
    enable_port = models.TextField()
    disable_port = models.TextField()
    
    def __unicode__(self):
        return u"%s" % self.name
    

    
    