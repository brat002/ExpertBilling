# -*- coding:utf-8 -*-
from django.contrib import admin
from files.models import File, FileCategory

admin.site.register(File)
admin.site.register(FileCategory)