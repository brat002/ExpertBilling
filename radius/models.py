#-*-coding=utf-8-*-

from django.db import models
from mikrobill.billservice.models import Account
SERVICE_TYPES=(
        (u"PPTP",u"PPTP"),
        (u"L2TP",u"L2TP"),
        (u"PPPOE",u"PPPOE"),
        )
SESSION_STATUS=(
                (u"ACTIVE", u"Активна",),
                (u"NACK", u"Не сброшена",),
                (u"ACK", u"Cброшена",),
                )
# Create your models here.
class Session(models.Model):
    account=models.ForeignKey(Account)
    #Атрибут радиуса Acct-Session-Id
    sessionid=models.CharField(max_length=255, blank=True)
    #Время последнего обновления
    interrim_update=models.DateTimeField(auto_now_add=True, blank=True, null=True)
    #Время старта сессии
    date_start=models.DateTimeField(blank=True, null=True)
    #Время конца сессии
    date_end=models.DateTimeField(null=True,blank=True)
    #Атрибут радиуса Calling-Station-Id. IP адрес или мак-адрес
    caller_id=models.CharField(max_length=255, blank=True)
    #Атрибут радиуса Called-Station-Id (IP адрес или имя сервиса для PPPOE)
    called_id=models.CharField(max_length=255, blank=True)
    #Атрибут радиуса NAS-IP-Address
    nas_id=models.CharField(max_length=255, blank=True)
    #Атрибут радиуса Acct-Session-Time
    session_time=models.IntegerField(default=0, null=True,blank=True)
    #Нужно определить каким образом клиент подключился к серверу
    framed_protocol=models.CharField(max_length=32, choices=SERVICE_TYPES,radio_admin=True)
    #Атрибут радиуса Acct-Input-Packets
    bytes_in=models.IntegerField(null=True,blank=True)
    #Атрибут радиуса Acct-Output-Packets
    bytes_out=models.IntegerField(null=True,blank=True)
    #Выставляется в случае, если был произведён платёж
    checkouted_by_time = models.BooleanField(default=False, blank=True)
    checkouted_by_trafic = models.BooleanField(default=False, blank=True)
    disconnect_status=models.CharField(max_length=32, null=True, blank=True)



    class Admin:
        ordering = ['-id']
        list_display = ('account','bytes_in','bytes_out','sessionid', 'date_start', 'interrim_update', 'date_end','caller_id','called_id','nas_id','session_time')

    class Meta:
        pass

    def __unicode__(self):
        return u"%s" % self.account.username


# Create your models here.
class ActiveSession(models.Model):
    account=models.ForeignKey(Account)
    #Атрибут радиуса Acct-Session-Id
    sessionid=models.CharField(max_length=255, blank=True)
    #Время последнего обновления
    interrim_update=models.DateTimeField(auto_now_add=True, blank=True, null=True)
    #Время старта сессии
    date_start=models.DateTimeField(blank=True, null=True)
    #Время конца сессии
    date_end=models.DateTimeField(null=True,blank=True)
    #Атрибут радиуса Calling-Station-Id. IP адрес или мак-адрес
    caller_id=models.CharField(max_length=255, blank=True)
    #Атрибут радиуса Called-Station-Id (IP адрес или имя сервиса для PPPOE)
    called_id=models.CharField(max_length=255, blank=True)
    #Атрибут радиуса NAS-IP-Address
    nas_id=models.CharField(max_length=255, blank=True)
    #Атрибут радиуса Acct-Session-Time
    session_time=models.IntegerField(default=0, null=True,blank=True)
    #Нужно определить каким образом клиент подключился к серверу
    framed_protocol=models.CharField(max_length=32, choices=SERVICE_TYPES,radio_admin=True)
    #Атрибут радиуса Acct-Input-Octets
    bytes_in=models.IntegerField(null=True,blank=True)
    #Атрибут радиуса Acct-Output-Octets
    bytes_out=models.IntegerField(null=True,blank=True)
    #Выставляется в случае, если был произведён платёж
    session_status=models.CharField(max_length=32, choices=SESSION_STATUS, null=True, blank=True)



    class Admin:
        ordering = ['-id']
        list_display = ('account','bytes_in','bytes_out','sessionid', 'date_start', 'interrim_update','date_end','caller_id','called_id','session_time', 'session_status')

    class Meta:
        pass

    def __unicode__(self):
        return u"%s" % self.sessionid
