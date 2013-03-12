#-*- coding: utf-8 -*-
from sendsms.api import get_connection
from sendsms.signals import sms_post_send
from django.conf import settings
from django.db import models
from utils import get_backend_choices
import datetime


class Message(models.Model):
    from_phone = models.CharField(default=getattr(settings, 'SENDSMS_DEFAULT_FROM_PHONE', ''))
    to = models.CharField(max_length=64)
    body = models.TextField()
    flash = models.BooleanField(blank=True, default=False)
    backend = models.CharField(choices=get_backend_choices(), max_length=128)
    sended = models.DateTimeField(blank=True, null=True)
    publish_date = models.DateTimeField(blank=True, null=True)
    
    def get_connection(self, fail_silently=False):
        if not self.backend: return
        self.connection = get_connection(path=self.backend, fail_silently=fail_silently)
        return self.connection

    def save(self, *args, **kwargs):
        if not self.id and not self.publish_date and not self.sended:
            """
            Если это новое сообщение, без даты публикации и оно не помечено отосланным
            """
            now = datetime.datetime.now()
            self.get_connection(False).send_message(self)
            self.publish_date = now
            self.sended = now
            
        super(Message, self).save(*args, **kwargs)
            
    def send(self, fail_silently=False):
        """
        Sends the sms message
        """
        if not self.to:
            # Don't bother creating the connection if there's nobody to send to
            return 0
        res = self.get_connection(fail_silently).send_message(self)
        sms_post_send.send(sender=self, to=self.to, from_phone=self.from_phone, body=self.body)
        return res
    