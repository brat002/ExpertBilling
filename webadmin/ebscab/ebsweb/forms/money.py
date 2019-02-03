# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.conf import settings
from django.db import transaction
from django.forms import Form, ValidationError
from django.forms.fields import (
    CharField,
    ChoiceField,
    FloatField,
    IntegerField
)
from django.forms.models import ModelChoiceField
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext_lazy as _

from ebsadmin.cardlib import activate_pay_card
from getpaid.models import Order
from getpaid.utils import get_backend_choices
from billservice.models import Account, Transaction, TransactionType

from ebsweb.forms.base import UserKwargModelFormMixin
from ebsweb.forms.widgets import (
    NumberInput,
    PasswordInput,
    RadioSelect,
    TextInput
)


PAYMENT_BACKEND_CHOICES = get_backend_choices()


class PaymentForm(Form):
    backend = ChoiceField(
        label=_(u'Способ оплаты'),
        choices=PAYMENT_BACKEND_CHOICES,
        initial=(PAYMENT_BACKEND_CHOICES[0][0]
                 if PAYMENT_BACKEND_CHOICES else None),
        widget=RadioSelect
    )
    # TODO: wtf?
    order = ModelChoiceField(
        queryset=Order.objects.all(),
        required=False,
        widget=HiddenInput
    )


class PromiseForm(UserKwargModelFormMixin, Form):
    error_messages = {
        'sum_too_large': _(u'Превышен максимальный размер обещанного платежа'),
        'sum_not_positive': _(u'Сумма должна быть положительной')
    }

    sum = FloatField(
        label=_(u'Сумма'),
        widget=NumberInput
    )

    def __init__(self, *args, **kwargs):
        super(PromiseForm, self).__init__(*args, **kwargs)
        self.tariff = self.initial.pop('tariff')
        self.promise_sum = self.initial.pop('promise_sum')
        self.promise_left_date = self.initial.pop('promise_left_date')

        self.fields['sum'].help_text = \
            _(u'Макс. {0} {1}'.format(self.promise_sum, settings.CURRENCY))

    def clean_sum(self):
        sum = self.cleaned_data['sum']
        if sum > self.promise_sum:
            raise ValidationError(
                self.error_messages['sum_too_large'],
                code='sum_too_large'
            )
        elif sum <= 0:
            raise ValidationError(
                self.error_messages['sum_not_positive'],
                code='sum_not_positive'
            )
        return sum

    def create(self):
        Transaction.objects.create(
            account=self.user.account,
            description=_(u'Обещанный платёж'),
            type=TransactionType.objects.get(internal_name='PROMISE_PAYMENT'),
            tarif=self.tariff,
            end_promise=self.promise_left_date,
            summ=self.cleaned_data['sum']
        )


class TransferForm(UserKwargModelFormMixin, Form):
    error_messages = {
        'username_not_exist': _(u'Пользователь не существует')
    }

    username = CharField(
        label=_(u'Логин адресата'),
        widget=TextInput
    )

    def __init__(self, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)

        self.to_user = None
        self.allowed_sum = self.user.account.allowed_transfer_sum_20

        self.fields['sum'] = FloatField(
            label=_(u'Сумма'),
            help_text=_(u'Макс. {0:.2f} {1}'.format(
                self.allowed_sum, settings.CURRENCY)),
            widget=NumberInput,
            min_value=0,
            max_value=self.allowed_sum
        )

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            self.to_user = Account.objects.get(username=username)
        except Account.DoesNotExist:
            raise ValidationError(
                self.error_messages['username_not_exist'],
                code='username_not_exist'
            )

    def send(self):
        from_user = self.user.account
        to_user = self.to_user
        with transaction.atomic():
            Transaction.objects.create(
                account=from_user,
                bill=to_user,
                description=_(u'Перевод средств на аккаунт {}'.format(
                    self.to_user.username)),
                type=TransactionType.objects.get(
                    internal_name='MONEY_TRANSFER_TO'),
                tarif=from_user.get_account_tariff(),
                summ=-self.cleaned_data['sum']
            )

            Transaction.objects.create(
                account=to_user,
                bill=from_user,
                description=_(u'Перевод средств с аккаунта {}'.format(
                    from_user.username)),
                type=TransactionType.objects.get(
                    internal_name='MONEY_TRANSFER_FROM'),
                tarif=to_user.get_account_tariff(),
                summ=self.cleaned_data['sum']
            )


class CardForm(UserKwargModelFormMixin, Form):
    if not settings.HOTSPOT_ONLY_PIN:
        number = IntegerField(
            label=_(u'Номер карты'),
            widget=NumberInput
        )
    pin = CharField(
        label=_(u'ПИН'),
        widget=PasswordInput
    )

    def save(self):
        return activate_pay_card(self.user.account.id,
                                 self.cleaned_data.get('number'),
                                 self.cleaned_data['pin'])
