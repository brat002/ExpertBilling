#-*- coding=utf-8 -*-
from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from billservice.models import SystemUser
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class TableSettings(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=128)
    value = JSONField()
    per_page = models.IntegerField()
    
    
from django.db.models.signals import class_prepared

def longer_username(sender, *args, **kwargs):
    # You can't just do `if sender == django.contrib.auth.models.User`
    # because you would have to import the model
    # You have to test using __name__ and __module__
    if sender.__name__ == "User" and sender.__module__ == "django.contrib.auth.models":
        sender._meta.get_field("username").max_length = 256
        sender._meta.get_field("first_name").max_length = 256
        sender._meta.get_field("last_name").max_length = 256
        sender._meta.get_field("email").max_length = 256

class Comment(models.Model):
  
    content_type    = models.ForeignKey(ContentType, related_name="comments_set", null=True, blank=True)
    object_id       = models.PositiveIntegerField(null=True, blank=True)
    object  = generic.GenericForeignKey(ct_field='content_type', fk_field='object_id')
    comment = models.TextField(verbose_name=_(u'Комментарий'))
    done_comment = models.TextField(verbose_name=_(u'Финальный комментарий'), blank=True, null=True)
    created = models.DateTimeField(verbose_name = _(u'Создан'), auto_now_add=True, blank=True, null=True)
    done_date = models.DateTimeField(verbose_name=_(u'Когда выполнен'), blank=True, null=True)
    done_systemuser = models.ForeignKey(SystemUser, verbose_name=_(u'Кем выполнен'), on_delete=models.SET_NULL, blank=True, null=True)
    due_date = models.DateTimeField(verbose_name=_(u'Выполнить до '), blank=True, null=True)
    deleted = models.DateTimeField(verbose_name=_(u'Удалён'), blank=True, null=True)
   
    def get_remove_url(self):
        return "%s?id=%s" % (reverse('comment_delete'), self.id)

    class Meta:
        ordering = ('-created', )

class_prepared.connect(longer_username)


