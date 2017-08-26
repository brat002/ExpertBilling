# -*- encoding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from nas.models import Nas

from billservice.models import Card, Dealer, IPPool, SaleCard, Tariff


class CardForm(forms.ModelForm):

    class Meta:
        model = Card
        fields = '__all__'


class CardGenerationForm(forms.Form):
    card_type = forms.ChoiceField(
        required=True,
        choices=(
            (0, _(u"Экспресс-оплаты")),
            (1, _(u'Хотспот')),
            (2, _(u'VPN доступ')),
            (3, _(u'Телефония'))
        ),
        widget=forms.HiddenInput
    )
    series = forms.CharField(
        label=u"Серия",
        widget=forms.widgets.Input(attrs={
            'class': 'input-small'
        })
    )
    count = forms.IntegerField(
        label=u"Количество",
        widget=forms.widgets.Input(attrs={
            'class': 'input-small'
        })
    )
    login_length_from = forms.IntegerField(
        required=False,
        widget=forms.widgets.Input(attrs={
            'class': 'input-small'
        })
    )
    login_length_to = forms.IntegerField(
        required=False,
        widget=forms.widgets.Input(attrs={
            'class': 'input-small'
        })
    )
    login_numbers = forms.BooleanField(
        required=False, label="0-9", widget=forms.CheckboxInput)
    login_letters = forms.BooleanField(
        required=False, label="a-Z", widget=forms.CheckboxInput)
    pin_length_from = forms.IntegerField(
        widget=forms.widgets.Input(attrs={'class': 'input-small'}))
    pin_length_to = forms.IntegerField(
        widget=forms.widgets.Input(attrs={'class': 'input-small'}))
    pin_numbers = forms.BooleanField(
        label="0-9", required=False, widget=forms.CheckboxInput)
    pin_letters = forms.BooleanField(
        label="a-Z", required=False, widget=forms.CheckboxInput)
    nominal = forms.FloatField(
        label=_(u"Номинал"),
        widget=forms.widgets.Input(attrs={
            'class': 'input-small'
        })
    )
    tariff = forms.ModelChoiceField(
        queryset=Tariff.objects.all(), label=_(u"Тариф"), required=False)
    nas = forms.ModelChoiceField(
        queryset=Nas.objects.all(),
        label=_(u"Сервер доступа"),
        required=False
    )
    ippool = forms.ModelChoiceField(
        queryset=IPPool.objects.all(), label=u"IP пул", required=False)
    date_start = forms.DateTimeField(
        label=_(u'Активировать с'),
        required=True,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    date_end = forms.DateTimeField(
        label=_(u'Активировать по'),
        required=True,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )

    def clean(self):
        cleaned_data = super(CardGenerationForm, self).clean()
        if cleaned_data.get("card_type") in [1, 2, 3] and not \
            (cleaned_data.get("login_numbers") or
             cleaned_data.get("login_letters")):
            raise forms.ValidationError(_(u'Вы должны выбрать состав логина'))
        if not (cleaned_data.get("pin_numbers") or
                cleaned_data.get("pin_letters")):
            raise forms.ValidationError(_(u'Вы должны выбрать состав пина'))

        return cleaned_data


class CardBatchChangeForm(forms.Form):
    cards = forms.CharField(required=True, widget=forms.widgets.HiddenInput)
    card_type = forms.ChoiceField(
        required=False,
        choices=(
            (-1, _(u"Не менять")),
            (0, _(u"Экспресс-оплаты")),
            (1, _(u'Хотспот')),
            (2, _(u'VPN доступ')),
            (3, _(u'Телефония'))
        )
    )
    series = forms.CharField(
        required=False,
        label=_(u"Серия"),
        widget=forms.widgets.TextInput(attrs={
            'class': 'span5'
        })
    )
    change_login = forms.BooleanField(
        required=False, label=_(u"Изменить логин"))
    login_length_from = forms.IntegerField(
        required=False, widget=forms.widgets.Input(attrs={'class': 'input-small'}))
    login_length_to = forms.IntegerField(
        required=False, widget=forms.widgets.Input(attrs={'class': 'input-small'}))
    login_numbers = forms.BooleanField(
        required=False, label="0-9", widget=forms.CheckboxInput)
    login_letters = forms.BooleanField(
        required=False, label="a-Z", widget=forms.CheckboxInput)
    change_pin = forms.BooleanField(required=False, label=_(u"Изменить пин"))
    pin_length_from = forms.IntegerField(
        required=False, widget=forms.widgets.Input(attrs={'class': 'input-small'}))
    pin_length_to = forms.IntegerField(
        required=False, widget=forms.widgets.Input(attrs={'class': 'input-small'}))
    pin_numbers = forms.BooleanField(
        required=False, label="0-9", widget=forms.CheckboxInput)
    pin_letters = forms.BooleanField(
        required=False, label="a-Z", widget=forms.CheckboxInput)
    change_nominal = forms.BooleanField(
        required=False, label=_(u"Изменить номинал"))
    nominal = forms.FloatField(required=False, label=_(
        u"Номинал"), widget=forms.widgets.Input(attrs={'class': 'input-small'}))
    tariff = forms.ModelChoiceField(
        queryset=Tariff.objects.all(), label=_(u"Тариф"), required=False)
    nas = forms.ModelChoiceField(
        queryset=Nas.objects.all(),
        label=_(u"Сервер доступа"),
        required=False
    )
    ippool = forms.ModelChoiceField(
        queryset=IPPool.objects.all(), label=_(u"IP пул"), required=False)

    date_start = forms.DateTimeField(
        label=_(u'Активировать с'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    date_end = forms.DateTimeField(
        label=_(u'Активировать по'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )


class SaleCardForm(forms.ModelForm):
    cards = forms.ModelMultipleChoiceField(
        queryset=Card.objects.all(),
        required=True,
        label=_(u"Карты"),
        widget=forms.widgets.MultipleHiddenInput
    )
    dealer = forms.ModelChoiceField(
        queryset=Dealer.objects.all(),
        required=True,
        label=_(u"Дилер"),
        widget=forms.widgets.HiddenInput
    )
    prepayment_sum = forms.FloatField(
        label=_(u"Внесено предоплаты"), required=False)

    def __init__(self, *args, **kwargs):
        super(SaleCardForm, self).__init__(*args, **kwargs)
        self.fields['cards'].widget = forms.widgets.MultipleHiddenInput()

    class Meta:
        model = SaleCard
        fields = '__all__'


class ActivationCardForm(forms.Form):
    if not settings.HOTSPOT_ONLY_PIN:
        card_id = forms.IntegerField(
            label=_(u"Номер карты"),
            required=True,
            error_messages={
                'required': _(u'Обязательное поле!')
            }
        )
    pin = forms.CharField(
        label=_(u"ПИН"),
        required=True,
        widget=forms.PasswordInput,
        error_messages={
            'required': _(u'Обязательное поле!')
        }
    )
