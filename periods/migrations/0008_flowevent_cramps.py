# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0007_auto_20150301_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='flowevent',
            name='cramps',
            field=models.IntegerField(blank=True, default=None, null=True),
            preserve_default=True,
        ),
    ]
