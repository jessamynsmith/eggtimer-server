# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('start_time', models.TimeField(null=True, blank=True)),
                ('length', models.IntegerField(null=True, blank=True)),
                ('userprofile', models.ForeignKey(related_name='periods', to='userprofiles.UserProfile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('average_cycle_length', models.IntegerField(default=28)),
                ('userprofile', models.OneToOneField(related_name='statistics', to='userprofiles.UserProfile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='period',
            unique_together=set([('userprofile', 'start_date')]),
        ),
    ]
