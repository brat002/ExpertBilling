# -*- coding: utf-8 -*-

from django.urls import reverse
from django.views.generic.base import RedirectView


class IndexView(RedirectView):

    def get_redirect_url(self):
        return reverse('ebsweb:account')
