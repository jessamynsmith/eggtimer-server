from django.contrib import admin

from egg_timer.apps.userprofiles import models

admin.site.register(models.UserProfile)
