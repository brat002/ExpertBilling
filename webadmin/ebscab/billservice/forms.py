# -*- encoding: utf-8 -*-
from django import forms
from datetime import datetime, date
from django.forms import ModelForm
from billservice.models import Tariff, TPChangeRule, Account, SubAccount, AccountTarif, AccountAddonService, Document, SuspendedPeriod

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
    
class CardForm(forms.Form):
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
    contract = forms.CharField(required=False)
    username = forms.CharField(required=False)
    fullname = forms.CharField(required=False)
    contactperson = forms.CharField(required=False)
    city = forms.CharField(required=False)
    street = forms.CharField(required=False)
    house = forms.CharField(required=False)
    house_bulk = forms.CharField(required=False)
    room = forms.CharField(required=False)
    status = forms.IntegerField(required=False)
    ballance_exp = forms.CharField(required=False)
    ballance = forms.DecimalField(required=False)
    credit_exp = forms.CharField(required=False)
    credit = forms.DecimalField(required=False)
    tariff_filter = forms.MultipleChoiceField(required=False)
    group_filter = forms.MultipleChoiceField(required=False)
    ballance_blocked = forms.CheckboxInput()
    limit_blocked = forms.CheckboxInput()
    nas_filter = forms.MultipleChoiceField(required=False)
    ipn_added = forms.CheckboxInput()
    ipn_enabled = forms.CheckboxInput()
    ipn_sleep = forms.CheckboxInput()
    systemuser_filter = forms.MultipleChoiceField(required=False)
    created_from = forms.DateTimeField(required=False)
    created_to = forms.DateTimeField(required=False)

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
            
class AccountTariffForm(ModelForm):
    class Meta:
        model = AccountTarif
    
class AccountForm(ModelForm):
    class Meta:
        model = Account
        exclude = ('ballance',)

class SubAccountForm(ModelForm):
    class Meta:
        model = SubAccount
        exclude = ('ipn_ipinuse','vpn_ipinuse',)
        