from django.core.urlresolvers import reverse
from django.db import models
from egg_timer.apps.userprofiles import models as userprofile_models


class Period(models.Model):

    userprofile = models.ForeignKey(userprofile_models.UserProfile)
    start_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)

    def __unicode__(self):
        start_time = ''
        if self.start_time:
            start_time = ' %s' % self.start_time
        return "%s (%s%s)" % (self.userprofile.full_name, self.start_date,
                              start_time)

    def get_absolute_url(self):
        return reverse('period_detail', args=[self.pk])
