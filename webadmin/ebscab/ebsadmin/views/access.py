# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import AccessParametersForm
from billservice.utils import systemuser_required
from billservice.models import Tariff, TimeSpeed
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from ebscab.lib.decorators import render_to
from object_log.models import LogItem

from ebsadmin.tables import TimeSpeedTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_accessparameters.html')
def accessparameters(request):
    item = None
    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    prepaidtable = None

    if tariff:
        if request.method == 'POST':
            id = request.POST.get("id")
            if tariff.access_parameters:
                model = tariff.access_parameters
                form = AccessParametersForm(request.POST, instance=model)
            else:
                form = AccessParametersForm(request.POST)

            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                item = model

                if id:
                    log('EDIT', request.user, model)
                else:
                    log('CREATE', request.user, model)

                messages.success(request,
                                 _(u'Параметры доступа успешно сохранены.'),
                                 extra_tags='alert-success')
                return HttpResponseRedirect(
                    "%s?tariff_id=%s" %
                    (reverse("tariff_accessparameters"), tariff.id))
            else:
                messages.error(
                    request,
                    _(u'При сохранении параметров доступа произошла ошибка.'),
                    extra_tags='alert-danger')
        else:
            item = tariff.access_parameters

        if not (request.user.account.has_perm('billservice.view_tariff')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')

        form = AccessParametersForm(instance=item)
        items = TimeSpeed.objects.filter(access_parameters=item)
        table = TimeSpeedTable(items)
        RequestConfig(request, paginate=False).configure(table)

    else:
        if not (request.user.account.has_perm('billservice.view_tariff')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if not (request.user.account.has_perm('billservice.change_tariff')):
            messages.error(
                request,
                _(u'У вас нет прав на редактирование тарифного плана'),
                extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')

        form = AccessParametersForm()

    return {
        'formset': None,
        'table': table,
        'tariff': tariff,
        'item': item,
        'form': form,
        'active': 'accessparameters'
    }
