# -*- encoding: utf-8 -*-
from django import forms
from django.contrib.admin import widgets   
from datetime import datetime, date
from django.forms import ModelForm
from billservice.models import Tariff, AddonService, TPChangeRule, Account, SubAccount, AccountTarif, AccountAddonService, Document, SuspendedPeriod, Transaction, PermissionGroup, Permission
from billservice.models import PeriodicalService, TimePeriod, SystemUser, TransactionType, SettlementPeriod, RadiusTraffic, RadiusTrafficNode, PeriodicalServiceLog, Switch
from billservice.models import Organization, BalanceHistory, PrepaidTraffic, TrafficTransmitNodes, BankData, Group, AccessParameters, TimeSpeed, OneTimeService, TrafficTransmitService, SheduleLog
from billservice.models import RadiusAttrs, AccountPrepaysTrafic, Template, AccountPrepaysRadiusTrafic, TimeAccessService, ContractTemplate, TimeAccessNode, TrafficLimit, SpeedLimit, AddonService, AddonServiceTarif
from billservice.models import AccountSuppAgreement, SuppAgreement, City, Street, Operator, SaleCard, DealerPay, Dealer, News, Card, TPChangeRule, House, TimePeriodNode, IPPool, Manufacturer, AccountHardware, Model, HardwareType, Hardware,AccountGroup,AccountPrepaysTime

from dynamicmodel.models import DynamicSchemaField
from dynamicmodel.models import DynamicForm, DynamicExtraForm
from nas.models import Nas
from getpaid.models import Payment, PAYMENT_STATUS_CHOICES

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Reset,  HTML, Button, Row, Field, Fieldset
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from django.contrib.auth.models import Group as AuthGroup

from django.core.urlresolvers import reverse
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectMultipleWidget, AutoCompleteSelectField
from itertools import chain
from widgets import SplitDateTimeWidget, CheckboxSelectMultipleWithSelectAll
from django.utils.translation import ugettext as _
from django_select2 import *
import IPy, ipaddr
from Crypto.Cipher import ARC4
from base64 import b64encode, b64decode
from django.conf import settings
from captcha.fields import CaptchaField
import selectable.forms as selectable
from ebscab.lookups import HardwareLookup

class HardwareChoices(AutoModelSelect2Field):
    queryset = Hardware.objects#.filter(accounthardware__isnull=True)
    max_results = 20
    search_fields = ['name__icontains', 'model__name__icontains', 'sn__icontains', 'comment__icontains']
    
class NewHardwareChoices(AutoModelSelect2Field):
    queryset = Hardware.objects.filter(accounthardware__isnull=True)
    max_results = 20
    search_fields = ['name__icontains', 'model__name__icontains', 'sn__icontains', 'comment__icontains']

class PasswordTextInput(forms.widgets.Input):
    input_type = 'text'
    def render(self, name, value, attrs=None):
        if attrs.get('id'):
            attrs['id']=attrs['id'].replace('_0', '')
        return super(PasswordTextInput, self).render(name, value, attrs=attrs)
        
class HiddenPasswordInput(forms.widgets.Input):
    input_type = 'hidden'

    def __init__(self, attrs=None):
        super(HiddenPasswordInput, self).__init__(attrs)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if not value: return None
        obj1 = ARC4.new(settings.PGCRYPTO_DEFAULT_KEY)
        value = obj1.decrypt(b64decode(value))
        return value
    
    def render(self, name, value, attrs=None):
        obj1 = ARC4.new(settings.PGCRYPTO_DEFAULT_KEY)
        value = b64encode(obj1.encrypt(unicode(value)))
        return super(HiddenPasswordInput, self).render(name, value, attrs)
    
class CustomPasswordWidget(forms.widgets.MultiWidget):

    def __init__(self, attrs=None, ):
        widgets = (PasswordTextInput(attrs=attrs), HiddenPasswordInput(attrs=attrs))
        super(CustomPasswordWidget, self).__init__(widgets, attrs)

    def value_from_datadict(self, data, files, name):
        values =  [widget.value_from_datadict(data, files, name + '_%s' % i) for i, widget in enumerate(self.widgets)]
        value = values[0] or values[1]
        return value
    
    def decompress(self, value):
        if value:
            return [None, value]
        return [None, None]

    def format_output(self, rendered_widgets):
        rendered_widgets.insert(-1, '')
        return u''.join(rendered_widgets)
    

class DateRangeField(forms.DateField):
    def __init__(self, *args, **kwargs):
        super(DateRangeField, self ).__init__(*args, **kwargs)
        self.widget.attrs['class'] = 'daterange'
        
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

class PhoneField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(PhoneField, self ).__init__(*args, **kwargs)

        
    def clean(self, value):
        
        if isinstance(value, unicode) and value:
            value = '+%s' % value.replace('+', '').replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('_', '')
        print type(value),value
        return super(PhoneField, self).clean(value)
    
class FloatConditionField(forms.FloatField):
    def clean(self, value):
        if isinstance(value, unicode):
            if value and value[0] not in ['>', '<']:

                return super(forms.FloatField, self).clean(value)
            elif value and value[0] in ['>', '<']:

                return value[0], super(forms.FloatField, self).clean(value[1:])
        return super(forms.FloatField, self).clean(value)
    
from django.utils.html import escape

class ModelLinkWidget(forms.widgets.HiddenInput):

   
    def render(self, name, value, attrs=None):

        return super(ModelLinkWidget, self).render(
                name, value, attrs) + mark_safe('''
                <a id="objectselect1" href="#" class='dialog11'>%s</a>
<div id="dialog11" title="Basic dialog" class='hidden'>
  <p>This is the default dialog which is useful for displaying information. The dialog window can be moved, resized and closed with the 'x' icon.</p>
</div>
<script type="text/javascript"> 
    $(document).ready(function() {
    
                
        $("#objectselect1").click(function(){
            $( "#dialog11" ).dialog(
            {
            modal: false,
            position: {
   my: "center",
   at: "center",
   of: window
}
            });
            //event.preventDefault(event);
        })
    });
</script>
                ''' % ( escape(unicode(value))))

        
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
    username = forms.CharField(label=_(u"Логин"), required = True, error_messages={'required':_(u'Вы не ввели имя пользователя!')})
    user = forms.CharField(label=_(u"User"), required = False)
    password = forms.CharField(label=_(u"Пароль"), widget=forms.PasswordInput, required = False)
    pin = forms.CharField(label=_(u"Пин"), widget=forms.PasswordInput(attrs={'class': 'unset'}), required = False)
    
    
class RegisterForm(forms.Form):
    fullname = forms.CharField(label=_(u"ФИО"), required = True, error_messages={'required':_(u'Вы не ввели ФИО')})
    address = forms.CharField(label=_(u"Адрес"), help_text = _(u'Ваш адрес'), required = True)
    phone = forms.CharField(label=_(u"Телефон"), help_text = _(u'Мобильный телефон'), required = True)
    login = forms.CharField(label=_(u"Логин"), help_text = _(u'Имя пользователя'), required = False)
    password = forms.CharField(label=_(u"Пароль"), widget=forms.PasswordInput, required = False)
    captcha = CaptchaField()
    
class PromiseForm(forms.Form):
    sum = forms.FloatField(label=_(u"Сумма"), required = True, error_messages={'required':_(u'Вы не указали размер платежа!')})
    
class EmailForm(forms.Form):
    new_email = forms.EmailField(label=_(u"Новый e-mail"), required = False,  error_messages={'required':_(u'Обязательное поле!')} )
    repeat_email = forms.EmailField(label=_(u"Повторите e-mail"), required = False, error_messages={'required':_(u'Обязательное поле!')} )
    
    
class PasswordForm(forms.Form):
    old_password = forms.CharField(label=_(u"Старый пароль"), required = True, widget=forms.PasswordInput, error_messages={'required':_(u'Обязательное поле!')} )
    new_password = forms.CharField(label=_(u"Новый пароль"), required = True, widget=forms.PasswordInput, error_messages={'required':_(u'Обязательное поле!')} )
    repeat_password = forms.CharField(label=_(u"Повторите пароль"), required = True, widget=forms.PasswordInput, error_messages={'required':_(u'Обязательное поле!')} )



class SimplePasswordForm(forms.Form):
    new_password = forms.CharField(label=_(u"Новый пароль"), required = True, widget=forms.PasswordInput, error_messages={'required':_(u'Обязательное поле!')} )
    repeat_password = forms.CharField(label=_(u"Повторите"), required = True, widget=forms.PasswordInput, error_messages={'required':_(u'Обязательное поле!')} )
    
class ActivationCardForm(forms.Form):
    #series = forms.IntegerField(label=_(u"Введите серию"), required = True, error_messages={'required':_(u'Обязательное поле!')})
    card_id = forms.IntegerField(label=_(u"Введите ID карты"), required = True, error_messages={'required':_(u'Обязательное поле!')})
    pin = forms.CharField(label=_(u"ПИН"), required = True, widget=forms.PasswordInput, error_messages={'required':_(u'Обязательное поле!')})
    
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

    contract = AutoCompleteSelectMultipleField( 'account_contract', label=_(u'Договор'), required = False)
    organization = AutoCompleteSelectMultipleField( 'organization_name', label = _(u"Организация"), required = False, widget = forms.TextInput(attrs={'class': 'input-small'}))
    username = AutoCompleteSelectMultipleField( 'account_username', required = False, label=_(u"Имя аккаунта"))
    fullname = AutoCompleteSelectMultipleField( 'account_fullname', required = False, label=_(u"ФИО"))
    contactperson = AutoCompleteSelectMultipleField( 'account_contactperson', required = False, label =_(u"Контактное лицо"))
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False,  label= _(u"Город"))
    street = forms.CharField(label =_(u"Улица"), required=False, widget = forms.TextInput(attrs={'class': 'input-large', 'placeholder': u'Улица'}))#AutoCompleteSelectMultipleField('street_name', required = False, label =u"Улица", attrs={'class': 'input-large'})
    house = forms.CharField(label =_(u"Дом"), required=False, widget = forms.TextInput(attrs={'class': 'input-medium', 'placeholder': u'Дом'}))#AutoCompleteSelectMultipleField( 'house_name', required = False, label =u"Дом", placeholder='№ дома', attrs={'class': 'input-small input-street-no'})
    house_bulk = forms.CharField(label =_(u"Подъезд"), required=False, widget = forms.TextInput(attrs={'class': 'input-small'}))
    room = forms.CharField(label =_(u"Квартира"), required=False, widget = forms.TextInput(attrs={'class': 'input-medium', 'placeholder': u'Кв'}))
    status = forms.ChoiceField(required=False, choices = (('0', _(u"--Любой--"), ), ('1', _(u'Активен')), ('2', _(u'Не активен, списывать периодические услуги')),('3', _(u'Не активен, не списывать периодические услуги')),('4', _(u'Пользовательская блокировка')),))
    id = forms.IntegerField(required=False, widget = forms.TextInput(attrs={'class': 'input-small'}))
    #ballance_exp = forms.ChoiceField(required=False, choices = (('>', u"Больше", ), ('<', u'Меньше'), ('', u'Не важно'),), widget = forms.RadioSelect(renderer=MyCustomRenderer))
    ballance = FloatConditionField(label =_(u"Баланс"), required=False, help_text=u"Используйте знаки >меньше и <больше", widget = forms.TextInput(attrs={'class': 'input-small'}))
    #credit_exp = forms.ChoiceField(required=False, choices = (('>', u"Больше", ), ('<', u'Меньше'), ('', u'Не важно'),), widget = forms.RadioSelect(renderer=MyCustomRenderer))
    credit = FloatConditionField(label =_(u"Кредит"), required=False, help_text=u"Используйте знаки >меньше и <больше", widget = forms.TextInput(attrs={'class': 'input-small'}))
    
    vpn_ip_address = forms.CharField(label=_(u"VPN IP адрес"), required = False)
    ipn_ip_address = forms.CharField(label=_(u"IPN IP адрес"), required = False)
    ipn_mac_address = forms.CharField(label=_(u"MAC адрес"), required = False)
    
    ipn_status = forms.MultipleChoiceField(required=False, choices = (('added', _(u"Добавлен"), ), ('enabled', _(u'Активен')), ('undefined', _(u'Не важно')),), widget=MyMultipleCheckBoxInput, initial = ["undefined", ])
    
    
    phone = forms.CharField(label=_(u"Телефон"), required = False)
    passport = forms.CharField(label=_(u"№ паспорта"), required = False)
    row = forms.CharField(label=_(u"Этаж"), required = False, widget = forms.TextInput(attrs={'class': 'input-small',}))
    
    tariff = forms.ModelMultipleChoiceField(queryset=Tariff.objects.all(), required=False, widget = forms.widgets.SelectMultiple(attrs={'size': '10',}))
    group_filter = forms.MultipleChoiceField(required=False)
    ballance_blocked = forms.ChoiceField(label=_(u'Блокировка по балансу'), required=False, choices = (('yes', _(u"Да"), ), ('no', _(u'Нет')), ('undefined', _(u'Не важно')),), widget = forms.RadioSelect(renderer=MyCustomRenderer))
    limit_blocked = forms.ChoiceField(label=_(u'Блокировка по лимитам'), required=False, choices = (('yes', _(u"Да"), ), ('no', _(u'Нет')), ('undefined', _(u'Не важно')),), widget = forms.RadioSelect(renderer=MyCustomRenderer))
    nas = forms.ModelMultipleChoiceField(label=_(u"Сервер доступа субаккаунта"), queryset=Nas.objects.all(), required=False)
    deleted = forms.BooleanField(label=_(u"В архиве"), widget = forms.widgets.CheckboxInput, required=False)
    systemuser = forms.ModelChoiceField(queryset=SystemUser.objects.all(),label=_(u'Менеджер'),  required=False)
    elevator_direction = forms.CharField(required=False, label=_(u'Направление от лифта'))
    created = DateRangeField(required=False, label=_(u"Создан"))
    suppagreement = forms.ModelChoiceField(queryset = SuppAgreement.objects.all(), label=_(u"Доп. соглашение"), required=False)
    addonservice = forms.ModelChoiceField(queryset = AddonService.objects.all(), label=_(u"Подключаемая услуга"), required=False)

class CashierAccountForm(forms.Form):

    contract = forms.CharField(label=_(u'Договор'), required = False)
    username = forms.CharField(required = False, label=_(u"Имя аккаунта"))
    fullname = forms.CharField(required = False, label=_(u"ФИО"))

    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False,  label= _(u"Город"))
    street = forms.CharField(label =_(u"Улица"), required=False, widget = forms.TextInput(attrs={'class': 'input-large', 'placeholder': u'Улица'}))#AutoCompleteSelectMultipleField('street_name', required = False, label =u"Улица", attrs={'class': 'input-large'})
    house = forms.CharField(label =_(u"Дом"), required=False, widget = forms.TextInput(attrs={'class': 'input-medium', 'placeholder': u'Дом'}))#AutoCompleteSelectMultipleField( 'house_name', required = False, label =u"Дом", placeholder='№ дома', attrs={'class': 'input-small input-street-no'})
    #house_bulk = forms.CharField(label =u"Подъезд", required=False, widget = forms.TextInput(attrs={'class': 'input-small'}))
    room = forms.CharField(label =_(u"Квартира"), required=False, widget = forms.TextInput(attrs={'class': 'input-medium', 'placeholder': u'Кв'}))
    phone = forms.CharField(label=_(u"Телефон"), required = False)

    
    def __init__(self, *args, **kwargs):
        super(CashierAccountForm, self).__init__(*args, **kwargs)
        
        
        
class AccountAddonForm(forms.Form):
    account = forms.IntegerField(required=False)
    subaccount = forms.IntegerField(required=False)    
    id = forms.IntegerField(required=False)
    activated = forms.DateTimeField(required=True)
    deactivated = forms.DateTimeField(required=False)
    temporary_blocked = forms.CheckboxInput()
    
    

    
class DocumentRenderForm(forms.Form):
    account = forms.IntegerField(required=False)
    transaction = forms.IntegerField(required=False)
    template = forms.IntegerField(label=_(u'Шаблон'), required=True)
    cards = forms.ModelMultipleChoiceField(queryset=Card.objects.all(), required=False)


class TransactionReportForm(forms.Form):

    start_date = forms.DateTimeField(required=False, label=_(u'С'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    end_date = forms.DateTimeField(required=False, label=_(u'По'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))


    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)

    systemuser = forms.ModelMultipleChoiceField(label=_(u"Администратор"),queryset=SystemUser.objects.all(), widget=forms.SelectMultiple(attrs={'size':'10'}), required=False)
    #start_date = forms.DateTimeField(label=u"Начало",required=False)
    #end_date = forms.DateTimeField(label=u"Конец",required=False)
    
class ActionLogFilterForm(forms.Form):
    systemuser = forms.ModelChoiceField(queryset=SystemUser.objects.all(), required=False)
    start_date = forms.DateTimeField(required=False, label=_(u'С'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    end_date = forms.DateTimeField(required=False, label=_(u'По'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))

    
class SearchAuthLogForm(forms.Form):
    start_date = forms.DateTimeField(required=False, label=_(u'С'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    end_date = forms.DateTimeField(required=False, label=_(u'По'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    account = AutoCompleteSelectMultipleField( 'account_fts', label=_(u'Аккаунт'), required = False)
    nas = forms.ModelMultipleChoiceField(label=_(u"Сервер доступа"), queryset=Nas.objects.all(), required=False)

class IpInUseLogForm(forms.Form):
    start_date = forms.DateTimeField(required=False, label=_(u'С'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    end_date = forms.DateTimeField(required=False, label=_(u'По'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)
    subaccount = AutoCompleteSelectMultipleField( 'subaccount_fts', required = False)
    ippool = forms.ModelMultipleChoiceField(label=_(u"Пул"), queryset=IPPool.objects.all(), required=False)
    ip = forms.IPAddressField(required=False)
    types = forms.ChoiceField(required=False, choices = (('dynamic', _(u"Динамические"), ), ('static', _(u'Статические')), ('', _(u'Любые')),), widget = forms.RadioSelect(renderer=MyCustomRenderer))
    


class AccountTariffBathForm(forms.Form):
    accounts = forms.CharField(required=True)
    tariff = forms.IntegerField(required=True)
    date = forms.DateTimeField(required=True)
    
class AccountAddonServiceModelForm(ModelForm):
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, widget = forms.widgets.HiddenInput)
    subaccount = forms.ModelChoiceField(queryset=SubAccount.objects.all(), required=False, widget = forms.widgets.HiddenInput)
    
    
    
    def __init__(self, *args, **kwargs):
        super(AccountAddonServiceModelForm, self).__init__(*args, **kwargs)
        self.fields['activated'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['deactivated'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['temporary_blocked'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['service'].widget.attrs['class']='input-xlarge span4'
        self.fields['cost'].widget.attrs['class']='input-xlarge span4'
        #self.fields['service'].widget = ModelLinkWidget()


    class Meta:
        model = AccountAddonService
        exclude = ('action_status', 'speed_status', 'last_checkout',)
      
class DocumentModelForm(ModelForm):
    class Meta:
        model = Document
   
class SuspendedPeriodModelForm(ModelForm):
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    def __init__(self, *args, **kwargs):
        super(SuspendedPeriodModelForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['end_date'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})

    class Meta:
        model = SuspendedPeriod
        exclude = ('activated_by_account',)

class SuspendedPeriodBatchForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(queryset=Account.objects.all(), widget = forms.widgets.MultipleHiddenInput)
    start_date = forms.DateTimeField(widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    end_date = forms.DateTimeField(widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))



class TransactionModelForm(ModelForm):
    #created = forms.DateTimeField(required=True)
    account = forms.ModelChoiceField(queryset=Account.objects.all(), widget = forms.HiddenInput)
    type = forms.ModelChoiceField(queryset=TransactionType.objects.filter(is_bonus=False), widget = forms.widgets.Select(attrs={'class': 'input-xlarge'}) )

    def __init__(self, *args, **kwargs):
        super(TransactionModelForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['description'].widget = forms.widgets.TextInput(attrs={'class': 'input-xlarge span5'})
        self.fields['account'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['type'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['bill'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['created'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['end_promise'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})

    def clean_summ(self):
        summ = self.cleaned_data.get('summ',0)
        if summ==0:
            raise forms.ValidationError(_(u'Укажите сумму'))
        return summ
    class Meta:
        model = Transaction
        exclude = ('systemuser', 'accounttarif', 'approved', 'tarif', 'promise_expired', 'prev_balance', 'is_bonus')

class BonusTransactionModelForm(ModelForm):
    #created = forms.DateTimeField(required=True)
    account = forms.ModelChoiceField(queryset=Account.objects.all(), widget = forms.HiddenInput)
    type = forms.ModelChoiceField(queryset=TransactionType.objects.filter(is_bonus=True), widget = forms.widgets.Select(attrs={'class': 'input-xlarge'}) )

    def __init__(self, *args, **kwargs):
        super(BonusTransactionModelForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['description'].widget = forms.widgets.TextInput(attrs={'class': 'input-xlarge span5'})
        self.fields['type'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['bill'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['created'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['created'].initial = datetime.now()

    def clean_summ(self):
        summ = self.cleaned_data.get('summ',0)
        if summ==0:
            raise forms.ValidationError(_(u'Укажите сумму'))
        return summ

    class Meta:
        model = Transaction
        exclude = ('systemuser', 'prev_balance', 'accounttarif', 'tarif', 'promise_expired', 'approved', 'end_promise', 'is_bonus')

        
class AccountTariffForm(ModelForm):
    account = forms.ModelChoiceField(label=_(u'Аккаунт'), queryset=Account.objects.all(), widget = forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        super(AccountTariffForm, self).__init__(*args, **kwargs)

        self.fields['datetime'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        
    class Meta:
        model = AccountTarif
    
class BatchAccountTariffForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(queryset=Account.objects.all(), widget = forms.widgets.MultipleHiddenInput)
    tariff = forms.ModelChoiceField(label=_(u'Тариф'), queryset=Tariff.objects.all())
    datetime = forms.DateTimeField(label=_(u'С даты'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    

        


class SettlementPeriodForm(ModelForm):
    time_start = forms.DateTimeField(label=_(u'Начало периода'), required = True, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
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
              
class AccountForm(DynamicForm):
    username = forms.CharField(label =_(u"Имя пользователя"), required=True, widget = forms.widgets.TextInput(attrs={'class': 'input-medium'}))
    #password = forms.CharField(label = _(u"Пароль") if  settings.HIDE_PASSWORDS==False else _(u"Изменить пароль"), required=False, widget = forms.widgets.PasswordInput(attrs={'class': 'input-medium'}, render_value=False))
    password = forms.CharField(label = _(u"Пароль") if  settings.HIDE_PASSWORDS==False else _(u"Изменить пароль"), required=False, widget = CustomPasswordWidget(attrs={'class': 'input-medium'})  if  settings.HIDE_PASSWORDS==True else forms.widgets.TextInput(attrs={'class': 'input-medium'}))
    
        
    city = forms.ModelChoiceField(label=_(u"Город"),queryset=City.objects.all(), required=False, widget = forms.widgets.Select(attrs={'class': 'input-large',}))
    
    street = forms.CharField(label=_(u"Улица"),  required=False, widget = forms.widgets.TextInput(attrs={'class': 'input-large',}))#AutoCompleteSelectMultipleField('street_name', required = False, label =u"Улица", attrs={'class': 'input-large'})
    house = forms.CharField(label=_(u"Дом"), required=False, widget = forms.widgets.TextInput(attrs={'class': 'input-small', 'placeholder': u'Дом'}))#AutoCompleteSelectMultipleField( 'house_name', required = False, label =u"Дом", placeholder='№ дома', attrs={'class': 'input-small input-street-no'})
    contract = forms.CharField(label=_(u'Номер договора'), required = False)
    contract_num = forms.ModelChoiceField(label=_(u"Номер договора"), queryset=ContractTemplate.objects.all(), required=False, widget = forms.widgets.Select(attrs={'class': 'input-large',}))
    organization = forms.BooleanField(label=_(u"Юр.лицо"), required=False, widget = forms.widgets.CheckboxInput)
    #created = forms.DateTimeField(label=u'Создан', required = True, widget=forms.widgets.SplitDateTimeWidget(attrs={'class':'input-small'}))
    #credit = forms.CharField(label =u"Кредит", required=True, widget = forms.TextInput(attrs={'class': 'input-small'}))
    #--Organization fields
    
    

    
    def __init__(self, *args, **kwargs):
        #if settings.HIDE_PASSWORDS:
        #    self.old_password = kwargs['instance'].password
        #    kwargs['instance'].password=''
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'input-xlarge'
        self.fields['systemuser'].widget.attrs['class'] = 'input-xlarge'
        self.fields['account_group'].widget.attrs['class'] = 'input-xlarge'
        self.fields['contract'].widget.attrs['class'] = 'input-large'
        self.fields['contract_num'].widget.attrs['class'] = 'input-large'
        #self.fields['username'].widget.attrs['class'] = 'input-small'
        #self.fields['password'].widget.attrs['class'] = 'input-small'
        self.fields['credit'].widget.attrs['class'] = 'input-small'
        self.fields['comment'].widget.attrs['class'] = 'input-xlarge span10'
        self.fields['comment'].widget.attrs['cols'] =10
        self.fields['created'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['birthday'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['phone_m'] = PhoneField(required=False)
        self.fields['phone_h'] = PhoneField(required=False)
        self.fields['contactperson_phone'] = PhoneField(required=False)

            

        
    
    class Meta:
        model = Account
        exclude = ('ballance',)
        widgets = {
          'comment': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
        
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        existing = SystemUser.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_(u"Нельзя создать пользователя с именем существующего администратора."))
        else:
            return self.cleaned_data['username']
        
    def clean(self):
        super(AccountForm, self).clean()
        data = self.cleaned_data

        if settings.HIDE_PASSWORDS and not data.get('password'):
            data['password'] = self.instance.password

        return data
        
class AccountExtraForm(DynamicExtraForm):
    
    class Meta:
        model = Account
        
class AccessParametersForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = AccessParameters
        
class AccessParametersTariffForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = AccessParameters
        exclude = ('max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx', 'priority', 'sessionscount')
        
class GroupForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = Group

class TariffForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TariffForm, self).__init__(*args, **kwargs)
        self.fields['access_parameters'].widget = forms.widgets.HiddenInput()
        self.fields['time_access_service'].widget = forms.widgets.HiddenInput()
        self.fields['traffic_transmit_service'].widget = forms.widgets.HiddenInput()
        self.fields['radius_traffic_transmit_service'].widget = forms.widgets.HiddenInput()
        
        self.fields['description'].widget.attrs['rows'] =5
        self.fields['description'].widget.attrs['class'] = 'span10'
        
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = Tariff

class TimeSpeedForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TimeSpeedForm, self).__init__(*args, **kwargs)
        self.fields['access_parameters'].widget = forms.widgets.HiddenInput()
        
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)

    class Meta:
        model = TimeSpeed

class PeriodicalServiceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PeriodicalServiceForm, self).__init__(*args, **kwargs)
        self.fields['tarif'].widget = forms.widgets.HiddenInput()

        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'input-xlarge span5'


        self.fields['created'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['deactivated'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        


    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    #activation_type = forms.BooleanField(required=False, label=u'Начать списание с начала расчётного периода', widget=forms.widgets.CheckboxInput)
    
    class Meta:
        exclude = ('deleted',)
        model = PeriodicalService

class OneTimeServiceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OneTimeServiceForm, self).__init__(*args, **kwargs)
        self.fields['tarif'].widget = forms.widgets.HiddenInput()
        
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = OneTimeService

class TrafficTransmitServiceForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = TrafficTransmitService

class TrafficTransmitNodeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TrafficTransmitNodeForm, self).__init__(*args, **kwargs)
        self.fields['traffic_transmit_service'].widget = forms.widgets.HiddenInput()
        
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)

    class Meta:
        model = TrafficTransmitNodes
      
class PrepaidTrafficForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    traffic_transmit_service = forms.ModelChoiceField(queryset=TrafficTransmitService.objects.all(), widget=forms.widgets.HiddenInput)
    class Meta:
        model = PrepaidTraffic  

class RadiusTrafficForm(ModelForm):
        
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = RadiusTraffic  

class TimeAccessServiceForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = TimeAccessService

class TimeAccessNodeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TimeAccessNodeForm, self).__init__(*args, **kwargs)
        self.fields['time_access_service'].widget = forms.widgets.HiddenInput()
        
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = TimeAccessNode

class RadiusTrafficNodeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RadiusTrafficNodeForm, self).__init__(*args, **kwargs)
        self.fields['radiustraffic'].widget = forms.widgets.HiddenInput()
        
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = RadiusTrafficNode  
        exclude = ('created','deleted')
        
class TrafficLimitForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TrafficLimitForm, self).__init__(*args, **kwargs)
        self.fields['tarif'].widget = forms.widgets.HiddenInput()
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    
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
        self.fields['service_activation_action'].widget.attrs['rows'] = 3
        self.fields['service_deactivation_action'].widget.attrs['class'] = 'span8'
        self.fields['service_deactivation_action'].widget.attrs['rows'] = 3  
        self.fields['comment'].widget.attrs['class'] = 'input-xlarge span6'
        self.fields['comment'].widget.attrs['rows'] = 3
        
    class Meta:
        model = AddonService  

class AddonServiceTarifForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddonServiceTarifForm, self).__init__(*args, **kwargs)
        self.fields['tarif'].widget = forms.widgets.HiddenInput()
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = AddonServiceTarif  
        
class ContractTemplateForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = ContractTemplate  
        exclude =('counter',)

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
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(AccountPrepaysTraficForm, self).__init__(*args, **kwargs)

        self.fields['account_tarif'].widget = forms.HiddenInput()
        self.fields['prepaid_traffic'].widget = forms.HiddenInput()
        self.fields['current'].widget = forms.HiddenInput()
        self.fields['reseted'].widget = forms.HiddenInput()

    class Meta:
        model = AccountPrepaysRadiusTrafic     

class AccountPrepaysTimeForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(AccountPrepaysTimeForm, self).__init__(*args, **kwargs)

        self.fields['account_tarif'].widget = forms.HiddenInput()
        self.fields['prepaid_time_service'].widget = forms.HiddenInput()
        self.fields['current'].widget = forms.HiddenInput()
        self.fields['reseted'].widget = forms.HiddenInput()
        
    class Meta:
        model = AccountPrepaysTime    
        


class AccountPrepaysTraficForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(AccountPrepaysTraficForm, self).__init__(*args, **kwargs)

        self.fields['account_tarif'].widget = forms.HiddenInput()
        self.fields['prepaid_traffic'].widget = forms.HiddenInput()
        self.fields['current'].widget = forms.HiddenInput()
        self.fields['reseted'].widget = forms.HiddenInput()
            
    
    class Meta:
        model = AccountPrepaysTrafic     

class TransactionTypeForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        exclude=('is_deletable',)
        model = TransactionType     

class SuppAgreementForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = SuppAgreement   
        widgets = {
          'description': forms.Textarea(attrs={'rows':4, 'cols':15, 'class': 'span8'}),
          'body': forms.Textarea(attrs={'rows': 10, 'cols':25, 'class': 'span8'}),
        }

class AccountSuppAgreementForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    
        
    class Meta:
        model = AccountSuppAgreement   

        widgets = {
          'account': forms.widgets.HiddenInput,
          'created': forms.widgets.DateTimeInput(attrs={'class':'datepicker'}),
          'closed': forms.widgets.DateTimeInput(attrs={'class':'datepicker'}),
        }

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
    last_ip = forms.CharField(label=_(u"Последний логин с IP"), widget = forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    last_login = forms.CharField(label=_(u"Последний логин"), widget = forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    created = forms.CharField(label=_(u"Создан"), widget = forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    authgroup = forms.ModelMultipleChoiceField(label=_(u"Группа доступа"), queryset = AuthGroup.objects.all(), required=False)
    is_superuser = forms.BooleanField(label=_(u"Суперадминистратор"),widget=forms.CheckboxInput, required=False)
    text_password = forms.CharField(label = _(u"Пароль") if  settings.HIDE_PASSWORDS==False else _(u"Изменить пароль"), required=False, widget = CustomPasswordWidget()  if  settings.HIDE_PASSWORDS==True else forms.widgets.TextInput())
    class Meta:
        model = SystemUser
        exclude = ('last_ip', 'last_login', 'created', 'password')
        
        
    
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
    time_start = forms.DateTimeField(label=_(u'Начало периода'), required = True, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    time_end = forms.DateTimeField(label=_(u'Конец периода'), required = True, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
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
    name = forms.CharField(required=True, label=_(u"Название"))
    class Meta:
        model = Manufacturer

class AccountHardwareForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, widget = forms.widgets.HiddenInput)
    #hardware = AutoCompleteSelectField( 'hardware_fts', label = _(u"Устройство"), required = True, widget = forms.TextInput(attrs={'class': 'input-xlarge'}), help_text=u"Поиск устройства по всем полям")
    hardware = forms.ModelChoiceField(queryset = Hardware.objects.all(), widget=selectable.AutoComboboxSelectWidget(HardwareLookup))
    
    
    comment = forms.CharField(label=_(u'Комментарий'), required=False, widget=forms.widgets.Textarea(attrs={'rows':5, 'class': 'input-large span5'}))
    
    def __init__(self, *args, **kwargs):
        super(AccountHardwareForm, self).__init__(*args, **kwargs)


    
    class Meta:
        model = AccountHardware
     
class ModelHardwareForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    name = forms.CharField(required=True, label=_(u"Название"))
    class Meta:
        model = Model
           
class HardwareTypeForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    name = forms.CharField(required=True, label=_(u"Название"))
    class Meta:
        model = HardwareType
        
class HardwareForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    
    class Meta:
        model = Hardware 

class AccountGroupForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    name = forms.CharField(required=True, label=_(u"Название"))
    class Meta:
        model = AccountGroup
        
class PermissionGroupForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    permissions = forms.ModelMultipleChoiceField(label=_(u'Права'), queryset = Permission.objects.all(), widget = CheckboxSelectMultipleWithSelectAll)
    class Meta:
        exclude = ('deletable',)
        model = PermissionGroup
        
        
class TPChangeRuleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TPChangeRuleForm, self).__init__(*args, **kwargs)

        
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    

    class Meta:
        model = TPChangeRule
        
class TPChangeMultipleRuleForm(forms.Form):
    from_tariff = forms.ModelChoiceField(queryset=Tariff.objects.all())
    to_tariffs = forms.ModelMultipleChoiceField(queryset=Tariff.objects.all(), label=_(u'Тарифные планы'), required=False, widget=forms.widgets.SelectMultiple)
    disabled = forms.BooleanField(label=_(u'Временно запретить'), initial=False, required=False)
    cost = forms.FloatField(label=_(u'Стоимость перехода'), initial=0)
    ballance_min = forms.FloatField(label=_(u'Минимальный баланс'), initial=0)
    on_next_sp = forms.BooleanField(label=_(u'Со следующего расчётного периода'), required=False)
    settlement_period = forms.ModelChoiceField(queryset=SettlementPeriod.objects.all(), label=_(u'Расчётный период'), required=False)
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    mirror = forms.BooleanField(label=_(u'Создать зеркальное правило'),required=False)
    
    def __init__(self, *args, **kwargs):
        super(TPChangeMultipleRuleForm, self).__init__(*args, **kwargs)
        self.fields['to_tariffs'].widget.attrs['size'] =20
        
 
    

        
class NewsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget.attrs['class'] = 'input-xlarge span8'
        self.fields['created'].widget =forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['age'].widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'})

    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    accounts = AutoCompleteSelectMultipleField( 'account_fts', label=_(u'Аккаунты'), required = False)
    class Meta:
        model = News

class CardForm(ModelForm):
    class Meta:
        model = Card
    
class CardGenerationForm(forms.Form):

    card_type = forms.ChoiceField(required=True, choices = ((0, _(u"Экспресс-оплаты"), ), (1, _(u'Хотспот')), (2, _(u'VPN доступ')), (3, _(u'Телефония')),), widget = forms.HiddenInput)
    series = forms.CharField(label=u"Серия", widget=forms.widgets.Input(attrs={'class':'input-small'}))
    count = forms.IntegerField(label=u"Количество", widget=forms.widgets.Input(attrs={'class':'input-small'}))
    login_length_from = forms.IntegerField(required=False, widget=forms.widgets.Input(attrs={'class':'input-small'}))
    login_length_to = forms.IntegerField(required=False, widget=forms.widgets.Input(attrs={'class':'input-small'}))
    login_numbers = forms.BooleanField(required=False, label="0-9", widget = forms.CheckboxInput)
    login_letters = forms.BooleanField(required=False, label="a-Z", widget = forms.CheckboxInput)
    pin_length_from = forms.IntegerField(widget=forms.widgets.Input(attrs={'class':'input-small'}))
    pin_length_to = forms.IntegerField(widget=forms.widgets.Input(attrs={'class':'input-small'}))
    pin_numbers = forms.BooleanField(label="0-9", required=False, widget = forms.CheckboxInput)
    pin_letters = forms.BooleanField(label="a-Z", required=False, widget = forms.CheckboxInput)
    nominal = forms.FloatField(label=_(u"Номинал"),widget=forms.widgets.Input(attrs={'class':'input-small'}))
    tariff = forms.ModelChoiceField(queryset=Tariff.objects.all(), label=_(u"Тариф"), required=False)
    #template = forms.ModelChoiceField(queryset=Template.objects.filter(type__id=7), label=u"Шаблон печати")
    nas = forms.ModelChoiceField(queryset=Nas.objects.all(), label=_(u"Сервер доступа"), required=False)
    ippool = forms.ModelChoiceField(queryset=IPPool.objects.all(), label=u"IP пул", required=False)
    date_start = forms.DateTimeField(label=_(u'Активировать с'), required = True, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=_(u'Активировать по'), required = True, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    
    def clean(self):
        cleaned_data = super(CardGenerationForm, self).clean()
        if cleaned_data.get("card_type") in [1,2,3] and not (cleaned_data.get("login_numbers") or cleaned_data.get("login_letters")):
            raise forms.ValidationError(_(u'Вы должны выбрать состав логина'))
        if not (cleaned_data.get("pin_numbers") or cleaned_data.get("pin_letters")):
            raise forms.ValidationError(_(u'Вы должны выбрать состав пина'))

        return cleaned_data
    
class CardSearchForm(forms.Form):
    id = forms.IntegerField(required=False)
    card_type = forms.ChoiceField(required=False, choices = (('', u"", ), (0, _(u"Экспресс-оплаты"), ), (1, _(u'Хотспот')), (2, _(u'VPN доступ')), (3, _(u'Телефония')),))
    dealer = forms.ModelChoiceField(queryset = Dealer.objects.all(), required=False, label=_(u"Дилер"))
    series = forms.CharField(required=False, label=_(u"Серия"))
    login = forms.CharField(required=False)
    pin = forms.CharField(required=False)
    ext_id = forms.CharField(required=False)
    nominal = FloatConditionField(required=False, label=_(u"Номинал"))
    tariff = forms.ModelChoiceField(queryset=Tariff.objects.all(), label=_(u"Тариф"), required=False)
    #template = forms.ModelChoiceField(required=False, queryset=Template.objects.all(), label=u"Шаблон печати")
    nas = forms.ModelChoiceField(queryset=Nas.objects.all(), label=_(u"Сервер доступа"), required=False)
    ippool = forms.ModelChoiceField(queryset=IPPool.objects.all(), label=_(u"IP пул"), required=False)
    sold = DateRangeField(required=False, label=_(u"Проданы"))
    not_sold = forms.BooleanField(required=False, label=_(u"Не проданные"))
    activated = DateRangeField(label=_(u'Активированы'), required=False)
    activated_by = AutoCompleteSelectMultipleField( 'account_username', label=_(u'Активатор'), required = False)
    created = DateRangeField(label=_(u'Созданы'), required=False )
    
class CardBatchChangeForm(forms.Form):
    cards = forms.CharField(required=True, widget = forms.widgets.HiddenInput)
    card_type = forms.ChoiceField(required=False, choices = ((-1, _(u"Не менять")), (0, _(u"Экспресс-оплаты"), ), (1, _(u'Хотспот')), (2, _(u'VPN доступ')), (3, _(u'Телефония')),))
    #change_series = forms.BooleanField(label=u"Изменить серию", widget=forms.widgets.CheckboxInput)
    series = forms.CharField(required=False, label=_(u"Серия"), widget=forms.widgets.TextInput(attrs={'class':'span5'}))
    change_login = forms.BooleanField(required=False, label=_(u"Изменить логин"))
    login_length_from = forms.IntegerField(required=False, widget=forms.widgets.Input(attrs={'class':'input-small'}))
    login_length_to = forms.IntegerField(required=False, widget=forms.widgets.Input(attrs={'class':'input-small'}))
    login_numbers = forms.BooleanField(required=False, label="0-9", widget = forms.CheckboxInput)
    login_letters = forms.BooleanField(required=False, label="a-Z", widget = forms.CheckboxInput)
    change_pin = forms.BooleanField(required=False, label=_(u"Изменить пин"))
    pin_length_from = forms.IntegerField(required=False, widget=forms.widgets.Input(attrs={'class':'input-small'}))
    pin_length_to = forms.IntegerField(required=False, widget=forms.widgets.Input(attrs={'class':'input-small'}))
    pin_numbers = forms.BooleanField(required=False, label="0-9", widget = forms.CheckboxInput)
    pin_letters = forms.BooleanField(required=False, label="a-Z", widget = forms.CheckboxInput)
    change_nominal = forms.BooleanField(required=False, label=_(u"Изменить номинал"))
    nominal = forms.FloatField(required=False, label=_(u"Номинал"),widget=forms.widgets.Input(attrs={'class':'input-small'}))
    tariff = forms.ModelChoiceField(queryset=Tariff.objects.all(), label=_(u"Тариф"), required=False)
    #template = forms.ModelChoiceField(required=False, queryset=Template.objects.filter(type__id=7), label=u"Шаблон печати")
    nas = forms.ModelChoiceField(queryset=Nas.objects.all(), label=_(u"Сервер доступа"), required=False)
    ippool = forms.ModelChoiceField(queryset=IPPool.objects.all(), label=_(u"IP пул"), required=False)
    
    date_start = forms.DateTimeField(label=_(u'Активировать с'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=_(u'Активировать по'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    

class DealerForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = Dealer    

class SaleCardForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SaleCardForm, self).__init__(*args, **kwargs)
        self.fields['cards'].widget = forms.widgets.MultipleHiddenInput()
    
    cards = forms.ModelMultipleChoiceField(queryset=Card.objects.all(), required=True, label=_(u"Карты"), widget=forms.widgets.MultipleHiddenInput)
    dealer = forms.ModelChoiceField(queryset=Dealer.objects.all(), required=True, label=_(u"Дилер"), widget=forms.widgets.HiddenInput)

    prepayment_sum = forms.FloatField(label=_(u"Внесено предоплаты"), required=False)
    
    class Meta:
        model = SaleCard    

class DealerPayForm(ModelForm):
    class Meta:
        model = DealerPay    

class OperatorForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OperatorForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'input-xlarge span8'
        
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    
    class Meta:
        model = Operator    

class BallanceHistoryForm(forms.Form):
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)
    start_date = forms.DateTimeField(required=False, label=_(u'С'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    end_date = forms.DateTimeField(required=False, label=_(u'По'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))

class PeriodicalServiceLogSearchForm(forms.Form):
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)
    tariff = forms.ModelChoiceField(queryset=Tariff.objects.all(), required=False)
    periodicalservice = forms.ModelChoiceField(queryset=PeriodicalService.objects.all(), required=False)
    
class SheduleLogSearchForm(forms.Form):
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)

    
#TO-DO: добавить exclude в periodicalservice
class SubAccountForm(ModelForm):
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, widget = forms.HiddenInput)
    password = forms.CharField(label = _(u"Пароль") if  settings.HIDE_PASSWORDS==False else _(u"Изменить пароль"), required=False, widget = CustomPasswordWidget()  if  settings.HIDE_PASSWORDS==True else forms.widgets.TextInput())
    ipn_speed = forms.CharField(label=_(u'IPN скорость'), help_text=_(u"Не менять указанные настройки скорости"), required = False, widget = forms.TextInput(attrs={'class': 'span6'}))
    vpn_speed = forms.CharField(label=_(u'VPN скорость'), help_text=_(u"Не менять указанные настройки скорости"), required = False, widget = forms.TextInput(attrs={'class': 'span6'}))
    ipv4_vpn_pool = forms.ModelChoiceField(queryset=IPPool.objects.filter(type=0), required=False)
    ipv6_vpn_pool = forms.ModelChoiceField(queryset=IPPool.objects.filter(type=2), required=False)
    ipv4_ipn_pool = forms.ModelChoiceField(queryset=IPPool.objects.filter(type=1), required=False)
    ipn_status = forms.MultipleChoiceField(required=False, choices = (('added', _(u"Добавлен"), ), ('enabled', _(u'Активен')), ('suspended', _(u'Не менять состояние')),), widget=MyMultipleCheckBoxInput, initial = ["undefined", ])
    
            
    class Meta:
        model = SubAccount
        exclude = ('ipn_ipinuse','vpn_ipinuse',)


    def clean(self):
        cleaned_data = super(SubAccountForm, self).clean()
        
        if cleaned_data.get('username',''):
            subaccs = SubAccount.objects.filter(username = cleaned_data.get('username')).exclude(account = cleaned_data.get('account')).count()

            #print 'subaccs', subaccs
            if subaccs>0:
                raise forms.ValidationError(_(u'Указанный логин субаккаунта используется в другом аккаунте'))


        if cleaned_data.get('ipn_mac_address'):    
            subaccs = SubAccount.objects.exclude(account = cleaned_data.get('account')).filter(ipn_mac_address = cleaned_data.get('ipn_mac_address')).count()

            if subaccs>0:
                raise forms.ValidationError(_(u'Указанный MAC-адрес используется в другом аккаунте'))

        if str(cleaned_data.get('vpn_ip_address')) not in ('','0.0.0.0', '0.0.0.0/32'):    
            subaccs = SubAccount.objects.exclude(account = cleaned_data.get('account')).filter(vpn_ip_address = cleaned_data.get('vpn_ip_address')).count()

            if subaccs>0:
                raise forms.ValidationError(_(u'Указанный VPN IP адрес используется в другом аккаунте'))
            if cleaned_data.get('ipv4_vpn_pool'):
                if not IPy.IP(cleaned_data.get('ipv4_vpn_pool').start_ip).int()<=IPy.IP(cleaned_data.get('vpn_ip_address')).int()<=IPy.IP(cleaned_data.get('ipv4_vpn_pool').end_ip).int():
                    raise forms.ValidationError(_(u'Выбранный VPN IP адрес не принадлежит указанному VPN пулу'))
                
            
        if str(cleaned_data.get('ipn_ip_address')) not in ('', '0.0.0.0', '0.0.0.0/32'):    

            subaccs = SubAccount.objects.exclude(account = cleaned_data.get('account')).filter(ipn_ip_address = cleaned_data.get('ipn_ip_address')).count()

            if subaccs>0:

                raise forms.ValidationError(_(u'Указанный IPN IP адрес используется в другом аккаунте'))
            if cleaned_data.get('ipv4_ipn_pool'):
                if not ipaddr.IPv4Network(cleaned_data.get('ipv4_ipn_pool').start_ip)<=ipaddr.IPv4Network(cleaned_data.get('ipn_ip_address'))<=ipaddr.IPv4Network(cleaned_data.get('ipv4_ipn_pool').end_ip):
                    raise forms.ValidationError(_(u'Выбранный IPN IP адрес не принадлежит указанному IPN пулу'))
                



        if str(cleaned_data.get('vpn_ipv6_ip_address')) not in ('','::', ':::'):    
            subaccs = SubAccount.objects.exclude(account = cleaned_data.get('account')).filter(vpn_ipv6_ip_address = cleaned_data.get('vpn_ipv6_ip_address')).count()

            if subaccs>0:
                raise forms.ValidationError(_(u'Указанный VPN IPv6 IP адрес используется в другом аккаунте'))
            
            if cleaned_data.get('ipv6_vpn_pool'):
                if not IPy.IP(cleaned_data.get('ipv6_vpn_pool').start_ip).int()<=IPy.IP(cleaned_data.get('vpn_ipv6_ip_address')).int()<=IPy.IP(cleaned_data.get('ipv6_vpn_pool').end_ip).int():
                    raise forms.ValidationError(_(u'Выбранный IPv6 VPN IP адрес не принадлежит указанному IPv6 IPN пулу'))
                

        
        return cleaned_data
    
    
class SubAccountPartialForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, widget = forms.widgets.HiddenInput)
    password = forms.CharField(label = _(u"Пароль") if  settings.HIDE_PASSWORDS==False else _(u"Изменить пароль"), required=False, widget = CustomPasswordWidget()  if  settings.HIDE_PASSWORDS==True else forms.widgets.TextInput())
    ipv4_vpn_pool = forms.ModelChoiceField(queryset=IPPool.objects.filter(type=0), required=False)
    ipv6_vpn_pool = forms.ModelChoiceField(queryset=IPPool.objects.filter(type=2), required=False)
    ipv4_ipn_pool = forms.ModelChoiceField(queryset=IPPool.objects.filter(type=1), required=False)

    
    def clean(self):
        super(SubAccountPartialForm, self).clean()
        cleaned_data = self.cleaned_data
        
#===============================================================================
#        if cleaned_data.get('username',''):
#            if cleaned_data.get('account'):
#                subaccs = SubAccount.objects.filter(username = cleaned_data.get('username')).exclude(account = cleaned_data.get('account')).count()
#            else:
#                subaccs = SubAccount.objects.filter(username = cleaned_data.get('username')).count()
#            
# 
#            #print 'subaccs', subaccs
#            if subaccs>0:
#                raise forms.ValidationError(_(u'Указанный логин субаккаунта используется в другом аккаунте'))
#===============================================================================


#===============================================================================
#        if cleaned_data.get('ipn_mac_address'):    
#            if cleaned_data.get('account'):
#                subaccs = SubAccount.objects.exclude(account = cleaned_data.get('account')).filter(ipn_mac_address = cleaned_data.get('ipn_mac_address')).count()
#            else:
#                subaccs = SubAccount.objects.filter(ipn_mac_address = cleaned_data.get('ipn_mac_address')).count()
# 
#            if subaccs>0:
#                raise forms.ValidationError(_(u'Указанный MAC-адрес используется в другом аккаунте'))
#===============================================================================

        if str(cleaned_data.get('vpn_ip_address')) not in ('','0.0.0.0', '0.0.0.0/32'):    
            #===================================================================
            # if cleaned_data.get('account'):
            #    subaccs = SubAccount.objects.exclude(account = cleaned_data.get('account')).filter(vpn_ip_address = cleaned_data.get('vpn_ip_address')).count()
            # else:
            #    subaccs = SubAccount.objects.filter(vpn_ip_address = cleaned_data.get('vpn_ip_address')).count()
            # if subaccs>0:
            #    raise forms.ValidationError(_(u'Указанный VPN IP адрес используется в другом аккаунте'))
            #===================================================================
            if cleaned_data.get('ipv4_vpn_pool'):
                if not IPy.IP(cleaned_data.get('ipv4_vpn_pool').start_ip).int()<=IPy.IP(cleaned_data.get('vpn_ip_address')).int()<=IPy.IP(cleaned_data.get('ipv4_vpn_pool').end_ip).int():
                    raise forms.ValidationError(_(u'Выбранный VPN IP адрес не принадлежит указанному VPN пулу'))
                
            
        if str(cleaned_data.get('ipn_ip_address')) not in ('', '0.0.0.0', '0.0.0.0/32'):    
#===============================================================================
#            if cleaned_data.get('account'):
#                subaccs = SubAccount.objects.exclude(account = cleaned_data.get('account')).filter(ipn_ip_address = cleaned_data.get('ipn_ip_address')).count()
#            else:
#                subaccs = SubAccount.objects.filter(ipn_ip_address = cleaned_data.get('ipn_ip_address')).count()
#            if subaccs>0:
# 
#                raise forms.ValidationError(_(u'Указанный IPN IP адрес используется в другом аккаунте'))
#===============================================================================
            if cleaned_data.get('ipv4_ipn_pool'):
                if not ipaddr.IPv4Network(cleaned_data.get('ipv4_ipn_pool').start_ip)<=ipaddr.IPv4Network(cleaned_data.get('ipn_ip_address'))<=ipaddr.IPv4Network(cleaned_data.get('ipv4_ipn_pool').end_ip):
                    raise forms.ValidationError(_(u'Выбранный IPN IP адрес не принадлежит указанному IPN пулу'))
                



        if str(cleaned_data.get('vpn_ipv6_ip_address')) not in ('','::', ':::'):    
            #===================================================================
            # if cleaned_data.get('account'):
            #    subaccs = SubAccount.objects.exclude(account = cleaned_data.get('account')).filter(vpn_ipv6_ip_address = cleaned_data.get('vpn_ipv6_ip_address')).count()
            # else:
            #    subaccs = SubAccount.objects.filter(vpn_ipv6_ip_address = cleaned_data.get('vpn_ipv6_ip_address')).count()
            #    
            # if subaccs>0:
            #    raise forms.ValidationError(_(u'Указанный VPN IPv6 IP адрес используется в другом аккаунте'))
            #===================================================================
            
            if cleaned_data.get('ipv6_vpn_pool'):
                if not IPy.IP(cleaned_data.get('ipv6_vpn_pool').start_ip).int()<=IPy.IP(cleaned_data.get('vpn_ipv6_ip_address')).int()<=IPy.IP(cleaned_data.get('ipv6_vpn_pool').end_ip).int():
                    raise forms.ValidationError(_(u'Выбранный IPv6 VPN IP адрес не принадлежит указанному IPv6 IPN пулу'))
                
        return cleaned_data
    
    class Meta:
        model = SubAccount
        fields = ['id', 'nas', 'username', 'password', 'ipn_mac_address', 'ipn_ip_address', 'vpn_ip_address', 'vpn_ipv6_ip_address', 'ipv4_vpn_pool', 'ipv6_vpn_pool', 'ipv4_ipn_pool', 'sessionscount', 'switch', 'switch_port', 'vlan']
        exclude = ('ipn_ipinuse','vpn_ipinuse', 'account', 'allow_dhcp', 'allow_dhcp_with_null', 'allow_dhcp_with_minus', 'allow_dhcp_with_block', 'allow_dhcp_with_block', 'allow_vpn_with_null', 'allow_vpn_with_minus', 'allow_vpn_with_block', 'allow_ipn_with_null', 'allow_ipn_with_minus', 'allow_ipn_with_block', 'associate_pptp_ipn_ip', 'associate_pppoe_ipn_mac')

        
class TemplateSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TemplateSelectForm, self).__init__(*args, **kwargs)
        self.fields['template'].widget.attrs['class'] = 'span5'
    template = forms.ModelChoiceField(queryset = Template.objects.all())
    
class DealerSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DealerSelectForm, self).__init__(*args, **kwargs)
        self.fields['dealer_item'].widget.attrs['class'] = 'span5'
    dealer_item = forms.ModelChoiceField(queryset = Dealer.objects.all())
    
    
class SwitchForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-SwitchForm'
        self.helper.form_class = 'well form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse("switch_edit")
        self.helper.layout = Layout(
            Fieldset(
                _(u'Общее'),
                 'id',
                'name',
                'comment',

            ),    
            Fieldset(
                _(u'Данные техпаспорта'),
                'manufacturer',
                'model',
                'sn',
            ),    
            Fieldset(
                _(u'Место установки'),
                'city',
                'street',
                'house',
                'place'
            ),    
            Fieldset(
                _(u'SNMP'),
                'snmp_support',
                'snmp_version',
                'snmp_community',
            ),                  
            Fieldset(
                _(u'Управление портами'),
                HTML(_(u'Обратите внимание, что в текущей версии управление портами не реализовано')),
                'management_method',
                'username',
                'password',
                'enable_port',
                'disable_port',
            ),       
            Fieldset(
                _(u'Сетевая идентификация'),
                'ports_count',
                'ipaddress',
                'macaddress',
            ),
            Fieldset(
                _(u'Option82'),
                'option82',
                'option82_auth_type',
                'option82_template',
                'identify',
                'secret',
                'remote_id'
            ),
            FormActions(
                Submit('save', _(u'Сохранить'), css_class="btn-primary")
            )
               
        )
        
        #self.helper.add_input(Submit('submit', 'Сохранить'))
        #self.helper.add_input(Reset('reset', 'Сбросить'))
        super(SwitchForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs['class'] = 'input-xlarge span6'
        self.fields['comment'].widget.attrs['rows'] = 3
        self.fields['place'].widget.attrs['class'] = 'input-xlarge span6'
        self.fields['place'].widget.attrs['rows'] = 3
        self.fields['enable_port'].widget.attrs['class'] = 'input-xlarge span6'
        self.fields['enable_port'].widget.attrs['rows'] = 3
        
        self.fields['disable_port'].widget.attrs['class'] = 'input-xlarge span6'
        self.fields['disable_port'].widget.attrs['rows'] = 3
        
    class Meta:
        model = Switch
        exclude = ('broken_ports', 'uplink_ports', 'protected_ports', 'monitored_ports', 'disabled_ports')
        
class GroupStatSearchForm(forms.Form):

    accounts = AutoCompleteSelectMultipleField( 'account_username', label=_(u'Аккаунты'), required = False)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), label=_(u'Группы трафика'), required=False)
    date_start = forms.DateTimeField(label=_(u'С'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=_(u'По'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    
class GlobalStatSearchForm(forms.Form):

    accounts = AutoCompleteSelectMultipleField( 'account_username', label=_(u'Аккаунты'), required = False)
    #groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), label=u'Группы трафика', required=False)
    start_date = forms.DateTimeField(required=False, label=_(u'С'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    end_date = forms.DateTimeField(required=False, label=_(u'По'), widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))

    
class AccountPrepaysTraficSearchForm(forms.Form):
    date_start = forms.DateTimeField(label=_(u'С'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=_(u'По'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    account = AutoCompleteSelectMultipleField( 'account_username', label=_(u'Аккаунты'), required = False)
    group = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), label=_(u'Группы трафика'), required=False)
    tariff = forms.ModelMultipleChoiceField(queryset=Tariff.objects.all(), required=False, label=_(u'Тарифный план'))

    current  = forms.BooleanField(label=_(u'Только текущие значения'), help_text=_(u'Иначе будет показана информация и за прошлые периоды'), required=False, initial=True)
    
class AccountPrepaysRadiusTraficSearchForm(forms.Form):
    date_start = forms.DateTimeField(label=_(u'С'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=_(u'По'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    account = AutoCompleteSelectMultipleField( 'account_username', label=_(u'Аккаунты'), required = False)
    tariff = forms.ModelMultipleChoiceField(queryset=Tariff.objects.all(), required=False, label=_(u'Тарифный план'))
    current  = forms.BooleanField(label=u'Только текущие значения', help_text=_(u'Иначе будет показана информация и за прошлые периоды'), required=False, initial=True)
    
class AccountPrepaysTimeSearchForm(forms.Form):
    date_start = forms.DateTimeField(label=_(u'С'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=_(u'По'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    account = AutoCompleteSelectMultipleField( 'account_username', label=_(u'Аккаунты'), required = False)
    tariff = forms.ModelMultipleChoiceField(queryset=Tariff.objects.all(), required=False, label=_(u'Тарифный план'))
    
    current  = forms.BooleanField(label=_(u'Только текущие значения'), help_text=_(u'Иначе будет показана информация и за прошлые периоды'), required=False, initial=True)
    
class AccountManagementForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(queryset = Account.objects.all_with_deleted())

class PaymentSearchForm(forms.Form):
    accounts = AutoCompleteSelectMultipleField( 'account_username', label=_(u'Аккаунты'), required = False)
    payment = forms.CharField(initial='', label=_(u'Номер платежа'), required=False)
    date_start = forms.DateTimeField(label=_(u'Создан с'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=_(u'Создан по'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    paid_start = forms.DateTimeField(label=_(u'Оплачен с'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    paid_end = forms.DateTimeField(label=_(u'Оплачен по'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    status = forms.ChoiceField(choices=[('', '---')]+PAYMENT_STATUS_CHOICES, required=False, initial='')
    
class PaymentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['account'].widget = forms.widgets.HiddenInput()
        self.fields['order'].widget = forms.widgets.HiddenInput()
        #self.fields['created_on'].widget =forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        self.fields['paid_on'].widget =forms.widgets.DateTimeInput(attrs={'class':'datepicker'})
        

    id = forms.IntegerField(required=False, widget = forms.HiddenInput)

    class Meta:
        model = Payment
        
class SearchSmsForm(forms.Form):
    from sendsms.utils import get_backend_choices
    bc = get_backend_choices()
    accounts = AutoCompleteSelectMultipleField( 'account_username', label=_(u'Аккаунты'), required = False)
    phone = forms.CharField(label=_(u'Телефон'), required = False, widget = forms.TextInput)
    backend = forms.ChoiceField(label=_(u'Оператор'), choices = bc, initial = bc[0][0] if bc else '', required=False)
    publish_date = forms.DateTimeField(label=_(u'Опубликовать'), help_text = _(u'Когда должно быть отослано сообщение'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    sended_from = forms.DateTimeField(label=_(u'Отправлено с'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    sended_to = forms.DateTimeField(label=_(u'Отправлено по'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    
class SendSmsForm(forms.Form):
    from sendsms.utils import get_backend_choices
    bc = get_backend_choices()
    accounts = forms.ModelMultipleChoiceField(queryset=Account.objects.filter(phone_m__isnull=False), widget = forms.widgets.MultipleHiddenInput)
    backend = forms.ChoiceField(label=_(u'Оператор'), choices = bc, initial = bc[0][0] if bc else '', widget = forms.widgets.Select(attrs={'rows':4, 'class': 'input-large span5'}))
    body = forms.CharField(label=_(u'Сообщение'), widget = forms.widgets.Textarea(attrs={'rows':4, 'class': 'input-large span5'}), help_text=_(u"Можно использовать {{account.ballance}}, {{account.fullname}}, {{account.username}}, {{account.contract}}"))
    publish_date = forms.DateTimeField(label=_(u'Опубликовать'), help_text = _(u'Не указывайте, если сообщения должны быть отправлены сразу'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    

    
class DynamicSchemaFieldForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    
    class Meta:
        model = DynamicSchemaField

