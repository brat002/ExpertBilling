# -*- encoding: utf-8 -*-
from django import forms
from django.contrib.admin import widgets   
from datetime import datetime, date
from django.forms import ModelForm
from billservice.models import Tariff, AddonService, TPChangeRule, Account, SubAccount, AccountTarif, AccountAddonService, Document, SuspendedPeriod, Transaction
from billservice.models import PeriodicalService, TimePeriod, SystemUser, TransactionType, SettlementPeriod, RadiusTraffic, RadiusTrafficNode
from billservice.models import Organization, BalanceHistory, PrepaidTraffic, TrafficTransmitNodes, BankData, Group, AccessParameters, TimeSpeed, OneTimeService, TrafficTransmitService
from billservice.models import RadiusAttrs, AccountPrepaysTrafic, Template, AccountPrepaysRadiusTrafic, TimeAccessService, ContractTemplate, TimeAccessNode, TrafficLimit, SpeedLimit, AddonService, AddonServiceTarif
from billservice.models import City, Street, Operator, SaleCard, DealerPay, Dealer, News, Card, TPChangeRule, House, TimePeriodNode, IPPool, Manufacturer, AccountHardware, Model, HardwareType, Hardware

from nas.models import Nas

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Reset,  HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from django.contrib.auth.models import Group as AuthGroup

from django.core.urlresolvers import reverse
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectMultipleWidget, AutoCompleteSelectField
from itertools import chain

class DateRangeField(forms.DateField):
    def clean(self, value):
        if isinstance(value, unicode):
            if value.rfind(" - ")!=-1:
                date_start, date_end = value.split(" - ")
                date_start = self.to_python(date_start)
                self.validate(date_start)
                self.run_validators(date_start)
                date_end = self.to_python(date_end)
                self.validate(date_end)
                self.run_validators(date_end)
                return date_start, date_end
        return super(DateRangeField, self).clean(value)

class FloatConditionField(forms.FloatField):
    def clean(self, value):
        if isinstance(value, unicode):
            if value and value[0] not in ['>', '<']:

                return super(forms.FloatField, self).clean(value)
            elif value and value[0] in ['>', '<']:

                return value[0], super(forms.FloatField, self).clean(value[1:])
        return super(forms.FloatField, self).clean(value)
    
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode


class MyRadioInput(forms.widgets.RadioInput):
    def __unicode__(self):
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        return mark_safe(u'<label class="radio inline" %s>%s %s</label>' % (label_for,  self.tag(), choice_label,))
    
    

class MyCustomRenderer(forms.widgets.RadioFieldRenderer ):

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield MyRadioInput(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return MyRadioInput(self.name, self.value, self.attrs.copy(), choice, idx)
    
    def render(self):
        return mark_safe(u'\n'.join([u'%s' %
                         force_unicode(w) for w in self]))

###

class MyMultipleCheckBoxInput(forms.widgets.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<label class="radio inline" %s>%s %s</label>' % (label_for, rendered_cb, option_label))
        return mark_safe(u'\n'.join(output))
    
       
                
class LoginForm(forms.Form):
    username = forms.CharField(label=u"Имя пользователя", required = True, error_messages={'required':u'Вы не ввели имя пользователя!'})
    user = forms.CharField(label=u"User", required = False)
    password = forms.CharField(label=u"Пароль", widget=forms.PasswordInput, required = False)
    pin = forms.CharField(label=u"Пин", widget=forms.PasswordInput(attrs={'class': 'unset'}), required = False)
    
class PromiseForm(forms.Form):
    sum = forms.FloatField(label=u"Сумма", required = True, error_messages={'required':u'Вы не указали размер платежа!'})
    
class EmailForm(forms.Form):
    new_email = forms.EmailField(label=u"Новый e-mail", required = False,  error_messages={'required':u'Обязательное поле!'} )
    repeat_email = forms.EmailField(label=u"Повторите e-mail", required = False, error_messages={'required':u'Обязательное поле!'} )
    
    
class PasswordForm(forms.Form):
    old_password = forms.CharField(label=u"Старый пароль", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )
    new_password = forms.CharField(label=u"Новый пароль", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )
    repeat_password = forms.CharField(label=u"Повторите пароль", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )



class SimplePasswordForm(forms.Form):
    new_password = forms.CharField(label=u"Новый пароль", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )
    repeat_password = forms.CharField(label=u"Повторите", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )
    
class ActivationCardForm(forms.Form):
    series = forms.IntegerField(label=u"Введите серию", required = True, error_messages={'required':u'Обязательное поле!'})
    card_id = forms.IntegerField(label=u"Введите ID карты", required = True, error_messages={'required':u'Обязательное поле!'})
    pin = forms.CharField(label=u"ПИН", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'})
    
class ChangeTariffForm(forms.Form):
    #tariff_id = forms.ChoiceField(choices=[('','----')]+[(x.id, x.name) for x in Tariff.objects.all().order_by('name')], label=u"Выберите тарифный план", widget=forms.Select(attrs={'size': 1, 'onchange':'set_cost()'}))
    
    def __init__(self, user=None, account_tariff=None,  *args, **kwargs):
        time = (datetime.now() - account_tariff.datetime).seconds
        tariffs = [x.id for x in TPChangeRule.objects.filter(ballance_min__lte=user.ballance, from_tariff = account_tariff.tarif)]
        self.base_fields.insert(5, 'tariff_id', forms.ChoiceField(choices=[('','----')]+[(x.id, x.to_tariff.name) for x in TPChangeRule.objects.filter(ballance_min__lte=user.ballance, from_tariff = account_tariff.tarif)], label=u"Выберите тарифный план", widget=forms.Select(attrs={'size': 1, 'onchange':'set_cost()'})))
        if kwargs.has_key('with_date') and kwargs['with_date'] == True:
            self.base_fields.insert(5, 'from_date', forms.DateTimeField(label = u'С даты', input_formats = ['%d-%m-%Y %H:%M:%S',], widget=forms.TextInput(attrs={'onclick':"NewCssCal('id_from_date','ddmmyyyy','dropdown',true,24,false);"})))
            kwargs.clear()
        super(ChangeTariffForm, self).__init__(*args, **kwargs)
        
class StatististicForm(forms.Form):
    date_from = forms.DateField(label=u'с даты', input_formats=('%d/%m/%Y',), required = False)
    date_to = forms.DateField(label=u'по дату', input_formats=('%d/%m/%Y',), required = False)
    
    
class SearchAccountForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.action = reverse('account_list')
        super(SearchAccountForm, self).__init__(*args, **kwargs)
        
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)

    contract = AutoCompleteSelectMultipleField( 'account_contract', required = False)
    organization = AutoCompleteSelectMultipleField( 'organization_name', label = u"Организация", required = False, widget = forms.TextInput(attrs={'class': 'input-small'}))
    username = AutoCompleteSelectMultipleField( 'account_username', required = False, label=u"Имя аккаунта")
    fullname = AutoCompleteSelectMultipleField( 'account_fullname', required = False, label=u"ФИО")
    contactperson = AutoCompleteSelectMultipleField( 'account_contactperson', required = False, label =u"Контактное лицо")
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False,  label= u"Город")
    street = forms.CharField(label =u"Улица", required=False, widget = forms.TextInput(attrs={'class': 'input-large', 'placeholder': u'Улица'}))#AutoCompleteSelectMultipleField('street_name', required = False, label =u"Улица", attrs={'class': 'input-large'})
    house = forms.CharField(label =u"Дом", required=False, widget = forms.TextInput(attrs={'class': 'input-xsmall', 'placeholder': u'Дом'}))#AutoCompleteSelectMultipleField( 'house_name', required = False, label =u"Дом", placeholder='№ дома', attrs={'class': 'input-small input-street-no'})
    house_bulk = forms.CharField(label =u"Подъезд", required=False, widget = forms.TextInput(attrs={'class': 'input-small'}))
    room = forms.CharField(label =u"Квартира", required=False, widget = forms.TextInput(attrs={'class': 'input-xsmall', 'placeholder': u'Кв'}))
    status = forms.ChoiceField(required=False, choices = (('0', u"--Любой--", ), ('1', u'Активен'), ('2', u'Не активен, списывать периодические услуги'),('3', u'Не активен, не списывать периодические услуги'),('4', u'Пользовательская блокировка'),))
    id = forms.IntegerField(required=False, widget = forms.TextInput(attrs={'class': 'input-small'}))
    #ballance_exp = forms.ChoiceField(required=False, choices = (('>', u"Больше", ), ('<', u'Меньше'), ('', u'Не важно'),), widget = forms.RadioSelect(renderer=MyCustomRenderer))
    ballance = FloatConditionField(label =u"Баланс", required=False, help_text=u"Используйте знаки >меньше и <больше", widget = forms.TextInput(attrs={'class': 'input-small'}))
    #credit_exp = forms.ChoiceField(required=False, choices = (('>', u"Больше", ), ('<', u'Меньше'), ('', u'Не важно'),), widget = forms.RadioSelect(renderer=MyCustomRenderer))
    credit = FloatConditionField(label =u"Кредит", required=False, help_text=u"Используйте знаки >меньше и <больше", widget = forms.TextInput(attrs={'class': 'input-small'}))
    
    vpn_ip_address = forms.CharField(label=u"VPN IP адрес", required = False)
    ipn_ip_address = forms.CharField(label=u"IPN IP адрес", required = False)
    ipn_mac_address = forms.CharField(label=u"MAC адрес", required = False)
    
    ipn_status = forms.MultipleChoiceField(required=False, choices = (('added', u"Добавлен", ), ('enabled', u'Активен'), ('undefined', u'Не важно'),), widget=MyMultipleCheckBoxInput, initial = ["undefined", ])
    
    
    phone = forms.CharField(label=u"Телефон", required = False)
    passport = forms.CharField(label=u"№ паспорта", required = False)
    row = forms.CharField(label=u"Этаж", required = False, widget = forms.TextInput(attrs={'class': 'input-small',}))
    
    tariff = forms.ModelMultipleChoiceField(queryset=Tariff.objects.all(), required=False)
    group_filter = forms.MultipleChoiceField(required=False)
    ballance_blocked = forms.ChoiceField(label=u'Блокировка по балансу', required=False, choices = (('yes', u"Да", ), ('no', u'Нет'), ('undefined', u'Не важно'),), widget = forms.RadioSelect(renderer=MyCustomRenderer))
    limit_blocked = forms.ChoiceField(label=u'Блокировка по лимитам', required=False, choices = (('yes', u"Да", ), ('no', u'Нет'), ('undefined', u'Не важно'),), widget = forms.RadioSelect(renderer=MyCustomRenderer))
    nas = forms.ModelMultipleChoiceField(label=u"Сервер доступа субаккаунта", queryset=Nas.objects.all(), required=False)
    deleted = forms.BooleanField(label=u"В архиве", widget = forms.widgets.CheckboxInput, required=False)
    systemuser_filter = forms.MultipleChoiceField(required=False)
    created = DateRangeField(required=False, label=u"Создан")

class AccountAddonForm(forms.Form):
    account = forms.IntegerField(required=False)
    subaccount = forms.IntegerField(required=False)    
    id = forms.IntegerField(required=False)
    activated = forms.DateTimeField(required=True)
    deactivated = forms.DateTimeField(required=False)
    temporary_blocked = forms.CheckboxInput()
    
class DocumentRenderForm(forms.Form):
    account = forms.IntegerField(required=True)
    #subaccount = forms.IntegerField(required=False)
    contractnumber = forms.CharField(required=False)    
    template = forms.IntegerField(required=True)
    date_start = forms.DateTimeField(required=True)
    date_end = forms.DateTimeField(required=False)

class TransactionReportForm(forms.Form):

    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)

    systemuser = forms.ModelMultipleChoiceField(label=u"Администратор",queryset=SystemUser.objects.all(), widget=forms.SelectMultiple(attrs={'size':'10'}), required=False)
    start_date = forms.DateTimeField(label=u"Начало",required=False)
    end_date = forms.DateTimeField(label=u"Конец",required=False)
    
class ActionLogFilterForm(forms.Form):
    systemuser = forms.ModelChoiceField(queryset=SystemUser.objects.all(), required=False)
    start_date = forms.DateTimeField(required=True)
    end_date = forms.DateTimeField(required=True)
    
class SearchAuthLogForm(forms.Form):
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)
    nas = forms.ModelMultipleChoiceField(label=u"Сервер доступа", queryset=Nas.objects.all(), required=False)

class IpInUseLogForm(forms.Form):
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)
    subaccount = AutoCompleteSelectMultipleField( 'subaccount_fts', required = False)
    ip = forms.IPAddressField(required=False)
    types = forms.ChoiceField(required=False, choices = (('dynamic', u"Динамические", ), ('static', u'Статические'), ('', u'Любые'),), widget = forms.RadioSelect(renderer=MyCustomRenderer))
    
class AccountTariffBathForm(forms.Form):
    accounts = forms.CharField(required=True)
    tariff = forms.IntegerField(required=True)
    date = forms.DateTimeField(required=True)
    
class AccountAddonServiceModelForm(ModelForm):
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    subaccount = forms.ModelChoiceField(queryset=SubAccount.objects.all(), required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    class Meta:
        model = AccountAddonService
      
class DocumentModelForm(ModelForm):
    class Meta:
        model = Document
   
class SuspendedPeriodModelForm(ModelForm):
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    class Meta:
        model = SuspendedPeriod
        exclude = ('activated_by_account',)

class TransactionModelForm(ModelForm):
    description = forms.CharField(required=False)
    created = forms.DateTimeField(required=True)
    account = forms.ModelChoiceField(queryset=Account.objects.all(), widget = forms.HiddenInput)
    promise_never_expire = forms.CharField(widget = forms.widgets.CheckboxInput)
    type = forms.ModelChoiceField(queryset=TransactionType.objects.all(), widget = forms.widgets.Select(attrs={'class': 'input-xlarge'}) )
    
    class Meta:
        model = Transaction
        exclude = ('systemuser', 'accounttarif', 'approved', 'tarif', 'promise_expired')
        
class AccountTariffForm(ModelForm):
    account = forms.ModelChoiceField(queryset=Account.objects.all(), widget = forms.TextInput(attrs={'readonly':'readonly'}))
    
    class Meta:
        model = AccountTarif
    
class SettlementPeriodForm(ModelForm):
    time_start = forms.DateTimeField(label=u'Начало периода', required = True, widget=forms.widgets.SplitDateTimeWidget(attrs={'class':'input-small'}))
    class Meta:
        model = SettlementPeriod
  
class OrganizationForm(ModelForm):
    #id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, widget = forms.widgets.HiddenInput)
    bank = forms.ModelChoiceField(queryset=BankData.objects.all(), required=False, widget = forms.widgets.HiddenInput)
    
    
    class Meta:
        model = Organization
        
class BankDataForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = BankData
              
class AccountForm(ModelForm):
    username = forms.CharField(label =u"Имя пользователя", required=True, widget = forms.TextInput(attrs={'class': 'input-large'}))
    password = forms.CharField(label =u"Пароль", required=True, widget = forms.TextInput(attrs={'class': 'input-large'}))
    city = forms.ModelChoiceField(label=u"Город",queryset=City.objects.all(), required=False, widget = forms.widgets.Select(attrs={'class': 'input-large',}))
    
    street = forms.CharField(label=u"Улица",  required=False, widget = forms.widgets.TextInput(attrs={'class': 'input-large',}))#AutoCompleteSelectMultipleField('street_name', required = False, label =u"Улица", attrs={'class': 'input-large'})
    house = forms.CharField(label=u"Дом", required=False, widget = forms.widgets.TextInput(attrs={'class': 'input-small', 'placeholder': u'Дом'}))#AutoCompleteSelectMultipleField( 'house_name', required = False, label =u"Дом", placeholder='№ дома', attrs={'class': 'input-small input-street-no'})
    contract = forms.CharField(label=u'Номер договора', required = False)
    contract_num = forms.ModelChoiceField(label=u"Номер договора", queryset=ContractTemplate.objects.all(), required=False, widget = forms.widgets.Select(attrs={'class': 'input-large',}))
    organization = forms.BooleanField(label=u"Юр.лицо", required=False, widget = forms.widgets.CheckboxInput)
    created = forms.DateTimeField(label=u'Создан', required = True, widget=forms.widgets.SplitDateTimeWidget(attrs={'class':'input-small'}))
    credit = forms.CharField(label =u"Кредит", required=True, widget = forms.TextInput(attrs={'class': 'input-small'}))
    #--Organization fields
    
    

    
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'input-xlarge'
        self.fields['systemuser'].widget.attrs['class'] = 'input-xlarge'
        self.fields['contract'].widget.attrs['class'] = 'input-medium'
        self.fields['username'].widget.attrs['class'] = 'input-medium'
        self.fields['password'].widget.attrs['class'] = 'input-medium'
        self.fields['comment'].widget.attrs['cols'] =10
    
    class Meta:
        model = Account
        exclude = ('ballance',)
        widgets = {
          'comment': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
class AccessParametersForm(ModelForm):
    class Meta:
        model = AccessParameters
        
class GroupForm(ModelForm):
    class Meta:
        model = Group

class TariffForm(ModelForm):
    class Meta:
        model = Tariff

class TimeSpeedForm(ModelForm):
    class Meta:
        model = TimeSpeed

class PeriodicalServiceForm(ModelForm):
    class Meta:
        model = PeriodicalService

class OneTimeServiceForm(ModelForm):
    class Meta:
        model = OneTimeService

class TrafficTransmitServiceForm(ModelForm):
    class Meta:
        model = TrafficTransmitService

class TrafficTransmitNodeForm(ModelForm):
    class Meta:
        model = TrafficTransmitNodes
      
class PrepaidTrafficForm(ModelForm):
    class Meta:
        model = PrepaidTraffic  

class RadiusTrafficForm(ModelForm):
    class Meta:
        model = RadiusTraffic  

class TimeAccessServiceForm(ModelForm):
    class Meta:
        model = TimeAccessService

class TimeAccessNodeForm(ModelForm):
    class Meta:
        model = TimeAccessNode

class RadiusTrafficNodeForm(ModelForm):
    class Meta:
        model = RadiusTrafficNode  
        exclude = ('created','deleted')
        
class TrafficLimitForm(ModelForm):
    class Meta:
        model = TrafficLimit  
 
class SpeedLimitForm(ModelForm):
    class Meta:
        model = SpeedLimit  

class AddonServiceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddonServiceForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'input-xlarge'
        
        self.fields['service_activation_action'].widget.attrs['class'] = 'span8'
        self.fields['service_deactivation_action'].widget.attrs['class'] = 'span8'
          
    class Meta:
        model = AddonService  

class AddonServiceTarifForm(ModelForm):
    class Meta:
        model = AddonServiceTarif  
        
class ContractTemplateForm(ModelForm):
    class Meta:
        model = ContractTemplate  

class RadiusAttrsForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    nas = forms.ModelChoiceField(queryset=Nas.objects.all(), required=False, widget = forms.HiddenInput)
    tarif = forms.ModelChoiceField(queryset=Tariff.objects.all(), required=False, widget = forms.HiddenInput)
    class Meta:
        model = RadiusAttrs  

class TemplateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'input-xlarge'
        
        #self.fields['service_activation_action'].widget.attrs['class'] = 'span8'
        #self.fields['body'].widget.attrs['class'] = 'field span6'
        #self.fields['body'].widget.attrs['cols'] = 60
    class Meta:
        model = Template


class AccountPrepaysRadiusTraficForm(ModelForm):
    class Meta:
        model = AccountPrepaysRadiusTrafic     

class AccountPrepaysTraficForm(ModelForm):
    class Meta:
        model = AccountPrepaysTrafic     

class TransactionTypeForm(ModelForm):
    class Meta:
        model = TransactionType     

class CityForm(ModelForm):
    class Meta:
        model = City     

class StreetForm(ModelForm):
    class Meta:
        model = Street     

class HouseForm(ModelForm):
    class Meta:
        model = House     
   
class SystemUserForm(ModelForm):
    last_ip = forms.CharField(label="Последний логин с IP", widget = forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    last_login = forms.CharField(label="Последний логин", widget = forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    created = forms.CharField(label="Создан", widget = forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    authgroup = forms.ModelMultipleChoiceField(queryset = AuthGroup.objects.all(), required=False)
    superuser = forms.BooleanField(label=u"Суперадминистратор",widget=forms.CheckboxInput, required=False)
    
    class Meta:
        model = SystemUser
        
        
    
class TimePeriodForm(ModelForm):
    class Meta:
        model = TimePeriod   
     
class TimePeriodNodeForm(ModelForm):
    def __init__(self, *args, **kw):
        super(TimePeriodNodeForm, self).__init__(*args, **kw)
        self.fields.keyOrder = [
                                'id',
                                'time_period',
                                'name',
                                'time_start',
                                'time_end',
                                'length',
                                'repeat_after'
                                ]
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    time_period = forms.ModelChoiceField(queryset=TimePeriod.objects.all(), required=True, widget = forms.HiddenInput)
    time_start = forms.DateTimeField(label=u'Начало периода', required = True, widget=forms.widgets.SplitDateTimeWidget(attrs={'class':'input-small'}))
    time_end = forms.DateTimeField(label=u'Конец периода', required = True, widget=forms.widgets.SplitDateTimeWidget(attrs={'class':'input-small'}))
    length = forms.IntegerField(required=False, widget = forms.HiddenInput)
    
    def clean(self):
        cleaned_data = super(TimePeriodNodeForm, self).clean()
        if cleaned_data.get("time_end") and cleaned_data.get("time_start"):
             cleaned_data["length"]=(cleaned_data.get("time_end")-cleaned_data.get("time_start")).days*86400+(cleaned_data.get("time_end")-cleaned_data.get("time_start")).seconds
        return cleaned_data
    
    class Meta:
        model = TimePeriodNode
                       
                       
class IPPoolForm(ModelForm):
    class Meta:
        model = IPPool
        
class ManufacturerForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    name = forms.CharField(required=True, label=u"Название")
    class Meta:
        model = Manufacturer

class AccountHardwareForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, widget = forms.widgets.HiddenInput)
    hardware = AutoCompleteSelectField( 'hardware_fts', label = u"Устройство", required = True, widget = forms.TextInput(attrs={'class': 'input-xlarge'}), help_text=u"Поиск устройства по всем полям")
    class Meta:
        model = AccountHardware
     
class ModelHardwareForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    name = forms.CharField(required=True, label=u"Название")
    class Meta:
        model = Model
           
class HardwareTypeForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    name = forms.CharField(required=True, label=u"Название")
    class Meta:
        model = HardwareType
        
class HardwareForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    
    class Meta:
        model = Hardware 

class TPChangeRuleForm(ModelForm):
    class Meta:
        model = TPChangeRule
        
class NewsForm(ModelForm):
    class Meta:
        model = News

class CardForm(ModelForm):
    class Meta:
        model = Card
    
class CardGenerationForm(forms.Form):

    card_type = forms.ChoiceField(required=True, choices = ((0, u"Экспресс-оплаты", ), (1, u'Хотспот'), (2, u'VPN доступ'), (3, u'Телефония'),), widget = forms.HiddenInput)
    series = forms.CharField(label=u"Серия", widget=forms.widgets.Input(attrs={'class':'input-small'}))
    count = forms.IntegerField(label=u"Количество", widget=forms.widgets.Input(attrs={'class':'input-small'}))
    login_length_from = forms.IntegerField(required=False, widget=forms.widgets.Input(attrs={'class':'input-small'}))
    login_length_to = forms.IntegerField(required=False, widget=forms.widgets.Input(attrs={'class':'input-small'}))
    login_numbers = forms.BooleanField(required=False, label="0-9", widget = forms.CheckboxInput)
    login_letters = forms.BooleanField(required=False, label="a-Z", widget = forms.CheckboxInput)
    pin_length_from = forms.IntegerField(widget=forms.widgets.Input(attrs={'class':'input-small'}))
    pin_length_to = forms.IntegerField(widget=forms.widgets.Input(attrs={'class':'input-small'}))
    pin_numbers = forms.BooleanField(label="0-9", widget = forms.CheckboxInput)
    pin_letters = forms.BooleanField(label="a-Z", widget = forms.CheckboxInput)
    nominal = forms.FloatField(label=u"Номинал",widget=forms.widgets.Input(attrs={'class':'input-small'}))
    tariff = forms.ModelChoiceField(queryset=Tariff.objects.all(), label=u"Тариф", required=False)
    template = forms.ModelChoiceField(queryset=Template.objects.filter(type__id=7), label=u"Шаблон печати")
    nas = forms.ModelChoiceField(queryset=Nas.objects.all(), label=u"Сервер доступа", required=False)
    ippool = forms.ModelChoiceField(queryset=IPPool.objects.all(), label=u"IP пул", required=False)
    date_start = forms.DateTimeField(label=u'Активировать с', required = True, widget=forms.widgets.SplitDateTimeWidget(attrs={'class':'input-small'}))
    date_end = forms.DateTimeField(label=u'Активировать по', required = True, widget=forms.widgets.SplitDateTimeWidget(attrs={'class':'input-small'}))
    
class CardSearchForm(forms.Form):
    id = forms.IntegerField(required=False)
    card_type = forms.ChoiceField(required=False, choices = (('', u"", ), (0, u"Экспресс-оплаты", ), (1, u'Хотспот'), (2, u'VPN доступ'), (3, u'Телефония'),))
    series = forms.CharField(required=False, label=u"Серия")
    login = forms.CharField(required=False)
    pin = forms.CharField(required=False)
    ext_id = forms.CharField(required=False)
    nominal = FloatConditionField(required=False, label=u"Номинал")
    tariff = forms.ModelChoiceField(queryset=Tariff.objects.all(), label=u"Тариф", required=False)
    template = forms.ModelChoiceField(required=False, queryset=Template.objects.all(), label=u"Шаблон печати")
    nas = forms.ModelChoiceField(queryset=Nas.objects.all(), label=u"Сервер доступа", required=False)
    ippool = forms.ModelChoiceField(queryset=IPPool.objects.all(), label=u"IP пул", required=False)
    sold = DateRangeField(required=False, label=u"Проданы")
    activated = DateRangeField(required=False, label=u"Активированы")
    activated_by = AutoCompleteSelectMultipleField( 'account_username', required = False)
    created = DateRangeField(required=False, label=u"Созданы")
    
    
class DealerForm(ModelForm):
    class Meta:
        model = Dealer    

class SaleCardForm(ModelForm):
    class Meta:
        model = SaleCard    

class DealerPayForm(ModelForm):
    class Meta:
        model = DealerPay    

class OperatorForm(ModelForm):
    class Meta:
        model = Operator    

class BallanceHistoryForm(forms.Form):
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)

#TO-DO: добавить exclude в periodicalservice
class SubAccountForm(ModelForm):
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, widget = forms.HiddenInput)
    ipn_speed = forms.CharField(label=u'IPN скорость', help_text=u"Не менять указанные настройки скорости", required = False, widget = forms.TextInput(attrs={'class': 'span6'}))
    vpn_speed = forms.CharField(label=u'VPN скорость', help_text=u"Не менять указанные настройки скорости", required = False, widget = forms.TextInput(attrs={'class': 'span6'}))
    ipv4_vpn_pool = forms.ModelChoiceField(queryset=IPPool.objects.filter(type=0), required=False)
    ipv4_ipn_pool = forms.ModelChoiceField(queryset=IPPool.objects.filter(type=1), required=False)
    ipn_status = forms.MultipleChoiceField(required=False, choices = (('added', u"Добавлен", ), ('enabled', u'Активен'), ('suspended', u'Не менять состояние'),), widget=MyMultipleCheckBoxInput, initial = ["undefined", ])
    
    class Meta:
        model = SubAccount
        #exclude = ('ipn_ipinuse','vpn_ipinuse',)
        
class TemplateSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TemplateSelectForm, self).__init__(*args, **kwargs)
        self.fields['template'].widget.attrs['class'] = 'span5'
    template = forms.ModelChoiceField(queryset = Template.objects.all())
    
    