# -*- coding: utf-8 -*-

from django.contrib.auth import logout
from django.urls import reverse
from django.views.generic.base import RedirectView


class SignoutView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('ebsweb:index')

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super(SignoutView, self).dispatch(request, *args, **kwargs)
