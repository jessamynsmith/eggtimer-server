from django.contrib import admin

from eggtimer.apps.periods import models

admin.site.register(models.Period)
admin.site.register(models.Statistics)
