# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import FieldError
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.html import escape

from billservice.inputs import HiddenPasswordInput, PasswordTextInput


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
