# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import OperatorForm
from billservice.helpers import systemuser_required
from billservice.models import Operator
from ebscab.lib.decorators import render_to
from object_log.models import LogItem


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/operator_edit.html')
def operator_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        if id:
            model = Operator.objects.get(id=id)
            form = OperatorForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_operator')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование данных о провайдере'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = OperatorForm(request.POST)
            if not (request.user.account.has_perm('billservice.add_operator')):
                messages.error(
                    request,
                    _(u'У вас нет прав на создание данных о провайдере'),
                    extra_tags='alert-danger')

                return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return HttpResponseRedirect(reverse("operator_edit"))
        else:
            print form._errors
            return {
                'form': form,
                'status': False
            }

    else:
        if not (request.user.account.has_perm('billservice.view_operator')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')

        items = Operator.objects.all()
        if items:
            item = items[0]
            form = OperatorForm(instance=item)
        else:
            form = OperatorForm()

    return {
        'form': form,
        'status': False,
        'item': item
    }
