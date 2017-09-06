# -*- coding: utf-8 -*-

from django.shortcuts import render

from billservice.utils import systemuser_required
from ebscab.utils.decorators import render_to

from helpdesk.forms import TicketTypeForm
from helpdesk.utils import staff_member_required
from helpdesk.models import Queue


@systemuser_required
@render_to('helpdesk/queueselect_window.html')
def queueselect(request):
    form = TicketTypeForm()
    return {
        'form': form
    }


@staff_member_required
def rss_list(request):
    return render(request,
                  'helpdesk/rss_list.html',
                  {'queues': Queue.objects.all()})
