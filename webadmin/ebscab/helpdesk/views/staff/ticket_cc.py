# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from helpdesk.forms import TicketCCForm
from helpdesk.lib import staff_member_required
from helpdesk.models import Ticket, TicketCC


@staff_member_required
def ticket_cc(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    copies_to = ticket.ticketcc_set.all()
    return render(request,
                  'helpdesk/ticket_cc_list.html',
                  {
                      'copies_to': copies_to,
                      'ticket': ticket
                  })


@staff_member_required
def ticket_cc_add(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = TicketCCForm(request.POST)
        if form.is_valid():
            ticketcc = form.save(commit=False)
            ticketcc.ticket = ticket
            ticketcc.save()
            return HttpResponseRedirect(reverse(
                'helpdesk_ticket_cc',
                kwargs={'ticket_id': ticket.id}))
    else:
        form = TicketCCForm()
    return render(request,
                  'helpdesk/ticket_cc_add.html',
                  {
                      'ticket': ticket,
                      'form': form
                  })


@staff_member_required
def ticket_cc_del(request, ticket_id, cc_id):
    cc = get_object_or_404(TicketCC, ticket__id=ticket_id, id=cc_id)
    if request.method == 'POST':
        cc.delete()
        return HttpResponseRedirect(reverse(
            'helpdesk_ticket_cc',
            kwargs={'ticket_id': cc.ticket.id}))
    return render(request, 'helpdesk/ticket_cc_del.html', {'cc': cc})
