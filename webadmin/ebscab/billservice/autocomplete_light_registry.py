# -*- coding: utf-8 -*-

from autocomplete_light import shortcuts as autocomplete_light
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from models import Account, SystemUser


class AccountAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['^username', 'contract', 'fullname']
    choice_template = 'template_autocomplete/templated_choice.html'

    def choices_for_request(self):
        choices = super(AccountAutocomplete, self).choices_for_request()

        if not self.request.user.is_staff:
            return []

        return choices


class UserAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['username']
    choice_template = 'autocomplete_light/model_template/nourl_choice.html'

    def choices_for_request(self):
        choices = super(UserAutocomplete, self).choices_for_request()

        if not self.request.user.is_staff:
            return []

        return choices


class SystemUserAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['username']
    choice_template = 'template_autocomplete/templated_choice.html'

    def choices_for_request(self):
        choices = super(SystemUserAutocomplete, self).choices_for_request()

        if not self.request.user.is_staff:
            return []

        return choices


autocomplete_light.register(
    Account,
    AccountAutocomplete,
    autocomplete_js_attributes={
        'minimum_characters': 0,
        'placeholder': _(u'Логин, договор или ФИО аккаунта')
    }
)

autocomplete_light.register(
    User,
    UserAutocomplete,
    autocomplete_js_attributes={
        'minimum_characters': 0,
        'placeholder': _(u'Введите логин')
    }
)

autocomplete_light.register(
    SystemUser,
    SystemUserAutocomplete,
    autocomplete_js_attributes={
        'minimum_characters': 0,
        'placeholder': _(u'Введите логин')
    }
)
