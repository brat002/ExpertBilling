# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from billservice.models.constants import PERMISSION_ROLES


class Permission(models.Model):
    name = models.CharField(max_length=500, verbose_name=_(u"Название"))
    app = models.CharField(max_length=500, verbose_name=_(u"Приложение"))
    internal_name = models.CharField(
        max_length=500, verbose_name=_(u"Внутреннее имя"))
    ordering = models.IntegerField()

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _(u"Право доступа")
        verbose_name_plural = _(u"Права доступа")


class PermissionGroup(models.Model):
    name = models.CharField(max_length=128, verbose_name=_(u"Название"))
    role = models.CharField(
        max_length=64, choices=PERMISSION_ROLES, verbose_name=_(u"Роль"))
    permissions = models.ManyToManyField(
        'billservice.Permission', verbose_name=_(u"Права"))

    deletable = models.BooleanField(default=False, blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _(u"Группа доступа")
        verbose_name_plural = _(u"Группы доступа")

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('permissiongroup_delete'), self.id)
