# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import auth
from django.db import migrations


def update_averages(apps, schema_editor):
    User = auth.get_user_model()
    for user in User.objects.all():
        period = user.get_previous_period()
        if period:
            period.save()


def reverse_update_averages(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0010_statistics_all_time_average_cycle_length'),
    ]

    operations = [
        migrations.RunPython(update_averages, reverse_update_averages),
    ]
