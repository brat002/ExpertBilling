# -*- coding:utf-8 -*-
# $Id$
import datetime
from django import forms
from django.forms.widgets import Widget, Select, Input, CheckboxInput
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.encoding import smart_unicode
from django.template import loader, Context
from django.utils.simplejson import JSONEncoder
from django.conf import settings

class JQueryAutoCompleteFilter(forms.TextInput):
    def __init__(self, source, options={}, attrs={}):
        """source can be a list containing the autocomplete values or a
        string containing the url used for the XHR request.

        For available options see the autocomplete sample page::
        sources: http://bassistance.de/jquery-plugins/jquery-plugin-autocomplete/
        demo: http://jquery.bassistance.de/autocomplete/
        """

        self.options = None
        self.attrs = {'autocomplete': 'on'}
        self.source = source
        if len(options) > 0:
            self.options = JSONEncoder().encode(options)

        self.attrs.update(attrs)

    def render_js(self, field_id):
        if isinstance(self.source, list):
            source = JSONEncoder().encode(self.source)
        elif isinstance(self.source, str):
            source = "'%s'" % escape(self.source)
        else:
            raise ValueError('source type is not valid')

        options = ''
        if self.options:
            options += ',%s' % self.options
        return u"""jQuery('#%s').autocomplete(%s%s);""" % (field_id, source, options)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = escape(smart_unicode(value))

        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name

        return mark_safe(u'''<input type="text" %(attrs)s/><a href="#" class="selector-search" onclick="user_filter()"><img src="%(media_url)shelpdesk_img/selector-search.gif"></a>
        <script type="text/javascript">%(js)s</script>
        ''' % {
                'attrs' : forms.util.flatatt(final_attrs),
                'js' : self.render_js(final_attrs['id']),
                'media_url':settings.MEDIA_URL,
        })

class SelectDateTimeWidget(Widget):

    month_field = '%s_month'
    day_field = '%s_day'
    year_field = '%s_year'
    hour_field = '%s_hour'
    minute_field = '%s_minute'
    null_field = '%s_null'
    template = 'lib/widgets/select_date_time_widget.html'

    def __init__(self, attrs=None, years=None, show_time=True, default=None, null=False):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year-2, this_year+3)
        self.show_time = show_time
        if isinstance(default, datetime.datetime):
            self.default = default
        else:
            self.default = datetime.datetime.now()
        self.null = null
        self.is_null = False

    def render(self, name, value, attrs=None):
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            value = datetime.datetime(value.year, value.month, value.day)
        if not value:
            value = self.default
        elif type(value) in ('str', 'unicode'):
            try:
                value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M')
            except:
                value = self.default
        year_val, month_val, day_val, hour_val, minute_val = value.year, value.month, value.day, value.hour, value.minute
        output = []
        month_choices = MONTHS.items()
        month_choices.sort()
        select_html = Select(choices=month_choices).render(self.month_field % name, month_val)
        output.append(select_html)

        day_choices = [(i, i) for i in range(1, 32)]
        select_html = Select(choices=day_choices, attrs={'style':'width: 50px'}).render(self.day_field % name, day_val)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        select_html = Select(choices=year_choices, attrs={'style':'width: 70px'}).render(self.year_field % name, year_val)
        output.append(select_html)

        if self.show_time:
            html = Input(attrs={'size':5}).render(self.hour_field % name, hour_val)
            output.append('&nbsp;&nbsp;' + html)

            html = Input(attrs={'size':5}).render(self.minute_field % name, minute_val)
            output.append(html)

        null_field = None
        if self.null:
            null_field = CheckboxInput(attrs={'id': self.null_field % name}).render(self.null_field % name, self.is_null)

        t = loader.get_template(self.template)
        return t.render(Context({
                                 'select_field': mark_safe(u'\n'.join(output)),
                                 'null_field': null_field,
                                 'name': name,
                                 }))

    def value_from_datadict(self, data, files, name):
        null_field = self.null_field % name
        if null_field in data and data[null_field]:
            self.is_null = True
            return None

        y, m, d, h, mi = data.get(self.year_field % name, None), data.get(self.month_field % name, None), data.get(self.day_field % name, None), data.get(self.hour_field % name, None) or u'00', data.get(self.minute_field % name, None) or u'00'
        if y and m and d:
            return '%s-%s-%s %s:%s' % (y, m, d, h, mi)

        value = data.get(name, None)
        if not value:
            self.is_null = True
        return value