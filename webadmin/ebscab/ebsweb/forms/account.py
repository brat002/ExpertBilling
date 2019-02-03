# -*- coding: utf-8 -*-

from datetime import datetime

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.forms import Form, ModelForm, ValidationError
from django.forms.fields import (
    CharField,
    ChoiceField,
    EmailField,
    IntegerField
)
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext, ugettext_lazy as _

from billservice.models import (
    Account,
    AccountAddonService,
    AccountTarif,
    SubAccount,
    TPChangeRule,
    Transaction,
    TransactionType
)
from billservice.utils import settlement_period_info
from ebsadmin.cardlib import add_addonservice, del_addonservice

from ebsweb.forms.base import UserKwargModelFormMixin
from ebsweb.forms.widgets import EmailInput, PasswordInput, TariffSelect


class TariffChangeForm(UserKwargModelFormMixin, Form):
    error_messages = {
        'tariff_invalid': ugettext(u'Не верный тариф'),
        'tariff_unavailable': ugettext(
            u'Вы не можете перейти на выбранный тариф'),
        'tariff_not_expired': _(
            u'Для перехода на новый тариф вам необходимо использовать старый '
            u'еще не менее %(x)s дней'),
        'balance_invalid': _(u'Ваш баланс меньше допустимого для перехода '
                             u'на этот тариф')
    }

    rule_id = ChoiceField(
        label='',
        widget=TariffSelect
    )

    def __init__(self, *args, **kwargs):
        super(TariffChangeForm, self).__init__(*args, **kwargs)

        account = self.user.account
        account_tariff = (AccountTarif.objects
                          .filter(account=account, datetime__lt=datetime.now())
                          .order_by('-datetime')
                          .first())
        current_tariff = account.get_account_tariff()
        change_rules = (TPChangeRule.objects
                        .filter(from_tariff=account_tariff.tarif))
        tariff_change_rules = []
        for rule in change_rules:
            date_start = None
            if rule.on_next_sp:
                sp = current_tariff.settlement_period
                if sp:
                    if sp.autostart:
                        start = account_tariff.datetime
                    else:
                        start = sp.time_start
                    sp_datetime = settlement_period_info(
                        start, sp.length_in, sp.length)
                    date_start = sp_datetime[1]
            rule.date_start = date_start
            tariff_change_rules.append(rule)
        tariff_id_choices = []
        for r in tariff_change_rules:
            detail = {
                'title': r.to_tariff.name,
                'description': r.to_tariff.description,
                'price': r.cost,
                'balance_min': r.ballance_min,
                'date_start': r.date_start
            }
            tariff_id_choices.append((r.id, detail))

        self.fields['rule_id'].choices = tariff_id_choices

        # NOTE: avoid double-request to DB
        self.account_tariff = account_tariff
        self.current_tariff = current_tariff
        self.change_rules_ids = [r.id for r in change_rules]

    def clean_rule_id(self):
        try:
            rule_id = int(self.cleaned_data['rule_id'])
        except (TypeError, ValueError):
            raise ValidationError(self.error_messages['tariff_invalid'])

        if rule_id not in self.change_rules_ids:
            raise ValidationError(self.error_messages['tariff_unavailable'])

        account = self.user.account
        account_tariff = self.account_tariff
        rule = TPChangeRule.objects.get(id=rule_id)
        sp = rule.settlement_period

        if float(rule.ballance_min) > float(account.ballance + account.credit):
            raise ValidationError(self.error_messages['balance_invalid'])

        if sp:
            seconds_per_day = 86400
            sp_datetime = settlement_period_info(account_tariff.datetime,
                                                 sp.length_in,
                                                 sp.length)
            difference = datetime.now() - account_tariff.datetime
            delta = (difference.seconds + difference.days *
                     seconds_per_day - sp_datetime[2])
            if delta < 0:
                raise ValidationError(
                    self.error_messages['tariff_not_expired'],
                    params={'x': delta / seconds_per_day * -1})
        # NOTE: avoid double-request to DB
        self.rule = rule
        return rule_id

    def save(self):
        account = self.user.account
        account_tariff = self.account_tariff
        current_tariff = self.current_tariff
        now = datetime.now()

        rule = self.rule
        date_start = now
        date_start_active = False
        if rule.on_next_sp:
            sp = current_tariff.settlement_period
            if sp:
                if sp.autostart:
                    start = account_tariff.datetime
                else:
                    start = sp.time_start
                td = settlement_period_info(start, sp.length_in, sp.length)
                date_start = td[1]
                date_start_active = True

        tariff = AccountTarif.objects.create(
            account=account,
            tarif=rule.to_tariff,
            datetime=date_start)
        for service in (AccountAddonService.objects
                        .filter(account=account, deactivated__isnull=True)):
            if service.service.cancel_subscription:
                service.deactivated = date_start
                service.save()

        if rule.cost:
            Transaction.objects.create(
                account=account,
                bill=ugettext(u'Списание средств за переход на тарифный план '
                              u'{tariff_name}').format(tariff_name=tariff.tarif.name),
                type=TransactionType.objects.get(internal_name='TP_CHANGE'),
                tarif=current_tariff,
                summ=-(rule.cost))
            message_cost = ugettext(
                u'За переход на данный тариф с вашего счета будет списано '
                u'<span class="m--font-bold">{tariff_change_cost}{currency}'
                u'</span>.').format(tariff_change_cost=rule.cost,
                                    currency=settings.CURRENCY)
        else:
            message_cost = ''

        if date_start_active:
            message_success = ugettext(
                u'Тариф будет изменен в следующем расчетном периоде с '
                u'{settlement_date_start}.').format(
                    settlement_date_start=date_start)
        else:
            message_success = ugettext(u'Тариф успешно изменен.')
        if message_cost:
            message_success += '<br>' + message_cost
        return message_success


class AddonServiceAddForm(UserKwargModelFormMixin, Form):
    tariff_addon_service_id = IntegerField()

    def save(self):
        return add_addonservice(self.user.account.id,
                                self.cleaned_data['tariff_addon_service_id'])


class AddonServiceDelForm(UserKwargModelFormMixin, Form):
    account_addon_service_id = IntegerField()

    def save(self):
        return del_addonservice(self.user.account.id,
                                self.cleaned_data['account_addon_service_id'])


class EmailChangeForm(ModelForm):
    error_messages = {
        'invalid': _(u'Email не корректен.'),
        'email_mismatch': _(u'Email не совпали.')
    }

    email_new_1 = EmailField(
        label=_(u'Новый email'),
        widget=EmailInput
    )
    email_new_2 = EmailField(
        label=_(u'Повторите email'),
        widget=EmailInput
    )

    class Meta:
        model = Account
        fields = ('email_new_1', 'email_new_2')

    def clean_email_new_2(self):
        email_1 = self.cleaned_data.get('email_new_1')
        email_2 = self.cleaned_data.get('email_new_2')
        if email_1 != email_2:
            raise ValidationError(
                self.error_messages['email_mismatch'],
                code='email_mismatch'
            )
        return email_2

    def save(self, commit=True):
        self.instance.email = self.cleaned_data['email_new_2']
        if commit:
            self.instance.save()
        return self.instance


class AccountPasswordChangeForm(ModelForm):
    error_messages = {
        'password_incorrect': _(u'Пароль не корректен. Пожалуйста, попробуйте '
                                u'еще раз.'),
        'password_mismatch': _(u'Пароли не совпали.')
    }

    password_old = CharField(
        label=_(u'Старый пароль'),
        strip=False,
        widget=PasswordInput
    )
    password_new_1 = CharField(
        label=_(u'Новый пароль'),
        strip=False,
        widget=PasswordInput
    )
    password_new_2 = CharField(
        label=_(u'Повторите пароль'),
        strip=False,
        widget=PasswordInput
    )

    class Meta:
        model = Account
        fields = ('password_old', 'password_new_1', 'password_new_2')

    def clean_password_old(self):
        password_old = self.cleaned_data['password_old']
        if self.instance.password != password_old:
            raise ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect'
            )
        return password_old

    def clean_password_new_2(self):
        password_1 = self.cleaned_data.get('password_new_1')
        password_2 = self.cleaned_data.get('password_new_2')
        if password_1 and password_2 and password_1 != password_2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch'
            )
        validate_password(password_2)
        return password_2

    def save(self, commit=True):
        self.instance.password = self.cleaned_data['password_new_1']
        if commit:
            self.instance.save()
        return self.instance


class SubAccountPasswordChangeForm(AccountPasswordChangeForm):

    class Meta(AccountPasswordChangeForm.Meta):
        model = SubAccount
