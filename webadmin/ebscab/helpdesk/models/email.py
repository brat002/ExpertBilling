# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _


class EmailTemplate(models.Model):
    """
    Since these are more likely to be changed than other templates, we store
    them in the database.

    This means that an admin can change email templates without having to have
    access to the filesystem.
    """

    template_name = models.CharField(
        _('Template Name'),
        max_length=100,
        unique=True,
    )

    subject = models.CharField(
        _('Subject'),
        max_length=100,
        help_text=_('This will be prefixed with "[ticket.ticket] ticket.title"'
                    '. We recommend something simple such as "(Updated") or "(Closed)"'
                    ' - the same context is available as in plain_text, below.'),
    )

    heading = models.CharField(
        _('Heading'),
        max_length=100,
        help_text=_('In HTML e-mails, this will be the heading at the top of '
                    'the email - the same context is available as in plain_text, '
                    'below.'),
    )

    plain_text = models.TextField(
        _('Plain Text'),
        help_text=_('The context available to you includes {{ ticket }}, '
                    '{{ queue }}, and depending on the time of the call: '
                    '{{ resolution }} or {{ comment }}.'),
    )

    html = models.TextField(
        _('HTML'),
        help_text=_('The same context is available here as in plain_text, '
                    'above.'),
    )

    def __unicode__(self):
        return u'%s' % self.template_name

    class Meta:
        ordering = ['template_name', ]
        verbose_name = _(u'email template')
        verbose_name_plural = _(u'Email templates')


class IgnoreEmail(models.Model):
    """
    This model lets us easily ignore e-mails from certain senders when
    processing IMAP and POP3 mailboxes, eg mails from postmaster or from
    known trouble-makers.
    """
    queues = models.ManyToManyField(
        'helpdesk.Queue',
        blank=True,
        help_text=_('Leave blank for this e-mail to be ignored on all '
                    'queues, or select those queues you wish to ignore '
                    'this e-mail for.')
    )

    name = models.CharField(
        _('Name'),
        max_length=100
    )

    date = models.DateField(
        _('Date'),
        help_text=_('Date on which this e-mail address was added'),
        blank=True,
        editable=False
    )

    email_address = models.CharField(
        _('E-Mail Address'),
        max_length=150,
        help_text=_('Enter a full e-mail address, or portions with '
                    'wildcards, eg *@domain.com or postmaster@*.')
    )

    keep_in_mailbox = models.BooleanField(
        _('Save Emails in Mailbox?'),
        blank=True,
        default=False,
        help_text=_('Do you want to save emails from this address in the '
                    'mailbox? If this is unticked, emails from this address '
                    'will be deleted.')
    )

    def __unicode__(self):
        return u'%s' % self.name

    def save(self):
        if not self.date:
            self.date = datetime.now()
        return super(IgnoreEmail, self).save()

    def test(self, email):
        """
        Possible situations:
            1. Username & Domain both match
            2. Username is wildcard, domain matches
            3. Username matches, domain is wildcard
            4. username & domain are both wildcards
            5. Other (no match)

            1-4 return True, 5 returns False.
        """

        own_parts = self.email_address.split("@")
        email_parts = email.split("@")

        if self.email_address == email or \
                own_parts[0] == "*" and own_parts[1] == email_parts[1] or \
                own_parts[1] == "*" and own_parts[0] == email_parts[0] or \
                own_parts[0] == "*" and own_parts[1] == "*":
            return True
        else:
            return False

    class Meta:
        verbose_name = _(u'ignored email')
        verbose_name_plural = _(u'Ignored emails')
