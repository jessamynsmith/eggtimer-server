from custom_user.admin import EmailUserAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from periods import models


class FlowAdmin(admin.ModelAdmin):

    list_display = ['user', 'timestamp', 'first_day', 'level', 'color', 'clots']
    list_filter = ['timestamp', 'first_day', 'level', 'color', 'clots']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'timestamp', 'level',
                     'color', 'clots', 'comment']


class StatisticsAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'average_cycle_length']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']


class UserAdmin(EmailUserAdmin):

    list_display = ['email', 'first_name', 'last_name', 'is_active', 'send_emails']
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'password')}),
        (_('Settings'), {'fields': ('send_emails', 'luteal_phase_length', 'birth_date')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    search_fields = ['email', 'first_name', 'last_name']


admin.site.register(models.FlowEvent, FlowAdmin)
admin.site.register(models.Statistics, StatisticsAdmin)
admin.site.register(models.User, UserAdmin)
