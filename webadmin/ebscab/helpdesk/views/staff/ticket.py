# -*- coding: utf-8 -*-

import pickle
import cPickle
import mimetypes
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core import paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import engines
from django.utils.translation import ugettext as _

from billservice.utils import systemuser_required
from billservice.models import Account
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.utils.decorators import ajax_request, render_to
from object_log.models import LogItem

from helpdesk.forms import AssignToForm, EditTicketForm, FilterForm, TicketForm
from helpdesk.lib import (
    apply_query,
    b64decode,
    b64encode,
    safe_template_context,
    send_templated_mail,
    staff_member_required
)
from helpdesk.models import (
    Attachment,
    FollowUp,
    PreSetReply,
    Queue,
    SavedSearch,
    Ticket,
    TicketChange
)
from helpdesk.settings import HAS_TAG_SUPPORT
from helpdesk.tables import TicketTable

if HAS_TAG_SUPPORT:
    from tagging.models import Tag, TaggedItem


log = LogItem.objects.log_action


@staff_member_required
def tickets(request):
    if request.method == 'GET':
        items = Ticket.objects.all()
        if request.GET:
            form = FilterForm(request.GET)
            form.fields['saved_query'].queryset = SavedSearch.objects.filter(
                Q(shared=True) | Q(systemuser=request.user.account))
            filter = {}
            save = request.GET.get('save')
            run = request.GET.get('run')
            if form.is_valid():
                saved_query = form.cleaned_data.get('saved_query')

                if run:
                    print saved_query.query
                    print pickle.loads(saved_query.query)
                    # load and check query
                    data = pickle.loads(saved_query.query)
                    print data
                    form = FilterForm(data)
                    form.is_valid()

                date_start = form.cleaned_data.get('date_start')
                if date_start:
                    filter.update({'created__gte': date_start})

                date_end = form.cleaned_data.get('date_end')
                if date_end:
                    filter.update({'created__lte': date_end})

                owner = form.cleaned_data.get('owner')
                if owner:
                    filter.update({'owner': owner})

                queue = form.cleaned_data.get('queue')
                if queue:
                    filter.update({'queue__in': queue})

                account = form.cleaned_data.get('account')
                if account:
                    filter.update({'account': account})

                assigned_to = form.cleaned_data.get('assigned_to')
                if assigned_to:
                    filter.update({'assigned_to__in': assigned_to})

                assigned_to = form.cleaned_data.get('assigned_to')
                if assigned_to:
                    filter.update({'assigned_to': assigned_to})

                status = form.cleaned_data.get('status')

                if status and str(status) != '0':
                    filter.update({'status__in': status})

                priority = form.cleaned_data.get('priority')

                if priority and str(priority) != '0':
                    filter.update({'priority': priority})

                keywords = form.cleaned_data.get('keywords')

                if keywords:
                    filter.update({'title__icontains': keywords})
                    filter.update({'description__icontains': keywords})

                if save:
                    filter_name = form.cleaned_data.get('filter_name')
                    m = SavedSearch.objects.create(
                        title=filter_name,
                        query=pickle.dumps(request.GET),
                        systemuser=request.user.account,
                        shared=form.cleaned_data.get('share_filter'))
                    m.save()

                items = items.filter(**filter)
        else:
            form = FilterForm()
            form.fields['saved_query'].queryset = SavedSearch.objects.filter(
                Q(shared=True) | Q(systemuser=request.user.account))

        table = TicketTable(items)
        if request.GET.get('paginate') == 'False':
            table_paginate = False
        else:
            table_paginate = {
                'per_page': request.COOKIES.get('ebs_per_page')
            }
        table_to_report = RequestConfig(request, paginate=table_paginate)
        table_to_report = table_to_report.configure(table)
        if table_to_report:
            return create_report_http_response(table_to_report, request)

    return render(request,
                  'helpdesk/tickets.html',
                  {
                      'form': form,
                      'table': table
                  })


@systemuser_required
@render_to('helpdesk/ticket_assign.html')
def ticket_assign(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        form = AssignToForm(request.POST, request.FILES)
        if not (request.user.account.has_perm('helpdesk.ticket_reassign')):
            messages.error(request,
                           _(u'У вас нет прав на перевод заявок'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect(request.path)

        if form.is_valid():
            ticket = form.cleaned_data['ticket']
            model = ticket
            model.assigned_to = form.cleaned_data['systemuser']
            model.save(force_update=True)

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Задача переведена.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(request,
                           _(u'При переводе заявки возникли ошибки.'),
                           extra_tags='alert-danger')
            if form._errors:
                for k, v in form._errors.items():
                    messages.error(request,
                                   '%s=>%s' % (k, ','.join(v)),
                                   extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        ticket_id = request.GET.get("ticket_id")
        systemuser_id = request.GET.get("systemuser_id")

        if not (request.user.account.has_perm('helpdesk.ticket_reassign')):
            messages.error(request,
                           _(u'У вас нет прав на перевод заявок.'),
                           extra_tags='alert-danger')
            return {}
        if ticket_id:
            item = Ticket.objects.get(id=ticket_id)
            if systemuser_id and item:
                # BUG. User can assign to anyone
                item.assigned_to = request.user.account
                item.save()
                return {
                    'form': None,
                    'status': True
                }
            form = AssignToForm(initial={'ticket': item})

    return {
        'form': form,
        'status': False
    }


def update_ticket(request, ticket_id, public=False):
    if not (public or (request.user.is_authenticated() and
                       request.user.is_active and
                       request.user.is_staff)):
        return HttpResponseForbidden(_('Sorry, you need to login to do that.'))

    ticket = get_object_or_404(Ticket, id=ticket_id)
    comment = request.POST.get('comment', '')
    new_status = int(request.POST.get('new_status', ticket.status))
    title = request.POST.get('title', ticket.title)
    public = request.POST.get('public', public)
    owner = int(request.POST.get('owner', 0))
    priority = int(request.POST.get('priority', ticket.priority))
    tags = request.POST.get('tags', '')

    if public:
        ticket.notify_owner = True
    else:
        ticket.notify_owner = False
    # We need to allow the 'ticket' and 'queue' contexts to be applied to the
    # comment.
    context = safe_template_context(ticket)
    comment = engines['django'].from_string(comment).render(context)

    if owner is None and ticket.assigned_to:
        owner = ticket.assigned_to.id

    f = FollowUp(ticket=ticket, date=datetime.now(), comment=comment)

    if request.user.is_authenticated():
        f.user = request.user

    f.public = public
    reassigned = False

    if owner is not None:
        if owner != 0 and ((ticket.assigned_to and
                            owner != ticket.assigned_to.id) or not
                           ticket.assigned_to):
            new_user = User.objects.get(id=owner)
            f.title = _('Assigned to %(username)s') % {
                'username': new_user.username,
            }
            ticket.assigned_to = new_user
            reassigned = True
        elif owner == 0 and ticket.assigned_to is not None:
            f.title = _('Unassigned')
            ticket.assigned_to = None

    if new_status != ticket.status:
        ticket.status = new_status
        ticket.save()
        f.new_status = new_status
        if f.title:
            f.title += ' and %s' % ticket.get_status_display()
        else:
            f.title = '%s' % ticket.get_status_display()

    if not f.title:
        if f.comment:
            f.title = _('Comment')
        else:
            f.title = _('Updated')

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
            followup=f,
            field=_('Title'),
            old_value=ticket.title,
            new_value=title
        )
        c.save()
        ticket.title = title

    if priority != ticket.priority:
        c = TicketChange(
            followup=f,
            field=_('Priority'),
            old_value=ticket.priority,
            new_value=priority
        )
        c.save()
        ticket.priority = priority

    if HAS_TAG_SUPPORT:
        if tags != ticket.tags:
            c = TicketChange(
                followup=f,
                field=_('Tags'),
                old_value=ticket.tags,
                new_value=tags
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

    if ticket.assigned_to and \
        request.user.account != ticket.assigned_to and \
            ticket.assigned_to.email and \
            ticket.assigned_to.email not in messages_sent_to:
        # We only send e-mails to staff members if the ticket is updated by
        # another user. The actual template varies, depending on what has been
        # changed.
        if reassigned:
            template_staff = 'assigned_to'
        elif f.new_status == Ticket.RESOLVED_STATUS:
            template_staff = 'resolved_asigned_to'
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

    if request.user.is_staff:
        return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        return HttpResponseRedirect(ticket.ticket_url)


@staff_member_required
def mass_update(request):
    tickets = request.POST.getlist('ticket_id')
    action = request.POST.get('action', None)
    if not (tickets and action):
        return HttpResponseRedirect(reverse('helpdesk_list'))

    if action.startswith('assign_'):
        parts = action.split('_')
        user = User.objects.get(id=parts[1])
        action = 'assign'
    elif action == 'take':
        user = request.user
        action = 'assign'

    for t in Ticket.objects.filter(id__in=tickets):
        if action == 'assign' and t.assigned_to != user:
            t.assigned_to = user
            t.save()
            f = FollowUp(
                ticket=t,
                date=datetime.now(),
                title=_('Assigned to %(username)s in bulk update' % {
                    'username': user.username}),
                public=True,
                user=request.user)
            f.save()
        elif action == 'unassign' and t.assigned_to is not None:
            t.assigned_to = None
            t.save()
            f = FollowUp(
                ticket=t,
                date=datetime.now(),
                title=_('Unassigned in bulk update'),
                public=True,
                user=request.user)
            f.save()
        elif action == 'close' and t.status != Ticket.CLOSED_STATUS:
            t.status = Ticket.CLOSED_STATUS
            t.save()
            f = FollowUp(
                ticket=t,
                date=datetime.now(),
                title=_('Closed in bulk update'),
                public=False,
                user=request.user,
                new_status=Ticket.CLOSED_STATUS)
            f.save()
        elif action == 'close_public' and t.status != Ticket.CLOSED_STATUS:
            t.status = Ticket.CLOSED_STATUS
            t.save()
            f = FollowUp(
                ticket=t,
                date=datetime.now(),
                title=_('Closed in bulk update'),
                public=True,
                user=request.user,
                new_status=Ticket.CLOSED_STATUS)
            f.save()
            # Send email to Submitter, Owner, Queue CC
            context = {
                'ticket': t,
                'queue': t.queue,
                'resolution': t.resolution,
            }

            messages_sent_to = []

            if t.submitter_email:
                send_templated_mail(
                    'closed_owner',
                    context,
                    recipients=t.submitter_email,
                    sender=t.queue.from_address,
                    fail_silently=True
                )
                messages_sent_to.append(t.submitter_email)

            for cc in t.ticketcc_set.all():
                if cc.email_address not in messages_sent_to:
                    send_templated_mail(
                        'closed_owner',
                        context,
                        recipients=cc.email_address,
                        sender=t.queue.from_address,
                        fail_silently=True
                    )
                    messages_sent_to.append(cc.email_address)

            if t.assigned_to and \
                    request.user != t.assigned_to and \
                    t.assigned_to.email and \
                    t.assigned_to.email not in messages_sent_to:
                send_templated_mail(
                    'closed_assigned_to',
                    context,
                    recipients=t.assigned_to.email,
                    sender=t.queue.from_address,
                    fail_silently=True
                )
                messages_sent_to.append(t.assigned_to.email)

            if t.queue.updated_ticket_cc and \
                    t.queue.updated_ticket_cc not in messages_sent_to:
                send_templated_mail(
                    'closed_cc',
                    context,
                    recipients=t.queue.updated_ticket_cc,
                    sender=t.queue.from_address,
                    fail_silently=True
                )

        elif action == 'delete':
            t.delete()

    return HttpResponseRedirect(reverse('helpdesk_list'))


@staff_member_required
def ticket_list(request):
    context = {}

    # Query_params will hold a dictionary of paramaters relating to
    # a query, to be saved if needed:
    query_params = {
        'filtering': {},
        'sorting': None,
        'sortreverse': False,
        'keyword': None,
        'other_filter': None,
    }

    from_saved_query = False

    # If the user is coming from the header/navigation search box, lets' first
    # look at their query to see if they have entered a valid ticket number. If
    # they have, just redirect to that ticket number. Otherwise, we treat it as
    # a keyword search.

    if request.GET.get('search_type', None) == 'header':
        query = request.GET.get('q')
        filter = None
        if query.find('-') > 0:
            queue, id = query.split('-')
            try:
                id = int(id)
            except ValueError:
                id = None

            if id:
                filter = {
                    'queue__slug': queue,
                    'id': id
                }
        else:
            try:
                query = int(query)
            except ValueError:
                query = None

            if query:
                filter = {
                    'id': int(query)
                }

        if filter:
            try:
                ticket = Ticket.objects.get(**filter)
                return HttpResponseRedirect(ticket.staff_url)
            except Ticket.DoesNotExist:
                # Go on to standard keyword searching
                pass

    if request.GET.get('saved_query', None):
        from_saved_query = True
        try:
            saved_query = SavedSearch.objects.get(
                pk=request.GET.get('saved_query'))
        except SavedSearch.DoesNotExist:
            return HttpResponseRedirect(reverse('helpdesk_list'))
        if not (saved_query.shared or saved_query.user == request.user):
            return HttpResponseRedirect(reverse('helpdesk_list'))

        query_params = cPickle.loads(b64decode(str(saved_query.query)))
    elif not (request.GET.has_key('queue') or
              request.GET.has_key('assigned_to') or
              request.GET.has_key('owner') or
              request.GET.has_key('status') or
              request.GET.has_key('q') or
              request.GET.has_key('sort') or
              request.GET.has_key('sortreverse') or
              request.GET.has_key('tags')):

        # Fall-back if no querying is being done, force the list to only
        # show open/reopened/resolved (not closed) cases sorted by creation
        # date.

        query_params = {
            'filtering': {
                'status__in': [1, 2, 3]
            },
            'sorting': 'created'
        }
    else:
        queues = request.GET.getlist('queue')
        if queues:
            queues = [int(q) for q in queues]
            query_params['filtering']['queue__id__in'] = queues

        assigned_to = request.GET.getlist('assigned_to')
        if assigned_to:
            assigned_to = [int(u) for u in assigned_to]
            query_params['filtering']['assigned_to__id__in'] = assigned_to

        owner = request.GET.getlist('owner')
        if owner:
            owner = [int(u) for u in owner]
            query_params['filtering']['owner__id__in'] = owner

        statuses = request.GET.getlist('status')
        if statuses:
            statuses = [int(s) for s in statuses]
            query_params['filtering']['status__in'] = statuses

        # KEYWORD SEARCHING
        q = request.GET.get('q', None)

        if q:
            qset = (
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(resolution__icontains=q) |
                Q(submitter_email__icontains=q)
            )
            context = dict(context, query=q)

            query_params['other_filter'] = qset

        # SORTING
        sort = request.GET.get('sort', None)
        if sort not in ('status', 'assigned_to', 'created', 'title',
                        'queue', 'priority'):
            sort = 'created'
        query_params['sorting'] = sort
        sortreverse = request.GET.get('sortreverse', None)
        query_params['sortreverse'] = sortreverse

    ticket_qs = apply_query(Ticket.objects.select_related(), query_params)

    # TAG MATCHING
    if HAS_TAG_SUPPORT:
        tags = request.GET.getlist('tags')
        if tags:
            ticket_qs = TaggedItem.objects.get_by_model(ticket_qs, tags)
            query_params['tags'] = tags

    ticket_paginator = paginator.Paginator(
        ticket_qs,
        request.user.usersettings.settings.get('tickets_per_page') or 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tickets = ticket_paginator.page(page)
    except (paginator.EmptyPage, paginator.InvalidPage):
        tickets = ticket_paginator.page(ticket_paginator.num_pages)

    search_message = ''
    if context.has_key('query') and settings.DATABASE_ENGINE.startswith('sqlite'):
        search_message = _('''\
<p><strong>Note:</strong> Your keyword search is case sensitive because of \
your database. This means the search will <strong>not</strong> be accurate. \
By switching to a different database system you will gain better searching! \
For more information, read the \
<a href="http://docs.djangoproject.com/en/dev/ref/databases/#sqlite-string-matching">\
Django Documentation on string matching in SQLite</a>.''')

    urlsafe_query = b64encode(cPickle.dumps(query_params))
    user_saved_queries = SavedSearch.objects.filter(
        Q(user=request.user) | Q(shared__exact=True))

    query_string = []
    for get_key, get_value in request.GET.iteritems():
        if get_key != "page":
            query_string.append("%s=%s" % (get_key, get_value))

    tag_choices = []
    if HAS_TAG_SUPPORT:
        # FIXME: restrict this to tags that are actually in use
        tag_choices = Tag.objects.all()

    return render(request,
                  'helpdesk/ticket_list.html',
                  dict(
                      context,
                      query_string="&".join(query_string),
                      tickets=tickets,
                      assigned_to_choices=User.objects.filter(
                          is_active=True, is_staff=True),
                      owner_choices=User.objects.filter(
                          is_active=True),
                      queue_choices=Queue.objects.all(),
                      status_choices=Ticket.STATUS_CHOICES,
                      tag_choices=tag_choices,
                      urlsafe_query=urlsafe_query,
                      user_saved_queries=user_saved_queries,
                      query_params=query_params,
                      from_saved_query=from_saved_query,
                      search_message=search_message,
                      tags_enabled=HAS_TAG_SUPPORT
                  ))


@staff_member_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = EditTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()
            return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        form = EditTicketForm(instance=ticket)

    return render(request,
                  'helpdesk/create_ticket.html',
                  {
                      'form': form,
                      'tags_enabled': HAS_TAG_SUPPORT
                  })


@staff_member_required
def create_ticket(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            ticket = get_object_or_404(Ticket, id=id)
            form = EditTicketForm(request.POST, request.FILES, instance=ticket)
        else:
            form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            if id:
                ticket = form.save()
            else:
                ticket = form.save(user=request.user)
            return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        initial_data = {}
        id = request.GET.get('id')
        account_id = request.GET.get('account_id')
        if account_id:
            initial_data['account'] = Account.objects.get(id=account_id)

        if request.user.usersettings.settings.get(
                'use_email_as_submitter', False) and \
                request.user.account.email:
            initial_data['submitter_email'] = request.user.account.email

        if id:
            ticket = get_object_or_404(Ticket, id=id)
            form = EditTicketForm(instance=ticket)
        else:
            form = TicketForm(initial=initial_data)

        form.fields['assigned_to'].initial = request.user.account
        form.fields['owner'].initial = request.user

    return render(request,
                  'helpdesk/create_ticket.html',
                  {
                      'form': form,
                      'tags_enabled': HAS_TAG_SUPPORT
                  })


@systemuser_required
@ajax_request
def ticket_info(request):
    ticket = Ticket.objects.get(id=request.GET.get('id'))
    return {
        'body': ticket.description
    }


@staff_member_required
def delete_ticket(request, ticket_id):
    if not (request.user.account.has_perm('helpdesk.delete_ticket')):
        messages.error(request,
                       _(u'У вас нет прав на удаление заявок'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect(request.path)
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'GET':
        return render(request,
                      'helpdesk/delete_ticket.html',
                      {'ticket': ticket})
    else:
        ticket.delete()
        return HttpResponseRedirect(reverse('helpdesk_home'))


@staff_member_required
def view_ticket(request, ticket_id):
    if not (request.user.account.has_perm('helpdesk.view_ticket')):
        messages.error(request,
                       _(u'У вас нет прав на просмотр заявок'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect(request.path)
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.GET.has_key('take'):
        # Allow the user to assign the ticket to themselves whilst viewing it.
        ticket.assigned_to = request.user.account
        ticket.save()

    if request.GET.has_key('close') and \
            ticket.status == Ticket.RESOLVED_STATUS:
        if not ticket.assigned_to:
            owner = 0
        else:
            owner = ticket.assigned_to.id

        # Trick the update_ticket() view into thinking it's being called with
        # a valid POST.
        request.POST = {
            'new_status': Ticket.CLOSED_STATUS,
            'public': 1,
            'owner': owner,
            'title': ticket.title,
            'comment': _('Accepted resolution and closed ticket')
        }

        return update_ticket(request, ticket_id)

    return render(request,
                  'helpdesk/ticket.html',
                  {
                      'ticket': ticket,
                      'active_users': (User.objects
                                       .filter(is_active=True)
                                       .filter(is_staff=True)),
                      'priorities': Ticket.PRIORITY_CHOICES,
                      'preset_replies': (PreSetReply.objects
                                         .filter(Q(queues=ticket.queue) |
                                                 Q(queues__isnull=True))),

                      'tags_enabled': HAS_TAG_SUPPORT
                  })


@staff_member_required
def hold_ticket(request, ticket_id, unhold=False):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if unhold:
        ticket.on_hold = False
        title = _('Ticket taken off hold')
    else:
        ticket.on_hold = True
        title = _('Ticket placed on hold')

    f = FollowUp(
        ticket=ticket,
        systemuser=request.user.account,
        title=title,
        date=datetime.now(),
        public=True,
    )
    f.save()

    ticket.save()

    return HttpResponseRedirect(ticket.get_absolute_url())


@staff_member_required
def unhold_ticket(request, ticket_id):
    return hold_ticket(request, ticket_id, unhold=True)
