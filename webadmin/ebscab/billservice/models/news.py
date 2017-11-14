# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class AccountViewedNewsQuerySet(models.QuerySet):

    def ordered(self):
        return self.order_by('viewed', '-news__created')

    def viewed(self):
        return self.filter(viewed=True)

    def unviewed(self):
        return self.filter(viewed=False)


class News(models.Model):
    created = models.DateTimeField(
        verbose_name=_(u'Актуальна с'),
        default=timezone.now
    )
    age = models.DateTimeField(
        verbose_name=_(u'Актуальна до'),
        help_text=_(u'Не указывайте ничего, если новость должна отображаться '
                    u'всегда'),
        blank=True,
        null=True
    )
    title = models.CharField(
        verbose_name=_(u'Заголовок'),
        max_length=64
    )
    description = models.CharField(
        verbose_name=_(u'Краткое описание'),
        help_text=_(u'Не более 64 символов'),
        max_length=64
    )
    body = models.TextField(
        verbose_name=_(u'Текст')
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
        verbose_name=_(u'Показать через агент'),
        default=False
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = _(u'Новость')
        verbose_name_plural = _(u'Новости')
        permissions = (
            ('news_view', _(u'Просмотр')),
        )

    def get_remove_url(self):
        return '{}?id={}'.format(reverse('news_delete'), self.id)


class AccountViewedNews(models.Model):
    news = models.ForeignKey('billservice.News')
    account = models.ForeignKey('billservice.Account')
    viewed = models.BooleanField(
        default=False
    )

    objects = AccountViewedNewsQuerySet.as_manager()

    class Meta:
        ordering = ('-news__created',)

    def get_absolute_url(self):
        return reverse('ebsweb:notification_detail', kwargs={'pk': self.pk})
