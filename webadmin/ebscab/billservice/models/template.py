# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class TemplateType(models.Model):
    name = models.TextField(verbose_name=_(u"Название типа шаблона"))

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        ordering = ['id']
        verbose_name = _(u"Тип шаблона")
        verbose_name_plural = _(u"Типы шаблонов")
        permissions = (
            ("templatetype_view", _(u"Просмотр")),
        )


class Template(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(TemplateType, on_delete=models.CASCADE)
    body = models.TextField()

    def __unicode__(self):
        return u"%s" % (self.name)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('template_delete'), self.id)

    class Meta:
        ordering = ['type']
        verbose_name = _(u"Шаблон")
        verbose_name_plural = _(u"Шаблоны")
        permissions = (
            ("template_view", _(u"Просмотр")),
        )


class ContractTemplate(models.Model):
    template = models.CharField(
        max_length=128,
        verbose_name=_(u'Шаблон'),
        help_text=u'''\
%(contract_num)i - номер заключаемого договора этого типа
%(account_id)i - идентификатор аккаунта
%(day)i,%(month)i,%(year)i,%(hour)i,%(minute)i,%(second)i - дата подключения на тариф
'''
    )
    counter = models.IntegerField()

    class Meta:
        ordering = ['template']
        verbose_name = _(u"Шаблон номера договора")
        verbose_name_plural = _(u"Шаблоны номеров договоров")
        permissions = (
            ("contracttemplate_view", _(u"Просмотр")),
        )

    def __unicode__(self):
        return unicode(self.template)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('contracttemplate_delete'), self.id)
