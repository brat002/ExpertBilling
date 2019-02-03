# -*- coding: utf-8 -*-

"""
Jutda Helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

views/feeds.py - A handful of staff-only RSS feeds to provide ticket details
                 to feed readers or similar software.
"""

from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.translation import ugettext as _

from helpdesk.models import Ticket, FollowUp, Queue


class OpenTicketsByUser(Feed):
    title_template = 'helpdesk/rss/ticket_title.html'
    description_template = 'helpdesk/rss/ticket_description.html'

    def get_object(self, bits):
        if len(bits) < 1:
            raise ObjectDoesNotExist
        user = User.objects.get(username__exact=bits[0])
        if len(bits) == 2:
            queue = Queue.objects.get(slug__exact=bits[1])
        else:
            queue = False

        return {
            'user': user,
            'queue': queue
        }

    def title(self, obj):
        if obj['queue']:
            return _("Helpdesk: Open Tickets in queue %(queue)s for %(username)s") % {
                'queue': obj['queue'].title,
                'username': obj['user'].username,
            }
        else:
            return _("Helpdesk: Open Tickets for %(username)s") % {
                'username': obj['user'].username,
            }

    def description(self, obj):
        if obj['queue']:
            return _("Open and Reopened Tickets in queue %(queue)s for %(username)s") % {
                'queue': obj['queue'].title,
                'username': obj['user'].username,
            }
        else:
            return _("Open and Reopened Tickets for %(username)s") % {
                'username': obj['user'].username,
            }

    def link(self, obj):
        if obj['queue']:
            return u'%s?assigned_to=%s&queue=%s' % (
                reverse('helpdesk_list'),
                obj['user'].id,
                obj['queue'].id,
            )
        else:
            return u'%s?assigned_to=%s' % (
                reverse('helpdesk_list'),
                obj['user'].id,
            )

    def items(self, obj):
        if obj['queue']:
            return (Ticket.objects
                    .filter(assigned_to=obj['user'])
                    .filter(queue=obj['queue'])
                    .filter(Q(status=Ticket.OPEN_STATUS) |
                            Q(status=Ticket.REOPENED_STATUS)))
        else:
            return (Ticket.objects
                    .filter(assigned_to=obj['user'])
                    .filter(Q(status=Ticket.OPEN_STATUS) |
                            Q(status=Ticket.REOPENED_STATUS)))

    def item_pubdate(self, item):
        return item.created

    def item_author_name(self, item):
        if item.assigned_to:
            return item.assigned_to.username
        else:
            return _('Unassigned')


class UnassignedTickets(Feed):
    title_template = 'helpdesk/rss/ticket_title.html'
    description_template = 'helpdesk/rss/ticket_description.html'

    title = _('Helpdesk: Unassigned Tickets')
    description = _('Unassigned Open and Reopened tickets')
    link = ''  # %s?assigned_to=' % reverse('helpdesk_list')

    def items(self, obj):
        return Ticket.objects.filter(
            assigned_to__isnull=True
        ).filter(
            Q(status=Ticket.OPEN_STATUS) | Q(status=Ticket.REOPENED_STATUS)
        )

    def item_pubdate(self, item):
        return item.created

    def item_author_name(self, item):
        if item.assigned_to:
            return item.assigned_to.username
        else:
            return _('Unassigned')


class RecentFollowUps(Feed):
    title_template = 'helpdesk/rss/recent_activity_title.html'
    description_template = 'helpdesk/rss/recent_activity_description.html'

    title = _('Helpdesk: Recent Followups')
    description = _(
        'Recent FollowUps, such as e-mail replies, comments, attachments and resolutions')
    link = '/tickets/'  # reverse('helpdesk_list')

    def items(self):
        return FollowUp.objects.order_by('-date')[:20]


class OpenTicketsByQueue(Feed):
    title_template = 'helpdesk/rss/ticket_title.html'
    description_template = 'helpdesk/rss/ticket_description.html'

    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Queue.objects.get(slug__exact=bits[0])

    def title(self, obj):
        return _('Helpdesk: Open Tickets in queue %(queue)s') % {
            'queue': obj.title,
        }

    def description(self, obj):
        return _('Open and Reopened Tickets in queue %(queue)s') % {
            'queue': obj.title,
        }

    def link(self, obj):
        return '%s?queue=%s' % (
            reverse('helpdesk_list'),
            obj.id,
        )

    def items(self, obj):
        return (Ticket.objects
                .filter(queue=obj)
                .filter(Q(status=Ticket.OPEN_STATUS) |
                        Q(status=Ticket.REOPENED_STATUS)))

    def item_pubdate(self, item):
        return item.created

    def item_author_name(self, item):
        if item.assigned_to:
            return item.assigned_to.username
        else:
            return _('Unassigned')


feed_setup = {
    'user': OpenTicketsByUser,
    'queue': OpenTicketsByQueue,
    'recent_activity': RecentFollowUps,
    'unassigned': UnassignedTickets,
}
