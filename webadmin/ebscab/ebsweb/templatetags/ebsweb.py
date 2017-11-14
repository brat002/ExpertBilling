# -*- coding: utf-8 -*-

from django.template import Library
from django.utils.translation import ugettext as _

from billservice.models import AccountViewedNews


register = Library()


@register.simple_tag(takes_context=True)
def unviewed_notifications(context):
    account = context['request'].user.account
    return AccountViewedNews.objects.filter(account=account).unviewed()


@register.filter(name='format_money')
def format_money(value):
    return '{:.2f}'.format(float(value))


@register.filter(name='default_dash')
def default_dash(value):
    if value:
        return value
    return '-'


@register.filter(name='format_traffic')
def format_traffic(value, unit='B'):
    available_units = ('B', 'KB', 'MB', 'GB')
    if unit not in available_units:
        raise ValueError(
            'Argument "unit" must be one of: ' + ','.join(available_units))
    KB = 1024
    MB = 1024 * 1024
    GB = 1024 * 1024 * 1024

    v = float(value)
    if unit == 'B':
        return _(u'{value:.2f} Б').format(value=v)
    elif unit == 'KB':
        return _(u'{value:.2f} КБ').format(value=float(v / KB))
    elif unit == 'MB':
        return _(u'{value:.2f} МБ').format(value=float(v / MB))
    elif unit == 'GB':
        return _(u'{value:.2f} МБ').format(value=float(v / GB))


@register.inclusion_tag('ebsweb/tags/progress.html')
def progress(value=None, max=None, value_text=None, max_text=None):
    context = locals()
    context['value'] = float(float(value) / (float(max) / 100))
    return context
