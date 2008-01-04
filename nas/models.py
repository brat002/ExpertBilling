#-*-coding=utf-8-*-

from django.db import models
from mikrobill.billing.models import Account

# Create your models here.

class Nas(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ipaddress = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user_add_action = models.TextField(verbose_name=u'Действие при создании пользователя',blank=True, null=True)
    user_enable_action = models.TextField(verbose_name=u'Действие при разрешении работы пользователя',blank=True, null=True)
    user_disable_action = models.TextField(verbose_name=u'Действие при запрещении работы пользователя',blank=True, null=True)
    user_delete_action = models.TextField(verbose_name=u'Действие при удалении пользователя',blank=True, null=True)
    
    class Admin:
          ordering = ['-name']
          list_display = ('name','ipaddress','description')
    
    def __str__(self):
        return self.name

class Collector(models.Model):
    name=models.CharField(max_length=255)
    ipaddress = models.IPAddressField()
    description = models.TextField(blank=True)
    version=models.IntegerField()
    
    class Admin:
          ordering = ['-name']
          list_display = ('name','ipaddress','description')
    
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
    start = models.IntegerField()
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

    def save(self):
        try:
            nfstream = NetFlowStream.objects.get(collector=self.collector,src_addr=self.src_addr,dst_addr=self.dst_addr, next_hop=self.next_hop,in_index=self.in_index,out_index=self.out_index, src_port=self.src_port,dst_port=self.dst_port,protocol=self.protocol)
            a=nfstream.date_start - self.date_start
            print a.minutes
            #if nfstream.date_start.secconds - self.date_start.secconds<120:
            nfstream.octets += self.octets
            nfstream.groups +=1
            nfstream.save()
            #else:
            #    super(NetFlowStream, self).save()
        except:
               super(NetFlowStream, self).save()

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
    
class TrafficClass(models.Model):
    name = models.CharField(max_length=255)
    weight = models.IntegerField()
    color = models.IntegerField()
    trafficnode=models.ManyToManyField(to=TrafficNode)
    
    def __unicode__(self):
        return u"%s" % self.name
        
    class Admin:
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
