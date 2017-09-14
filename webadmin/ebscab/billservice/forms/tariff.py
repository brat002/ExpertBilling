# -*- encoding: utf-8 -*-

from datetime import datetime

from django import forms
from django.utils.translation import ugettext as _

from billservice.models import (
    NotificationsSettings,
    SettlementPeriod,
    Tariff,
    TPChangeRule
)


class TariffForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(TariffForm, self).__init__(*args, **kwargs)
        self.fields['access_parameters'].widget = forms.widgets.HiddenInput()
        self.fields['time_access_service'].widget = forms.widgets.HiddenInput()
        self.fields['traffic_transmit_service'].widget = \
            forms.widgets.HiddenInput()
        self.fields['radius_traffic_transmit_service'].widget = \
            forms.widgets.HiddenInput()

        self.fields['description'].widget.attrs['rows'] = 5
        self.fields['description'].widget.attrs['class'] = 'span10'

    class Meta:
        model = Tariff
        fields = '__all__'


class ChangeTariffForm(forms.Form):

    def __init__(self, user=None, account_tariff=None, *args, **kwargs):
        time = (datetime.now() - account_tariff.datetime).seconds
        tariffs = [x.id for x in
                   TPChangeRule.objects.filter(
                       ballance_min__lte=user.ballance,
                       from_tariff=account_tariff.tarif
                   )]
        self.base_fields['tariff_id'] = forms.ChoiceField(
            choices=[('', '----')] + [
                (x.id, x.to_tariff.name) for x in TPChangeRule.objects.filter(
                    ballance_min__lte=user.ballance,
                    from_tariff=account_tariff.tarif
                )
            ],
            label=_(u"Выберите тарифный план"),
            widget=forms.Select(attrs={
                'size': 1,
                'onchange': 'set_cost()'
            })
        )

        if kwargs.has_key('with_date') and kwargs['with_date'] == True:
            self.base_fields.insert(
                5,
                'from_date',
                forms.DateTimeField(
                    label=u'С даты',
                    input_formats=['%d-%m-%Y %H:%M:%S'],
                    widget=forms.TextInput(attrs={
                        'onclick': ("NewCssCal('id_from_date', 'ddmmyyyy', "
                                    "'dropdown', true, 24, false);")
                    })
                )
            )
            kwargs.clear()

        super(ChangeTariffForm, self).__init__(*args, **kwargs)


class NotificationsSettingsForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(NotificationsSettingsForm, self).__init__(*args, **kwargs)
        self.fields['payment_notifications_template'].widget.attrs['class'] = \
            'span9'
        self.fields['balance_notifications_template'].widget.attrs['class'] = \
            'span9'

    class Meta:
        model = NotificationsSettings
        fields = '__all__'


class TPChangeRuleForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(TPChangeRuleForm, self).__init__(*args, **kwargs)

    class Meta:
        model = TPChangeRule
        fields = '__all__'


class TPChangeMultipleRuleForm(forms.Form):
    from_tariff = forms.ModelChoiceField(queryset=Tariff.objects.all())
    to_tariffs = forms.ModelMultipleChoiceField(
        queryset=Tariff.objects.all(),
        label=_(u'Тарифные планы'),
        required=False,
        widget=forms.widgets.SelectMultiple
    )
    disabled = forms.BooleanField(
        label=_(u'Временно запретить'), initial=False, required=False)
    cost = forms.FloatField(label=_(u'Стоимость перехода'), initial=0)
    ballance_min = forms.FloatField(label=_(u'Минимальный баланс'), initial=0)
    on_next_sp = forms.BooleanField(
        label=_(u'Со следующего расчётного периода'), required=False)
    settlement_period = forms.ModelChoiceField(
        queryset=SettlementPeriod.objects.all(),
        label=_(u'Расчётный период'),
        required=False
    )
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    mirror = forms.BooleanField(
        label=_(u'Создать зеркальное правило'), required=False)

    def __init__(self, *args, **kwargs):
        super(TPChangeMultipleRuleForm, self).__init__(*args, **kwargs)
        self.fields['to_tariffs'].widget.attrs['size'] = 20
