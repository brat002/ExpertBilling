# -*- encoding: utf-8 -*-
from django import forms
from django.contrib.admin import widgets   


class SplitDateTimeWidget(forms.widgets.MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """

    format = None

    def __init__(self, date_attrs=None, time_attrs=None, date_format=None, time_format=None):
        widgets = (forms.widgets.DateInput(attrs=date_attrs, format=None),
                   forms.widgets.TimeInput(attrs=time_attrs, format=None))
        super(SplitDateTimeWidget, self).__init__(widgets, None)

    def decompress(self, value):
        if value:
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]