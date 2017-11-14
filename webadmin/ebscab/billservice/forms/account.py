# -*- encoding: utf-8 -*-

from datetime import datetime

import IPy
import ipaddr
import selectable.forms as selectable
from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from ajax_select.fields import AutoCompleteSelectMultipleField
from dynamicmodel.models import DynamicForm, DynamicExtraForm

from billservice.fields import PhoneField
from billservice.models import (
    Account,
    AccountAddonService,
    AccountGroup,
    AccountHardware,
    AccountPrepaysRadiusTrafic,
    AccountPrepaysTime,
    AccountPrepaysTrafic,
    AccountTarif,
    City,
    ContractTemplate,
    Group,
    Hardware,
    House,
    IPPool,
    Street,
    SubAccount,
    SystemUser,
    Tariff
)
from billservice.lookups import HardwareLookup
from billservice.widgets import CustomPasswordWidget, MyMultipleCheckBoxInput


class AccountAddonForm(forms.Form):
    account = forms.IntegerField(required=False)
    subaccount = forms.IntegerField(required=False)
    id = forms.IntegerField(required=False)
    activated = forms.DateTimeField(required=True)
    deactivated = forms.DateTimeField(required=False)
    temporary_blocked = forms.CheckboxInput()


class AccountAddonServiceModelForm(forms.ModelForm):
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        widget=forms.widgets.HiddenInput
    )
    subaccount = forms.ModelChoiceField(
        queryset=SubAccount.objects.all(),
        required=False,
        widget=forms.widgets.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        super(AccountAddonServiceModelForm, self).__init__(*args, **kwargs)
        self.fields['activated'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})
        self.fields['deactivated'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})
        self.fields['temporary_blocked'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})
        self.fields['service'].widget.attrs['class'] = 'input-xlarge span4'
        self.fields['cost'].widget.attrs['class'] = 'input-xlarge span4'

    class Meta:
        model = AccountAddonService
        exclude = ('action_status', 'speed_status', 'last_checkout',)


class AccountExtraForm(DynamicExtraForm):

    class Meta:
        model = Account
        fields = '__all__'


class AccountForm(DynamicForm):
    username = forms.CharField(
        label=_(u"Имя пользователя"),
        required=True,
        widget=forms.widgets.TextInput(attrs={
            'class': 'input-medium'
        })
    )
    password = forms.CharField(
        label=_(u"Пароль") if settings.HIDE_PASSWORDS == False
        else _(u"Изменить пароль"),
        required=False,
        widget=CustomPasswordWidget(attrs={'class': 'input-medium'})
        if settings.HIDE_PASSWORDS == True
        else forms.widgets.TextInput(attrs={'class': 'input-medium'})
    )
    city = forms.ModelChoiceField(
        label=_(u"Город"),
        queryset=City.objects.all(),
        required=False,
        widget=forms.widgets.Select(attrs={
            'class': 'input-large'
        })
    )
    street = forms.CharField(
        label=_(u"Улица"),
        required=False,
        widget=forms.widgets.TextInput(attrs={
            'class': 'input-large'
        })
    )
    house = forms.CharField(
        label=_(u"Дом"),
        required=False,
        widget=forms.widgets.TextInput(attrs={
            'class': 'input-small',
            'placeholder': u'Дом'
        })
    )
    contract = forms.CharField(label=_(u'Номер договора'), required=False)
    contract_num = forms.ModelChoiceField(
        label=_(u"Номер договора"),
        queryset=ContractTemplate.objects.all(),
        required=False,
        widget=forms.widgets.Select(attrs={
            'class': 'input-large'
        })
    )
    organization = forms.BooleanField(
        label=_(u"Юр.лицо"),
        required=False,
        widget=forms.widgets.CheckboxInput
    )
    # organization fields
    disable_notifications = forms.BooleanField(
        label=_(u"Отключить уведомления"),
        required=False,
        widget=forms.widgets.CheckboxInput
    )

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'input-xlarge'
        self.fields['systemuser'].widget.attrs['class'] = 'input-xlarge'
        self.fields['account_group'].widget.attrs['class'] = 'input-xlarge'
        self.fields['contract'].widget.attrs['class'] = 'input-large'
        self.fields['contract_num'].widget.attrs['class'] = 'input-large'
        self.fields['credit'].widget.attrs['class'] = 'input-small'
        self.fields['comment'].widget.attrs['class'] = 'input-xlarge span10'
        self.fields['comment'].widget.attrs['cols'] = 10
        self.fields['created'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})
        self.fields['birthday'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})
        self.fields['phone_m'] = PhoneField(required=False)
        self.fields['phone_h'] = PhoneField(required=False)
        self.fields['contactperson_phone'] = PhoneField(required=False)

    class Meta:
        model = Account
        exclude = ('ballance',)
        widgets = {
          'comment': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        existing = SystemUser.objects.filter(
            username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(
                _(u"Нельзя создать пользователя с именем существующего "
                  u"администратора."))
        else:
            return self.cleaned_data['username']

    def clean(self):
        super(AccountForm, self).clean()
        data = self.cleaned_data

        if settings.HIDE_PASSWORDS and not data.get('password'):
            data['password'] = self.instance.password

        if data['disable_notifications']:
            data['disable_notifications'] = datetime.now()
        else:
            data['disable_notifications'] = None
        return data


class AccountGroupForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(required=True, label=_(u"Название"))

    class Meta:
        model = AccountGroup
        fields = '__all__'


class AccountHardwareForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        widget=forms.widgets.HiddenInput
    )
    hardware = forms.ModelChoiceField(
        queryset=Hardware.objects.all(),
        widget=selectable.AutoComboboxSelectWidget(HardwareLookup)
    )

    comment = forms.CharField(
        label=_(u'Комментарий'),
        required=False,
        widget=forms.widgets.Textarea(attrs={
            'rows': 5,
            'class': 'input-large span5'
        })
    )

    def __init__(self, *args, **kwargs):
        super(AccountHardwareForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AccountHardware
        fields = '__all__'


class AccountManagementForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.all_with_deleted())


class AccountPrepaysRadiusTraficForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(AccountPrepaysTraficForm, self).__init__(*args, **kwargs)

        self.fields['account_tarif'].widget = forms.HiddenInput()
        self.fields['prepaid_traffic'].widget = forms.HiddenInput()
        self.fields['current'].widget = forms.HiddenInput()
        self.fields['reseted'].widget = forms.HiddenInput()

    class Meta:
        model = AccountPrepaysRadiusTrafic
        fields = '__all__'


class AccountPrepaysTimeForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(AccountPrepaysTimeForm, self).__init__(*args, **kwargs)

        self.fields['account_tarif'].widget = forms.HiddenInput()
        self.fields['prepaid_time_service'].widget = forms.HiddenInput()
        self.fields['current'].widget = forms.HiddenInput()
        self.fields['reseted'].widget = forms.HiddenInput()

    class Meta:
        model = AccountPrepaysTime
        fields = '__all__'


class AccountPrepaysTraficForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(AccountPrepaysTraficForm, self).__init__(*args, **kwargs)

        self.fields['account_tarif'].widget = forms.HiddenInput()
        self.fields['prepaid_traffic'].widget = forms.HiddenInput()
        self.fields['current'].widget = forms.HiddenInput()
        self.fields['reseted'].widget = forms.HiddenInput()

    class Meta:
        model = AccountPrepaysTrafic
        fields = '__all__'


class AccountPrepaysRadiusTraficSearchForm(forms.Form):
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
    account = AutoCompleteSelectMultipleField(
        'account_username', label=_(u'Аккаунты'), required=False)
    tariff = forms.ModelMultipleChoiceField(
        queryset=Tariff.objects.all(),
        required=False,
        label=_(u'Тарифный план')
    )
    current = forms.BooleanField(
        label=u'Только текущие значения',
        help_text=_(u'Иначе будет показана информация и за прошлые периоды'),
        required=False,
        initial=True
    )


class AccountPrepaysTimeSearchForm(forms.Form):
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
    account = AutoCompleteSelectMultipleField(
        'account_username', label=_(u'Аккаунты'), required=False)
    tariff = forms.ModelMultipleChoiceField(
        queryset=Tariff.objects.all(),
        required=False,
        label=_(u'Тарифный план')
    )
    current = forms.BooleanField(
        label=_(u'Только текущие значения'),
        help_text=_(u'Иначе будет показана информация и за прошлые периоды'),
        required=False,
        initial=True
    )


class AccountPrepaysTraficSearchForm(forms.Form):
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
    account = AutoCompleteSelectMultipleField(
        'account_username', label=_(u'Аккаунты'), required=False)
    group = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        label=_(u'Группы трафика'),
        required=False
    )
    tariff = forms.ModelMultipleChoiceField(
        queryset=Tariff.objects.all(),
        required=False,
        label=_(u'Тарифный план')
    )
    current = forms.BooleanField(
        label=_(u'Только текущие значения'),
        help_text=_(u'Иначе будет показана информация и за прошлые периоды'),
        required=False,
        initial=True
    )


class AccountTariffBathForm(forms.Form):
    accounts = forms.CharField(required=True)
    tariff = forms.IntegerField(required=True)
    date = forms.DateTimeField(required=True)


class AccountTariffForm(forms.ModelForm):
    account = forms.ModelChoiceField(
        label=_(u'Аккаунт'),
        queryset=Account.objects.all(),
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        super(AccountTariffForm, self).__init__(*args, **kwargs)

        self.fields['datetime'].widget = forms.widgets.DateTimeInput(
            attrs={'class': 'datepicker'})

    class Meta:
        model = AccountTarif
        fields = '__all__'


# TODO: добавить exclude в periodicalservice
class SubAccountForm(forms.ModelForm):
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        widget=forms.HiddenInput
    )
    password = forms.CharField(
        label=_(u"Пароль") if settings.HIDE_PASSWORDS == False
        else _(u"Изменить пароль"),
        required=False,
        widget=CustomPasswordWidget() if settings.HIDE_PASSWORDS == True
        else forms.widgets.TextInput())
    ipn_speed = forms.CharField(
        label=_(u'IPN скорость'),
        help_text=_(u"Не менять указанные настройки скорости"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'span6'
        })
    )
    vpn_speed = forms.CharField(
        label=_(u'VPN скорость'),
        help_text=_(u"Не менять указанные настройки скорости"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'span6'
        })
    )
    ipv4_vpn_pool = forms.ModelChoiceField(
        queryset=IPPool.objects.filter(type=0), required=False)
    ipv6_vpn_pool = forms.ModelChoiceField(
        queryset=IPPool.objects.filter(type=2), required=False)
    ipv4_ipn_pool = forms.ModelChoiceField(
        queryset=IPPool.objects.filter(type=1), required=False)
    ipn_status = forms.MultipleChoiceField(
        required=False,
        choices=(
            ('added', _(u"Добавлен")),
            ('enabled', _(u'Активен')),
            ('suspended', _(u'Не менять состояние'))
        ),
        widget=MyMultipleCheckBoxInput,
        initial=["undefined"]
    )

    class Meta:
        model = SubAccount
        exclude = ('ipn_ipinuse', 'vpn_ipinuse',)

    def clean(self):
        cleaned_data = super(SubAccountForm, self).clean()

        if cleaned_data.get('username', ''):
            subaccs = (SubAccount.objects
                       .filter(username=cleaned_data.get('username'))
                       .exclude(account=cleaned_data.get('account'))
                       .count())

            if subaccs > 0:
                raise forms.ValidationError(
                    _(u'Указанный логин субаккаунта используется в '
                      u'другом аккаунте'))

        if cleaned_data.get('ipn_mac_address'):
            subaccs = (SubAccount.objects
                       .exclude(account=cleaned_data.get('account'))
                       .filter(ipn_mac_address=cleaned_data
                               .get('ipn_mac_address'))
                       .count())

            if subaccs > 0:
                raise forms.ValidationError(
                    _(u'Указанный MAC-адрес используется в другом аккаунте'))

        if str(cleaned_data.get('vpn_ip_address')) not in \
                ('', '0.0.0.0', '0.0.0.0/32'):
            subaccs = (SubAccount.objects
                       .exclude(account=cleaned_data.get('account'))
                       .filter(vpn_ip_address=cleaned_data
                               .get('vpn_ip_address'))
                       .count())

            if subaccs > 0:
                raise forms.ValidationError(
                    _(u'Указанный VPN IP адрес используется в '
                      u'другом аккаунте'))
            if cleaned_data.get('ipv4_vpn_pool'):
                if not IPy.IP(cleaned_data
                              .get('ipv4_vpn_pool')
                              .start_ip).int() <= \
                        IPy.IP(cleaned_data.get('vpn_ip_address')).int() <= \
                        IPy.IP(cleaned_data.get('ipv4_vpn_pool').end_ip).int():
                    raise forms.ValidationError(
                        _(u'Выбранный VPN IP адрес не принадлежит '
                          u'указанному VPN пулу'))

        if str(cleaned_data.get('ipn_ip_address')) not in \
                ('', '0.0.0.0', '0.0.0.0/32'):
            subaccs = (SubAccount.objects
                       .exclude(account=cleaned_data.get('account'))
                       .filter(ipn_ip_address=cleaned_data
                               .get('ipn_ip_address'))
                       .count())

            if subaccs > 0:
                raise forms.ValidationError(
                    _(u'Указанный IPN IP адрес используется в '
                      u'другом аккаунте'))

            if cleaned_data.get('ipv4_ipn_pool'):
                if not ipaddr.IPv4Network(
                    cleaned_data.get('ipv4_ipn_pool').start_ip) <= \
                    ipaddr.IPv4Network(cleaned_data.get('ipn_ip_address')) <= \
                    ipaddr.IPv4Network(
                        cleaned_data.get('ipv4_ipn_pool').end_ip):
                    raise forms.ValidationError(
                        _(u'Выбранный IPN IP адрес не принадлежит '
                          u'указанному IPN пулу'))

        if str(cleaned_data.get('vpn_ipv6_ip_address')) not in \
                ('', '::', ':::'):
            subaccs = (SubAccount.objects
                       .exclude(account=cleaned_data.get('account'))
                       .filter(vpn_ipv6_ip_address=cleaned_data
                               .get('vpn_ipv6_ip_address'))
                       .count())

            if subaccs > 0:
                raise forms.ValidationError(
                    _(u'Указанный VPN IPv6 IP адрес используется в '
                      u'другом аккаунте'))

            if cleaned_data.get('ipv6_vpn_pool'):
                if not IPy.IP(
                        cleaned_data.get('ipv6_vpn_pool').start_ip).int() <= \
                        IPy.IP(cleaned_data.get('vpn_ipv6_ip_address')).int() <= \
                        IPy.IP(cleaned_data.get('ipv6_vpn_pool').end_ip).int():
                    raise forms.ValidationError(
                        _(u'Выбранный IPv6 VPN IP адрес не принадлежит '
                          u'указанному IPv6 IPN пулу'))

        return cleaned_data


class SubAccountPartialForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        widget=forms.widgets.HiddenInput
    )
    password = forms.CharField(
        label=_(u"Пароль") if settings.HIDE_PASSWORDS == False
        else _(u"Изменить пароль"),
        required=False,
        widget=CustomPasswordWidget() if settings.HIDE_PASSWORDS == True
        else forms.widgets.TextInput()
    )
    ipv4_vpn_pool = forms.ModelChoiceField(
        queryset=IPPool.objects.filter(type=0), required=False)
    ipv6_vpn_pool = forms.ModelChoiceField(
        queryset=IPPool.objects.filter(type=2), required=False)
    ipv4_ipn_pool = forms.ModelChoiceField(
        queryset=IPPool.objects.filter(type=1), required=False)

    def clean(self):
        super(SubAccountPartialForm, self).clean()
        cleaned_data = self.cleaned_data

        if str(cleaned_data.get('vpn_ip_address')) not in \
                ('', '0.0.0.0', '0.0.0.0/32'):
            if cleaned_data.get('ipv4_vpn_pool'):
                if not IPy.IP(
                        cleaned_data.get('ipv4_vpn_pool').start_ip).int() <= \
                        IPy.IP(cleaned_data.get('vpn_ip_address')).int() <= \
                        IPy.IP(cleaned_data.get('ipv4_vpn_pool').end_ip).int():
                    raise forms.ValidationError(
                        _(u'Выбранный VPN IP адрес не принадлежит '
                          u'указанному VPN пулу'))

        if str(cleaned_data.get('ipn_ip_address')) not in \
                ('', '0.0.0.0', '0.0.0.0/32'):
            if cleaned_data.get('ipv4_ipn_pool'):
                if not ipaddr.IPv4Network(
                    cleaned_data.get('ipv4_ipn_pool').start_ip) <= \
                    ipaddr.IPv4Network(cleaned_data.get('ipn_ip_address')) <= \
                    ipaddr.IPv4Network(
                        cleaned_data.get('ipv4_ipn_pool').end_ip):
                    raise forms.ValidationError(
                        _(u'Выбранный IPN IP адрес не принадлежит '
                          u'указанному IPN пулу'))

        if str(cleaned_data.get('vpn_ipv6_ip_address')) not in \
                ('', '::', ':::'):
            if cleaned_data.get('ipv6_vpn_pool'):
                if not IPy.IP(
                        cleaned_data.get('ipv6_vpn_pool').start_ip).int() <= \
                        IPy.IP(cleaned_data.get('vpn_ipv6_ip_address')).int() <= \
                        IPy.IP(cleaned_data.get('ipv6_vpn_pool').end_ip).int():
                    raise forms.ValidationError(
                        _(u'Выбранный IPv6 VPN IP адрес не принадлежит '
                          u'указанному IPv6 IPN пулу'))

        return cleaned_data

    class Meta:
        model = SubAccount
        fields = [
            'id',
            'ipn_ip_address',
            'ipn_mac_address',
            'ipv4_ipn_pool',
            'ipv4_vpn_pool',
            'ipv6_vpn_pool',
            'nas',
            'password',
            'sessionscount',
            'switch',
            'switch_port',
            'username',
            'vlan',
            'vpn_ip_address',
            'vpn_ipv6_ip_address'
        ]
        exclude = (
            'account',
            'allow_dhcp',
            'allow_dhcp_with_block',
            'allow_dhcp_with_block',
            'allow_dhcp_with_minus',
            'allow_dhcp_with_null',
            'allow_ipn_with_block',
            'allow_ipn_with_minus',
            'allow_ipn_with_null',
            'allow_vpn_with_block',
            'allow_vpn_with_minus',
            'allow_vpn_with_null',
            'associate_pppoe_ipn_mac',
            'associate_pptp_ipn_ip',
            'ipn_ipinuse',
            'vpn_ipinuse'
        )


class BatchAccountTariffForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.all(),
        widget=forms.widgets.MultipleHiddenInput
    )
    tariff = forms.ModelChoiceField(
        label=_(u'Тариф'), queryset=Tariff.objects.all())
    datetime = forms.DateTimeField(
        label=_(u'С даты'),
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )


class CashierAccountForm(forms.Form):
    contract = forms.CharField(label=_(u'Договор'), required=False)
    username = forms.CharField(required=False, label=_(u"Имя аккаунта"))
    fullname = forms.CharField(required=False, label=_(u"ФИО"))
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=False,
        label=_(u"Город")
    )
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
    room = forms.CharField(
        label=_(u"Квартира"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': _(u'Кв')
        })
    )
    phone = forms.CharField(label=_(u"Телефон"), required=False)

    def __init__(self, *args, **kwargs):
        super(CashierAccountForm, self).__init__(*args, **kwargs)


class CityForm(forms.ModelForm):

    class Meta:
        model = City
        fields = '__all__'


class StreetForm(forms.ModelForm):

    class Meta:
        model = Street
        fields = '__all__'


class HouseForm(forms.ModelForm):

    class Meta:
        model = House
        fields = '__all__'


class BallanceHistoryForm(forms.Form):
    account = AutoCompleteSelectMultipleField('account_fts', required=False)
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
