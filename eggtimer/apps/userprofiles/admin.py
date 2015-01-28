from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from tastypie.models import create_api_key

from eggtimer.apps.userprofiles import models as userprofile_models


admin.site.register(userprofile_models.UserProfile)

models.signals.post_save.connect(create_api_key, sender=User)
