# -*- coding: utf-8 -*-

import string
import random
import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import (
    CardBatchChangeForm,
    CardForm,
    CardGenerationForm,
    CardSearchForm,
    SaleCardForm
)
from billservice.helpers import systemuser_required
from billservice.models import Card, Dealer, SaleCard, DealerPay
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import CardTable, SaleCardTable, SaleCardsTable
from ebsadmin.randgen import GenPasswd2


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/card/list.html')
def card(request):
    if not (request.user.account.has_perm('billservice.view_card')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = Card.objects.all()
    if request.GET:
        form = CardSearchForm(request.GET)
        date_start, date_end = None, None
        ac_date_start, ac_date_end = None, None
        s_date_start, s_date_end = None, None
        if form.is_valid():
            created = form.cleaned_data.get("created")
            id = form.cleaned_data.get("id")
            card_type = form.cleaned_data.get("card_type")
            series = form.cleaned_data.get("series")
            login = form.cleaned_data.get("login")
            pin = form.cleaned_data.get("pin")
            nominal = form.cleaned_data.get("nominal")
            tariff = form.cleaned_data.get("tariff")
            template = form.cleaned_data.get("template")
            nas = form.cleaned_data.get("nas")
            ippool = form.cleaned_data.get("ippool")
            sold = form.cleaned_data.get("sold")
            not_sold = form.cleaned_data.get("not_sold")
            activated = form.cleaned_data.get("activated")
            activated_by = form.cleaned_data.get("activated_by")
            dealer = form.cleaned_data.get("dealer")

            if type(created) == tuple:
                date_start, date_end = created

            if date_start:
                res = res.filter(created__gte=date_start,
                                 created__lte=date_end)

            elif created:
                res = res.filter(created=created)

            if id:
                res = res.filter(id=id)

            if card_type:
                res = res.filter(type=card_type)

            if series:
                res = res.filter(series=series)

            if tariff:
                res = res.filter(tarif=tariff)

            if login:
                res = res.filter(login=login)

            if pin:
                res = res.filter(pin=pin)

            if template:
                res = res.filter(template=template)

            if nas:
                res = res.filter(nas=nas)

            if ippool:
                res = res.filter(ippool=ippool)

            if type(activated) == tuple:
                ac_date_start, ac_date_end = activated

            if ac_date_start:
                res = res.filter(activated__gte=ac_date_start,
                                 activated__lte=ac_date_end)
            elif activated:
                res = res.filter(activated=activated)

            if activated_by:
                res = res.filter(activated_by__in=activated_by)

            if dealer:
                res = res.filter(salecard__dealer=dealer)

            if not_sold == True:
                res = res.filter(salecard__isnull=True)
            elif sold:
                if type(sold) == tuple:
                    s_date_start, s_date_end = sold

                if s_date_start:
                    res = res.filter(
                        salecard__created__gte=s_date_start,
                        salecard__created__lte=s_date_end)
                elif sold:
                    res = res.filter(salecard__created=sold)

            if type(nominal) == tuple:
                cond, value = nominal
                if cond == ">":
                    res = res.filter(nominal__gte=value)
                elif cond == "<":
                    res = res.filter(nominal__lte=value)
            elif nominal:
                res = res.filter(nominal=nominal)

        table = CardTable(res)
        table_to_report = RequestConfig(
            request,
            paginate=False if request.GET.get('paginate') == 'False' else True)
        table_to_report = table_to_report.configure(table)
        if table_to_report:
            return create_report_http_response(table_to_report, request)

    else:
        form = CardSearchForm()
        table = CardTable(res)
        table_to_report = RequestConfig(
            request,
            paginate=False if request.GET.get('paginate') == 'False' else True)
        table_to_report = table_to_report.configure(table)
        if table_to_report:
            return create_report_http_response(table_to_report, request)

    return {
        "table": table,
        'form': form
    }


@systemuser_required
@render_to('ebsadmin/card/edit.html')
def card_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        if id:
            model = Card.objects.get(id=id)
            form = CardForm(request.POST, instance=model)
            if not (request.user.account.has_perm('billservice.change_card')):
                messages.error(request,
                               _(u'У вас нет прав на редактирование карт'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = CardForm(request.POST)
            if not (request.user.account.has_perm('billservice.add_card')):
                messages.error(request,
                               _(u'У вас нет прав на создание карт'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return HttpResponseRedirect(reverse("card"))
        else:
            messages.error(request,
                           form.errors['__all__'],
                           extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_card')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return {
                'status': False
            }
        if id:
            item = Card.objects.get(id=id)

            form = CardForm(instance=item)
        else:
            form = CardForm()

    return {
        'form': form,
        'status': False
    }


@systemuser_required
@render_to('ebsadmin/salecard/edit.html')
def salecard_edit(request):
    id = request.POST.get("id")
    item = None
    ids = request.GET.getlist('d')

    if request.method == 'POST':
        if id:
            model = SaleCard.objects.get(id=id)
            form = SaleCardForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_salecard')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование накладных на карты'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = SaleCardForm(request.POST)
            if not (request.user.account.has_perm(
                    'billservice.add_salecard')):
                messages.error(
                    request,
                    _(u'У вас нет прав на создание накладных на карты'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        now = datetime.datetime.now()
        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            cards = form.cleaned_data.get("cards")
            if not id:
                for c in cards:
                    c.salecard = model
                    c.sold = now
                    c.save()
                if form.cleaned_data.get('prepayment_sum') > 0:
                    m = DealerPay()
                    m.salecard = model
                    m.dealer = model.dealer
                    m.pay = form.cleaned_data.get('prepayment_sum')
                    m.created = model.created
                    m.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return HttpResponseRedirect(reverse("card"))
        else:
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_salecard')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return {
                'status': False
            }
        if id:
            item = SaleCard.objects.get(id=id)
            dealer = item.dealer
            form = SaleCardForm(instance=item)
            res = Card.objects.filter(salecard=item)
            cards_sum = (res
                         .aggregate(total_sum=Sum('nominal'))
                         .get("total_sum"))
        else:
            d = request.GET.getlist('d')
            dealer_id = request.GET.get('dealer')
            dealer = None
            if dealer_id:
                dealer = Dealer.objects.get(id=dealer_id)
            form = SaleCardForm(
                initial={
                    'cards': d,
                    'dealer': dealer,
                    'paydeffer': dealer.paydeffer,
                    'prepayment': dealer.prepayment
                }
            )
            res = Card.objects.filter(id__in=ids)
            cards_sum = (Card.objects
                         .filter(id__in=ids)
                         .aggregate(total_sum=Sum('nominal'))
                         .get("total_sum"))

        table = SaleCardsTable(res)

        table_to_report = RequestConfig(request, paginate=False).configure(
            table)
        if table_to_report:
            return create_report_http_response(table_to_report, request)

    return {
        'form': form,
        'table': table,
        'status': False,
        'dealer': dealer,
        'cards_sum': cards_sum
    }


@systemuser_required
@render_to('ebsadmin/card/generate.html')
def card_generate(request):
    id = request.GET.get("id")
    item = None
    model = None
    if request.method == 'POST':
        form = CardGenerationForm(request.POST)
        if not (request.user.account.has_perm('billservice.add_card')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return {
                'status': False,
                'form': form
            }

        if form.is_valid():
            card_type = int(form.cleaned_data.get("card_type"))
            pin_mask = ''
            if form.cleaned_data.get("pin_letters") == True:
                pin_mask += string.letters
            if form.cleaned_data.get("pin_numbers") == True:
                pin_mask += string.digits
            login_mask = ''
            if form.cleaned_data.get("login_letters") == True:
                login_mask += string.letters
            if form.cleaned_data.get("login_numbers") == True:
                login_mask += string.digits

            dnow = datetime.datetime.now()
            if card_type in [1, 2, 3]:
                tarif = form.cleaned_data.get("tariff")

            template = form.cleaned_data.get("template")

            if card_type in [2, ]:
                nas = form.cleaned_data.get("nas")

            pool = None
            if card_type in [1, 2]:
                pool = form.cleaned_data.get("pool")

            cards_count = form.cleaned_data.get("count")
            series = form.cleaned_data.get("series")
            nominal = form.cleaned_data.get("nominal")
            template = form.cleaned_data.get("template")

            date_start = form.cleaned_data.get("date_start")
            date_end = form.cleaned_data.get("date_end")

            pin_length_from = form.cleaned_data.get("pin_length_from")
            pin_length_to = form.cleaned_data.get("pin_length_to")

            login_length_from = form.cleaned_data.get("login_length_from")
            login_length_to = form.cleaned_data.get("login_length_to")

            i = 0
            bad = 0
            # типы карт
            # 0 - экспресс оплата
            # 1 - хотспот
            # 2- vpn доступ
            while i < cards_count:
                if bad >= 100:
                    return {
                        'form': form,
                        'status': False,
                        'message': _(u"Было сгенерировано только %s карт.\n"
                                     u"Расширьте условия генерации для "
                                     u"уменьшения количества дублирующихся "
                                     u"логинов.") % i
                    }
                model = Card()
                model.series = series
                model.pin = GenPasswd2(
                    length=random.randint(pin_length_from, pin_length_to),
                    chars=pin_mask)
                model.type = 0
                if card_type == 2:
                    model.login = GenPasswd2(
                        length=random.randint(
                            login_length_from, login_length_to),
                        chars=login_mask)
                    model.tarif = tarif
                    model.ippool = pool
                    model.nas = nas
                    model.type = 2
                if card_type == 1:
                    model.login = GenPasswd2(
                        length=random.randint(
                            login_length_from, login_length_to),
                        chars=login_mask)
                    model.tarif = tarif
                    model.type = 1
                    model.ippool = pool or None
                if card_type == 2:
                    model.login = GenPasswd2(
                        length=random.randint(
                            login_length_from, login_length_to),
                        chars=login_mask)
                    model.tarif = tarif
                    model.type = 3

                model.nominal = nominal
                model.start_date = date_start
                model.end_date = date_end
                model.template = template

                model.created = dnow
                try:
                    print model.pin
                    print model.login
                    model.save()
                    i += 1
                except Exception, e:
                    print repr(e)
                    bad += 1

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(request,
                           form.errors['__all__'],
                           extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        now = datetime.datetime.now()
        card_type = request.GET.get("card_type")
        form = CardGenerationForm(initial={
            'card_type': card_type,
            'count': 100,
            'nominal': 0,
            "date_start": now,
            'date_end': now + datetime.timedelta(days=365),
            'login_length_from': 6,
            'login_length_to': 6,
            'pin_length_from': 6,
            'pin_length_to': 6,
            'login_letters': True,
            'login_numbers': True,
            'pin_letters': True,
            'pin_numbers': True
        })

    return {
        'form': form,
        'status': False
    }


@systemuser_required
@render_to('ebsadmin/card_update.html')
def card_update(request):
    item = None
    model = None
    ids = request.GET.getlist('d')
    if request.method == 'POST':
        form = CardBatchChangeForm(request.POST)
        if not (request.user.account.has_perm('billservice.change_card')):
            messages.error(request,
                           _(u'У вас нет прав на изменение карт.'),
                           extra_tags='alert-danger')
            return {
                'status': False,
                'form': form
            }

        if form.is_valid():
            card_type = int(form.cleaned_data.get("card_type"))
            pin_mask = ''
            if form.cleaned_data.get("pin_letters") == True:
                pin_mask += string.letters
            if form.cleaned_data.get("pin_numbers") == True:
                pin_mask += string.digits
            login_mask = ''
            if form.cleaned_data.get("login_letters") == True:
                login_mask += string.letters
            if form.cleaned_data.get("login_numbers") == True:
                login_mask += string.digits

            tarif = form.cleaned_data.get("tariff")

            template = form.cleaned_data.get("template")

            nas = form.cleaned_data.get("nas")

            pool = None
            pool = form.cleaned_data.get("pool")

            series = form.cleaned_data.get("series")
            change_pin = form.cleaned_data.get("change_pin")
            change_login = form.cleaned_data.get("change_login")
            nominal = form.cleaned_data.get("nominal")
            template = form.cleaned_data.get("template")

            date_start = form.cleaned_data.get("date_start")
            date_end = form.cleaned_data.get("date_end")

            pin_length_from = form.cleaned_data.get("pin_length_from")
            pin_length_to = form.cleaned_data.get("pin_length_to")

            login_length_from = form.cleaned_data.get("login_length_from")
            login_length_to = form.cleaned_data.get("login_length_to")

            i = 0
            bad = 0
            # типы карт
            # 0 - экспресс оплата
            # 1 - хотспот
            # 2- vpn доступ
            ids = form.cleaned_data.get("cards", '').split(",")
            for id in ids:
                model = Card.objects.get(id=id)
                if series:
                    model.series = series
                if change_pin:
                    model.pin = GenPasswd2(length=random.randint(
                        pin_length_from, pin_length_to), chars=pin_mask)
                if int(card_type) > -1:
                    model.type = card_type
                if change_login:
                    model.login = GenPasswd2(length=random.randint(
                        login_length_from, login_length_to), chars=login_mask)
                if tarif:
                    model.tarif = tarif

                if pool:
                    model.pool = pool
                if nas:
                    model.nas = nas
                if nominal:
                    model.nominal = nominal
                if template:
                    model.template = template

                if date_start:
                    model.start_date = date_start

                if date_end:
                    model.end_date = date_end

                try:
                    model.save()
                    i += 1
                except Exception, e:
                    print repr(e)

                log('EDIT', request.user, model)
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(request,
                           form.errors['__all__'],
                           extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:

        if not (request.user.account.has_perm('billservice.edit_card')):
            return {
                'status': False
            }

        card_type = request.GET.get("card_type")
        form = CardBatchChangeForm(initial={
            'cards': ','.join(ids),
            'card_type': card_type,
            'login_length_from': 6,
            'login_length_to': 6,
            'pin_length_from': 6,
            'pin_length_to': 6,
            'login_letters': True,
            'login_numbers': True,
            'pin_letters': True,
            'pin_numbers': True
        })

    return {
        'form': form,
        'status': False
    }


@ajax_request
@systemuser_required
def card_delete(request):
    if not (request.user.account.has_perm('billservice.delete_card')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление карточек')
        }
    id = request.GET.getlist('d')
    if id:
        try:
            items = Card.objects.filter(id__in=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная карта не найдена %s") % str(e)
            }
        for item in items:
            log('DELETE', request.user, item)
            item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "Card not found"
        }


@ajax_request
@systemuser_required
def card_manage(request):
    if not (request.user.account.has_perm('billservice.edit_card')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование карточек')
        }
    id = request.GET.getlist('d')
    action = request.GET.get('action')
    if id:
        try:
            items = Card.objects.filter(id__in=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная карта не найдена %s") % str(e)
            }
        for item in items:
            if action == 'enable':
                log('EDIT', request.user, item)
                item.disabled = False
                item.save()
            elif action == 'disable':
                log('EDIT', request.user, item)
                item.disabled = True
                item.save()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "Card not found"
        }


@systemuser_required
@render_to('ebsadmin/common/list.html')
def salecard(request):
    if not (request.user.account.has_perm('billservice.view_salecard')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = SaleCard.objects.all()
    table = SaleCardTable(res)
    table_to_report = RequestConfig(
        request,
        paginate=True if not request.GET.get('paginate') == 'False' else False)
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)

    return {
        "list_url": reverse('salecard'),
        "list_header": _(u'Накладные на карты'),
        "table": table
    }
