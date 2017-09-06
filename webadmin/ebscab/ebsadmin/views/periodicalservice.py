# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import PeriodicalServiceForm
from billservice.utils import systemuser_required
from billservice.models import PeriodicalService, Tariff
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from ebscab.utils.decorators import ajax_request, render_to
from object_log.models import LogItem

from ebsadmin.tables import PeriodicalServiceTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_periodicalservice.html')
def periodicalservice(request):
    if not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    item = None
    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    items = PeriodicalService.objects.filter(tarif__id=tariff_id)
    tariff = Tariff.objects.get(id=tariff_id)
    if items:
        table = PeriodicalServiceTable(items)
        RequestConfig(request, paginate=False).configure(table)
    else:
        form = PeriodicalServiceForm(initial={'tarif': tariff_id})
        table = PeriodicalServiceTable({})

    return {
        'formset': None,
        'table': table,
        'tariff': tariff,
        'active': 'ps'
    }


@systemuser_required
@render_to('ebsadmin/periodicalservice_edit.html')
def periodicalservice_edit(request):
    item = None
    if request.method == 'POST':
        if not (request.user.account.has_perm('billservice.change_tariff')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на редактирование '
                             u'тарифного плана')
            }
        id = request.POST.get("id")
        if id:
            model = PeriodicalService.objects.get(id=id)
            form = PeriodicalServiceForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_periodicalservice')):
                return {
                    'status': False,
                    'message': _(u'У вас нет прав на редактирование '
                                 u'периодических услуг')
                }
        else:

            form = PeriodicalServiceForm(request.POST)
        if not (request.user.account.has_perm(
                'billservice.add_periodicalservice')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на добавление периодических '
                             u'услуг')
            }

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Периодическая услуга сохранена.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(
                request,
                _(u'При сохранении периодической услуги произошла ошибка.'),
                extra_tags='alert-danger')

            return {
                'form': form,
                'status': False
            }
    else:
        if not (request.user.account.has_perm('billservice.view_tariff')):
            return {
                'status': False
            }
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        if id:
            item = PeriodicalService.objects.get(id=id)
            form = PeriodicalServiceForm(instance=item)
        else:
            form = PeriodicalServiceForm(initial={'tarif': tariff_id})

    return {
        'formset': None,
        'form': form
    }


@ajax_request
@systemuser_required
def periodicalservice_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = PeriodicalService.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная периодическая услуга "
                             u"не найдена %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Периодическая услуга удалёна.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении периодической услуги произошла ошибка.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": "PeriodicalService not found"
        }
