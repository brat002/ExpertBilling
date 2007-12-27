# -*-coding=utf-8-*-

from django.db import models
from django.contrib.auth.models import User

ACTIVITY_CHOISES=(
        ("Enabled","Enabled"),
        ("Disabled","Disabled"),
        )
        

class Tarif(models.Model):
    name=models.CharField(max_length=255, unique=True)
    description=models.TextField()
    summ=models.FloatField()
    period=models.IntegerField()
    speed=models.CharField(max_length=255, blank=True)
    created=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=32, choices=ACTIVITY_CHOISES,radio_admin=True, default='Enabled')

    class Admin:
        ordering = ['name']
        list_display = ('name','status','description','summ', 'period','speed','created')
        #list_filter = ('name')

    def __unicode__(self):
        return self.name

class Account(models.Model):
    user=models.ForeignKey(User,verbose_name='Системный пользователь', related_name='user_account1')
    username=models.CharField(verbose_name='Имя пользователя',max_length=200,unique=True)
    password=models.CharField(verbose_name='Пароль',max_length=200)
    firstname=models.CharField(verbose_name='Имя',max_length=200)
    lastname=models.CharField(verbose_name='Фамилия',max_length=200)
    address=models.TextField(verbose_name='Домашний адрес')
    tarif=models.ForeignKey(Tarif,verbose_name='Тарифный план')
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

class Pay(models.Model):
    account=models.ForeignKey(Account)
    summ=models.FloatField()
    created=models.DateTimeField()

    class Admin:
        ordering = ['-created']
        list_display = ('account','summ', 'created')

    def __unicode__(self):
        return self.account.username
    
    def save(self):
        self.account.ballance+=self.summ
        self.account.save()

        super(Pay, self).save()
        
    def delete(self):
        self.account.ballance-=self.summ
        self.account.save()
        super(Pay, self).delete()


class Bonus(models.Model):
    name=models.CharField(max_length=255,unique=True)
    description=models.TextField()
    users=models.ManyToManyField(Account, blank=True, filter_interface=models.HORIZONTAL)
    period_start=models.DateTimeField()
    period_end=models.DateTimeField()

    class Admin:
        ordering = ['-period_end']
        list_display = ('name','description','period_start', 'period_end')
        #list_filter = ('account')


    def __unicode__(self):
        return self.name

class Transaction(models.Model):
    account=models.ForeignKey(Account)
    tarif=models.ForeignKey(Tarif)
    summ=models.FloatField(blank=True)
    created=models.DateTimeField(auto_now_add=True)

    class Admin:
        list_display=('account', 'tarif', 'summ', 'created')
    
    class Meta:
        pass
    
    def save(self):
        self.account.ballance-=self.summ
        self.account.save()
        super(Transaction, self).save()

    def delete(self):
        self.account.ballance+=self.summ
        self.account.save()
        super(Transaction, self).delete()
