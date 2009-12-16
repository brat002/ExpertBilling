# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

  

def get_tickets(self):
    from ticket.models import Ticket
    return Ticket.objects.filter(owner__id=self.id)

User.add_to_class('get_tickets', get_tickets)

class Departament(models.Model):
    name = models.CharField( max_length = 255, verbose_name = u"Название отдела")
    user = models.ManyToManyField(User)
    
    def __unicode__(self):
        return self.name
    
    def get_tickets(self):
        from ticket.models import Ticket
        return Ticket.objects.filter(departament__id = self.id)
    
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
    postcode = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=255)
    house_bulk = models.CharField(max_length=255)
    entrance = models.CharField(max_length=255)
    room = models.CharField(max_length=255)
    
    #assign_vpn_ip_from_dhcp = models.BooleanField(blank=True, default=False)
    #nas = models.ForeignKey(to=Nas, blank=True, verbose_name=u'Сервер доступа')
    #vpn_pool = models.ForeignKey(to=IPAddressPool, related_name='virtual_pool', blank=True, null=True)
    vpn_ip_address = models.IPAddressField(u'Статический IP VPN адрес', help_text=u'Если не назначен-выбрать из пула, указанного в тарифном плане', blank=True, default='0.0.0.0')
    assign_ipn_ip_from_dhcp = models.BooleanField(blank=True, default=False)
    #ipn_pool = models.ForeignKey(to=IPAddressPool, related_name='ipn_pool', blank=True, null=True)
    ipn_ip_address = models.IPAddressField(u'IP адрес клиента', help_text=u'Для IPN тарифных планов', blank=True, default='0.0.0.0')
    ipn_mac_address = models.CharField(u'MAC адрес клиента', max_length=32, help_text=u'Для IPN тарифных планов', blank=True, default='')
    ipn_status = models.BooleanField(verbose_name=u"Статус на сервере доступа", default=False, blank=True)
    status=models.IntegerField(verbose_name=u'Статус пользователя', default=1)
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
    
    def __unicode__(self):
        return self.username
    
    class Meta:
        db_table="billservice_account"