# -*- coding: utf-8 -*-
import autocomplete_light

from models import Account, SystemUser
from django.contrib.auth.models import User

class AccountAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['^username', 'contract', 'fullname']
    choice_template='template_autocomplete/templated_choice.html'

class UserAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['username']
    choice_template='autocomplete_light/model_template/nourl_choice.html'
    
class SystemUserAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['username']
    choice_template='template_autocomplete/templated_choice.html'
    
autocomplete_light.register(Account, AccountAutocomplete,     autocomplete_js_attributes={
        'minimum_characters': 0,
        'placeholder': u'Логин, договор или ФИО аккаунта',
    })

autocomplete_light.register(User, UserAutocomplete,     autocomplete_js_attributes={
        'minimum_characters': 0,
        'placeholder': u'Введите логин',
    })

autocomplete_light.register(SystemUser, SystemUserAutocomplete,     autocomplete_js_attributes={
        'minimum_characters': 0,
        'placeholder': u'Введите логин',
    })

