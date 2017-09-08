# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from helpdesk.forms import EmailIgnoreForm
from helpdesk.utils import superuser_required
from helpdesk.models import IgnoreEmail


@superuser_required
def email_ignore(request):
    return render(request,
                  'helpdesk/email_ignore_list.html',
                  {'ignore_list': IgnoreEmail.objects.all()})


@superuser_required
def email_ignore_add(request):
    if request.method == 'POST':
        form = EmailIgnoreForm(request.POST)
        if form.is_valid():
            ignore = form.save()
            return HttpResponseRedirect(reverse('helpdesk_email_ignore'))
    else:
        form = EmailIgnoreForm(request.GET)

    return render(request,
                  'helpdesk/email_ignore_add.html',
                  {'form': form})


@superuser_required
def email_ignore_del(request, id):
    ignore = get_object_or_404(IgnoreEmail, id=id)
    if request.method == 'POST':
        ignore.delete()
        return HttpResponseRedirect(reverse('helpdesk_email_ignore'))
    else:
        return render(request,
                      'helpdesk/email_ignore_del.html',
                      {'ignore': ignore})
