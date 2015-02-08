from custom_user.models import AbstractEmailUser
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
import datetime
from tastypie.models import create_api_key


def _today():
    # Create helper method to allow mocking during tests
    return datetime.date.today()


class User(AbstractEmailUser):
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    send_emails = models.BooleanField(_('send emails'), default=True)
    birth_date = models.DateTimeField(_('birth date'), null=True, blank=True)
    luteal_phase_length = models.IntegerField(_('luteal phase length'), default=14)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        full_name = full_name.strip()
        if not full_name:
            full_name = self.email
        return full_name

    def get_short_name(self):
        return self.first_name


class Period(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='periods', null=True)
    start_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = (("user", "start_date"),)

    def __str__(self):
        start_time = ''
        if self.start_time:
            start_time = ' %s' % self.start_time
        return u"%s (%s%s)" % (self.user.get_full_name(), self.start_date, start_time)

    def get_absolute_url(self):
        return reverse('period_detail', args=[self.pk])


class Statistics(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='statistics', null=True)
    average_cycle_length = models.IntegerField(default=28)

    @property
    def current_cycle_length(self):
        current_cycle = -1
        if self.user.periods.count() > 0:
            last_cycle = self.user.periods.order_by('-start_date')[0]
            current_cycle = (_today() - last_cycle.start_date).days
        return current_cycle

    @property
    def next_periods(self):
        next_dates = []
        if self.user.periods.count():
            last_period = self.user.periods.order_by('-start_date')[0]
            for i in range(1, 4):
                next_dates.append(last_period.start_date + datetime.timedelta(
                    days=i*self.average_cycle_length))
        return next_dates

    @property
    def next_ovulations(self):
        next_dates = []
        if self.user.periods.count():
            last_period = self.user.periods.order_by('-start_date')[0]
            for i in range(1, 4):
                next_dates.append(last_period.start_date + datetime.timedelta(
                    days=i*self.average_cycle_length - self.user.luteal_phase_length))
        return next_dates

    def __str__(self):
        return u"%s (avg: %s)" % (self.user.get_full_name(), self.average_cycle_length)

    def get_absolute_url(self):
        return reverse('statistics_detail', args=[self.pk])


def create_statistics(sender, instance, **kwargs):
    if not hasattr(instance, 'statistics'):
        stats = Statistics(user=instance)
        stats.save()


def update_length(sender, instance, **kwargs):
    previous_periods = instance.user.periods.filter(
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

    next_periods = instance.user.periods.filter(
        start_date__gt=instance.start_date).order_by('start_date')
    try:
        next_period = next_periods[0]
        delta = next_period.start_date - instance.start_date
        instance.length = delta.days
    except IndexError:
        # If no next period, nothing to set
        pass


def update_length_delete(sender, instance, **kwargs):
    next_periods = instance.user.periods.filter(
        start_date__gt=instance.start_date).order_by('start_date')
    start_date = None
    try:
        start_date = next_periods[0].start_date
    except IndexError:
        # If no next period, nothing to set
        pass

    previous_periods = instance.user.periods.filter(
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
    stats_list = Statistics.objects.filter(user=instance.user)
    if not stats_list:
        # There may not be statistics, for example when deleting a user
        return

    stats = stats_list[0]

    cycle_lengths = [x for x in instance.user.periods.values_list('length', flat=True)
                     if x is not None]

    # Calculate average (if possible) and update statistics object
    if len(cycle_lengths) > 0:
        avg = sum(cycle_lengths) / len(cycle_lengths)
        stats.average_cycle_length = int(round(avg))
    stats.save()


signals.post_save.connect(create_api_key, sender=User)

signals.post_save.connect(create_statistics, sender=settings.AUTH_USER_MODEL)

signals.pre_save.connect(update_length, sender=Period)
signals.pre_delete.connect(update_length_delete, sender=Period)
signals.post_save.connect(update_statistics, sender=Period)
signals.post_delete.connect(update_statistics, sender=Period)
