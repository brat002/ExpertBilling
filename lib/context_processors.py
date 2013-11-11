# -*- coding=utf-8 -*-
# $Id$
from django.conf import settings

def default_current_view_name(request):
    return {'current_view_name':''}


def project_settings(request):
    return {'settings':settings}
