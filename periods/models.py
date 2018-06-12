import datetime
import pytz
import statistics

from custom_user.models import AbstractEmailUser
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.postgres.fields import JSONField
from django.core.cache import cache
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django_enumfield import enum

from rest_framework.authtoken.models import Token
from timezone_field import TimeZoneField
import requests


def today():
    # Create helper method to allow mocking during tests
    return datetime.datetime.now(pytz.utc)


# TODO break user out into user app
class User(AbstractEmailUser):
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    # TODO enter birth_date in user-specified timezone
    # Ugly workaround to prevent Django allauth from trying and failing to serialize timezone
    _timezone = TimeZoneField(default='America/New_York')
    send_emails = models.BooleanField(_('send emails'), default=True)
    birth_date = models.DateTimeField(_('birth date'), null=True, blank=True)
    luteal_phase_length = models.IntegerField(_('luteal phase length'), default=14)

    # Convenience method so we can use timezone rather than _timezone in most code
    @property
    def timezone(self):
        return self._timezone

    def first_days(self):
        return self.flow_events.filter(first_day=True).order_by('timestamp')

    def cycle_count(self):
        return self.first_days().count()

    def get_previous_period(self, previous_to):
        previous_periods = self.first_days().filter(timestamp__lte=previous_to)
        previous_periods = previous_periods.order_by('-timestamp')
        return previous_periods.first()

    def get_next_period(self, after=None):
        next_periods = self.first_days()
        if after:
            next_periods = next_periods.filter(timestamp__gte=after)
        next_periods = next_periods.order_by('timestamp')
        return next_periods.first()

    def get_cache_key(self, data_type):
        return 'user-%s-%s' % (self.pk, data_type)

    def get_cycle_lengths(self):
        key = self.get_cache_key('cycle_lengths')
        cycle_lengths = cache.get(key)
        if not cycle_lengths:
            cycle_lengths = []
            first_days = self.first_days()
            if first_days.exists():
                for i in range(1, self.cycle_count()):
                    duration = first_days[i].timestamp.date() - first_days[i-1].timestamp.date()
                    cycle_lengths.append(duration.days)
            cache.set(key, cycle_lengths)
        return cycle_lengths

    def get_sorted_cycle_lengths(self):
        key = self.get_cache_key('sorted_cycle_lengths')
        sorted_cycle_lengths = cache.get(key)
        if not sorted_cycle_lengths:
            sorted_cycle_lengths = sorted(self.get_cycle_lengths())
            cache.set(key, sorted_cycle_lengths)
        return sorted_cycle_lengths

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
        return "%s (%s)" % (self.get_full_name(), self.email)


class FlowLevel(enum.Enum):
    SPOTTING = 0
    LIGHT = 1
    MEDIUM = 2
    HEAVY = 3
    VERY_HEAVY = 4


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


class CrampLevel(enum.Enum):
    SLIGHT = 0
    MODERATE = 1
    SEVERE = 2


class FlowEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='flow_events', null=True)
    timestamp = models.DateTimeField()
    first_day = models.BooleanField(default=False)
    level = enum.EnumField(FlowLevel, default=FlowLevel.MEDIUM)
    color = enum.EnumField(FlowColor, default=FlowColor.RED)
    clots = enum.EnumField(ClotSize, default=None, null=True, blank=True)
    cramps = enum.EnumField(CrampLevel, default=None, null=True, blank=True)
    comment = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return "%s %s (%s)" % (self.user.get_full_name(), FlowLevel.label(self.level),
                               self.timestamp)


class Statistics(models.Model):

    class Meta:
        verbose_name_plural = "statistics"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='statistics', null=True)
    average_cycle_length = models.IntegerField(default=28)
    all_time_average_cycle_length = models.IntegerField(default=28)

    def _get_ordinal_value(self, index):
        value = None
        # Could cache this as performance optimization
        sorted_cycle_lengths = self.user.get_sorted_cycle_lengths()
        if len(sorted_cycle_lengths) >= 1:
            value = sorted_cycle_lengths[index]
        return value

    @property
    def cycle_length_minimum(self):
        return self._get_ordinal_value(0)

    @property
    def cycle_length_maximum(self):
        return self._get_ordinal_value(-1)

    def _get_statistics_value(self, method_name, num_values_required=1):
        value = None
        cycle_lengths = self.user.get_cycle_lengths()
        if len(cycle_lengths) >= num_values_required:
            value = method_name(cycle_lengths)
        return value

    @property
    def cycle_length_mean(self):
        mean = self._get_statistics_value(statistics.mean)
        if mean:
            mean = round(float(mean), 1)
        return mean

    @property
    def cycle_length_median(self):
        return self._get_statistics_value(statistics.median)

    @property
    def cycle_length_mode(self):
        try:
            return self._get_statistics_value(statistics.mode)
        except statistics.StatisticsError:
            return None

    @property
    def cycle_length_standard_deviation(self):
        std_dev = self._get_statistics_value(statistics.stdev, 2)
        if std_dev:
            std_dev = round(std_dev, 3)
        return std_dev

    @property
    def current_cycle_length(self):
        current_cycle = -1
        today_date = today()
        previous_period = self.user.get_previous_period(previous_to=today_date)
        if previous_period:
            current_cycle = (today_date.date() - previous_period.timestamp.date()).days
        return current_cycle

    @property
    def first_date(self):
        if not hasattr(self, '_first_date'):
            self._first_date = ''
        return self._first_date

    @property
    def first_day(self):
        if not hasattr(self, '_first_day'):
            self._first_day = ''
        return self._first_day

    def set_start_date_and_day(self, min_timestamp):
        previous_period = self.user.get_previous_period(min_timestamp)
        next_period = self.user.get_next_period(min_timestamp)
        if previous_period:
            self._first_date = min_timestamp.date()
            self._first_day = (self._first_date - previous_period.timestamp.date()).days + 1
        elif next_period:
            self._first_date = next_period.timestamp.date()
            self._first_day = 1

    @property
    def predicted_events(self):
        events = []
        today_date = today()
        previous_period = self.user.get_previous_period(previous_to=today_date)
        if previous_period:
            for i in range(1, 4):
                ovulation_date = (previous_period.timestamp + datetime.timedelta(
                    days=i*self.average_cycle_length - self.user.luteal_phase_length)).date()
                events.append({'timestamp': ovulation_date, 'type': 'projected ovulation'})
                period_date = (previous_period.timestamp + datetime.timedelta(
                    days=i*self.average_cycle_length)).date()
                events.append({'timestamp': period_date, 'type': 'projected period'})
        return events

    def __str__(self):
        return "%s (%s)" % (self.user.get_full_name(), self.user.email)


class AerisData(models.Model):
    # Called AerisData for historical reasons; now pulling data from US Navy API
    # http://aa.usno.navy.mil/data/docs/api.php#phase
    to_date = models.DateField(unique=True)
    data = JSONField()

    @staticmethod
    def get_from_server(from_date):
        moon_phase_url = '{}/moon/phase'.format(settings.MOON_PHASE_URL)
        from_date_us_format = datetime.datetime.strptime(from_date, '%Y-%m-%d').strftime('%-m/%-d/%Y')
        params = {
            'nump': 8,
            'date': from_date_us_format,
        }
        try:
            result = requests.get(moon_phase_url, params)
            result = result.json()
        except requests.exceptions.ConnectionError:
            result = {'error': 'Unable to reach Moon Phase API'}
        return result

    @classmethod
    def get_for_date(cls, from_date, to_date):
        existing = cls.objects.filter(to_date=to_date)
        if existing.count() > 0:
            data = existing[0].data
        else:
            data = cls.get_from_server(from_date)
            if data and not data['error']:
                cls.objects.create(to_date=to_date, data=data)
        return data


def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


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

    cache.delete(instance.user.get_cache_key('cycle_lengths'))
    cache.delete(instance.user.get_cache_key('sorted_cycle_lengths'))

    cycle_lengths = instance.user.get_cycle_lengths()
    # Calculate average (if possible) and update statistics object
    if len(cycle_lengths) > 0:
        recent_cycle_lengths = cycle_lengths[-6:]
        avg = sum(recent_cycle_lengths) / len(recent_cycle_lengths)
        stats.average_cycle_length = int(round(avg))
        avg = sum(cycle_lengths) / len(cycle_lengths)
        stats.all_time_average_cycle_length = int(round(avg))
    stats.save()


signals.post_save.connect(create_auth_token, sender=settings.AUTH_USER_MODEL)
signals.post_save.connect(add_to_permissions_group, sender=settings.AUTH_USER_MODEL)
signals.post_save.connect(create_statistics, sender=settings.AUTH_USER_MODEL)

signals.post_save.connect(update_statistics, sender=FlowEvent)
signals.post_delete.connect(update_statistics, sender=FlowEvent)
