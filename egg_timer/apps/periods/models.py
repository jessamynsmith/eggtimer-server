from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from egg_timer.apps.userprofiles import models as userprofile_models


class Period(models.Model):

    userprofile = models.ForeignKey(userprofile_models.UserProfile,
                                    related_name='periods')
    start_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = (("userprofile", "start_date"),)

    def __unicode__(self):
        start_time = ''
        if self.start_time:
            start_time = ' %s' % self.start_time
        return "%s (%s%s)" % (self.userprofile.full_name, self.start_date,
                              start_time)

    def get_absolute_url(self):
        return reverse('period_detail', args=[self.pk])


class Statistics(models.Model):

    userprofile = models.OneToOneField(userprofile_models.UserProfile)
    average_cycle_length = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        average = self.average_cycle_length
        if not average:
            average = 'Not enough cycles to calculate'
        return "%s (avg: %s)" % (self.userprofile.full_name, average)

    def get_absolute_url(self):
        return reverse('statistics_detail', args=[self.pk])


def update_statistics(sender, instance, **kwargs):
    # Get or create statistics object
    stats_list = Statistics.objects.filter(userprofile=instance.userprofile)
    if len(stats_list) > 0:
        stats = stats_list[0]
    else:
        stats = Statistics(userprofile=instance.userprofile)

    # Find cycle lengths
    periods = instance.userprofile.periods.order_by('start_date')
    cycle_lengths = []
    for i in range(1, len(periods)):
        cycle_delta = periods[i].start_date - periods[i-1].start_date
        cycle_lengths.append(cycle_delta.days)

    # Calculate average (if possible) and update statistics object
    if len(cycle_lengths) > 0:
        avg = float(sum(cycle_lengths)) / len(cycle_lengths)
        stats.average_cycle_length = int(round(avg))
    stats.save()

signals.post_save.connect(update_statistics, sender=Period)
signals.post_delete.connect(update_statistics, sender=Period)
