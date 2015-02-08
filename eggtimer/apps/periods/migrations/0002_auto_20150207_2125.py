# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(db_index=True, max_length=255, verbose_name='email address', unique=True),
            preserve_default=True,
        ),
    ]
