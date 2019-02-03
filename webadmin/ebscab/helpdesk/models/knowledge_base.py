# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _


class KBCategory(models.Model):
    """
    Lets help users help themselves: the Knowledge Base is a categorised
    listing of questions & answers.
    """

    title = models.CharField(
        _('Title'),
        max_length=100,
    )

    slug = models.SlugField(
        _('Slug'),
    )

    description = models.TextField(
        _('Description'),
    )

    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        ordering = ['title', ]
        verbose_name = _(u'knowledge base category')
        verbose_name_plural = _(u'Knowledge base categories')

    def get_absolute_url(self):
        return ('helpdesk_kb_category', (), {'slug': self.slug})
    get_absolute_url = models.permalink(get_absolute_url)


class KBItem(models.Model):
    """
    An item within the knowledgebase. Very straightforward question/answer
    style system.
    """
    category = models.ForeignKey(KBCategory, on_delete=models.CASCADE)

    title = models.CharField(
        _('Title'),
        max_length=100,
    )

    question = models.TextField(
        _('Question'),
    )

    answer = models.TextField(
        _('Answer'),
    )

    votes = models.IntegerField(
        _('Votes'),
        help_text=_('Total number of votes cast for this item'),
    )

    recommendations = models.IntegerField(
        _('Positive Votes'),
        help_text=_('Number of votes for this item which were POSITIVE.'),
    )

    last_updated = models.DateTimeField(
        _('Last Updated'),
        help_text=_('The date on which this question was most recently '
                    'changed.'),
        blank=True,
    )

    def save(self, force_insert=False, force_update=False):
        if not self.last_updated:
            self.last_updated = datetime.now()
        return super(KBItem, self).save(force_insert, force_update)

    def _score(self):
        if self.votes > 0:
            return int(self.recommendations / self.votes)
        else:
            return _('Unrated')
    score = property(_score)

    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        ordering = ['title', ]
        verbose_name = _(u'knowledge base item')
        verbose_name_plural = _(u'Knowledge base items')

    def get_absolute_url(self):
        return ('helpdesk_kb_item', (self.id,))
    get_absolute_url = models.permalink(get_absolute_url)
