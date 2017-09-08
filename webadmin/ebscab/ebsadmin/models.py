# -*- coding: utf-8 -*-

from jsonfield import JSONField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from billservice.models import SystemUser


class Comment(models.Model):
    content_type = models.ForeignKey(
        ContentType, related_name="comments_set", null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object = GenericForeignKey(
        ct_field='content_type', fk_field='object_id')
    comment = models.TextField(verbose_name=_(u'Комментарий'))
    done_comment = models.TextField(
        verbose_name=_(u'Финальный комментарий'),
        blank=True,
        null=True)
    created = models.DateTimeField(
        verbose_name=_(u'Создан'),
        auto_now_add=True,
        blank=True,
        null=True)
    done_date = models.DateTimeField(
        verbose_name=_(u'Когда выполнен'),
        blank=True,
        null=True)
    done_systemuser = models.ForeignKey(
        SystemUser,
        verbose_name=_(u'Кем выполнен'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    due_date = models.DateTimeField(
        verbose_name=_(u'Выполнить до '),
        blank=True,
        null=True)
    deleted = models.DateTimeField(
        verbose_name=_(u'Удалён'), blank=True, null=True)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('comment_delete'), self.id)

    class Meta:
        ordering = ('-created', )


class TableSettings(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=128)
    value = JSONField()
    per_page = models.IntegerField()
