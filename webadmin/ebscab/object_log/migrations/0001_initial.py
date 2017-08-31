# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogAction',
            fields=[
                ('name', models.CharField(max_length=128, unique=True, serialize=False, primary_key=True)),
                ('template', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430')),
                ('object_id1', models.PositiveIntegerField(null=True)),
                ('serialized_data', models.TextField(null=True, verbose_name='\u0414\u0430\u043c\u043f')),
                ('changed_data', models.TextField(null=True, verbose_name='\u0418\u0437\u043c\u0435\u043d\u0451\u043d\u043d\u044b\u0435 \u043f\u043e\u043b\u044f')),
                ('action', models.ForeignKey(related_name='entries', verbose_name='\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435', to='object_log.LogAction')),
                ('object_type1', models.ForeignKey(related_name='log_items1', verbose_name='\u0422\u0438\u043f \u043e\u0431\u044a\u0435\u043a\u0442\u0430', to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(related_name='log_items', verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('timestamp',),
            },
            bases=(models.Model,),
        ),
    ]
