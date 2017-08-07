# -*- coding: utf-8 -*-

import datetime

import pytils
from django import template
from django.conf import settings

from lib.threadlocals import get_request


register = template.Library()

words = {
    u'отзыв': (u'отзыв, отзыва, отзывов', u'отзывов нет'),
    u'comment': (u'комментарий, комментария, комментариев',
                 u'Комментариев нет'),
    u'user': (u'пользователь, пользователя, пользователей',
              u'пользователей нет'),
    u'vote': (u'голос, голоса, голосов', u'голосов нет'),
}


def date_with_offset(value, arg):
    # Usage of date format
    # "%d %B %Y" = 12 january 2007
    # %d %B %Y, %H:%M
    try:
        timeoffset = get_request().user.timeoffset
        if not timeoffset:
            timeoffset = 0
    except:
        timeoffset = 0

    if not value:
        return u''
    if arg is None:
        arg = settings.DATE_FORMAT
    return pytils.dt.ru_strftime(
        arg,
        inflected=True,
        date=value + datetime.timedelta(seconds=timeoffset))


date_with_offset.is_safe = False
register.filter('date_with_offset', date_with_offset)


def ru_date(value, arg=u"%d %B %Y"):
    return pytils.dt.ru_strftime(arg, inflected=True, date=value)

register.filter('ru_date', ru_date)


@register.filter
def in_list(value, arg):
    return value in arg


@register.filter
def get_plural(value, arg):
    variants = words.get(arg, None)
    if not variants:
        return ''
    return pytils.numeral.get_plural(
        int(value), variants[0], absence=variants[1])


@register.filter
def choose_plural(value, arg):
    variants = words.get(arg, None)
    if not variants:
        return ''
    return pytils.numeral.choose_plural(int(value), variants[0])


@register.filter
def arithmetic(value, arg):
    funcs = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
    }
    try:
        return int(funcs[arg[0:1]](int(value), float(arg[1:])))
    except:
        return value
