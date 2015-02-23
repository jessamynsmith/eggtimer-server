# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.contrib import auth
from django.db import models, migrations

import periods


def populate_flow(apps, schema_editor):
    FlowEvent = apps.get_model("periods", "FlowEvent")
    Period = apps.get_model("periods", "Period")
    for period in Period.objects.all():
        if period.start_time:
            start_time = period.start_time
        else:
            start_time = datetime.time()
        flow = FlowEvent(user=period.user,
                    timestamp=datetime.datetime.combine(period.start_date, start_time),
                    first_day=True)
        flow.save()

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    app_config = apps.get_app_config('periods')
    # Hack! For some reason, this is just an AppConfigStub, so have to set models_module manually.
    app_config.models_module = periods.models
    auth.management.create_permissions(app_config, verbosity=0)
    try:
        group = Group.objects.get(name='users')
    except Group.DoesNotExist:
        group = Group(name='users')
        group.save()
    group.permissions.remove(*Permission.objects.filter(codename__endswith='_period').all())
    group.permissions.add(*Permission.objects.filter(codename__endswith='_flowevent').all())
    group.save()


def populate_period(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('periods', '0004_flowevent'),
    ]

    operations = [
        migrations.RunPython(populate_flow, populate_period),
    ]
