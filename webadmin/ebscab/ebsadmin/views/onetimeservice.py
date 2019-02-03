# -*-coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import OneTimeServiceForm
from billservice.utils import systemuser_required
from billservice.models import OneTimeService, Tariff
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from ebscab.utils.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import OneTimeServiceTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_onetimeservice.html')
def onetimeservice(request):
    if not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    item = None
    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    if tariff_id:

        items = OneTimeService.objects.filter(tarif__id=tariff_id)
        table = OneTimeServiceTable(items)
        RequestConfig(request, paginate=False).configure(table)
    else:
        form = OneTimeServiceForm(initial={'tarif': tariff_id})

    return {'formset': None, 'table': table, 'tariff': tariff, 'active': 'ots'}


@systemuser_required
@render_to('ebsadmin/onetimeservice_edit.html')
def onetimeservice_edit(request):
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
            model = OneTimeService.objects.get(id=id)
            form = OneTimeServiceForm(request.POST, instance=model)
        else:
            form = OneTimeServiceForm(request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Разовая услуга сохранена.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(
                request,
                _(u'При сохранении разовой  услуги произошла ошибка.'),
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
            item = OneTimeService.objects.get(id=id)
            form = OneTimeServiceForm(instance=item)
        else:
            form = OneTimeServiceForm(initial={'tarif': tariff_id})

    return {
        'formset': None,
        'form': form
    }


@ajax_request
@systemuser_required
def onetimeservice_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = OneTimeService.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная услуга не найдена %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Разовая услуга удалёна.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении разовой услуги произошла ошибка.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": _(u'OneTimeService not found')
        }
