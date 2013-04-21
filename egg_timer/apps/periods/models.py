from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from egg_timer.apps.userprofiles import models as userprofile_models
import datetime


def _today():
    # Create helper method to allow mocking during tests
    return datetime.date.today()


class Period(models.Model):

    userprofile = models.ForeignKey(userprofile_models.UserProfile,
                                    related_name='periods')
    start_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = (("userprofile", "start_date"),)

    def __unicode__(self):
        start_time = ''
        if self.start_time:
            start_time = ' %s' % self.start_time
        return u"%s (%s%s)" % (self.userprofile.full_name, self.start_date,
                              start_time)

    def get_absolute_url(self):
        return reverse('period_detail', args=[self.pk])


class Statistics(models.Model):

    userprofile = models.OneToOneField(userprofile_models.UserProfile,
                                       related_name='statistics')
    average_cycle_length = models.IntegerField(null=True, blank=True)

    @property
    def current_cycle_length(self):
        current_cycle = -1
        if self.userprofile.periods.count() > 0:
            last_cycle = self.userprofile.periods.order_by('-start_date')[0]
            current_cycle = (_today() - last_cycle.start_date).days
        return current_cycle

    @property
    def next_period_date(self):
        next_date = datetime.date(year=datetime.MINYEAR, month=1, day=1)
        if self.average_cycle_length:
            last_period = self.userprofile.periods.order_by('-start_date')[0]
            next_date = last_period.start_date + datetime.timedelta(
                days=self.average_cycle_length)
        return next_date

    def __unicode__(self):
        average = self.average_cycle_length
        if not average:
            average = 'Not enough cycles to calculate'
        return u"%s (avg: %s)" % (self.userprofile.full_name, average)

    def get_absolute_url(self):
        return reverse('statistics_detail', args=[self.pk])


def update_length(sender, instance, **kwargs):
    previous_periods = instance.userprofile.periods.filter(
        start_date__lt=instance.start_date).order_by('-start_date')
    try:
        previous_period = previous_periods[0]
        delta = instance.start_date - previous_period.start_date
        previous_period.length = delta.days
        signals.pre_save.disconnect(update_length, sender=Period)
        previous_period.save()
        signals.pre_save.connect(update_length, sender=Period)
    except IndexError:
        # If no previous period, nothing to set
        pass

    try:
        next_periods = instance.userprofile.periods.filter(
            start_date__gt=instance.start_date).order_by('start_date')
        next_period = next_periods[0]
        delta = next_period.start_date - instance.start_date
        instance.length = delta.days
    except IndexError:
        # If no next period, nothing to set
        pass


def update_statistics(sender, instance, **kwargs):
    # Get or create statistics object
    stats_list = Statistics.objects.filter(userprofile=instance.userprofile)
    if len(stats_list) > 0:
        stats = stats_list[0]
    else:
        stats = Statistics(userprofile=instance.userprofile)

    cycle_lengths = [x for x in instance.userprofile.periods.values_list('length', flat=True) if x is not None]

    # Calculate average (if possible) and update statistics object
    if len(cycle_lengths) > 0:
        avg = float(sum(cycle_lengths)) / len(cycle_lengths)
        stats.average_cycle_length = int(round(avg))
    else:
        stats.average_cycle_length = None
    stats.save()

signals.pre_save.connect(update_length, sender=Period)
signals.post_save.connect(update_statistics, sender=Period)
signals.post_delete.connect(update_statistics, sender=Period)
