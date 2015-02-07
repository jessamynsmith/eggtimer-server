# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0003_auto_20150206_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='period',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='periods'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='statistics',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, null=True, related_name='statistics'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='period',
            unique_together=set([('user', 'start_date'), ('userprofile', 'start_date')]),
        ),
    ]
