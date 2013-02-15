from django.contrib import admin

from egg_timer.apps.periods import models

admin.site.register(models.Period)
