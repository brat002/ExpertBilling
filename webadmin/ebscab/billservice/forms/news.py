# -*- encoding: utf-8 -*-

from django.forms import DateTimeInput, HiddenInput, Textarea
from django.forms import IntegerField
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from ajax_select.fields import AutoCompleteSelectMultipleField

from billservice.models import News


class NewsForm(ModelForm):
    # NOTE: avoid browser error "An invalid form control with name='body'
    # is not focusable."
    use_required_attribute = False

    id = IntegerField(
        required=False,
        widget=HiddenInput
    )
    accounts = AutoCompleteSelectMultipleField(
        'account_fts',
        label=_(u'Аккаунты'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)

    class Meta:
        model = News
        fields = '__all__'
        widgets = {
            'created': DateTimeInput(attrs={'class': 'datepicker'}),
            'age': DateTimeInput(attrs={'class': 'datepicker'}),
            'body': Textarea(attrs={
                'class': 'input-xlarge span8',
            })
        }
