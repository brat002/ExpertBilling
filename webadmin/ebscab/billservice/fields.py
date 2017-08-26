# -*- coding: utf-8 -*-

from django import forms


class DateRangeField(forms.DateField):

    def __init__(self, *args, **kwargs):
        super(DateRangeField, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] = 'daterange'

    def clean(self, value):
        if isinstance(value, unicode):
            if value.rfind(" - ") != -1:
                date_start, date_end = value.split(" - ")
                date_start = self.to_python(date_start)
                self.validate(date_start)
                self.run_validators(date_start)
                date_end = self.to_python(date_end)
                self.validate(date_end)
                self.run_validators(date_end)
                return date_start, date_end
        return super(DateRangeField, self).clean(value)


class PhoneField(forms.CharField):

    def __init__(self, *args, **kwargs):
        super(PhoneField, self).__init__(*args, **kwargs)

    def clean(self, value):

        if isinstance(value, unicode) and value:
            value = '+%s' % (value
                             .replace('+', '')
                             .replace('-', '')
                             .replace('(', '')
                             .replace(')', '')
                             .replace(' ', '')
                             .replace('_', '')
                             )

        print type(value), value

        return super(PhoneField, self).clean(value)


class FloatConditionField(forms.FloatField):

    def clean(self, value):
        if isinstance(value, unicode):
            if value and value[0] not in ['>', '<']:

                return super(forms.FloatField, self).clean(value)
            elif value and value[0] in ['>', '<']:

                return value[0], super(forms.FloatField, self).clean(value[1:])
        return super(forms.FloatField, self).clean(value)
