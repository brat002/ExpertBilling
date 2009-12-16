#-*-coding:utf-8-*-
from django.db import models
from django.contrib.auth.models import User
from account.models import Account,Departament


STATUS = (
          (1, u'Открыт'),
          (2, u'Закрыт'),
          (3 , u'В работе'),
          (4, u'Решен'),
          (5, u'Недействительный'),
          (6, u'Переоткрыт'),
          )

ADDITIONAL_STATUS = (
                     (1, u"Ошибка пользователя"),
                     (2, u"Ошибка системы"),
                     (3, u"Сбой оборудования"),
                     (4, u"Вирусы"),
                     (5, u"Попытка обмана"),
                     (6, u"Другое"),
                     )


class Type(models.Model):
    name = models.CharField(max_length=255, verbose_name = u'назвавние')
    
    def __unicode__(self):
        return self.name
    
class Ticket(models.Model):
    created_by=models.ForeignKey(to = Account,  verbose_name =u'создатель тикета', null=True, blank=True)
    departament = models.ForeignKey(to =Departament, verbose_name = u"Отдел", null=True, blank=True)
    owner = models.ForeignKey(to = User, verbose_name = u"Владелец",null=True, blank=True )
    email = models.EmailField(verbose_name="e-mail", null=True, blank=True)
    address = models.CharField(max_length=255,verbose_name=u"адрес", null=True, blank=True)
    phone = models.CharField(max_length=255,verbose_name=u"телефон", null=True, blank=True)
    tittle = models.CharField(max_length=255,verbose_name=u"заголовок письма")
    description = models.CharField(max_length=255,verbose_name=u"описание")
    type = models.ForeignKey(to = Type)
    status = models.IntegerField(max_length=255,verbose_name=u"статус", choices=STATUS)
    additional_status = models.IntegerField(max_length=255,verbose_name=u"дополнительный статус",null=True, blank=True, choices =ADDITIONAL_STATUS )
    
    def __unicode__(self):
        return self.tittle
    
    def save(self):
        if self.owner:
            self.departament=None
        elif self.departament:
            self.owner=None
        super(Ticket, self).save()
    