# -*- coding: utf-8 -*-

import mimetypes
from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import engines
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from helpdesk.forms import PublicTicketForm
from helpdesk.lib import (
    send_templated_mail,
    safe_template_context,
    text_is_spam
)
from helpdesk.models import (
    Attachment,
    FollowUp,
    Queue,
    Ticket,
    TicketChange
)
from helpdesk.settings import HAS_TAG_SUPPORT
from ebscab.lib.decorators import render_to, login_required


@login_required
def add_ticket(request):
    if request.user.is_staff:
        if getattr(request.user.usersettings.settings,
                   'login_view_ticketlist',
                   False):
            return HttpResponseRedirect(reverse('helpdesk_list'))
        else:
            return HttpResponseRedirect(reverse('helpdesk_dashboard'))

    if request.method == 'POST':
        form = PublicTicketForm(request.POST, request.FILES)
        form.fields['queue'].choices = [('', '--------')] + [
            [q.id, q.title]
            for q in Queue.objects.filter(allow_public_submission=True)
        ]
        if form.is_valid():
            if text_is_spam(form.cleaned_data['body'], request):
                # This submission is spam. Let's not save it.
                return get_template('helpdesk/public_spam.html').render(
                    {}, request)
            else:
                ticket = form.save(request.user)
                return HttpResponseRedirect('%s?ticket=%s&email=%s' % (
                    reverse('helpdesk_public_view'),
                    ticket.ticket_for_url,
                    ticket.submitter_email)
                )
    else:
        try:
            queue = Queue.objects.get(slug=request.GET.get('queue', None))
        except Queue.DoesNotExist:
            queue = None
        initial_data = {}
        if queue:
            initial_data['queue'] = queue.id
        if request.user.is_authenticated() and request.user.account.email:
            initial_data['submitter_email'] = request.user.account.email

        form = PublicTicketForm(initial=initial_data)
        form.fields['queue'].choices = [('', '--------')] + [
            [q.id, q.title]
            for q in Queue.objects.filter(allow_public_submission=True)
        ]

    return get_template('helpdesk/public_homepage.html').render(
        {'form': form}, request)


@login_required
def view_ticket(request):
    ticket_req = request.GET.get('ticket', '')
    ticket = False
    email = request.GET.get('email', '')
    error_message = ''

    if ticket_req:
        parts = ticket_req.split('-')
        queue = '-'.join(parts[0:-1])
        ticket_id = parts[-1]

        try:
            ticket = Ticket.objects.get(id=ticket_id, owner=request.user)
            if ticket.notify_owner:
                ticket.notify_owner = False
                ticket.save()
                ticket.notify_owner = True
        except:
            ticket = False
            error_message = _(
                'Invalid ticket ID or e-mail address. Please try again.')

        if ticket:
            if request.GET.has_key('close') and ticket.status == Ticket.RESOLVED_STATUS:
                from helpdesk.views.staff import update_ticket
                # Trick the update_ticket() view into thinking it's being called with
                # a valid POST.
                request.POST = {
                    'new_status': Ticket.CLOSED_STATUS,
                    'public': 1,
                    'owner': ticket.owner.id,
                    'title': ticket.title,
                    'comment': _(
                        'Submitter accepted resolution and closed ticket'),
                }
                request.GET = {}

                return update_ticket(request, ticket_id, public=True)

            return get_template('helpdesk/public_view_ticket.html').render(
                {'ticket': ticket}, request)

    return get_template('helpdesk/public_view_form.html').render(
        {
            'ticket': ticket,
            'email': email,
            'error_message': error_message
        },
        request)


@login_required
@render_to("accounts/account_helpdesk.html")
def view_tickets(request):
    tickets = Ticket.objects.filter(owner=request.user).order_by('-created')
    return {
        'tickets': tickets
    }


@login_required
def update_ticket(request, ticket_id, public=False):
    ticket = get_object_or_404(Ticket, id=ticket_id, owner=request.user)
    comment = request.POST.get('comment', '')
    new_status = int(request.POST.get('new_status', ticket.status))
    title = request.POST.get('title', ticket.title)
    public = True
    owner = ticket.owner
    tags = request.POST.get('tags', '')

    # We need to allow the 'ticket' and 'queue' contexts to be applied to the
    # comment.
    context = safe_template_context(ticket)
    comment = engines['django'].from_string(comment).render(context)

    f = FollowUp(ticket=ticket, date=datetime.now(), comment=comment)
    f.account = request.user.account
    f.public = True

    reassigned = False

    if new_status != ticket.status:
        ticket.status = new_status
        ticket.save()
        f.new_status = new_status
        if f.title:
            f.title += _(u'%(STATUS)s %(USER)s ') % {
                'USER': request.user.account,
                'STATUS': ticket.get_status_display()}
        else:
            f.title = _(u'%(STATUS)s %(USER)s ') % {
                'USER': request.user.account,
                'STATUS': ticket.get_status_display()}

    if not f.title:
        if f.comment:
            f.title = _(u'Добавлен комментарий от %(USER)s ') % {
                'USER': request.user.account}
        else:
            f.title = _(u'Обновлено %(USER)s ') % {
                'USER': request.user.account}

    f.save()
    files = []
    if request.FILES:
        for file in request.FILES.getlist('attachment'):
            filename = file.name.replace(' ', '_')
            a = Attachment(
                followup=f,
                filename=filename,
                mime_type=mimetypes.guess_type(
                    filename)[0] or 'application/octet-stream',
                size=file.size,
            )
            a.file.save(file.name, file, save=False)
            a.save()

            if file.size < getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                # Only files smaller than 512kb (or as defined in
                # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
                files.append(a.file.path)

    if title != ticket.title:
        c = TicketChange(
            followup=f,
            field=_('Title'),
            old_value=ticket.title,
            new_value=title,
        )
        c.save()
        ticket.title = title

    if HAS_TAG_SUPPORT:
        if tags != ticket.tags:
            c = TicketChange(
                followup=f,
                field=_('Tags'),
                old_value=ticket.tags,
                new_value=tags,
            )
            c.save()
            ticket.tags = tags

    if f.new_status == Ticket.RESOLVED_STATUS:
        ticket.resolution = comment

    messages_sent_to = []

    context.update(
        resolution=ticket.resolution,
        comment=f.comment,
    )

    if ticket.submitter_email and public and \
            (f.comment or (f.new_status in
                           (Ticket.RESOLVED_STATUS, Ticket.CLOSED_STATUS))):

        if f.new_status == Ticket.RESOLVED_STATUS:
            template = 'resolved_owner'
        elif f.new_status == Ticket.CLOSED_STATUS:
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

    if ticket.assigned_to and request.user != ticket.assigned_to and ticket.assigned_to.email and ticket.assigned_to.email not in messages_sent_to:
        # We only send e-mails to staff members if the ticket is updated by
        # another user. The actual template varies, depending on what has been
        # changed.
        if reassigned:
            template_staff = 'assigned_to'
        elif f.new_status == Ticket.RESOLVED_STATUS:
            template_staff = 'resolved_assigned_to'
        elif f.new_status == Ticket.CLOSED_STATUS:
            template_staff = 'closed_assigned_to'
        else:
            template_staff = 'updated_assigned_to'

        if (not reassigned or
            (reassigned and ticket.assigned_to.usersettings.settings.get(
                'email_on_ticket_assign', False))) or \
                (not reassigned and
                    ticket.assigned_to.usersettings.settings.get(
                        'email_on_ticket_change', False)):
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
        elif f.new_status == Ticket.RESOLVED_STATUS:
            template_cc = 'resolved_cc'
        elif f.new_status == Ticket.CLOSED_STATUS:
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

    return HttpResponseRedirect(ticket.ticket_url)
