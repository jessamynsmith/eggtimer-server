# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('email', models.EmailField(verbose_name='email address', max_length=254, unique=True)),
                ('first_name', models.CharField(verbose_name='first name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', blank=True, max_length=30)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('send_emails', models.BooleanField(default=True, verbose_name='send emails')),
                ('birth_date', models.DateTimeField(blank=True, verbose_name='birth date', null=True)),
                ('luteal_phase_length', models.IntegerField(default=14, verbose_name='luteal phase length')),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', to='auth.Group', blank=True, verbose_name='groups', related_query_name='user', related_name='user_set')),
                ('user_permissions', models.ManyToManyField(help_text='Specific permissions for this user.', to='auth.Permission', blank=True, verbose_name='user permissions', related_query_name='user', related_name='user_set')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('start_date', models.DateField()),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='periods')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('average_cycle_length', models.IntegerField(default=28)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, null=True, related_name='statistics')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='period',
            unique_together=set([('user', 'start_date')]),
        ),
    ]
