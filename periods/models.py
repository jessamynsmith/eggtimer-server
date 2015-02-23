from custom_user.models import AbstractEmailUser
import datetime
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django_enumfield import enum
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

    def first_days(self):
        return self.flow_events.filter(first_day=True).order_by('timestamp')

    def get_previous_period(self, previous_to=None):
        previous_periods = self.first_days()
        if previous_to:
            previous_periods = previous_periods.filter(timestamp__lte=previous_to)
        previous_periods = previous_periods.order_by('-timestamp')
        if previous_periods.exists():
            return previous_periods[0]
        return None

    def get_next_period(self, after=None):
        next_periods = self.first_days()
        if after:
            next_periods = next_periods.filter(timestamp__gte=after)
        next_periods = next_periods.order_by('timestamp')
        if next_periods.exists():
            return next_periods[0]
        return None

    def get_cycle_lengths(self):
        cycle_lengths = []
        first_days = self.first_days()
        if first_days.exists():
            for i in range(1, first_days.count()):
                duration = first_days[i].timestamp.date() - first_days[i-1].timestamp.date()
                cycle_lengths.append(duration.days)
        return cycle_lengths

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        full_name = full_name.strip()
        if not full_name:
            full_name = self.email
        return full_name

    def get_short_name(self):
        short_name = self.first_name
        if not short_name:
            short_name = self.email
        return short_name

    def __str__(self):
        return u"%s (%s)" % (self.get_full_name(), self.email)


class FlowLevel(enum.Enum):
    SPOTTING = 0
    LIGHT = 1
    MEDIUM = 2
    HEAVY = 3


class FlowColor(enum.Enum):
    PINK = 0
    LIGHT_RED = 1
    RED = 2
    DARK_RED = 3
    BROWN = 4
    BLACK = 5


class ClotSize(enum.Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


class FlowEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='flow_events', null=True)
    timestamp = models.DateTimeField()
    first_day = models.BooleanField(default=False)
    level = enum.EnumField(FlowLevel, default=FlowLevel.MEDIUM)
    color = enum.EnumField(FlowColor, default=FlowColor.RED)
    clots = enum.EnumField(ClotSize, default=None, null=True, blank=True)
    comment = models.TextField(max_length=250, null=True, blank=True)

    def __str__(self):
        return u"%s %s (%s)" % (self.user.get_full_name(), FlowLevel.label(self.level),
                                self.timestamp)


class Statistics(models.Model):

    class Meta:
        verbose_name_plural = "statistics"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='statistics', null=True)
    average_cycle_length = models.IntegerField(default=28)

    @property
    def current_cycle_length(self):
        current_cycle = -1
        today = _today()
        previous_period = self.user.get_previous_period(previous_to=today)
        if previous_period:
            current_cycle = (today - previous_period.timestamp.date()).days
        return current_cycle

    @property
    def next_periods(self):
        next_dates = []
        previous_period = self.user.get_previous_period()
        if previous_period:
            for i in range(1, 4):
                next_dates.append((previous_period.timestamp + datetime.timedelta(
                    days=i*self.average_cycle_length)).date())
        return next_dates

    @property
    def next_ovulations(self):
        next_dates = []
        previous_period = self.user.get_previous_period()
        if previous_period:
            for i in range(1, 4):
                next_dates.append((previous_period.timestamp + datetime.timedelta(
                    days=i*self.average_cycle_length - self.user.luteal_phase_length)).date())
        return next_dates

    def __str__(self):
        return u"%s (%s)" % (self.user.get_full_name(), self.user.email)


def add_to_permissions_group(sender, instance, **kwargs):
    try:
        group = Group.objects.get(name='users')
    except Group.DoesNotExist:
        group = Group(name='users')
        group.save()
        group.permissions.add(*Permission.objects.filter(codename__endswith='_flowevent').all())
    group.user_set.add(instance)
    group.save()


def create_statistics(sender, instance, **kwargs):
    if not hasattr(instance, 'statistics'):
        stats = Statistics(user=instance)
        stats.save()


def update_statistics(sender, instance, **kwargs):
    try:
        stats = Statistics.objects.get(user=instance.user)
    except (Statistics.DoesNotExist, User.DoesNotExist):
        # There may not be statistics, for example when deleting a user
        return

    cycle_lengths = instance.user.get_cycle_lengths()
    # Calculate average (if possible) and update statistics object
    if len(cycle_lengths) > 0:
        avg = sum(cycle_lengths) / len(cycle_lengths)
        stats.average_cycle_length = int(round(avg))
    stats.save()


signals.post_save.connect(create_api_key, sender=settings.AUTH_USER_MODEL)
signals.post_save.connect(add_to_permissions_group, sender=settings.AUTH_USER_MODEL)
signals.post_save.connect(create_statistics, sender=settings.AUTH_USER_MODEL)

signals.post_save.connect(update_statistics, sender=FlowEvent)
signals.post_delete.connect(update_statistics, sender=FlowEvent)
