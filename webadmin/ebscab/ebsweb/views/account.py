# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic.base import RedirectView

from billservice.models import (
    AccountAddonService,
    AccountPrepaysRadiusTrafic,
    AccountPrepaysTime,
    AccountPrepaysTrafic,
    AccountSuppAgreement,
    AccountTarif,
    AddonServiceTarif,
    GroupStat,
    SubAccount,
    TrafficLimit
)
from billservice.utils import settlement_period_info

from ebsweb.forms.account import (
    AccountPasswordChangeForm,
    AddonServiceAddForm,
    AddonServiceDelForm,
    EmailChangeForm,
    SubAccountPasswordChangeForm,
    TariffChangeForm
)
from ebsweb.views.base import (
    ProtectedTemplateView,
    ProtectedDetailView,
    ProtectedFormView,
    ProtectedListView,
    ProtectedUpdateView,
    UserFormKwargsMixin,
    UserTariffMixin
)


class AccountView(RedirectView):

    def get_redirect_url(self):
        return reverse('ebsweb:account_info')


class AccountInfoView(UserTariffMixin, ProtectedDetailView):
    template_name = 'ebsweb/account/info.html'
    show_tariff_message = False

    B_IN_1MB = 1024 * 1024

    def get_object(self):
        return self.request.user.account

    def _get_traffic_limits(self):
        account = self.object
        tariff = self.tariff
        traffic_limits = []
        if tariff:
            traffic_limits_objects = TrafficLimit.objects.filter(tarif=tariff)
            for t_limit in traffic_limits_objects:
                settlement_period = (t_limit.settlement_period or
                                     t_limit.tarif.settlement_period)
                if settlement_period and settlement_period.autostart is True:
                    account_tariff = (AccountTarif.objects
                                      .filter(account=account,
                                              datetime__lt=datetime.now())
                                      .first())
                    sp_start = account_tariff.datetime
                else:
                    settlement_period = tariff.settlement_period
                    sp_start = (settlement_period.time_start
                                if settlement_period else None)

                settlement_period_start, settlement_period_end, delta = \
                    settlement_period_info(
                        time_start=sp_start,
                        repeat_after=settlement_period.length_in,
                        repeat_after_seconds=settlement_period.length)

                if t_limit.mode is True:
                    now = datetime.now()
                    settlement_period_start = now - timedelta(seconds=delta)
                    settlement_period_end = now

                try:
                    group_stat = GroupStat.objects.get(
                        group=t_limit.group,
                        account=account,
                        datetime__gt=settlement_period_start,
                        datetime__lt=settlement_period_end)
                except GroupStat.DoesNotExist:
                    traffic_used = 0
                else:
                    traffic_used = float(group_stat.bytes) / self.B_IN_1MB

                t_limit_dict = {
                    'name': t_limit.name,
                    'settlement_period_start': settlement_period_start,
                    'settlement_period_end': settlement_period_end,
                    'traffic_used': traffic_used,
                    'traffic_limit': float(t_limit.size) / self.B_IN_1MB
                }
                traffic_limits.append(t_limit_dict)
            return traffic_limits

    def _get_prepaid_items(self):
        account_tariff = (AccountTarif.objects
                          .filter(account=self.object,
                                  datetime__lte=datetime.now())
                          .order_by('-datetime')
                          .first())
        prepaid_traffic = (AccountPrepaysTrafic.objects
                           .filter(account_tarif=account_tariff,
                                   current=True))

        try:
            prepaid_time = (AccountPrepaysTime.objects
                            .get(account_tarif=account_tariff,
                                 current=True))
        except AccountPrepaysTime.DoesNotExist:
            prepaid_time = None

        try:
            prepaid_radius_traffic = (AccountPrepaysRadiusTrafic.objects
                                      .get(account_tarif=account_tariff,
                                           current=True))
        except AccountPrepaysRadiusTrafic.DoesNotExist:
            prepaid_radius_traffic = None

        return {
            'traffic': prepaid_traffic,
            'time': prepaid_time,
            'radius_traffic': prepaid_radius_traffic
        }

    def get_context_data(self, **kwargs):
        account = self.object
        tariff = self.tariff
        context = super(AccountInfoView, self).get_context_data(**kwargs)
        context['balance'] = account.ballance - account.credit
        context['credit'] = account.credit
        context['tariff'] = tariff.name if tariff else None
        context['connected'] = account.created
        context['fullname'] = account.fullname
        context['address'] = account.address_full
        context['email'] = account.email
        context['traffic_limits'] = self._get_traffic_limits()
        context['prepaid_items'] = self._get_prepaid_items()
        return context


class AccountSubAccountsView(ProtectedListView):
    context_object_name = 'subaccounts'
    paginate_by = 10
    template_name = 'ebsweb/account/subaccount_list.html'

    def get_queryset(self):
        return SubAccount.objects.filter(account=self.request.user.account)


class AccountSubAccountPasswordView(ProtectedUpdateView):
    form_class = SubAccountPasswordChangeForm
    model = SubAccount
    context_object_name = 'subaccount'
    template_name = 'ebsweb/account/subaccount_password_update.html'

    def get_success_url(self):
        return reverse('ebsweb:account_subaccount_password',
                       kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _(u'Пароль успешно изменен.'))
        return super(AccountSubAccountPasswordView, self).form_valid(form)


class AccountTariffView(UserFormKwargsMixin, ProtectedFormView):
    form_class = TariffChangeForm
    template_name = 'ebsweb/account/tariff_update.html'

    def get_success_url(self):
        return reverse('ebsweb:account_tariff')

    def form_valid(self, form):
        request = self.request
        now = datetime.now()
        supp_agreements = (AccountSuppAgreement.objects
                           .filter(Q(closed__isnull=True) | Q(closed__gte=now),
                                   account=request.user.account,
                                   created__lte=now,
                                   suppagreement__disable_tarff_change=True))
        if supp_agreements:
            supp_agreements_nums = ', '.join(['#{}'.format(i.contract)
                                              for i in supp_agreements])
            if len(supp_agreements) == 1:
                message_tmpl = _(
                    u'Вы не можете сменить тарифный план в связи с '
                    u'действующим доп. соглашением {numbers}')
            else:
                message_tmpl = _(
                    u'Вы не можете сменить тарифный план в связи с '
                    u'действующими доп. соглашениями {numbers}')
            messages.error(
                request, message_tmpl.format(numbers=supp_agreements_nums))
            return super(AccountTariffView, self).form_invalid(form)
        else:
            message = form.save()
            messages.success(self.request, message)
            return super(AccountTariffView, self).form_valid(form)


class AccountServicesView(UserTariffMixin, ProtectedListView):
    paginate_by = 10
    context_object_name = 'services'
    template_name = 'ebsweb/account/services.html'

    def get_queryset(self):
        return self.tariff.get_addon_services().order_by('service__name')

    def get_context_data(self, **kwargs):
        context = super(AccountServicesView, self).get_context_data(**kwargs)
        tariff_addon_services = context[self.context_object_name]
        services = []
        for t_addon_service in tariff_addon_services:
            account_addon_services = (
                self.request.user.account.get_addon_services()
                .filter(service=t_addon_service.service)
            )
            tas = t_addon_service.service  # alias
            is_used = bool(account_addon_services)
            t_addon_service_detail = {
                'name': tas.name,
                'description': tas.comment,
                'settlement_period': tas.render_sp_period(),
                'cost': tas.cost,
                'available_period': tas.timeperiod,
                'cost_preterm_deactivate': tas.wyte_cost,
                'using_period_min': tas.render_wyte_period(),
                'is_used': is_used
            }
            if not is_used:
                t_addon_service_detail['form'] = AddonServiceAddForm(initial={
                    'tariff_addon_service_id': t_addon_service.id
                })
            for a_addon_service in account_addon_services:
                # NOTE: add a_addon_service.end_wyte_date for show to user in
                # AccountServiceDelView (now not implemented)
                # if a_addon_service.service.wyte_period:
                #     settlement_datetime = settlement_period_info(
                #         a_addon_service.activated,
                #         a_addon_service.service.wyte_period.length_in,
                #         a_addon_service.service.wyte_period.length)
                #     delta = settlement_datetime[2]
                #     if (a_addon_service.activated +
                #             timedelta(seconds=delta)) > datetime.now():
                #         a_addon_service.end_wyte_date = (
                #             a_addon_service.activated +
                #             timedelta(seconds=delta))
                if not a_addon_service.deactivated:
                    t_addon_service_detail['form'] = AddonServiceDelForm(
                        initial={
                            'account_addon_service_id': a_addon_service.id
                        })
            services.append(t_addon_service_detail)
        context['services'] = sorted(
            services, key=lambda i: not i['is_used'])
        return context


class AccountServiceAddView(UserFormKwargsMixin, ProtectedFormView):
    form_class = AddonServiceAddForm

    def get_success_url(self):
        return reverse('ebsweb:account_services')

    def form_valid(self, form):
        request = self.request
        result = form.save()
        error_message = None
        if result == True:
            messages.success(request, _(u'Услуга услуга успешно подключена'))
        elif result == 'ACCOUNT_DOES_NOT_EXIST':
            error_message = _(
                u'Указанный пользователь не найден')
        elif result == 'ADDON_SERVICE_DOES_NOT_EXIST':
            error_message = _(
                u'Указанная подключаемая услуга не найдена')
        elif result == 'NOT_IN_PERIOD':
            error_message = _(
                u'Активация выбранной услуги в данный момент не доступна')
        elif result == 'ALERADY_HAVE_SPEED_SERVICE':
            error_message = _(
                u'У вас уже подключенны изменяющие скорость услуги')
        elif result == 'ACCOUNT_BLOCKED':
            error_message = _(
                u'Услуга не может быть подключена. Проверьте Ваш баланс '
                u'или обратитесь в службу поддержки')
        elif result == 'ADDONSERVICE_TARIF_DOES_NOT_ALLOWED':
            error_message = _(
                u'На вашем тарифном плане активация выбранной услуги '
                u'невозможна')
        elif result == 'TOO_MUCH_ACTIVATIONS':
            error_message = _(
                u'Превышенно допустимое количество активаций. Обратитесь '
                u'в службу поддержки')
        elif result == 'SERVICE_ARE_ALREADY_ACTIVATED':
            error_message = _(
                u'Указанная услуга уже подключена и не может быть '
                u'активирована дважды.')
        else:
            error_message = _(u'Услугу не возможно подключить')
        if error_message:
            messages.error(request, error_message)
        return super(AccountServiceAddView, self).form_valid(form)

    def get(self, *args, **kwargs):
        return HttpResponseRedirect(reverse('ebsweb:account_services'))


class AccountServiceDelView(UserFormKwargsMixin, ProtectedFormView):
    form_class = AddonServiceDelForm

    def get_success_url(self):
        return reverse('ebsweb:account_services')

    def form_valid(self, form):
        request = self.request
        result = form.save()
        error_message = None
        if result == True:
            messages.success(request, _(u'Услуга успешно отключена'))
        elif result == 'ACCOUNT_DOES_NOT_EXIST':
            error_message = _(u'Указанный пользователь не найден')
        elif result == 'ADDON_SERVICE_DOES_NOT_EXIST':
            error_message = _(u'Указанная подключаемая услуга не найдена')
        elif result == 'ACCOUNT_ADDON_SERVICE_DOES_NOT_EXIST':
            error_message = _(u'Вы не можете отключить выбранную услугу')
        elif result == 'NO_CANCEL_SUBSCRIPTION':
            error_message = _(
                u'Даннная услуга не может быть отключена. Обратитесь в '
                u'службу поддержки')
        else:
            error_message = _(u'Услугу не возможно отключить')
        if error_message:
            messages.error(request, error_message)
        return super(AccountServiceDelView, self).form_valid(form)

    def get(self, *args, **kwargs):
        return HttpResponseRedirect(reverse('ebsweb:account_services'))


class AccountEmailView(ProtectedUpdateView):
    form_class = EmailChangeForm
    template_name = 'ebsweb/account/email_update.html'

    def get_success_url(self):
        return reverse('ebsweb:account_email')

    def get_object(self):
        return self.request.user.account

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _(u'Email успешно изменен'))
        return super(AccountEmailView, self).form_valid(form)


class AccountPasswordView(ProtectedUpdateView):
    form_class = AccountPasswordChangeForm
    template_name = 'ebsweb/account/password_update.html'

    def get_success_url(self):
        return reverse('ebsweb:account_password')

    def get_object(self):
        return self.request.user.account

    def form_valid(self, form):
        request = self.request
        form.save()
        update_session_auth_hash(request, self.object)
        messages.success(request, _(u'Пароль успешно изменен'))
        return super(AccountPasswordView, self).form_valid(form)
