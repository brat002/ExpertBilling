# -*- coding:utf-8 -*-
from django import template

register = template.Library()

@register.inclusion_tag("helpdesk/templatetags/pannel_ticket_table.html")
def pannel_ticket_table(objects, objects_id):
    context = {}
    context['object_name'] = objects
    context['object_id'] = objects_id
    return context

@register.inclusion_tag("helpdesk/templatetags/table_tickets.html")
def table_ticket(object_var):
    context = {}
    object_var
    context['object'] = object_var
    return context
