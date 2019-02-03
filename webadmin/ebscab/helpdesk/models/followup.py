# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from billservice.models import Account, SystemUser

from helpdesk.models.ticket import STATUS_CHOICES


class FollowUpManager(models.Manager):

    def private_followups(self):
        return self.filter(public=False)

    def public_followups(self):
        return self.filter(public=True)


class FollowUp(models.Model):
    """
    A FollowUp is a comment and/or change to a ticket. We keep a simple
    title, the comment entered by the user, and the new status of a ticket
    to enable easy flagging of details on the view-ticket page.

    The title is automatically generated at save-time, based on what action
    the user took.

    Tickets that aren't public are never shown to or e-mailed to the submitter,
    although all staff can see them.
    """

    ticket = models.ForeignKey('helpdesk.Ticket', on_delete=models.CASCADE)

    date = models.DateTimeField(_('Date'),)
    title = models.CharField(_('Title'), max_length=200, blank=True, null=True)
    comment = models.TextField(_('Comment'), blank=True, null=True)
    public = models.BooleanField(
        _('Public'),
        blank=True,
        default=True,
        help_text=_('Public tickets are viewable by the submitter and all '
                    'staff, but non-public tickets can only be seen by staff.')
    )
    systemuser = models.ForeignKey(
        SystemUser, blank=True, null=True, on_delete=models.CASCADE)
    account = models.ForeignKey(
        Account, blank=True, null=True, on_delete=models.CASCADE)
    new_status = models.IntegerField(
        _('New Status'),
        choices=STATUS_CHOICES,
        blank=True,
        null=True
    )
    objects = FollowUpManager()

    class Meta:
        ordering = ['-date']
        verbose_name = _(u'follow up')
        verbose_name_plural = _(u'Follow ups')

    def __unicode__(self):
        return u'%s' % self.title

    def get_absolute_url(self):
        return u"%s#followup%s" % (self.ticket.get_absolute_url(), self.id)

    def save(self, force_insert=False, force_update=False):
        t = self.ticket
        t.modified = datetime.now()
        self.date = datetime.now()
        t.save()
        super(FollowUp, self).save(force_insert, force_update)
