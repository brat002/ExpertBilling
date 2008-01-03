#-*-coding=utf-8-*-

from django.db import models
from mikrobill.billservice.models import Account
SERVICE_TYPES=(
        ("PPTP","PPTP"),
        ("L2TP","PPTP"),
        ("PPPOE","PPTP"),
        )
# Create your models here.
class Session(models.Model):
    account=models.ForeignKey(Account)
    #Атрибут радиуса Acct-Session-Id
    sessionid=models.CharField(max_length=255, blank=True)
    #Время последнего обновления
    interrim_update=models.DateTimeField(null=True,blank=True)
    #Время старта сессии
    date_start=models.DateTimeField(auto_now_add=True)
    #Время конца сессии
    date_end=models.DateTimeField(null=True,blank=True)
    #Атрибут радиуса Calling-Station-Id. IP адрес или мак-адрес
    caller_id=models.CharField(max_length=255, blank=True)
    #Атрибут радиуса Called-Station-Id (IP адрес или имя сервиса для PPPOE)
    called_id=models.CharField(max_length=255, blank=True)
    #Атрибут радиуса NAS-IP-Address
    nas_id=models.CharField(max_length=255, blank=True)
    #Атрибут радиуса Acct-Session-Time
    session_time=models.IntegerField(null=True,blank=True)
    #Нужно определить каким образом клиент подключился к серверу
    framed_protocol=models.CharField(max_length=32, choices=SERVICE_TYPES,radio_admin=True, default='PPTP')
    #Атрибут радиуса Acct-Input-Packets
    bytes_in=models.IntegerField(null=True,blank=True)
    #Атрибут радиуса Acct-Output-Packets
    bytes_out=models.IntegerField(null=True,blank=True)

    

    class Admin:
        ordering = ['-date_start']
        list_display = ('account','bytes_in','bytes_out','sessionid', 'date_start','date_end','caller_id','called_id','nas_id','session_time')
    
    class Meta:
        pass
    
    def __unicode__(self):
        return self.account.username
