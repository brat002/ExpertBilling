# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from ebsadmin.cardlib import activate_pay_card
from ebscab.lib.decorators import render_to, ajax_request

from billservice.forms import ActivationCardForm


@render_to('accounts/card_form.html')
@login_required
def card_form(request):
    return {
        'form': ActivationCardForm()
    }


@ajax_request
@login_required
def card_acvation(request):
    user = request.user.account
    if not user.allow_expresscards:
        return {
            'error_message': _(u'Вам не доступна услуга активации карт '
                               u'экспресс оплаты.')
        }

    status = False
    if request.method == 'POST':
        form = ActivationCardForm(request.POST)
        error_message = ''
        if form.is_valid():
            res = activate_pay_card(user.id,
                                    form.cleaned_data.get('card_id'),
                                    form.cleaned_data['pin'])
            if res == 'CARD_NOT_FOUND':
                error_message = _(u'Ошибка активации. Карта не найдена.')
            elif res == 'CARD_NOT_SOLD':
                error_message = _(u'Ошибка активации. Карта не была продана.')
            elif res == 'CARD_ALREADY_ACTIVATED':
                error_message = _(
                    u'Ошибка активации. Карта была активирована раньше.')
            elif res == 'CARD_EXPIRED':
                error_message = _(
                    u'Ошибка активации. Срок действия карты истёк.')
            elif res == 'CARD_ACTIVATED':
                error_message = _(u'Карта успешно активирована.')
                status = True
            elif res == 'CARD_ACTIVATION_ERROR':
                error_message = _(u'Ошибка активации карты.')

            return {
                'error_message': error_message,
                'status': status
            }
        else:
            return {
                'error_message': _(u"Проверьте заполнение формы"),
                'status': status
            }
    else:
        return {
            'error_message': _(u"Ошибка активации карточки"),
            'status': status,
        }
