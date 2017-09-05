# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Queue(models.Model):
    """
    A queue is a collection of tickets into what would generally be business
    areas or departments.

    For example, a company may have a queue for each Product they provide, or
    a queue for each of Accounts, Pre-Sales, and Support.

    """

    title = models.CharField(
        _('Title'),
        max_length=100,
    )

    slug = models.SlugField(
        _('Slug'),
        help_text=_('This slug is used when building ticket ID\'s. Once set, '
                    'try not to change it or e-mailing may get messy.'),
    )

    email_address = models.EmailField(
        _('E-Mail Address'),
        blank=True,
        null=True,
        help_text=_('All outgoing e-mails for this queue will use this e-mail '
                    'address. If you use IMAP or POP3, this should be the '
                    'e-mail  address for that mailbox.'),
    )

    locale = models.CharField(
        _('Locale'),
        max_length=10,
        blank=True,
        null=True,
        help_text=_('Locale of this queue. All correspondence in this queue '
                    'will be in this language.'),
    )

    allow_public_submission = models.BooleanField(
        _('Allow Public Submission?'),
        blank=True,
        default=False,
        help_text=_('Should this queue be listed on the public submission '
                    'form?'),
    )

    allow_email_submission = models.BooleanField(
        _('Allow E-Mail Submission?'),
        blank=True,
        default=False,
        help_text=_('Do you want to poll the e-mail box below for new '
                    'tickets?'),
    )

    escalate_days = models.IntegerField(
        _('Escalation Days'),
        blank=True,
        null=True,
        help_text=_('For tickets which are not held, how often do you wish to '
                    'increase their priority? Set to 0 for no escalation.'),
    )

    new_ticket_cc = models.EmailField(
        _('New Ticket CC Address'),
        blank=True,
        null=True,
        help_text=_('If an e-mail address is entered here, then it will '
                    'receive notification of all new tickets created for '
                    'this queue'),
    )

    updated_ticket_cc = models.EmailField(
        _('Updated Ticket CC Address'),
        blank=True,
        null=True,
        help_text=_('If an e-mail address is entered here, then it will '
                    'receive notification of all activity (new tickets, '
                    'closed tickets, updates, reassignments, etc) for '
                    'this queue'),
    )

    email_box_type = models.CharField(
        _('E-Mail Box Type'),
        max_length=5,
        choices=(
            ('pop3', _('POP 3')),
            ('imap', _('IMAP'))
        ),
        blank=True,
        null=True,
        help_text=_('E-Mail server type for creating tickets automatically '
                    'from a mailbox - both POP3 and IMAP are supported.'),
    )

    email_box_host = models.CharField(
        _('E-Mail Hostname'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Your e-mail server address - either the domain name or '
                    'IP address. May be "localhost".'),
    )

    email_box_port = models.IntegerField(
        _('E-Mail Port'),
        blank=True,
        null=True,
        help_text=_('Port number to use for accessing e-mail. Default for '
                    'POP3 is "110", and for IMAP is "143". This may differ '
                    'on some servers. Leave it blank to use the defaults.'),
    )

    email_box_ssl = models.BooleanField(
        _('Use SSL for E-Mail?'),
        blank=True,
        default=False,
        help_text=_('Whether to use SSL for IMAP or POP3 - the default ports '
                    'when using SSL are 993 for IMAP and 995 for POP3.'),
    )

    email_box_user = models.CharField(
        _('E-Mail Username'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Username for accessing this mailbox.'),
    )

    email_box_pass = models.CharField(
        _('E-Mail Password'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Password for the above username'),
    )

    email_box_imap_folder = models.CharField(
        _('IMAP Folder'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('If using IMAP, what folder do you wish to fetch messages '
                    'from? This allows you to use one IMAP account for '
                    'multiple queues, by filtering messages on your IMAP '
                    'server into separate folders. Default: INBOX.'),
    )

    email_box_interval = models.IntegerField(
        _('E-Mail Check Interval'),
        help_text=_(
            'How often do you wish to check this mailbox? (in Minutes)'),
        blank=True,
        null=True,
        default='5',
    )

    email_box_last_check = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
        # This is updated by management/commands/get_mail.py.
    )

    def __unicode__(self):
        return u"[%s] %s" % (self.slug, self.title)

    class Meta:
        ordering = ('title',)
        verbose_name = _(u'queue')
        verbose_name_plural = _(u'Queues')

    def _from_address(self):
        """
        Short property to provide a sender address in SMTP format,
        eg 'Name <email>'. We do this so we can put a simple error message
        in the sender name field, so hopefully the admin can see and fix it.
        """
        if not self.email_address:
            return (u'NO QUEUE EMAIL ADDRESS DEFINED <%s>' %
                    settings.DEFAULT_FROM_EMAIL)
        else:
            return u'%s <%s>' % (self.title, self.email_address)
    from_address = property(_from_address)

    def save(self, force_insert=False, force_update=False):
        if self.email_box_type == 'imap' and not self.email_box_imap_folder:
            self.email_box_imap_folder = 'INBOX'

        if not self.email_box_port:
            if self.email_box_type == 'imap' and self.email_box_ssl:
                self.email_box_port = 993
            elif self.email_box_type == 'imap' and not self.email_box_ssl:
                self.email_box_port = 143
            elif self.email_box_type == 'pop3' and self.email_box_ssl:
                self.email_box_port = 995
            elif self.email_box_type == 'pop3' and not self.email_box_ssl:
                self.email_box_port = 110
        super(Queue, self).save(force_insert, force_update)
