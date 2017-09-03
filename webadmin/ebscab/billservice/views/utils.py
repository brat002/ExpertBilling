# -*- coding: utf-8 -*-

import datetime

from billservice.forms import StatististicForm


def addon_queryset(request, id_begin, field='datetime', field_to=None):
    if field_to == None:
        field_to = field

    addon_query = {}
    form = StatististicForm(request.GET)
    date_id_dict = request.session.get('date_id_dict', {})
    if form.is_valid():
        if form.cleaned_data['date_from']:
            addon_query[field + '__gte'] = form.cleaned_data['date_from']
            date_id_dict[id_begin + '_date_from'] = \
                request.GET.get('date_from', '')
        else:
            if date_id_dict.has_key(id_begin + '_date_from'):
                del(date_id_dict[id_begin + '_date_from'])
        if form.cleaned_data['date_to']:

            addon_query[field_to + '__lte'] = form.cleaned_data['date_to'] + \
                datetime.timedelta(hours=23, minutes=59, seconds=59)
            date_id_dict[id_begin +
                         '_date_to'] = request.GET.get('date_to', '')
        else:
            if date_id_dict.has_key(id_begin + '_date_to'):
                del(date_id_dict[id_begin + '_date_to'])
        request.session['date_id_dict'] = date_id_dict
        request.session.modified = True
    if request.GET.has_key('date_from') or request.GET.has_key('date_to'):
        is_range = True
    else:
        is_range = False
    return is_range, addon_query
