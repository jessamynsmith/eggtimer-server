from django import forms

from periods import models as period_models


class UserForm(forms.ModelForm):

    class Meta:
        model = period_models.User
        fields = ['first_name', 'last_name', 'send_emails', 'birth_date', 'luteal_phase_length']
