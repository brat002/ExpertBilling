# -*- coding:utf-8 -*-
from lib.decorators import render_to

from files.models import FileCategory

@render_to('files/file_categories.html')
def file_categories(request):
    categories = FileCategory.objects.all()
    return {
            'categories':categories,
            }
