# -*- coding: utf-8 -*-

from django.conf import settings
from django.forms import forms
from django.forms import widgets
from django.forms.fields import (
    CharField,
    ChoiceField,
    FloatField,
    MultipleChoiceField
)
from django.forms.models import ModelChoiceField
from django.forms.widgets import (
    HiddenInput,
    RadioFieldRenderer,
    RadioInput,
    RadioSelect
)
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from getpaid.models import Order

from utils import get_backend_choices, import_name


class PaymentRadioInput(RadioChoiceInput):

    def __init__(self, name, value, attrs, choice, index):
        super(PaymentRadioInput, self).__init__(
            name, value, attrs, choice, index)
        logo_url = import_name(choice[0]).PaymentProcessor.get_logo_url()
        if logo_url:
            self.choice_label = mark_safe('<img src="%s%s" alt="%s">' % (
                getattr(settings, 'STATIC_URL', ''),
                logo_url,
                force_unicode(choice[1])))


class PaymentRadioFieldRenderer(RadioFieldRenderer):

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield PaymentRadioInput(
                self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx]  # Let the IndexError propogate
        return PaymentRadioInput(
            self.name, self.value, self.attrs.copy(), choice, idx)


class PaymentRadioSelect(RadioSelect):
    renderer = PaymentRadioFieldRenderer


class PaymentMethodForm(forms.Form):
    """
    Displays all available payments backends as choice list.
    """

    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        backends = get_backend_choices()
        self.fields['backend'] = ChoiceField(
            choices=backends,
            initial=backends[0][0] if len(backends) else '',
            label=_("Payment method"),
            widget=PaymentRadioSelect
        )

    order = ModelChoiceField(
        widget=HiddenInput, required=False, queryset=Order.objects.all())
    summ = FloatField(label=_("Amount"), initial=0, required=True)


class SelectPaymentMethodForm(forms.Form):
    """
    Displays all available payments backends as choice list.
    """

    def __init__(self, *args, **kwargs):
        super(SelectPaymentMethodForm, self).__init__(*args, **kwargs)
        backends = get_backend_choices()
        self.fields['backend'] = ChoiceField(
            choices=backends,
            initial=backends[0][0] if len(backends) else '',
            label=_("Payment method"),
            widget=PaymentRadioSelect
        )

    order = ModelChoiceField(
        widget=HiddenInput, required=False, queryset=Order.objects.all())


class PaymentHiddenInputsPostForm(forms.Form):

    def __init__(self, items, *args, **kwargs):
        super(PaymentHiddenInputsPostForm, self).__init__(*args, **kwargs)

        for key in items:
            if type(items[key]) in [list, tuple]:
                self.fields[key] = MultipleChoiceField(
                    initial=items[key], widget=widgets.MultipleHiddenInput)
            else:
                self.fields[key] = CharField(
                    initial=items[key], widget=HiddenInput)


class GenericForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(GenericForm, self).__init__(*args, **kwargs)
        backends = get_backend_choices()
        self.fields['backend'] = ChoiceField(
            choices=backends,
            initial=backends[0][0] if len(backends) else '',
            widget=widgets.HiddenInput
        )
    summ = FloatField()
    order = ModelChoiceField(
        widget=HiddenInput, required=False, queryset=Order.objects.all())
