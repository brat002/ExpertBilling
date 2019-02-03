# -*- encoding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ajax_select.fields import AutoCompleteSelectMultipleField
from getpaid.models import PAYMENT_STATUS_CHOICES
from nas.models import Nas
from sendsms.utils import get_backend_choices

from billservice.fields import DateRangeField, FloatConditionField
from billservice.models import (
    AddonService,
    City,
    Dealer,
    Group,
    IPPool,
    PeriodicalService,
    SuppAgreement,
    SystemUser,
    Tariff
)
from billservice.widgets import InlineRadioSelect, MyMultipleCheckBoxInput


class SearchAccountForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.action = reverse('account_list')
        super(SearchAccountForm, self).__init__(*args, **kwargs)

    account = AutoCompleteSelectMultipleField('account_fts', required=False)
    contract = AutoCompleteSelectMultipleField(
        'account_contract', label=_(u'Договор'), required=False)
    organization = AutoCompleteSelectMultipleField(
        'organization_name',
        label=_(u"Организация"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-small'
        })
    )
    username = AutoCompleteSelectMultipleField(
        'account_username', required=False, label=_(u"Имя аккаунта"))
    fullname = AutoCompleteSelectMultipleField(
        'account_fullname', required=False, label=_(u"ФИО"))
    contactperson = AutoCompleteSelectMultipleField(
        'account_contactperson', required=False, label=_(u"Контактное лицо"))
    city = forms.ModelChoiceField(
        queryset=City.objects.all(), required=False, label=_(u"Город"))
    street = forms.CharField(
        label=_(u"Улица"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-large',
            'placeholder': _(u'Улица')
        })
    )
    house = forms.CharField(
        label=_(u"Дом"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': _(u'Дом')
        })
    )
    house_bulk = forms.CharField(
        label=_(u"Подъезд"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-small'
        })
    )
    room = forms.CharField(
        label=_(u"Квартира"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': _(u'Кв')
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=(
            ('0', _(u"--Любой--")),
            ('1', _(u'Активен')),
            ('2', _(u'Не активен, списывать периодические услуги')),
            ('3', _(u'Не активен, не списывать периодические услуги')),
            ('4', _(u'Пользовательская блокировка'))
        )
    )
    id = forms.IntegerField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'input-small'
            })
    )
    ballance = FloatConditionField(
        label=_(u"Баланс"),
        required=False,
        help_text=_(u"Используйте знаки >меньше и <больше"),
        widget=forms.TextInput(attrs={
            'class': 'input-small'
        })
    )
    credit = FloatConditionField(
        label=_(u"Кредит"),
        required=False,
        help_text=_(u"Используйте знаки >меньше и <больше"),
        widget=forms.TextInput(attrs={
            'class': 'input-small'
        })
    )
    vpn_ip_address = forms.CharField(label=_(u"VPN IP адрес"), required=False)
    ipn_ip_address = forms.CharField(label=_(u"IPN IP адрес"), required=False)
    ipn_mac_address = forms.CharField(label=_(u"MAC адрес"), required=False)
    ipn_status = forms.MultipleChoiceField(
        required=False,
        choices=(
            ('added', _(u"Добавлен")),
            ('enabled', _(u'Активен')),
            ('undefined', _(u'Не важно'))
        ),
        widget=MyMultipleCheckBoxInput,
        initial=["undefined"]
    )
    phone = forms.CharField(label=_(u"Телефон"), required=False)
    passport = forms.CharField(label=_(u"№ паспорта"), required=False)
    row = forms.CharField(
        label=_(u"Этаж"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-small'
        })
    )
    tariff = forms.ModelMultipleChoiceField(
        queryset=Tariff.objects.all(),
        required=False,
        widget=forms.widgets.SelectMultiple(attrs={
            'size': '10'
        })
    )
    group_filter = forms.MultipleChoiceField(required=False)
    ballance_blocked = forms.ChoiceField(
        label=_(u'Блокировка по балансу'),
        required=False,
        choices=(
            ('yes', _(u"Да")),
            ('no', _(u'Нет')),
            ('undefined', _(u'Не важно'))
        ),
        widget=InlineRadioSelect
    )
    limit_blocked = forms.ChoiceField(
        label=_(u'Блокировка по лимитам'),
        required=False,
        choices=(
            ('yes', _(u"Да")),
            ('no', _(u'Нет')),
            ('undefined', _(u'Не важно'))
        ),
        widget=InlineRadioSelect)
    nas = forms.ModelMultipleChoiceField(
        label=_(u"Сервер доступа субаккаунта"),
        queryset=Nas.objects.all(),
        required=False
    )
    deleted = forms.BooleanField(
        label=_(u"В архиве"),
        widget=forms.widgets.CheckboxInput,
        required=False)
    systemuser = forms.ModelChoiceField(
        queryset=SystemUser.objects.all(),
        label=_(u'Менеджер'),
        required=False
    )
    elevator_direction = forms.CharField(
        required=False, label=_(u'Направление от лифта'))
    created = DateRangeField(required=False, label=_(u"Создан"))
    suppagreement = forms.ModelChoiceField(
        queryset=SuppAgreement.objects.all(),
        label=_(u"Доп. соглашение"),
        required=False
    )
    addonservice = forms.ModelChoiceField(
        queryset=AddonService.objects.all(),
        label=_(u"Подключаемая услуга"),
        required=False
    )


class SearchAuthLogForm(forms.Form):
    start_date = forms.DateTimeField(
        required=False,
        label=_(u'С'),
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    end_date = forms.DateTimeField(
        required=False,
        label=_(u'По'),
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    account = AutoCompleteSelectMultipleField(
        'account_fts', label=_(u'Аккаунт'), required=False)
    nas = forms.ModelMultipleChoiceField(
        label=_(u"Сервер доступа"), queryset=Nas.objects.all(), required=False)


class SearchSmsForm(forms.Form):
    bc = get_backend_choices()
    accounts = AutoCompleteSelectMultipleField(
        'account_username', label=_(u'Аккаунты'), required=False)
    phone = forms.CharField(
        label=_(u'Телефон'),
        required=False,
        widget=forms.TextInput
    )
    backend = forms.ChoiceField(
        label=_(u'Оператор'),
        choices=bc,
        initial=bc[0][0] if bc else '',
        required=False
    )
    publish_date = forms.DateTimeField(
        label=_(u'Опубликовать'),
        help_text=_(u'Когда должно быть отослано сообщение'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    sended_from = forms.DateTimeField(
        label=_(u'Отправлено с'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    sended_to = forms.DateTimeField(
        label=_(u'Отправлено по'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )


class PaymentSearchForm(forms.Form):
    accounts = AutoCompleteSelectMultipleField(
        'account_username', label=_(u'Аккаунты'), required=False)
    payment = forms.CharField(
        initial='', label=_(u'Номер платежа'), required=False)
    date_start = forms.DateTimeField(
        label=_(u'Создан с'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    date_end = forms.DateTimeField(
        label=_(u'Создан по'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    paid_start = forms.DateTimeField(
        label=_(u'Оплачен с'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    paid_end = forms.DateTimeField(
        label=_(u'Оплачен по'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    status = forms.ChoiceField(
        choices=[('', '---')] + PAYMENT_STATUS_CHOICES,
        required=False,
        initial=''
    )


class GlobalStatSearchForm(forms.Form):
    accounts = AutoCompleteSelectMultipleField(
        'account_username', label=_(u'Аккаунты'), required=False)
    start_date = forms.DateTimeField(
        required=False,
        label=_(u'С'),
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    end_date = forms.DateTimeField(
        required=False,
        label=_(u'По'),
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )


class GroupStatSearchForm(forms.Form):

    accounts = AutoCompleteSelectMultipleField(
        'account_username', label=_(u'Аккаунты'), required=False)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        label=_(u'Группы трафика'),
        required=False
    )
    date_start = forms.DateTimeField(
        label=_(u'С'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    date_end = forms.DateTimeField(
        label=_(u'По'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )


class CardSearchForm(forms.Form):
    id = forms.IntegerField(required=False)
    card_type = forms.ChoiceField(
        required=False,
        choices=(
            ('', u""),
            (0, _(u"Экспресс-оплаты")),
            (1, _(u'Хотспот')),
            (2, _(u'VPN доступ')),
            (3, _(u'Телефония'))
        )
    )
    dealer = forms.ModelChoiceField(
        queryset=Dealer.objects.all(), required=False, label=_(u"Дилер"))
    series = forms.CharField(required=False, label=_(u"Серия"))
    login = forms.CharField(required=False)
    pin = forms.CharField(required=False)
    ext_id = forms.CharField(required=False)
    nominal = FloatConditionField(required=False, label=_(u"Номинал"))
    tariff = forms.ModelChoiceField(
        queryset=Tariff.objects.all(), label=_(u"Тариф"), required=False)
    nas = forms.ModelChoiceField(
        queryset=Nas.objects.all(),
        label=_(u"Сервер доступа"),
        required=False
    )
    ippool = forms.ModelChoiceField(
        queryset=IPPool.objects.all(), label=_(u"IP пул"), required=False)
    sold = DateRangeField(required=False, label=_(u"Проданы"))
    not_sold = forms.BooleanField(required=False, label=_(u"Не проданные"))
    activated = DateRangeField(label=_(u'Активированы'), required=False)
    activated_by = AutoCompleteSelectMultipleField(
        'account_username', label=_(u'Активатор'), required=False)
    created = DateRangeField(label=_(u'Созданы'), required=False)


class PeriodicalServiceLogSearchForm(forms.Form):
    account = AutoCompleteSelectMultipleField('account_fts', required=False)
    tariff = forms.ModelChoiceField(
        queryset=Tariff.objects.all(), required=False)
    periodicalservice = forms.ModelChoiceField(
        queryset=PeriodicalService.objects.all(), required=False)


class SheduleLogSearchForm(forms.Form):
    account = AutoCompleteSelectMultipleField('account_fts', required=False)
