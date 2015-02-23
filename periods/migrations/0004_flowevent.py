# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0003_auto_20150222_1233'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlowEvent',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('first_day', models.BooleanField(default=False)),
                ('level', models.IntegerField(default=2)),
                ('color', models.IntegerField(default=2)),
                ('clots', models.IntegerField(null=True, default=None, blank=True)),
                ('comment', models.TextField(max_length=250, null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='flow_events', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
