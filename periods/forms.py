from django.contrib.auth import get_user_model

import floppyforms.__future__ as forms

from periods import models as period_models


class UserForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'send_emails', 'timezone', 'birth_date',
                  'luteal_phase_length']


class PeriodForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = period_models.FlowEvent
        exclude = ['user']
