# -*- coding:utf-8 -*-
from django import template
from files.models import File, FileCategory 
register = template.Library()

@register.inclusion_tag('files/tags/files.html')
def categoty_files(category):
    files = File.objects.filter(category = category)
    return {'files':files}