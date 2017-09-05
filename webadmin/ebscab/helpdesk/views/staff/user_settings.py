# -*- coding: utf-8 -*-

from django.shortcuts import render

from helpdesk.forms import UserSettingsForm
from helpdesk.lib import staff_member_required


@staff_member_required
def user_settings(request):
    s = request.user.usersettings
    if request.POST:
        form = UserSettingsForm(request.POST)
        if form.is_valid():
            s.settings = form.cleaned_data
            s.save()
    else:
        form = UserSettingsForm(s.settings)

    return render(request,
                  'helpdesk/user_settings.html',
                  {'form': form})
