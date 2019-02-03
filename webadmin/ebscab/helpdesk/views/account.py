# -*- coding: utf-8 -*-
# $Id: account.py 56 2010-05-27 14:46:53Z dmitry $

""" VIEWS FOR CLIENT """

from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from helpdesk.forms import PublicTicketForm
from helpdesk.models import Queue, Ticket
from helpdesk.views.staff import update_ticket
from ebscab.utils.decorators import render_to, login_required


PublicTicketForm.base_fields['title'].widget.attrs = {'size': 80}
PublicTicketForm.base_fields['queue'].label = _(u'Ticket theme')


@login_required
@render_to('helpdesk/account/list.html')
def list_tickets(request):
    """List of tickets, created by a user"""
    context = {'title': _(u'Tickets')}
    tickets = Ticket.objects.filter(owner=request.user).order_by('-created')
    context['tickets'] = tickets
    context['current_view_name'] = 'helpdesk_account_tickets'
    return context


@login_required
@render_to('helpdesk/account/create.html')
def create_ticket(request):
    """ Creates a new ticket """
    context = {'title': _(u'Create a ticket')}
    context['current_view_name'] = 'helpdesk_account_tickets_add'

    if request.method == 'POST':
        form = PublicTicketForm(request.POST.copy())
        form.fields['queue'].choices = [
            [q.id, q.title]
            for q in Queue.objects.filter(allow_public_submission=True)
        ]
        if form.is_valid():
            ticket = form.save()
            ticket.owner = request.user
            ticket.account = request.user.account
            ticket.save()
            request.notifications.add(
                _(u'Ticket was created successfully and will be '
                  u'processed shortly'),
                'success')
            return HttpResponseRedirect(reverse('helpdesk_account_tickets'))
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
            initial_data['submitter'] = request.user.id

        form = PublicTicketForm(initial=initial_data)
        if 'submitter_email' in initial_data:
            PublicTicketForm.base_fields[
                'submitter_email'].widget = forms.HiddenInput()
        form.fields['queue'].choices = [
            [q.id, q.title]
            for q in Queue.objects.filter(allow_public_submission=True)
        ]
    context['form'] = form
    return context


@login_required
@render_to('helpdesk/account/view.html')
def view_ticket(request, ticket_id):
    """ Show a ticket comments, accepts new comments from user """
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == 'POST':
        if 'comment' in request.POST:
            _resp = update_ticket(request, ticket.id, public=True)
            del _resp
            request.notifications.add(u"Комментарий успешно сохранен",
                                      'success')

    return {
        'ticket': ticket,
        'current_view_name': 'helpdesk_account_tickets_view'
    }


@login_required
def reopen_ticket(request, ticket_id):
    """ Reopen ticket, created by user early """
    return {}
