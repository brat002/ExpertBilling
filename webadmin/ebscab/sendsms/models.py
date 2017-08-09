# -*- coding: utf-8 -*-

import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.template import Context, Template

from sendsms.api import get_connection
from billservice.models import Account

from utils import get_backend_choices


class Message(models.Model):
    account = models.ForeignKey(Account)
    to = models.CharField(max_length=64)
    body = models.TextField()
    flash = models.BooleanField(blank=True, default=False)
    backend = models.CharField(choices=get_backend_choices(), max_length=128)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    sended = models.DateTimeField(blank=True, null=True)
    publish_date = models.DateTimeField(blank=True, null=True, db_index=True)
    response = models.TextField(blank=True, null=True)

    def get_connection(self, fail_silently=False):
        if not self.backend:
            return
        self.connection = get_connection(
            path=self.backend, fail_silently=fail_silently)
        return self.connection

    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)
        if (not self.publish_date or self.publish_date and
            self.publish_date <= datetime.datetime.now()) and not \
                self.sended:
            """
            Если это новое сообщение, без даты публикации и оно не помечено отосланным
            """
            self.send()

    def set_body(self):
        self.body = Template(self.body).render(Context({
            'account': self.account
        }))
        super(Message, self).save()

    class Meta:
        ordering = ('-created',)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('sms_delete'), self.id)

    def send(self, fail_silently=False):
        """
        Sends the sms message
        """
        if not self.to:
            # Don't bother creating the connection if there's nobody to send to
            return 0
        self.set_body()
        self.get_connection(False).send_message(self)
