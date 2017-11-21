# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView

from billservice.models import SystemUser


class ProtectedViewMixin(object):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if isinstance(request.user.account, SystemUser):
            return HttpResponseRedirect(reverse('admin_dashboard'))
        return super(ProtectedViewMixin, self).dispatch(
            request, *args, **kwargs)


class UserFormKwargsMixin(object):

    def get_user(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super(UserFormKwargsMixin, self).get_form_kwargs()
        kwargs['user'] = self.get_user()
        return kwargs


class UserTariffMixin(object):
    show_tariff_message = True

    def dispatch(self, *args, **kwargs):
        tariff = self.request.user.account.get_account_tariff()
        if not tariff and self.show_tariff_message:
            messages.error(self.request, _(u'Вам не назначен тарифный план'))
        self.tariff = tariff
        return super(UserTariffMixin, self).dispatch(*args, **kwargs)


class ProtectedDetailView(ProtectedViewMixin, DetailView):
    pass


class ProtectedFormView(ProtectedViewMixin, FormView):
    pass


class ProtectedListView(ProtectedViewMixin, ListView):
    pass


class ProtectedTemplateView(ProtectedViewMixin, TemplateView):
    pass


class ProtectedUpdateView(ProtectedViewMixin, UpdateView):
    pass


class ProtectedView(ProtectedViewMixin, View):
    pass
