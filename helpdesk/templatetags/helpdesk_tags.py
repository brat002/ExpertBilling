# -*- coding:utf-8 -*-
from django import template

register = template.Library()

@register.inclusion_tag("helpdesk/templatetags/table_tickets.html")
def table_ticket(object_var):
    context = {}
    context['object'] = object_var
    context['object_name'] = object_var._meta.object_name
    print context['object_name']
    return context