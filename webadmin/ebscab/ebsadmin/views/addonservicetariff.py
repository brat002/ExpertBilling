# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import AddonServiceTarifForm
from billservice.utils import systemuser_required
from billservice.models import AddonServiceTarif, Tariff
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from ebscab.lib.decorators import ajax_request, render_to
from object_log.models import LogItem

from ebsadmin.tables import AddonServiceTarifTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_addonservice.html')
def addonservicetariff(request):
    if not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    item = None
    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    items = AddonServiceTarif.objects.filter(tarif__id=tariff_id)
    tariff = Tariff.objects.get(id=tariff_id)
    if items:
        table = AddonServiceTarifTable(items)
        RequestConfig(request, paginate=False).configure(table)
    else:
        form = AddonServiceTarifForm(initial={'tarif': tariff_id})
        table = AddonServiceTarifTable({})

    return {
        'table': table,
        'tariff': tariff,
        'active': 'addst'
    }


@systemuser_required
@render_to('ebsadmin/tariff_addonservicetariff_edit.html')
def addonservicetariff_edit(request):
    item = None
    if request.method == 'POST':
        if not (request.user.account.has_perm('billservice.change_tariff')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на редактирование тарифного '
                             u'плана')
            }
        id = request.POST.get("id")
        if id:
            model = AddonServiceTarif.objects.get(id=id)
            form = AddonServiceTarifForm(request.POST, instance=model)
        else:
            form = AddonServiceTarifForm(request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(
                request,
                _(u'Подключаемая услуга успешно добавлена в тарифный план.'),
                extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(request,
                           _(u'Ошибка при сохранении.'),
                           extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")

        if id:
            if not (request.user.account.has_perm('billservice.view_tariff')):
                messages.error(request,
                               _(u'У вас нет прав на доступ в этот раздел.'),
                               extra_tags='alert-danger')
                return {}

            item = AddonServiceTarif.objects.get(id=id)
            form = AddonServiceTarifForm(instance=item)
        else:
            form = AddonServiceTarifForm(initial={'tarif': tariff_id})

    return {
        'item': item,
        'form': form
    }


@ajax_request
@systemuser_required
def addonservicetariff_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = AddonServiceTarif.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное правило не найдено %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Подключаемая услуга удалена из тарифного плана.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении подклчюаемой услуги из тарифного плана '
              u'произошла ошибка.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": "AddonServiceTarif not found"
        }
