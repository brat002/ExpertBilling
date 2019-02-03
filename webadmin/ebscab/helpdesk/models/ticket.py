# -*- coding: utf-8 -*-

from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext

from billservice.models import SystemUser, Account

from helpdesk.settings import HAS_TAG_SUPPORT

if HAS_TAG_SUPPORT:
    from tagging.fields import TagField


OPEN_STATUS = 1
REOPENED_STATUS = 2
RESOLVED_STATUS = 3
CLOSED_STATUS = 4

STATUS_CHOICES_FORM = (
    (0, '---'),
    (OPEN_STATUS, _('Open')),
    (REOPENED_STATUS, _('Reopened')),
    (RESOLVED_STATUS, _('Resolved')),
    (CLOSED_STATUS, _('Closed'))
)

STATUS_CHOICES = (
    (OPEN_STATUS, _('Open')),
    (REOPENED_STATUS, _('Reopened')),
    (RESOLVED_STATUS, _('Resolved')),
    (CLOSED_STATUS, _('Closed'))
)

STATUS_COLORS = (
    (OPEN_STATUS, '#F2411D'),
    (REOPENED_STATUS, '#F5C425'),
    (RESOLVED_STATUS, '#13709E'),
    (CLOSED_STATUS, '#000')
)

PRIORITY_CHOICES_FORM = (
    (0, '---'),
    (1, _('Critical')),
    (2, _('High')),
    (3, _('Normal')),
    (4, _('Low')),
    (5, _('Very Low'))
)

PRIORITY_CHOICES = (
    (1, _('Critical')),
    (2, _('High')),
    (3, _('Normal')),
    (4, _('Low')),
    (5, _('Very Low'))
)

PRIORITY_COLORS = [
    (1, 'red'),
    (2, 'orange',),
    (3, 'blue'),
    (4, 'green'),
    (5, 'grey')
]

PRIORITY_COLORS_20 = {
    1: 'danger',
    2: 'warning',
    3: 'brand',
    4: 'info',
    5: 'default'
}

prio = {
    1: 'label-important',
    2: 'label-warning',
    3: 'label-success',
    4: 'label-info',
    5: 'label-inverse',
}

source_types = (
    ('phone', _(u'Телефон')),
    ('helpdesk', _(u'HelpDesk')),
    ('im', _(u'ICQ/Skype/Chat')),
    ('personally', _(u'Персонально'))
)


class Ticket(models.Model):
    """
    To allow a ticket to be entered as quickly as possible, only the
    bare minimum fields are required. These basically allow us to
    sort and manage the ticket. The user can always go back and
    enter more information later.

    A good example of this is when a customer is on the phone, and
    you want to give them a ticket ID as quickly as possible. You can
    enter some basic info, save the ticket, give the customer the ID
    and get off the phone, then add in further detail at a later time
    (once the customer is not on the line).

    Note that assigned_to is optional - unassigned tickets are displayed on
    the dashboard to prompt users to take ownership of them.
    """

    OPEN_STATUS = OPEN_STATUS
    REOPENED_STATUS = REOPENED_STATUS
    RESOLVED_STATUS = RESOLVED_STATUS
    CLOSED_STATUS = CLOSED_STATUS

    STATUS_CHOICES_FORM = STATUS_CHOICES_FORM

    STATUS_CHOICES = STATUS_CHOICES

    STATUS_COLORS = STATUS_COLORS

    PRIORITY_CHOICES_FORM = PRIORITY_CHOICES_FORM

    PRIORITY_CHOICES = PRIORITY_CHOICES

    PRIORITY_COLORS = PRIORITY_COLORS

    PRIORITY_COLORS_20 = PRIORITY_COLORS_20

    title = models.CharField(
        _('Title'),
        max_length=200,
    )

    queue = models.ForeignKey(
        'helpdesk.Queue', verbose_name=_(u'Queue'), on_delete=models.CASCADE)
    owner = models.ForeignKey(
        User,
        related_name='submitted_by',
        null=False, blank=False,
        verbose_name=_(u'Owner'),
        on_delete=models.CASCADE
    )
    source = models.CharField(
        choices=source_types,
        max_length=32,
        verbose_name=_(u'Источник'),
        blank=False,
        default='helpdesk'
    )
    account = models.ForeignKey(
        Account,
        verbose_name=_('Account'),
        blank=True,
        null=True,
        help_text=_(u'Аккаунт, с которым связана текущая задача'),
        on_delete=models.CASCADE
    )
    notify_owner = models.BooleanField(
        blank=True, default=True, verbose_name=_(u'Notify owner'))
    assigned_to = models.ForeignKey(
        SystemUser,
        verbose_name=_(u'Исполнитель'),
        related_name='assigned_to',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(_(u'Created'), blank=True)
    due_date = models.DateTimeField(_(u'Due'), blank=True, null=True)
    modified = models.DateTimeField(
        _(u'Modified'),
        blank=True,
        help_text=_(u'Date this ticket was most recently changed.'),
        auto_now=True
    )
    submitter_email = models.EmailField(
        _('Submitter E-Mail'),
        blank=True,
        null=True,
        help_text=_(u'The submitter will receive an email for all public '
                    'follow-ups left for this task.')
    )
    status = models.IntegerField(
        _(u'Status'), choices=STATUS_CHOICES, default=OPEN_STATUS)
    on_hold = models.BooleanField(
        _(u'On Hold'),
        blank=True,
        default=False,
        help_text=_(
            u'If a ticket is on hold, it will not automatically be escalated.')
    )
    description = models.TextField(_('Description'), blank=True, null=True)
    hidden_comment = models.TextField(
        _(u'Скрытый комментарий.'),
        blank=True,
        null=True,
        help_text=_(u'Комментарий будут видеть только администраторы.')
    )
    resolution = models.TextField(
        _('Resolution'),
        blank=True,
        null=True,
        help_text=_('The resolution provided to the customer by our staff.')
    )
    priority = models.IntegerField(
        _('Priority'), choices=PRIORITY_CHOICES, default=3, blank=3)

    last_escalation = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
        help_text=_(u'The date this ticket was last escalated - updated '
                    u'automatically by management/commands/escalate_tickets.py.')
    )

    def public_comments_count(self):
        return (apps.get_model('FollowUp').objects
                .public_followups()
                .filter(user__isnull=False, ticket=self)
                .exclude(comment__isnull=True).exclude(comment="")
                .count())

    def _get_assigned_to(self):
        """ Custom property to allow us to easily print 'Unassigned' if a
        ticket has no owner, or the users name if it's assigned. If the user
        has a full name configured, we use that, otherwise their username. """
        if not self.assigned_to:
            return _('Unassigned')
        return self.assigned_to
    get_assigned_to = property(_get_assigned_to)

    def _get_owner(self):
        """ Custom property to allow us to easily print 'Unassigned' if a
        ticket has no owner, or the users name if it's assigned. If the user
        has a full name configured, we use that, otherwise their username. """
        if not self.owner:
            return _('Unassigned')
        else:
            if self.owner.get_full_name():
                return self.owner.get_full_name()
            else:
                return self.owner.username
    get_owner = property(_get_owner)

    def _get_ticket(self):
        """ A user-friendly ticket ID, which is a combination of ticket ID
        and queue slug. This is generally used in e-mail subjects. """

        return u"[%s]" % (self.ticket_for_url)
    ticket = property(_get_ticket)

    def _get_ticket_for_url(self):
        """ A URL-friendly ticket ID, used in links. """
        return u"%s-%s" % (self.queue.slug, self.id)
    ticket_for_url = property(_get_ticket_for_url)

    def _get_priority_span(self):
        """
        A HTML <span> providing a CSS_styled representation of the priority.
        """
        return mark_safe(
            u'<center><span class="priority%s">%s</span></center>' %
            (self.priority, self.priority,))
    get_priority_span = property(_get_priority_span)

    def _get_status(self):
        """
        Displays the ticket status, with an "On Hold" message if needed.
        """
        held_msg = ''
        if self.on_hold:
            held_msg = _(' - On Hold')
        return u'%s%s' % (self.get_status_display(), held_msg)
    get_status = property(_get_status)

    def _get_ticket_url(self):
        """
        Returns a publicly-viewable URL for this ticket, used when giving
        a URL to the submitter of a ticket.
        """
        site = Site.objects.get_current()
        return u"%s?ticket=%s&email=%s" % (
            reverse('helpdesk_public_view'),
            self.ticket_for_url,
            self.submitter_email
        )
    ticket_url = property(_get_ticket_url)

    def _get_staff_url(self):
        """
        Returns a staff-only URL for this ticket, used when giving a URL to
        a staff member (in emails etc)
        """
        site = Site.objects.get_current()
        return u"http://%s%s" % (
            site.domain,
            reverse('helpdesk_view',
                    args=[self.id])
        )
    staff_url = property(_get_staff_url)

    if HAS_TAG_SUPPORT:
        tags = TagField(blank=True, verbose_name=_(u'Tags'))

    class Meta:
        get_latest_by = "created"
        verbose_name = _(u'ticket')
        verbose_name_plural = _(u'Tickets')

    def __unicode__(self):
        return u'%s' % self.title

    def get_absolute_url(self):
        return ('helpdesk_view', (self.id,))
    get_absolute_url = models.permalink(get_absolute_url)

    def save(self, force_insert=False, force_update=False):
        if not self.id:
            # This is a new ticket as no ID yet exists.
            self.created = datetime.now()

        if not self.priority:
            self.priority = 3

        self.modified = datetime.now()

        super(Ticket, self).save(force_insert, force_update)

    def render_priority(self):
        return mark_safe(
            '<span class="label %s">%s</span>' %
            (prio.get(self.priority), self.get_priority_display()))

    def get_status_color(self):
        return [y for x, y in self.STATUS_COLORS if x == self.status][0]

    def get_priority_color(self):
        return [y for x, y in self.PRIORITY_COLORS if x == self.priority][0]

    def get_priority_verbose(self):
        return [y for x, y in self.PRIORITY_CHOICES if x == self.priority][0]

    def get_absolute_url_20(self):
        return reverse('ebsweb:support_ticket', kwargs={'pk': self.pk})

    def render_id_20(self):
        return mark_safe('<span class="font-weight-bold">#{0}</span>'.format(
            self.id))

    @property
    def priority_color_20(self):
        return self.PRIORITY_COLORS_20.get(self.priority)

    @property
    def priority_verbose_20(self):
        for number, verbose in self.PRIORITY_CHOICES:
            if number == self.priority:
                return verbose

    def render_priority_20(self):
        return mark_safe(
            '<span class="m-badge m-badge--wide m-badge--{0}">{1}</span>'.format(
                self.priority_color_20, self.priority_verbose_20))

    @property
    def status_verbose_20(self):
        for code, verbose in STATUS_CHOICES:
            if self.status == code:
                return verbose

    def render_performer(self):
        if self.assigned_to:
            return self.assigned_to.username
        else:
            return ugettext(u'Не назначен')

    def render_submitter_email(self):
        if self.submitter_email:
            return self.submitter_email
        else:
            return ugettext(u'Не указан')


class TicketCC(models.Model):
    """
    Often, there are people who wish to follow a ticket who aren't the
    person who originally submitted it. This model provides a way for those
    people to follow a ticket.

    In this circumstance, a 'person' could be either an e-mail address or
    an existing system user.
    """

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        help_text=_('User who wishes to receive updates for this ticket.'),
        verbose_name=_(u'User'),
        on_delete=models.CASCADE
    )

    email = models.EmailField(
        _('E-Mail Address'),
        blank=True,
        null=True,
        help_text=_('For non-user followers, enter their e-mail address')
    )

    can_view = models.BooleanField(
        _('Can View Ticket?'),
        blank=True,
        default=False,
        help_text=_('Can this CC login to view the ticket details?')
    )

    can_update = models.BooleanField(
        _('Can Update Ticket?'),
        blank=True,
        default=False,
        help_text=_('Can this CC login and update the ticket?')
    )

    def _email_address(self):
        if self.user and self.user.email is not None:
            return self.user.email
        else:
            return self.email
    email_address = property(_email_address)

    def _display(self):
        if self.user:
            return self.user
        else:
            return self.email
    display = property(_display)

    def __unicode__(self):
        return u'%s for %s' % (self.display, self.ticket.title)

    class Meta:
        verbose_name = _(u'ticket CC')
        verbose_name_plural = _(u'Ticket CC')


class TicketChange(models.Model):
    """
    For each FollowUp, any changes to the parent ticket (eg Title, Priority,
    etc) are tracked here for display purposes.
    """

    followup = models.ForeignKey('helpdesk.FollowUp', on_delete=models.CASCADE)

    field = models.CharField(
        _('Field'),
        max_length=100,
    )

    old_value = models.TextField(
        _('Old Value'),
        blank=True,
        null=True,
    )

    new_value = models.TextField(
        _('New Value'),
        blank=True,
        null=True,
    )

    def __unicode__(self):
        str = u'%s ' % self.field
        if not self.new_value:
            str += ugettext('removed')
        elif not self.old_value:
            str += ugettext('set to %s') % self.new_value
        else:
            str += ugettext('changed from "%(old_value)s" to "%(new_value)s"') % {
                'old_value': self.old_value,
                'new_value': self.new_value
            }
        return str

    class Meta:
        verbose_name = _(u'ticket change')
        verbose_name_plural = _(u'Ticket changes')
