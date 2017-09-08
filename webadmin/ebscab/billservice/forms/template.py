# -*- encoding: utf-8 -*-

from django import forms

from billservice.models import ContractTemplate, Template


class TemplateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'input-xlarge'

    class Meta:
        model = Template
        fields = '__all__'


class TemplateSelectForm(forms.Form):
    template = forms.ModelChoiceField(queryset=Template.objects.all())

    def __init__(self, *args, **kwargs):
        super(TemplateSelectForm, self).__init__(*args, **kwargs)
        self.fields['template'].widget.attrs['class'] = 'span5'


class ContractTemplateForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContractTemplate
        exclude = ('counter',)
