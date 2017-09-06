# -*- coding: utf-8 -*-

import mimetypes

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from billservice.utils import systemuser_required
from ebscab.lib.decorators import render_to
from object_log.models import LogItem

from helpdesk.forms import FollowUpForm
from helpdesk.models import Attachment, FollowUp, Ticket


log = LogItem.objects.log_action


@systemuser_required
@render_to('helpdesk/followup_edit.html')
def followup_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        if id:
            model = FollowUp.objects.get(id=id)
            form = FollowUpForm(request.POST, instance=model)
            if not (request.user.account.has_perm('helpdesk.change_followup')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование комментариев '
                      u'к заявке'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = FollowUpForm(request.POST, request.FILES)
            if not (request.user.account.has_perm('helpdesk.add_followup')):
                messages.error(
                    request,
                    _(u'У вас нет прав на добавление комментариев '
                      u'к заявке'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            followup_type = form.cleaned_data.get('followup_type')
            if followup_type == 'comment':
                if not id:
                    model.title = _(u'Добавлен комментарий от %(USER)s ') % {
                        'USER': request.user.account}
            elif followup_type == 'files':
                if not id:
                    model.title = _(u'Добавлен файл от %(USER)s ') % {
                        'USER': request.user.account}

                files = []
                if request.FILES:
                    for file in request.FILES.getlist('file'):
                        filename = file.name.replace(' ', '_')
                        a = Attachment(
                            followup=model,
                            filename=filename,
                            mime_type=(mimetypes.guess_type(filename)[0] or
                                       'application/octet-stream'),
                            size=file.size
                        )
                        a.file.save(file.name, file, save=False)
                        a.save()

                        if file.size < \
                                getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                            # Only files smaller than 512kb (or as defined in
                            # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via
                            # email.
                            files.append(a.file.path)

            elif followup_type == 'new_status':
                model.title = _(u'Статус заявки изменён %(USER)s ') % {
                    'USER': request.user.account}
                if model.new_status != model.ticket:
                    model.ticket.status = model.new_status
                    if model.new_status in [3, 4]:
                        model.ticket.resolution = model.comment
                    model.ticket.save()
                    log('EDIT', request.user, model.ticket)

            model.systemuser = request.user.account
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Комментарий успешно сохранён.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(request,
                           _(u'При сохранении комментария возникли ошибки.'),
                           extra_tags='alert-danger')
            if form._errors:
                for k, v in form._errors.items():
                    messages.error(request,
                                   '%s=>%s' % (k, ','.join(v)),
                                   extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        ticket_id = request.GET.get("ticket_id")
        followup_type = request.GET.get("followup_type") or 'comment'
        new_status = request.GET.get("new_status")

        if not (request.user.account.has_perm('helpdesk.add_followup')):
            messages.error(request,
                           _(u'У вас нет прав на создание комментариев.'),
                           extra_tags='alert-danger')
            return {}
        if id:
            item = FollowUp.objects.get(id=id)
            form = FollowUpForm(instance=item)
        else:
            if new_status:
                form = FollowUpForm(initial={
                    'ticket': Ticket.objects.get(id=ticket_id),
                    'followup_type': followup_type,
                    'new_status': 2
                })
            else:
                form = FollowUpForm(initial={
                    'ticket': Ticket.objects.get(id=ticket_id),
                    'followup_type': followup_type
                })

    return {
        'form': form,
        'status': False
    }
