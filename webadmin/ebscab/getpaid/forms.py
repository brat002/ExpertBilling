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
    RadioSelect
)
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from getpaid.models import Order
from getpaid.utils import get_backend_choices, import_name


def backend_with_image_label(backends):
    result = []
    for backend in backends:
        backend_package = backend[0]
        backend_module = '{}.backend'.format(backend_package)
        backend_label = backend[1]
        logo_url = import_name(backend_module).PaymentProcessor.get_logo_url()
        if logo_url:
            backend_label = mark_safe('<img src="%s%s" alt="%s">' % (
                getattr(settings, 'STATIC_URL', ''),
                logo_url,
                force_unicode(backend_label)))
        result.append((backend_package, backend_label))
    return result


class PaymentMethodForm(forms.Form):
    """
    Displays all available payments backends as choice list.
    """

    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        backends = get_backend_choices()
        self.fields['backend'] = ChoiceField(
            choices=backend_with_image_label(backends),
            initial=backends[0][0] if backends else '',
            label=_("Payment method"),
            widget=RadioSelect
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
            choices=backend_with_image_label(backends),
            initial=backends[0][0] if backends else '',
            label=_("Payment method"),
            widget=RadioSelect
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
            choices=backend_with_image_label(backends),
            initial=backends[0][0] if backends else '',
            widget=widgets.HiddenInput
        )
    summ = FloatField()
    order = ModelChoiceField(
        widget=HiddenInput, required=False, queryset=Order.objects.all())
