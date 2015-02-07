# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from tastypie.models import ApiKey


def update_user(apps, schema_editor):
    # Create new users from existing user/userprofile
    UserProfile = apps.get_model("userprofiles", "UserProfile")
    User = apps.get_model("periods", "User")
    for profile in UserProfile.objects.all():
        print("working on profile: %s\n" % profile.id)
        user = User.objects.create(
            date_joined=profile.user.date_joined,
            email=profile.user.email,
            first_name=profile.user.first_name,
            id=profile.user.id,
            is_active=profile.user.is_active,
            is_staff=profile.user.is_staff,
            is_superuser=profile.user.is_superuser,
            last_login=profile.user.last_login,
            last_name=profile.user.last_name,
            password=profile.user.password,
            send_emails=False,
            birth_date=profile.birth_date,
            luteal_phase_length=profile.luteal_phase_length,
            )

        for perm in profile.user.user_permissions.all():
            user.user_permissions.add(perm)
        for group in profile.user.groups.all():
            user.groups.add(group)


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0002_user'),
    ]

    operations = [
        migrations.RunPython(update_user),
    ]
