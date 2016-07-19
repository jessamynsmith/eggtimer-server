# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0012_auto_20151024_2225'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='timezone',
            new_name='_timezone',
        ),
    ]
