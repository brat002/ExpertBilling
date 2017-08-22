# -*- coding: utf-8 -*-

import datetime
import re

from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

from django_tables2.config import RequestConfig

from ebsadmin.forms import chartdata
from ebsadmin.lib import digg_paginator
from ebsadmin.models import Comment
from ebsadmin.reportsystem.reports import rep
from ebsadmin.tables import CommentTable


register = template.Library()


@register.filter(name='format_paginator')
def format_paginator(cnt, current):
    d = digg_paginator(len(cnt), current)
    res = []
    if d['pages_outside_trailing_range']:
        res += d['pages_outside_trailing_range'] + ['...']
    res += d['page_numbers']
    if d['pages_outside_leading_range']:
        res += ['...'] + d['pages_outside_leading_range']

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
    return {
        'chartdata': sorted([(x, chartdata[x].get('name')) for x in chartdata],
                            key=lambda k: k[1])
    }


@register.inclusion_tag('ebsadmin/tags/textreports.html')
def textreports_menu():
    return {
        'reports': sorted([(x, rep[x][-1]) for x in rep], key=lambda k: k[1])
    }


@register.inclusion_tag('ebsadmin/tags/objectlog_link.html')
def objectlog(o):
    ct_id = None
    if o:
        ct_id = ContentType.objects.get_for_model(o).id

    return {
        'ct_id': ct_id,
        'item': o
    }


@register.inclusion_tag('ebsadmin/tags/object_comments.html', takes_context=True)
def object_comments(context, o):
    if not o:
        return {}
    ct = ContentType.objects.get_for_model(o)
    res = Comment.objects.filter(content_type=ct, object_id=o.id)
    comment_table = CommentTable(res)
    RequestConfig(
        context['request'],
        paginate=(False if context['request'].GET.get('paginate') == 'False'
                  else True)).configure(comment_table)

    return {
        'table': comment_table,
        'item': o,
        'request': context['request'],
        'content_type_id': ct.id
    }


def permission(parser, token):
    try:
        # get the arguments passed to the template tag;
        # first argument is the tag name
        tag_name, perm = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly 1 arguments" % token.contents.split()[0])
    # look for the 'endpermission' terminator tag
    nodelist = parser.parse(('endpermission',))
    parser.delete_first_token()
    return PermissionNode(nodelist, perm)


class PermissionNode(template.Node):

    def __init__(self, nodelist, permission):
        self.nodelist = nodelist
        # evaluate the user instance as a variable and store
        self.request = template.Variable('request')
        # store the permission string
        self.permission = permission

    def render(self, context):
        request = self.request.resolve(context)
        if request.user.account.has_perm(self.permission):
            content = self.nodelist.render(context)
            return content
        return ""


@register.assignment_tag(takes_context=True)
def get_server_time(context):
    try:
        return datetime.datetime.now()
    except:
        return None

register.tag('permission', permission)
