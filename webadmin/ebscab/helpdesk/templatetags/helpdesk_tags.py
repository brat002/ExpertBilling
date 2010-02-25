# -*- coding:utf-8 -*-
from django import template
from django.conf import settings

from helpdesk.models import Note

register = template.Library()

@register.inclusion_tag("helpdesk/templatetags/pannel_ticket_table.html")
def pannel_ticket_table(object_name, object_id):
    context = {}
    context['object_name'] = object_name
    context['object_id'] = object_id
    context["media_url"] = settings.MEDIA_URL
    return context

@register.inclusion_tag("helpdesk/templatetags/table_tickets.html")
def table_ticket(object_var, object_name, order_by, order_by_reverse, count):
    context = {}
    context['object'] = object_var
    tickets_id = object_var.get_tickets().values_list('id', flat=True)[:count]
    tickets = object_var.get_tickets().filter(id__in=tickets_id).order_by('-%s'%(order_by) if not order_by_reverse else '%s'%(order_by) )
    context['tickets'] = tickets
    context['object_name']=object_name
    context["media_url"] = settings.MEDIA_URL
    context['order_by'] = order_by
    context['order_by_reverse'] = order_by_reverse
    context['count'] = count
    context['MEDIA_URL'] = settings.MEDIA_URL
    return context

@register.inclusion_tag("helpdesk/templatetags/get_note.html")
def get_note(history_item):
    notes = Note.objects.filter(history = history_item)
    return {
            'notes':notes,
            }
    
@register.filter(name='normal_name')    
def normal_name(value):
    value = value.split('/')
    return value[len(value)-1]

@register.inclusion_tag("helpdesk/templatetags/get_note.html")
def ticket_get_note(ticket):
    notes = Note.objects.filter(ticket = ticket)
    return {
            'notes':notes,
            }




