# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_user(apps, schema_editor):
    # Update periods and statistics to have new user
    Period = apps.get_model("periods", "Period")
    Statistics = apps.get_model("periods", "Statistics")
    User = apps.get_model("periods", "User")
    for period in Period.objects.all():
        print("Working on period: %s\n" % period.id)
        period.user = User.objects.get(id=period.userprofile.user.id)
        period.save()
    for statistics in Statistics.objects.all():
        print("Working on statistics: %s\n" % period.id)
        statistics.user = User.objects.get(id=statistics.userprofile.user.id)
        statistics.save()


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0004_auto_20150206_2254'),
    ]

    operations = [
        migrations.RunPython(update_user),
    ]
