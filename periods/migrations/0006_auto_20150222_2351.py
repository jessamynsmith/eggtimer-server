# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0005_auto_20150222_1302'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='period',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='period',
            name='user',
        ),
        migrations.DeleteModel(
            name='Period',
        ),
    ]
