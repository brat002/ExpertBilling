# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from ebsadmin.cardlib import add_addonservice, del_addonservice
from ebscab.utils.decorators import render_to
from ebscab.utils.paginator import SimplePaginator

from billservice.models import (
    AccountAddonService,
    AddonService,
    AddonServiceTarif,
    AddonServiceTransaction,
    PeriodicalServiceHistory
)
from billservice.utils import settlement_period_info
from billservice.views.utils import addon_queryset


@render_to('accounts/addonservice.html')
@login_required
def addon_service(request):
    user = request.user.account
    addontarif_services = (AddonServiceTarif.objects
                           .filter(tarif=user.get_account_tariff(), type=0)
                           .order_by("service__name"))

    account_services = AccountAddonService.objects.filter(
        account=user, subaccount__isnull=True, deactivated__isnull=True)
    accountservices = []
    for uservice in account_services:
        if uservice.service.wyte_period_id:
            try:
                delta = settlement_period_info(
                    uservice.activated,
                    uservice.service.wyte_period.length_in,
                    uservice.service.wyte_period.length)[2]
                if uservice.activated + datetime.timedelta(seconds=delta) > \
                        datetime.datetime.now():
                    uservice.wyte = True
                    uservice.end_wyte_date = \
                        uservice.activated + datetime.timedelta(seconds=delta)
                else:
                    uservice.wyte = False
            except:
                uservice.wyte = True
        elif uservice.service.wyte_cost:
            uservice.wyte = True
        else:
            uservice.wyte = False
        accountservices.append(uservice)

    user_services_id = [x.service.id for x in accountservices
                        if not x.deactivated]
    addon_srvcs = []
    for adds in addontarif_services:
        accs = (AccountAddonService.objects
                .filter(service=adds.service,
                        account=user,
                        subaccount__isnull=True,
                        deactivated__isnull=True))

        for uservice in accs:
            if uservice.service.wyte_period_id:
                delta = settlement_period_info(
                    uservice.activated,
                    uservice.service.wyte_period.length_in,
                    uservice.service.wyte_period.length)[2]
                if uservice.activated + datetime.timedelta(seconds=delta) > \
                        datetime.datetime.now():
                    uservice.wyte = True
                    uservice.end_wyte_date = \
                        uservice.activated + datetime.timedelta(seconds=delta)
                else:
                    uservice.wyte = False
            elif uservice.service.wyte_cost:
                uservice.wyte = True
            else:
                uservice.wyte = False
        addon_srvcs.append((adds, accs))

    return_dict = {
        'addontarif_services': addontarif_services,
        'addon_srvcs': addon_srvcs,
        'account_services_id': user_services_id,
        'account_services': account_services,
        'user': user,
        'active_class': 'services-img'
    }

    if request.session.has_key('service_message'):
        return_dict['service_message'] = request.session['service_message']
        del(request.session['service_message'])

    return return_dict


@login_required
def service_action(request, action, id):
    """
    TODO: fix typo
    в случее set id являеться идентификатором добавляемой услуги
    в случее del id являеться идентификатором accountaddon_service
    """
    user = request.user.account

    if action == u'set':
        try:
            account_addon_service = AddonService.objects.get(id=id)
        except:
            request.session['service_message'] = _(
                u'Вы не можете подключить данную услугу')
            return HttpResponseRedirect('/services/')

        result = add_addonservice(account_id=user.id, service_id=id)
        if result == True:
            request.session['service_message'] = _(u'Услуга подключена')
            return HttpResponseRedirect('/services/')
        elif result == 'ACCOUNT_DOES_NOT_EXIST':
            request.session['service_message'] = _(
                u'Указанный пользователь не найден')
            return HttpResponseRedirect('/services/')
        elif result == 'ADDON_SERVICE_DOES_NOT_EXIST':
            request.session['service_message'] = _(
                u'Указанныя подключаемая услуга не найдена')
            return HttpResponseRedirect('/services/')
        elif result == 'NOT_IN_PERIOD':
            request.session['service_message'] = _(
                u'Активация выбранной услуги в данный момент не доступна')
            return HttpResponseRedirect('/services/')
        elif result == 'ALERADY_HAVE_SPEED_SERVICE':
            request.session['service_message'] = _(
                u'У вас уже подключенны изменяющие скорость услуги')
            return HttpResponseRedirect('/services/')
        elif result == 'ACCOUNT_BLOCKED':
            request.session['service_message'] = _(
                u'Услуга не может быть подключена. Проверьте Ваш баланс '
                u'или обратитесь в службу поддержки')
            return HttpResponseRedirect('/services/')
        elif result == 'ADDONSERVICE_TARIF_DOES_NOT_ALLOWED':
            request.session['service_message'] = _(
                u'На вашем тарифном плане активация выбранной услуги '
                u'невозможна')
            return HttpResponseRedirect('/services/')
        elif result == 'TOO_MUCH_ACTIVATIONS':
            request.session['service_message'] = _(
                u'Превышенно допустимое количество активаций. Обратитесь '
                u'в службу поддержки')
            return HttpResponseRedirect('/services/')
        elif result == 'SERVICE_ARE_ALREADY_ACTIVATED':
            request.session['service_message'] = _(
                u'Указанная услуга уже подключена и не может быть '
                u'активирована дважды.')
            return HttpResponseRedirect('/services/')
        else:
            request.session['service_message'] = _(
                u'Услугу не возможно подключить')
            return HttpResponseRedirect('/services/')
    elif action == u'del':
        result = del_addonservice(user.id, id)
        if result == True:
            request.session['service_message'] = _(u'Услуга отключена')
            return HttpResponseRedirect('/services/')
        elif result == 'ACCOUNT_DOES_NOT_EXIST':
            request.session['service_message'] = _(
                u'Указанный пользователь не найден')
            return HttpResponseRedirect('/services/')
        elif result == 'ADDON_SERVICE_DOES_NOT_EXIST':
            request.session['service_message'] = _(
                u'Указанныя подключаемая услуга не найдена')
            return HttpResponseRedirect('/services/')
        elif result == 'ACCOUNT_ADDON_SERVICE_DOES_NOT_EXIST':
            request.session['service_message'] = _(
                u'Вы не можите отключить выбранную услугу')
            return HttpResponseRedirect('/services/')
        elif result == 'NO_CANCEL_SUBSCRIPTION':
            request.session['service_message'] = _(
                u'Даннная услуга не может быть отключена. Обратитесь в '
                u'службу поддержки')
            return HttpResponseRedirect('/services/')
        else:
            request.session['service_message'] = _(
                u'Услугу не возможно отключить')
            return HttpResponseRedirect('/services/')
    else:
        request.session['service_message'] = _(
            u'Невозможно совершить действие')
        return HttpResponseRedirect('/services/')


@render_to('accounts/periodical_service_history.html')
@login_required
def periodical_service_history(request):
    is_range, addon_query = addon_queryset(request,
                                           'periodical_service_history',
                                           'created')
    qs = (PeriodicalServiceHistory.objects
          .filter(account=request.user.account, **addon_query)
          .order_by('-created'))
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    periodical_service_history = paginator.get_page_items()
    if is_range:
        for periodical_service in qs:
            summ += periodical_service.summ
        for periodical_service in periodical_service_history:
            summ_on_page += periodical_service.summ
    rec_count = len(periodical_service_history) + 1
    return {
        'periodical_service_history': periodical_service_history,
        'paginator': paginator,
        'is_range': is_range,
        'summ': summ,
        'summ_on_page': summ_on_page,
        'rec_count': rec_count,
        'active_class': 'statistic-img'
    }


@render_to('accounts/addon_service_transaction.html')
@login_required
def addon_service_transaction(request):
    is_range, addon_query = addon_queryset(request,
                                           'addon_service_transaction',
                                           'created')
    qs = (AddonServiceTransaction.objects
          .filter(account=request.user.account, **addon_query)
          .order_by('-created'))
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    addon_service_transaction = paginator.get_page_items()
    if is_range:
        for addon_service in qs:
            summ += addon_service.summ
        for addon_service in addon_service_transaction:
            summ_on_page += addon_service.summ
    addon_service_transaction = paginator.get_page_items()
    rec_count = len(addon_service_transaction) + 1
    return {
        'addon_service_transaction': addon_service_transaction,
        'paginator': paginator,
        'is_range': is_range,
        'summ': summ,
        'summ_on_page': summ_on_page,
        'rec_count': rec_count,
        'active_class': 'statistic-img'
    }


@render_to('accounts/services_info.html')
@login_required
def services_info(request):
    user = request.user.account
    is_range, addon_query = addon_queryset(request, 'services', 'activated')
    qs = (AccountAddonService.objects
          .filter(account=user, **addon_query)
          .order_by('-activated'))
    paginator = SimplePaginator(request, qs, 50, 'page')
    summ = 0
    summ_on_page = 0
    services = paginator.get_page_items()
    if is_range:
        for service in qs:
            service_summ = 0
            for transaction in (AddonServiceTransaction.objects
                                .filter(accountaddonservice=service)):
                service_summ += transaction.summ
            summ += service_summ
        for service in services:
            service_summ = 0
            for transaction in (AddonServiceTransaction.objects
                                .filter(accountaddonservice=service)):
                service_summ += transaction.summ
            summ_on_page += service_summ
    services = paginator.get_page_items()
    rec_count = len(services) + 1
    return {
        'services': services,
        'paginator': paginator,
        'user': user,
        'is_range': is_range,
        'summ': summ,
        'summ_on_page': summ_on_page,
        'rec_count': rec_count,
        'active_class': 'statistic-img'
    }
