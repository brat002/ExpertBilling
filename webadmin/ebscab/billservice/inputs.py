# -*- coding: utf-8 -*-

from base64 import b64encode, b64decode
from itertools import chain

from Crypto.Cipher import ARC4
from django import forms
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


class PasswordTextInput(forms.widgets.Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if attrs.get('id'):
            attrs['id'] = attrs['id'].replace('_0', '')
        return super(PasswordTextInput, self).render(name, value, attrs=attrs)


class HiddenPasswordInput(forms.widgets.Input):
    input_type = 'hidden'

    def __init__(self, attrs=None):
        super(HiddenPasswordInput, self).__init__(attrs)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if not value:
            return None
        obj1 = ARC4.new(settings.PGCRYPTO_DEFAULT_KEY)
        value = obj1.decrypt(b64decode(value))
        return value

    def render(self, name, value, attrs=None):
        obj1 = ARC4.new(settings.PGCRYPTO_DEFAULT_KEY)
        value = b64encode(obj1.encrypt(unicode(value)))
        return super(HiddenPasswordInput, self).render(name, value, attrs)


class MyMultipleCheckBoxInput(forms.widgets.CheckboxSelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs)
        output = []
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(
                chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(
                final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<label class="radio inline" %s>%s %s</label>' %
                          (label_for, rendered_cb, option_label))
        return mark_safe(u'\n'.join(output))


class InlineRadioSelect(forms.widgets.RadioSelect):
    template_name = 'billservice/inline_radio_select.html'
