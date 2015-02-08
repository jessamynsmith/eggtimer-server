from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import ugettext_lazy as _

from eggtimer.apps.periods import models
from eggtimer.apps.periods import forms as period_forms


class UserAdmin(auth_admin.UserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'birth_date',
                                         'luteal_phase_length')}),
        (_('Settings'), {'fields': ('send_emails',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),)
    form = period_forms.UserChangeForm
    add_form = period_forms.UserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'send_emails')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Period)
admin.site.register(models.Statistics)
