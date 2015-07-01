# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0008_flowevent_cramps'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default='America/New_York'),
            preserve_default=True,
        ),
    ]
