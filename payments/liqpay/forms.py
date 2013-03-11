from django import  forms
from django.forms.fields import ChoiceField
from django.utils.translation import ugettext as _
from getpaid.utils import get_backend_choices
from getpaid.models import Order

class AdditionalFieldsForm(forms.Form):
    phone = forms.CharField(required=False)
    summ = forms.FloatField()
    order = forms.ModelChoiceField(widget=forms.widgets.HiddenInput, required=False, queryset=Order.objects.all())
    backend = forms.CharField(initial='payments.liqpay', widget=forms.widgets.HiddenInput)