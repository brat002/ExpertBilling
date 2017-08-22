# -*- coding: utf-8 -*-

from django.template.loader import get_template


def render_to(template=None):
    def renderer(function):
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            tmpl = output.pop('TEMPLATE', template)
            return get_template(tmpl).render(output, request)
        return wrapper
    return renderer
