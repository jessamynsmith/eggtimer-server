import datetime
from django.contrib.auth import models as auth_models
from django.test import TestCase
from mock import patch

from egg_timer.apps.periods import models as period_models


class TestModels(TestCase):

    def setUp(self):
        self.user = auth_models.User.objects.create_user(username='jessamyn',
            password='bogus', email='jessamyn@example.com')
        self.user.first_name = u'Jessamyn'
        self.user.save()

    def _create_period(self, start_date, save=True):
        period = period_models.Period.objects.create(userprofile=self.user.userprofile,
            start_date=start_date)
        if save:
            period.save()
        return period

    def test_period_unicode_no_start_time(self):
        period = self._create_period(start_date=datetime.date(2013, 4, 15), save=False)
        self.assertEqual('Jessamyn (2013-04-15)', '%s' % period)

    def test_period_unicode_with_start_time(self):
        period = self._create_period(start_date=datetime.date(2013, 4, 15), save=False)
        period.start_time = datetime.time(1, 2, 3)
        self.assertEqual(u'Jessamyn (2013-04-15 01:02:03)', '%s' % period)

    def test_statistics_unicode_no_average(self):
        stats = period_models.Statistics.objects.filter(userprofile=self.user.userprofile)[0]

        self.assertEqual(u'Jessamyn (avg: Not enough cycles to calculate)', '%s' % stats)
        self.assertEqual([], stats.next_periods)
        self.assertEqual([], stats.next_ovulations)

    def test_statistics_unicode_with_average(self):
        self._create_period(start_date=datetime.date(2013, 2, 15))
        self._create_period(start_date=datetime.date(2013, 3, 15))
        self._create_period(start_date=datetime.date(2013, 4, 10))

        stats = period_models.Statistics.objects.filter(userprofile=self.user.userprofile)[0]

        self.assertEqual(u'Jessamyn (avg: 27)', '%s' % stats)
        expected_periods = [datetime.date(2013, 5, 7),
                            datetime.date(2013, 6, 3),
                            datetime.date(2013, 6, 30)]
        self.assertEqual(expected_periods, stats.next_periods)
        expected_ovulations = [datetime.date(2013, 4, 23),
                               datetime.date(2013, 5, 20),
                               datetime.date(2013, 6, 16)]
        self.assertEqual(expected_ovulations, stats.next_ovulations)

    def test_statistics_current_cycle_length_no_periods(self):
        stats = period_models.Statistics.objects.filter(userprofile=self.user.userprofile)[0]

        self.assertEqual(-1, stats.current_cycle_length)
        self.assertEqual([], stats.next_periods)
        self.assertEqual([], stats.next_ovulations)

    def test_update_length_none_existing(self):
        period = self._create_period(start_date=datetime.date(2013, 4, 15), save=False)

        period_models.update_length(period_models.Period, period)

        self.assertIsNone(period.length)

    def test_update_length_previous_exists(self):
        previous = self._create_period(start_date=datetime.date(2013, 4, 1))
        period = self._create_period(start_date=datetime.date(2013, 4, 15), save=False)

        period_models.update_length(period_models.Period, period)

        self.assertIsNone(period.length)
        self.assertEqual(14, period_models.Period.objects.get(pk=previous.pk).length)

    def test_update_length_next_exists(self):
        period = self._create_period(start_date=datetime.date(2013, 4, 15), save=False)
        self._create_period(start_date=datetime.date(2013, 4, 30))

        period_models.update_length(period_models.Period, period)

        self.assertEqual(15, period.length)

    @patch('egg_timer.apps.periods.models._today')
    def test_update_statistics_none_existing(self, mock_today):
        mock_today.return_value = datetime.date(2013, 5, 5)
        period = self._create_period(start_date=datetime.date(2013, 4, 15))

        period_models.update_statistics(period_models.Period, period)

        stats = period_models.Statistics.objects.get(userprofile=self.user.userprofile)
        self.assertIsNone(stats.average_cycle_length)
        self.assertEqual(20, stats.current_cycle_length)
        self.assertEqual([], stats.next_periods)

    @patch('egg_timer.apps.periods.models._today')
    def test_update_statistics_periods_exist(self, mock_today):
        mock_today.return_value = datetime.date(2013, 5, 5)
        self._create_period(start_date=datetime.date(2013, 4, 1))
        period = self._create_period(start_date=datetime.date(2013, 4, 15))
        self._create_period(start_date=datetime.date(2013, 4, 30))

        period_models.update_statistics(period_models.Period, period)

        stats = period_models.Statistics.objects.get(userprofile=self.user.userprofile)
        self.assertEqual(15, stats.average_cycle_length)
        self.assertEqual(5, stats.current_cycle_length)
        next_periods = [
            datetime.date(2013, 5, 15),
            datetime.date(2013, 5, 30),
            datetime.date(2013, 6, 14)
        ]
        self.assertEqual(next_periods, stats.next_periods)
