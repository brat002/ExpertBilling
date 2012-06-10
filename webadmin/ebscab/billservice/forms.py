# -*- encoding: utf-8 -*-
from django import forms
from django.contrib.admin import widgets   
from datetime import datetime, date
from django.forms import ModelForm
from billservice.models import Tariff, AddonService, TPChangeRule, Account, SubAccount, AccountTarif, AccountAddonService, Document, SuspendedPeriod, Transaction
from billservice.models import PeriodicalService, TimePeriod, SystemUser, TransactionType, SettlementPeriod, RadiusTraffic, RadiusTrafficNode
from billservice.models import Organization, PrepaidTraffic, TrafficTransmitNodes, BankData, Group, AccessParameters, TimeSpeed, OneTimeService, TrafficTransmitService
from billservice.models import RadiusAttrs, AccountPrepaysTrafic, Template, AccountPrepaysRadiusTrafic, TimeAccessService, ContractTemplate, TimeAccessNode, TrafficLimit, SpeedLimit, AddonService, AddonServiceTarif
from billservice.models import City, Street, Operator, SaleCard, DealerPay, Dealer, News, Card, TPChangeRule, House, TimePeriodNode, IPPool, Manufacturer, AccountHardware, Model, HardwareType, Hardware

from nas.models import Nas

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Reset,  HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions


from ajax_select.fields import AutoCompleteSelectMultipleField


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
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method= "GET"
        self.helper.form_action = "/ebsadmin/accountsreport/"
        self.helper.layout = Layout(
            FormActions(
                Submit('all', 'На одной странице', css_class="btn btn-success"),
                Submit('paging', 'С пагинацией', css_class="btn-primary"),
                Reset('reset', 'Очистить',  css_class="btn"),
            ),
            Field('account', css_class='input-xlarge'),
            Field('created_from', css_class='input-small'),
            Field('created_to', css_class='input-small'),
            Field('contract', css_class='input-xlarge'),
            Field('fullname', css_class='input-xlarge'),
            Field('contactperson', css_class='input-xlarge'),
            Field('city', css_class='input-xlarge'),
            
            Field('street', css_class='input-xlarge'),
            Field('house', css_class='input-xlarge'),
            FormActions(
                Submit('all', 'На одной странице', css_class="btn btn-success"),
                Submit('paging', 'С пагинацией', css_class="btn-primary"),
                Reset('reset', 'Очистить'),
            ),

        )
        super(SearchAccountForm, self).__init__(*args, **kwargs)
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False)
    contract = AutoCompleteSelectMultipleField( 'account_contract', label = u"Номер договора", required = False)
    username = AutoCompleteSelectMultipleField( 'account_username', required = False, help_text=u"Введите часть фразы для поиска")
    fullname = AutoCompleteSelectMultipleField( 'account_fullname', required = False, help_text=u"Введите часть фразы для поиска")
    contactperson = AutoCompleteSelectMultipleField( 'account_contactperson', required = False, help_text=u"Введите часть фразы для поиска")
    city = AutoCompleteSelectMultipleField( 'city_name', required = False, help_text=u"Введите часть фразы для поиска")
    street = AutoCompleteSelectMultipleField( 'street_name', required = False, help_text=u"Введите часть фразы для поиска")
    house = AutoCompleteSelectMultipleField( 'house_name', required = False, help_text=u"Введите часть фразы для поиска")
    house_bulk = forms.CharField(required=False)
    room = forms.CharField(required=False)
    status = forms.IntegerField(required=False)
    ballance_exp = forms.CharField(required=False)
    ballance = forms.DecimalField(required=False)
    credit_exp = forms.CharField(required=False)
    credit = forms.DecimalField(required=False)
    tariff = forms.ModelMultipleChoiceField(queryset=Nas.objects.all(), required=False)
    group_filter = forms.MultipleChoiceField(required=False)
    ballance_blocked = forms.CheckboxInput()
    limit_blocked = forms.CheckboxInput()
    nas = forms.ModelMultipleChoiceField(queryset=Nas.objects.all(), required=False)
    ipn_added = forms.CheckboxInput()
    ipn_enabled = forms.CheckboxInput()
    ipn_sleep = forms.CheckboxInput()
    systemuser_filter = forms.MultipleChoiceField(required=False)
    created_from = forms.DateField(required=False, label=u"C", widget =  widgets.AdminDateWidget )
    created_to = forms.DateField(required=False, label=u"по", widget =  widgets.AdminDateWidget)

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
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method= "GET"
        self.helper.form_action = "/ebsadmin/transactionreport2/"
        self.helper.layout = Layout(
            FormActions(
                Submit('all', 'На одной странице', css_class="btn btn-success"),
                Submit('paging', 'С пагинацией', css_class="btn-primary"),
                Reset('reset', 'Очистить',  css_class="btn"),
            ),
            Field('account', css_class='input-xlarge'),
            'start_date',
            'end_date',
            Field('tarif', css_class='input-xlarge'),
            Field('transactiontype', css_class='input-xlarge'),
            Field('promise', css_class='input-xlarge'),
            Field('promise_expired', css_class='input-xlarge'),
            
            Field('periodicalservice', css_class='input-xlarge'),
            Field('addonservice', css_class='input-xlarge'),
            'systemuser',
            FormActions(
                Submit('all', 'На одной странице', css_class="btn btn-success"),
                Submit('paging', 'С пагинацией', css_class="btn-primary"),
                Reset('reset', 'Очистить'),
            ),

        )
        super(TransactionReportForm, self).__init__(*args, **kwargs)
    account = forms.ModelMultipleChoiceField(label=u"Аккаунт", queryset=Account.objects.all(), widget=forms.SelectMultiple(attrs={'size':'10'}), required=False)
    #subaccount = forms.IntegerField(required=False)
    #tarif = forms.ModelMultipleChoiceField(label=u"Тарифный план",queryset=Tariff.objects.all(), widget=forms.SelectMultiple(attrs={'size':'10'}), required=False)
    #addonservice = forms.ModelMultipleChoiceField(label=u"Подключаемая услуга",queryset=AddonService.objects.all(), widget=forms.SelectMultiple(attrs={'size':'10'}), required=False)
    systemuser = forms.ModelMultipleChoiceField(label=u"Администратор",queryset=SystemUser.objects.all(), widget=forms.SelectMultiple(attrs={'size':'10'}), required=False)
    #periodicalservice = forms.ModelMultipleChoiceField(label=u"Периодическая услуга",queryset=PeriodicalService.objects.all(), widget=forms.SelectMultiple(attrs={'size':'10'}), required=False)
    transactiontype = forms.MultipleChoiceField(label=u"Тип проводки",choices=[(x.internal_name, x.name) for x in TransactionType.objects.all()], widget=forms.SelectMultiple(attrs={'size':'10'}), required=False)
    start_date = forms.DateTimeField(label=u"Начало",required=True, widget =  widgets.AdminSplitDateTime )
    end_date = forms.DateTimeField(label=u"Конец",required=False, widget =  widgets.AdminSplitDateTime)
    promise = forms.BooleanField(required=False, label=u"Только обещанный платёж")
    promise_expired = forms.BooleanField(required=False, label=u"Только обещанный платёж погашен")
    
class ActionLogFilterForm(forms.Form):
    systemuser = forms.ModelChoiceField(queryset=SystemUser.objects.all(), required=False)
    start_date = forms.DateTimeField(required=True)
    end_date = forms.DateTimeField(required=True)
    

    

                        
class AccountTariffBathForm(forms.Form):
    accounts = forms.CharField(required=True)
    tariff = forms.IntegerField(required=True)
    date = forms.DateTimeField(required=True)
    
class AccountAddonServiceModelForm(ModelForm):
    class Meta:
        model = AccountAddonService
      
class DocumentModelForm(ModelForm):
    class Meta:
        model = Document
   
class SuspendedPeriodModelForm(ModelForm):
    class Meta:
        model = SuspendedPeriod
        exclude = ('activated_by_account',)

class TransactionModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            FormActions(
                Submit('filter', 'Фильтровать', css_class="btn-primary"),
                Reset('reset', 'Очистить'),
            ),
            Field('account', css_class='input-xlarge'),
            Field('type', css_class='input-xlarge'),
            Field('description', css_class='input-xlarge'),
            Field('summ', css_class='input-xlarge'),
            Field('bill', css_class='input-xlarge'),
            Field('tarif', css_class='input-xlarge'),
            'created',
            'systemuser',


        )
        super(TransactionModelForm, self).__init__(*args, **kwargs)
    created = forms.DateTimeField(required=True, widget =  widgets.AdminSplitDateTime)
    class Meta:
        model = Transaction
        exclude = ('systemuser',)
        
class AccountTariffForm(ModelForm):
    class Meta:
        model = AccountTarif
    
class SettlementPeriodForm(ModelForm):
    class Meta:
        model = SettlementPeriod
  
class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        
class BankDataForm(ModelForm):
    class Meta:
        model = BankData
              
class AccountForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal container-fluid'
        self.helper.layout = Layout(
            FormActions(
                Submit('filter', 'Сохранить', css_class="btn-primary"),
                Submit('filter', 'Удалить', css_class="btn btn-danger"),
            ),
            Field('username', css_class='input-xlarge'),
            Field('pasword', css_class='input-xlarge'),
            Field('fullname', css_class='input-xlarge'),
            Field('ballance', css_class='input-xlarge'),
            Field('credit', css_class='input-xlarge'),
            Field('tarif', css_class='input-xlarge'),
            'created',
            'systemuser',


        )
        super(AccountForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Account
        exclude = ('ballance',)

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
    class Meta:
        model = AddonService  

class AddonServiceTarifForm(ModelForm):
    class Meta:
        model = AddonServiceTarif  
        
class ContractTemplateForm(ModelForm):
    class Meta:
        model = ContractTemplate  

class RadiusAttrsForm(ModelForm):
    class Meta:
        model = RadiusAttrs  

class TemplateForm(ModelForm):
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
    class Meta:
        model = SystemUser
    is_superuser = forms.CheckboxInput()     
    
class TimePeriodForm(ModelForm):
    class Meta:
        model = TimePeriod   
     
class TimePeriodNodeForm(ModelForm):
    class Meta:
        model = TimePeriodNode
                       
class IPPoolForm(ModelForm):
    class Meta:
        model = IPPool
        
class ManufacturerForm(ModelForm):
    class Meta:
        model = Manufacturer

class AccountHardwareForm(ModelForm):
    class Meta:
        model = AccountHardware
     
class ModelHardwareForm(ModelForm):
    class Meta:
        model = Model
           
class HardwareTypeForm(ModelForm):
    class Meta:
        model = HardwareType
        
class HardwareForm(ModelForm):
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
        
#TO-DO: добавить exclude в periodicalservice
class SubAccountForm(ModelForm):
    class Meta:
        model = SubAccount
        #exclude = ('ipn_ipinuse','vpn_ipinuse',)
        