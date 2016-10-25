import floppyforms.__future__ as forms

from periods import models as period_models


class PeriodForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = period_models.FlowEvent
        exclude = ['user']
