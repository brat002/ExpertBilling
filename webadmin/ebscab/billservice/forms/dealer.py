# -*- encoding: utf-8 -*-

from django import forms

from billservice.models import Dealer, DealerPay


class DealerForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Dealer
        fields = '__all__'


class DealerPayForm(forms.ModelForm):

    class Meta:
        model = DealerPay
        fields = '__all__'


class DealerSelectForm(forms.Form):
    dealer_item = forms.ModelChoiceField(queryset=Dealer.objects.all())

    def __init__(self, *args, **kwargs):
        super(DealerSelectForm, self).__init__(*args, **kwargs)
        self.fields['dealer_item'].widget.attrs['class'] = 'span5'
