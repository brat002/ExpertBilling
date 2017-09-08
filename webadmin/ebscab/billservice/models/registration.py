# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class RegistrationRequest(models.Model):
    fullname = models.CharField(verbose_name=_(u'ФИО'), max_length=512)
    address = models.CharField(verbose_name=_(u'Адрес'), max_length=1024)
    phone = models.CharField(verbose_name=_(u'Телефон'), max_length=64)
    email = models.EmailField(verbose_name=_(u'Email'), unique=True)
    datetime = models.DateTimeField(verbose_name=_(u'Дата'), auto_now_add=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['datetime', ]
        verbose_name = _(u"Заявка на подключение")
        verbose_name_plural = _(u"Заявки на подключение")

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('registrationrequest_delete'), self.id)
