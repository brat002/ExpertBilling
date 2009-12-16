#-*-coding:utf-8-*-
from django.db import models
from django.contrib.auth.models import User
from ticket.models import Ticket

class Comment(models.Model): 
    user = models.ForeignKey(to = User, verbose_name=u'Пользователь', blank=True, null=True)
    ticket = models.ForeignKey(to =Ticket, verbose_name=u'Тикет', blank=True, null=True)
    body = models.CharField(max_length=255,verbose_name = u"тело сообщения")
    is_hide = models.BooleanField(verbose_name = u"скрытый" )
    
    class Meta:
        verbose_name =u"комментарий"
        verbose_name_plural = u"комментраии"
        
    def save(self):
        print self.ticket.status in [2,4]
        print type(self.ticket.status)
        if self.ticket.status in [2,4]:
            self.ticket.status = 6
            self.ticket.save()
        super(Comment, self).save()