# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic.base import RedirectView

from helpdesk.models import Ticket
from helpdesk.utils import text_is_spam

from ebsweb.forms.support import TicketCreateForm, TicketFollowupForm
from ebsweb.views.base import (
    ProtectedDetailView,
    ProtectedFormView,
    ProtectedListView,
    ProtectedUpdateView,
    UserFormKwargsMixin
)


class SupportView(RedirectView):

    def get_redirect_url(self):
        return reverse('ebsweb:support_tickets')


class SupportTicketsView(ProtectedListView):
    context_object_name = 'tickets'
    paginate_by = 10
    template_name = 'ebsweb/support/tickets.html'

    def get_queryset(self):
        return (Ticket.objects
                .filter(owner=self.request.user)
                .order_by('-created'))


class SupportTicketCreateView(ProtectedFormView):
    form_class = TicketCreateForm
    template_name = 'ebsweb/support/ticket_create.html'
    SPAM_MESSAGE = _(u'''\
Наша система отметила ваше сообщение как <strong>спам</strong>, поэтому мы не \
можем его сохранить. Если это ошибка, пожалуйста, повторите \
попытку. Избегайте большого количества внешних ссылок.
<br>
Извините за неудобства.''')

    def get_initial(self):
        request = self.request
        initial = super(SupportTicketCreateView, self).get_initial()
        if request.user.is_authenticated() and request.user.account.email:
            initial['submitter_email'] = request.user.account.email
        return initial

    def form_valid(self, form):
        request = self.request
        if text_is_spam(form.cleaned_data['body'], self.request):
            messages.error(request, self.SPAM_MESSAGE)
            return super(SupportTicketCreateView, self).form_invalid(form)
        else:
            ticket = form.save(request.user)
            message = ugettext(u'Запрос {ticket_id} успешно создан!'.format(
                ticket_id=ticket.render_id_20()))
            messages.success(request, message)
            return HttpResponseRedirect(ticket.get_absolute_url_20())


class SupportTicketView(ProtectedDetailView):
    model = Ticket
    context_object_name = 'ticket'
    template_name = 'ebsweb/support/ticket.html'


class SupportFollowupCreateView(UserFormKwargsMixin, ProtectedUpdateView):
    model = Ticket
    form_class = TicketFollowupForm
    context_object_name = 'ticket'
    template_name = 'ebsweb/support/followup_create.html'

    def get_object(self):
        o = super(SupportFollowupCreateView, self).get_object()
        # HACK: get_success_url() not have access to self.object (is None),
        # maybe it's a bug
        self.object_cache = o
        return o

    def get_success_url(self):
        return self.object_cache.get_absolute_url_20()

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _(u'Комментарий успешно добавлен'))
        return super(SupportFollowupCreateView, self).form_valid(form)
