from custom_user.admin import EmailUserAdmin
from django.contrib import admin

from periods import models


class UserAdmin(EmailUserAdmin):
    pass


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Period)
admin.site.register(models.Statistics)
