import datetime
import pytz
import re

from django.contrib.auth import models as auth_models
from django.test import TestCase
from mock import patch

from periods import models as period_models
from periods.tests.factories import FlowEventFactory, UserFactory


TIMEZONE = pytz.timezone("US/Eastern")


class TestModels(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.basic_user = UserFactory.build(first_name='')

        self.period = FlowEventFactory()

    def test_user_get_full_name_email(self):
        self.assertTrue(re.match(r'user_[\d]+@example.com', '%s' % self.basic_user.get_full_name()))

    def test_user_get_full_name(self):
        self.assertEqual(u'Jessamyn', '%s' % self.user.get_full_name())

    def test_user_get_short_name_email(self):
        self.assertTrue(re.match(r'user_[\d]+@example.com',
                                 '%s' % self.basic_user.get_short_name()))

    def test_user_get_short_name(self):
        self.assertEqual(u'Jessamyn', '%s' % self.user.get_short_name())

    def test_user_str(self):
        self.assertEqual(u'Jessamyn', '%s' % self.user.get_short_name())

    def test_flow_event_unicode(self):
        self.assertTrue(re.match(r'Jessamyn MEDIUM \(2014-01-31 00:00:00-0[\d]:00\)',
                                 '%s' % self.period))

    def test_statistics_str(self):
        stats = period_models.Statistics.objects.filter(user=self.user)[0]

        self.assertEqual(u'Jessamyn (', ('%s' % stats)[:10])
        self.assertEqual([], stats.next_periods)
        self.assertEqual([], stats.next_ovulations)

    def test_statistics_with_average(self):
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 15)))
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 3, 15)))
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 4, 10)))

        stats = period_models.Statistics.objects.filter(user=self.period.user)[0]

        self.assertEqual(u'Jessamyn (', ('%s' % stats)[:10])
        self.assertEqual(23, stats.average_cycle_length)
        expected_periods = [datetime.date(2014, 5, 3),
                            datetime.date(2014, 5, 26),
                            datetime.date(2014, 6, 18)]
        self.assertEqual(expected_periods, stats.next_periods)
        expected_ovulations = [datetime.date(2014, 4, 19),
                               datetime.date(2014, 5, 12),
                               datetime.date(2014, 6, 4)]
        self.assertEqual(expected_ovulations, stats.next_ovulations)

    def test_statistics_current_cycle_length_no_periods(self):
        stats = period_models.Statistics.objects.filter(user=self.user)[0]

        self.assertEqual(-1, stats.current_cycle_length)
        self.assertEqual([], stats.next_periods)
        self.assertEqual([], stats.next_ovulations)

    def test_add_to_permissions_group_group_does_not_exist(self):
        self.user.groups.all().delete()

        period_models.add_to_permissions_group(period_models.User, self.user)

        groups = self.user.groups.all()
        self.assertEqual(1, groups.count())
        self.assertEqual(3, groups[0].permissions.count())
        for permission in groups[0].permissions.all():
            self.assertEqual('_flowevent', permission.codename[-10:])

    def test_add_to_permissions_group_group_exists(self):
        user = period_models.User(email='jane@jane.com')
        user.save()
        user.groups.all().delete()
        auth_models.Group(name='users').save()

        period_models.add_to_permissions_group(period_models.User, user)

        groups = user.groups.all()
        self.assertEqual(1, groups.count())
        self.assertEqual(0, groups[0].permissions.count())

    @patch('periods.models.Statistics.save')
    def test_update_statistics_deleted_user(self, mock_save):
        self.period.user.delete()
        pre_update_call_count = mock_save.call_count

        period_models.update_statistics(period_models.FlowEvent, self.period)

        self.assertEqual(pre_update_call_count, mock_save.call_count)

    @patch('periods.models._today')
    def test_update_statistics_none_existing(self, mock_today):
        mock_today.return_value = TIMEZONE.localize(datetime.datetime(2014, 4, 5))
        period = FlowEventFactory(user=self.period.user,
                                  timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 27)))

        period_models.update_statistics(period_models.FlowEvent, period)

        stats = period_models.Statistics.objects.get(user=self.period.user)
        self.assertEqual(27, stats.average_cycle_length)
        self.assertEqual(36, stats.current_cycle_length)
        next_periods = [
            datetime.date(2014, 3, 26),
            datetime.date(2014, 4, 22),
            datetime.date(2014, 5, 19)
        ]
        self.assertEqual(next_periods, stats.next_periods)

    @patch('periods.models._today')
    def test_update_statistics_periods_exist(self, mock_today):
        mock_today.return_value = TIMEZONE.localize(datetime.datetime(2014, 4, 5))
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 14)))
        period = FlowEventFactory(user=self.period.user,
                                  timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 28)))
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 3, 14)))

        period_models.update_statistics(period_models.FlowEvent, period)

        stats = period_models.Statistics.objects.get(user=self.period.user)
        self.assertEqual(14, stats.average_cycle_length)
        self.assertEqual(22, stats.current_cycle_length)
        next_periods = [
            datetime.date(2014, 3, 28),
            datetime.date(2014, 4, 11),
            datetime.date(2014, 4, 25)
        ]
        self.assertEqual(next_periods, stats.next_periods)
