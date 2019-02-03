# -*- coding: utf-8 -*-

from reports import rep


def report(request, slug):
    report = rep.get(slug)[0]
    return report(request, slug)
