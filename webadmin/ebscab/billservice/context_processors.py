# -*- coding: utf-8 -*-

from django.conf import settings


def settings(request):
    """
    Adds settings context variable to the context.

    """
    return {'settings': settings}
