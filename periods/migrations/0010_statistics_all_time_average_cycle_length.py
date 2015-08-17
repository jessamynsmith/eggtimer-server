# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0009_user_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistics',
            name='all_time_average_cycle_length',
            field=models.IntegerField(default=28),
            preserve_default=True,
        ),
    ]
