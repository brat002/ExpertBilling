# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class News(models.Model):
    body = models.TextField(verbose_name=_(u'Заголовок новости'))
    age = models.DateTimeField(
        verbose_name=_(u'Актуальна до'),
        help_text=_(u'Не указывайте ничего, если новость должна отображаться '
                    u'всегда'),
        blank=True,
        null=True
    )
    public = models.BooleanField(
        verbose_name=_(u'Публичная'),
        help_text=_(u'Отображать в публичной части веб-кабинета'),
        default=False
    )
    private = models.BooleanField(
        verbose_name=_(u'Приватная'),
        help_text=_(u'Отображать в приватной части веб-кабинета'),
        default=False
    )
    agent = models.BooleanField(
        verbose_name=_(u'Показать через агент'), default=False)
    created = models.DateTimeField(verbose_name=_(u'Актуальна с'), blank=True)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('news_delete'), self.id)

    class Meta:
        ordering = ['-created']
        verbose_name = _(u"Новость")
        verbose_name_plural = _(u"Новости")
        permissions = (
            ("news_view", _(u"Просмотр")),
        )


class AccountViewedNews(models.Model):
    news = models.ForeignKey('billservice.News')
    account = models.ForeignKey('billservice.Account')
    viewed = models.BooleanField(default=False)
