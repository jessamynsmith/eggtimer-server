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
    def next_periods(self):
        next_dates = []
        if self.average_cycle_length:
            last_period = self.userprofile.periods.order_by('-start_date')[0]
            for i in range(1, 4):
                next_dates.append(last_period.start_date + datetime.timedelta(
                    days=i*self.average_cycle_length))
        return next_dates

    def __unicode__(self):
        average = self.average_cycle_length
        if not average:
            average = 'Not enough cycles to calculate'
        return u"%s (avg: %s)" % (self.userprofile.full_name, average)

    def get_absolute_url(self):
        return reverse('statistics_detail', args=[self.pk])


def create_statistics(sender, instance, **kwargs):
    if not hasattr(instance, 'statistics'):
        stats = Statistics(userprofile=instance)
        stats.save()


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

    next_periods = instance.userprofile.periods.filter(
        start_date__gt=instance.start_date).order_by('start_date')
    try:
        next_period = next_periods[0]
        delta = next_period.start_date - instance.start_date
        instance.length = delta.days
    except IndexError:
        # If no next period, nothing to set
        pass


def update_length_delete(sender, instance, **kwargs):
    next_periods = instance.userprofile.periods.filter(
        start_date__gt=instance.start_date).order_by('start_date')
    start_date = None
    try:
        start_date = next_periods[0].start_date
    except IndexError:
        # If no next period, nothing to set
        pass

    previous_periods = instance.userprofile.periods.filter(
        start_date__lt=instance.start_date).order_by('-start_date')
    try:
        previous_period = previous_periods[0]
        if start_date:
            delta = start_date - previous_period.start_date
            previous_period.length = delta.days
        else:
            previous_period.length = None
        signals.pre_save.disconnect(update_length, sender=Period)
        previous_period.save()
        signals.pre_save.connect(update_length, sender=Period)
    except IndexError:
        # If no previous period, nothing to set
        pass


def update_statistics(sender, instance, **kwargs):
    stats_list = Statistics.objects.filter(userprofile=instance.userprofile)
    stats = stats_list[0]

    cycle_lengths = [x for x in instance.userprofile.periods.values_list('length', flat=True) if x is not None]

    # Calculate average (if possible) and update statistics object
    if len(cycle_lengths) > 0:
        avg = float(sum(cycle_lengths)) / len(cycle_lengths)
        stats.average_cycle_length = int(round(avg))
    else:
        stats.average_cycle_length = None
    stats.save()


signals.post_save.connect(create_statistics, sender=userprofile_models.UserProfile)

signals.pre_save.connect(update_length, sender=Period)
signals.pre_delete.connect(update_length_delete, sender=Period)
signals.post_save.connect(update_statistics, sender=Period)
signals.post_delete.connect(update_statistics, sender=Period)
