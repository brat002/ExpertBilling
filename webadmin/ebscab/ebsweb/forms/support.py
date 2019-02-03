# -*- coding: utf-8 -*-

import mimetypes
from datetime import datetime

from django.conf import settings
from django.forms import (
    CharField,
    ChoiceField,
    EmailField,
    FileField,
    ModelChoiceField
)
from django.forms import Form, ModelForm
from django.template import engines
from django.utils.translation import ugettext_lazy as _

from helpdesk.models import Attachment, FollowUp, Queue, Ticket, TicketChange
from helpdesk.models.ticket import STATUS_CHOICES
from helpdesk.settings import HAS_TAG_SUPPORT
from helpdesk.utils import safe_template_context, send_templated_mail

from ebsweb.forms.base import UserKwargModelFormMixin
from ebsweb.forms.widgets import (
    EmailInput,
    RadioSelect,
    Select,
    Textarea,
    TextInput
)


STATUS_CHOICES = STATUS_CHOICES[1:]


class TicketCreateForm(Form):
    queue = ModelChoiceField(
        label=_(u'Тема'),
        empty_label=_(u'Не выбрана'),
        queryset=Queue.objects.filter(allow_public_submission=True),
        widget=Select
    )
    title = CharField(
        label=_(u'Краткое описание'),
        # NOTE: from helpdesk.models.Ticket
        max_length=200,
        widget=TextInput
    )
    submitter_email = EmailField(
        label=_(u'Email адрес'),
        help_text=_(u'Мы отправим вам уведомление при обновлении этого '
                    u'запроса'),
        required=False,
        widget=EmailInput
    )
    body = CharField(
        label=_(u'Полное описание'),
        help_text=_(u'Пожалуйста, будьте максимально подробными, напишите '
                    u'любые детали, которые могут нам пригодиться, что бы '
                    u'ответить на ваш запрос'),
        widget=Textarea
    )
    priority = ChoiceField(
        label=_(u'Приоритет'),
        help_text=_(u'Пожалуйста, выбирайте ответственно'),
        choices=Ticket.PRIORITY_CHOICES,
        initial=Ticket.PRIORITY_CHOICES[2],
        widget=Select
    )
    attachment = FileField(
        label=_(u'Файл'),
        help_text=_(u'Вы можете прикрепить файл, например документ или '
                    u'скриншот экрана к этому запросу'),
        required=False
    )

    def save(self, owner):
        q = self.cleaned_data['queue']
        t = Ticket(
            title=self.cleaned_data['title'],
            owner=owner,
            submitter_email=self.cleaned_data['submitter_email'],
            created=datetime.now(),
            status=Ticket.OPEN_STATUS,
            queue=q,
            description=self.cleaned_data['body'],
            priority=self.cleaned_data['priority'],
            account=owner.account
        )
        t.save()

        f = FollowUp(
            ticket=t,
            title=_(u'Запрос создан через WEB'),
            date=datetime.now(),
            public=True,
            comment=self.cleaned_data['body'],
            account=owner.account
        )
        f.save()

        files = []
        if self.cleaned_data['attachment']:
            file = self.cleaned_data['attachment']
            filename = file.name.replace(' ', '_')
            a = Attachment(
                followup=f,
                filename=filename,
                mime_type=(mimetypes.guess_type(filename)[0] or
                           'application/octet-stream'),
                size=file.size,
            )
            a.file.save(file.name, file, save=False)
            a.save()

            if file.size < \
                    getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                # Only files smaller than 512kb (or as defined in
                # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
                files.append(a.file.path)

        context = {
            'ticket': t,
            'queue': q
        }
        messages_sent_to = []

        send_templated_mail(
            'newticket_owner',
            context,
            recipients=t.submitter_email,
            sender=q.from_address,
            fail_silently=True,
            files=files
        )
        messages_sent_to.append(t.submitter_email)

        if q.new_ticket_cc and q.new_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=q.new_ticket_cc,
                sender=q.from_address,
                fail_silently=True,
                files=files
            )
            messages_sent_to.append(q.new_ticket_cc)

        if q.updated_ticket_cc and q.updated_ticket_cc != q.new_ticket_cc and \
                q.updated_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=q.updated_ticket_cc,
                sender=q.from_address,
                fail_silently=True,
                files=files
            )

        return t


class TicketFollowupForm(UserKwargModelFormMixin, ModelForm):
    comment = CharField(
        label=_(u'Комментарий'),
        required=False,
        widget=Textarea,
    )
    new_status = ChoiceField(
        label=_(u'Новый статус'),
        required=False,
        choices=STATUS_CHOICES,
        initial=STATUS_CHOICES[0],
        widget=RadioSelect,
    )
    attachment = FileField(
        label=_(u'Файл'),
        required=False
    )

    class Meta:
        model = Ticket
        fields = ('comment', 'new_status', 'attachment')

    def clean_new_status(self):
        return int(self.cleaned_data['new_status'])

    def save(self):
        user = self.user
        ticket = self.instance
        title = self.cleaned_data.get('title', ticket.title)
        comment = self.cleaned_data['comment']
        new_status = self.cleaned_data['new_status']
        tags = self.cleaned_data.get('tags', '')

        # We need to allow the 'ticket' and 'queue' contexts to be applied to the
        # comment.
        context = safe_template_context(ticket)
        comment = engines['django'].from_string(comment).render(context)

        followup = FollowUp(
            ticket=ticket, date=datetime.now(), comment=comment)
        followup.account = user.account
        followup.public = True

        reassigned = False

        if new_status != ticket.status:
            ticket.status = new_status
            ticket.save()
            followup.new_status = new_status
            followup_title = _(u'{status} {user} '.format(
                status=ticket.status_verbose_20,
                user=user.account))
            if followup.title:
                followup.title += followup_title
            else:
                followup.title = followup_title

        if not followup.title:
            if followup.comment:
                followup.title = _(u'Добавлен комментарий от {user} '.format(
                    user=user.account))
            else:
                followup.title = _(
                    u'Обновлено {user} '.format(user=user.account))

        followup.save()
        files = []
        if self.cleaned_data['attachment']:
            file = self.cleaned_data['attachment']
            filename = file.name.replace(' ', '_')
            a = Attachment(
                followup=followup,
                filename=filename,
                mime_type=(mimetypes.guess_type(filename)[0] or
                           'application/octet-stream'),
                size=file.size
            )
            a.file.save(file.name, file, save=False)
            a.save()

            if file.size < getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                # Only files smaller than 512kb (or as defined in
                # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
                files.append(a.file.path)

        if title != ticket.title:
            c = TicketChange(
                followup=followup,
                field=_('Title'),
                old_value=ticket.title,
                new_value=title,
            )
            c.save()
            ticket.title = title

        if HAS_TAG_SUPPORT and tags != ticket.tags:
            c = TicketChange(
                followup=followup,
                field=_('Tags'),
                old_value=ticket.tags,
                new_value=tags,
            )
            c.save()
            ticket.tags = tags

        if followup.new_status == Ticket.RESOLVED_STATUS:
            ticket.resolution = comment

        messages_sent_to = []
        context.update(
            resolution=ticket.resolution,
            comment=followup.comment,
        )

        if ticket.submitter_email and \
                (followup.comment or (followup.new_status in
                                      (Ticket.RESOLVED_STATUS,
                                       Ticket.CLOSED_STATUS))):

            if followup.new_status == Ticket.RESOLVED_STATUS:
                template = 'resolved_owner'
            elif followup.new_status == Ticket.CLOSED_STATUS:
                template = 'closed_owner'
            else:
                template = 'updated_owner'

            send_templated_mail(
                template,
                context,
                recipients=ticket.submitter_email,
                sender=ticket.queue.from_address,
                fail_silently=True,
                files=files
            )
            messages_sent_to.append(ticket.submitter_email)

            for cc in ticket.ticketcc_set.all():
                if cc.email_address not in messages_sent_to:
                    send_templated_mail(
                        template,
                        context,
                        recipients=cc.email_address,
                        sender=ticket.queue.from_address,
                        fail_silently=True
                    )
                    messages_sent_to.append(cc.email_address)

        if ticket.assigned_to and user != ticket.assigned_to and \
                ticket.assigned_to.email and \
                ticket.assigned_to.email not in messages_sent_to:
            # We only send e-mails to staff members if the ticket is updated by
            # another user. The actual template varies, depending on what has been
            # changed.
            if reassigned:
                template_staff = 'assigned_to'
            elif followup.new_status == Ticket.RESOLVED_STATUS:
                template_staff = 'resolved_assigned_to'
            elif followup.new_status == Ticket.CLOSED_STATUS:
                template_staff = 'closed_assigned_to'
            else:
                template_staff = 'updated_assigned_to'

            usersettings = ticket.assigned_to.usersettings.settings
            email_on_ticket_assign = usersettings.get(
                'email_on_ticket_assign', False)
            email_on_ticket_change = usersettings.get(
                'email_on_ticket_change', False)
            if (not reassigned or (reassigned and email_on_ticket_assign)) or \
                    (not reassigned and email_on_ticket_change):
                send_templated_mail(
                    template_staff,
                    context,
                    recipients=ticket.assigned_to.email,
                    sender=ticket.queue.from_address,
                    fail_silently=True,
                    files=files
                )
                messages_sent_to.append(ticket.assigned_to.email)

        if ticket.queue.updated_ticket_cc and \
                ticket.queue.updated_ticket_cc not in messages_sent_to:
            if reassigned:
                template_cc = 'assigned_cc'
            elif followup.new_status == Ticket.RESOLVED_STATUS:
                template_cc = 'resolved_cc'
            elif followup.new_status == Ticket.CLOSED_STATUS:
                template_cc = 'closed_cc'
            else:
                template_cc = 'updated_cc'

            send_templated_mail(
                template_cc,
                context,
                recipients=ticket.queue.updated_ticket_cc,
                sender=ticket.queue.from_address,
                fail_silently=True,
                files=files
            )

        ticket.save()
