from custom_user.admin import EmailUserAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from periods import models


class PeriodAdmin(admin.ModelAdmin):

    list_display = ['user', 'start_date', 'start_time']
    list_filter = ['start_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'start_date']


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


admin.site.register(models.Period, PeriodAdmin)
admin.site.register(models.Statistics, StatisticsAdmin)
admin.site.register(models.User, UserAdmin)
