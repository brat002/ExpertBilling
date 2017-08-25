# -*- coding: utf-8 -*-

from django.template.loader import get_template
from django.shortcuts import render


def render_to(template=None):
    def renderer(function):
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            tmpl = output.pop('TEMPLATE', template)
            return render(request, tmpl, output)
        return wrapper
    return renderer
