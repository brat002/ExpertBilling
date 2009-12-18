# -*- coding:utf-8 -*-
from django import template

register = template.Library()

@register.inclusion_tag("helpdesk/templatetags/table_tickets.html")
def table_ticket(objects):
    context = {}
    context['objects'] = objects
    print objects
    return context