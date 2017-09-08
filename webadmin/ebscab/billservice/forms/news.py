# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

from ajax_select.fields import AutoCompleteSelectMultipleField

from billservice.models import News


class NewsForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    accounts = AutoCompleteSelectMultipleField(
        'account_fts', label=_(u'Аккаунты'), required=False)

    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget.attrs['class'] = 'input-xlarge span8'
        self.fields['created'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})
        self.fields['age'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})

    class Meta:
        model = News
        fields = '__all__'
