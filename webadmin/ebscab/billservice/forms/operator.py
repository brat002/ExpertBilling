# -*- encoding: utf-8 -*-

from django import forms

from billservice.models import Operator


class OperatorForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(OperatorForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'input-xlarge span8'

    class Meta:
        model = Operator
        fields = '__all__'
