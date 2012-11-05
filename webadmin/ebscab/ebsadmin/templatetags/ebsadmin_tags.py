from django import template
from ebsadmin.lib import digg_paginator
from django.utils.encoding import force_unicode
import re
from ebsadmin.forms import chartdata
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.filter(name='format_paginator')          
def format_paginator(cnt, current ):
    d = digg_paginator(len(cnt), current)
    res =[] 
    if d['pages_outside_trailing_range']:
        res +=d['pages_outside_trailing_range'] +['...']
    res +=d['page_numbers']
    if d['pages_outside_leading_range']:
        res +=['...'] + d['pages_outside_leading_range']

    return res

@register.filter('intspace')
def intspace(value):
    """
    Converts an integer to a string containing spaces every three digits.
    For example, 3000 becomes '3 000' and 45000 becomes '45 000'.
    See django.contrib.humanize app
    """
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1> \g<2>', orig)
    if orig == new:
        return new
    else:
        return intspace(new)
    
    
@register.inclusion_tag('ebsadmin/tags/charts.html')
def charts_menu():
    
    return {'chartdata': sorted([(x, chartdata[x].get('name')) for x in chartdata],  key=lambda k: k[1])}

@register.inclusion_tag('ebsadmin/tags/objectlog_link.html')
def objectlog(o):
    ct_id = None
    if o:
        ct_id = ContentType.objects.get_for_model(o).id
    
    return {'ct_id': ct_id, 'item':o}
