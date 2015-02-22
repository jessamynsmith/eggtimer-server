# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0002_auto_20150207_2125'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statistics',
            options={'verbose_name_plural': 'statistics'},
        ),
    ]
