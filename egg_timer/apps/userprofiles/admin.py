from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from tastypie.models import create_api_key

from egg_timer.apps.userprofiles import models as userprofile_models

models.signals.post_save.connect(create_api_key, sender=User)

admin.site.register(userprofile_models.UserProfile)
