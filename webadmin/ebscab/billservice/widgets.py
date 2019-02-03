# -*- coding: utf-8 -*-

from base64 import b64encode, b64decode
from itertools import chain

from Crypto.Cipher import ARC4
from django import forms
from django.conf import settings
from django.core.exceptions import FieldError
from django.template.loader import get_template
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape, escape
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


class SplitDateTimeWidget(forms.widgets.MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """

    format = None

    def __init__(self, date_attrs=None, time_attrs=None, date_format=None,
                 time_format=None):
        widgets = (forms.widgets.DateInput(attrs=date_attrs, format=None),
                   forms.widgets.TimeInput(attrs=time_attrs, format=None))
        super(SplitDateTimeWidget, self).__init__(widgets, None)

    def decompress(self, value):
        if value:
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]


class CheckboxSelectMultipleWithSelectAll(forms.CheckboxSelectMultiple):
    _all_selected = False

    def render(self, *args, **kwargs):
        empty = False
        if not self.choices:
            empty = True
        has_id = kwargs and ("attrs" in kwargs) and ("id" in kwargs["attrs"])
        if not has_id:
            raise FieldError("id required")
        select_all_id = kwargs["attrs"]["id"] + "_all"
        select_all_name = args[0] + "_all"
        original = super(CheckboxSelectMultipleWithSelectAll,
                         self).render(*args, **kwargs)
        template = get_template("widgets/MultipleSelectWithSelectAll.html")
        context = {
            "original_widget": original,
            "select_all_id": select_all_id,
            'select_all_name': select_all_name,
            'all_selected': self._all_selected,
            'empty': empty
        }
        return mark_safe(template.render(context))

    def value_from_datadict(self, *args, **kwargs):
        original = super(CheckboxSelectMultipleWithSelectAll,
                         self).value_from_datadict(*args, **kwargs)
        select_all_name = args[2] + "_all"

        if select_all_name in args[0]:
            self._all_selected = True
        else:
            self._all_selected = False

        return original


class CustomPasswordWidget(forms.widgets.MultiWidget):

    def __init__(self, attrs=None, ):
        widgets = (PasswordTextInput(attrs=attrs),
                   HiddenPasswordInput(attrs=attrs))
        super(CustomPasswordWidget, self).__init__(widgets, attrs)

    def value_from_datadict(self, data, files, name):
        values = [widget.value_from_datadict(data, files, name + '_%s' % i)
                  for i, widget in enumerate(self.widgets)]
        value = values[0] or values[1]
        return value

    def decompress(self, value):
        if value:
            return [None, value]
        return [None, None]

    def format_output(self, rendered_widgets):
        rendered_widgets.insert(-1, '')
        return u''.join(rendered_widgets)


class ModelLinkWidget(forms.widgets.HiddenInput):

    def render(self, name, value, attrs=None):
        return super(ModelLinkWidget, self).render(name, value, attrs) + \
            mark_safe('''
<a id="objectselect1" href="#" class='dialog11'>%s</a>
<div id="dialog11" title="Basic dialog" class='hidden'>
    <p>This is the default dialog which is useful for displaying information. The dialog window can be moved, resized and closed with the 'x' icon.</p>
</div>
<script type="text/javascript">
    $(document).ready(function() {
        $("#objectselect1").click(function() {
            $( "#dialog11" ).dialog({
                modal: false,
                position: {
                    my: "center",
                    at: "center",
                    of: window
                }
            });
        });
    });
</script>
''' % ( escape(unicode(value))))
