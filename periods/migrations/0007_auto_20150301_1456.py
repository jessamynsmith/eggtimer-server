# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0006_auto_20150222_2351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flowevent',
            name='comment',
            field=models.CharField(max_length=250, blank=True, null=True),
            preserve_default=True,
        ),
    ]
