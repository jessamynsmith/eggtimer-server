import datetime
import pytz
import re
import requests

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.test import TestCase
from mock import MagicMock, patch

from periods import models as period_models
from periods.tests.factories import FlowEventFactory, UserFactory

TIMEZONE = pytz.timezone("US/Eastern")


class TestUser(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.basic_user = UserFactory.build(first_name='')

        self.period = FlowEventFactory()
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 27)))
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 3, 24)))

    def test_get_cycle_lengths_no_data(self):
        self.assertEqual([], self.basic_user.get_cycle_lengths())

    def test_get_cycle_lengths(self):
        self.assertEqual([27, 25], self.period.user.get_cycle_lengths())

    def test_get_sorted_cycle_lengths_no_data(self):
        self.assertEqual([], self.basic_user.get_sorted_cycle_lengths())

    def test_get_sorted_cycle_lengths(self):
        self.assertEqual([25, 27], self.period.user.get_sorted_cycle_lengths())

    def test_get_full_name_email(self):
        self.assertTrue(re.match(r'user_[\d]+@example.com', '%s' % self.basic_user.get_full_name()))

    def test_get_full_name(self):
        self.assertEqual(u'Jessamyn', '%s' % self.user.get_full_name())

    def test_get_short_name_email(self):
        self.assertTrue(re.match(r'user_[\d]+@example.com',
                                 '%s' % self.basic_user.get_short_name()))

    def test_get_short_name(self):
        self.assertEqual(u'Jessamyn', '%s' % self.user.get_short_name())

    def test_str(self):
        self.assertTrue(re.match(r'user_[\d]+@example.com \(user_[\d]+@example.com\)',
                                 '%s' % self.basic_user))


class TestFlowEvent(TestCase):
    def setUp(self):
        self.period = FlowEventFactory()

    def test_str(self):
        self.assertEqual('Jessamyn Medium (2014-01-31 17:00:00+00:00)', '%s' % self.period)


class TestStatistics(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.period = FlowEventFactory()

    def test_str(self):
        stats = period_models.Statistics.objects.filter(user=self.user).first()

        self.assertEqual(u'Jessamyn (', ('%s' % stats)[:10])

    def test_with_average(self):
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 15)))
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 3, 15)))
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 4, 10)))

        stats = period_models.Statistics.objects.filter(user=self.period.user).first()

        self.assertEqual(u'Jessamyn (', ('%s' % stats)[:10])
        self.assertEqual(23, stats.average_cycle_length)
        self.assertEqual(15, stats.cycle_length_minimum)
        self.assertEqual(28, stats.cycle_length_maximum)
        self.assertEqual(23, stats.cycle_length_mean)
        self.assertEqual(26, stats.cycle_length_median)
        self.assertEqual(None, stats.cycle_length_mode)
        self.assertEqual(7.0, stats.cycle_length_standard_deviation)
        expected_events = [{'timestamp': datetime.date(2014, 4, 19), 'type': 'projected ovulation'},
                           {'timestamp': datetime.date(2014, 5, 3), 'type': 'projected period'},
                           {'timestamp': datetime.date(2014, 5, 12), 'type': 'projected ovulation'},
                           {'timestamp': datetime.date(2014, 5, 26), 'type': 'projected period'},
                           {'timestamp': datetime.date(2014, 6, 4), 'type': 'projected ovulation'},
                           {'timestamp': datetime.date(2014, 6, 18), 'type': 'projected period'}]
        self.assertEqual(expected_events, stats.predicted_events)

    def test_current_cycle_length_no_periods(self):
        stats = period_models.Statistics.objects.filter(user=self.user).first()

        self.assertEqual(-1, stats.current_cycle_length)
        self.assertEqual(28, stats.average_cycle_length)
        self.assertEqual(None, stats.cycle_length_minimum)
        self.assertEqual(None, stats.cycle_length_maximum)
        self.assertEqual(None, stats.cycle_length_mean)
        self.assertEqual(None, stats.cycle_length_median)
        self.assertEqual(None, stats.cycle_length_mode)
        self.assertEqual(None, stats.cycle_length_standard_deviation)
        self.assertEqual([], stats.predicted_events)

    def test_set_start_date_and_day_no_periods(self):
        stats = period_models.Statistics.objects.filter(user=self.user).first()
        min_timestamp = TIMEZONE.localize(datetime.datetime(2014, 2, 12))

        stats.set_start_date_and_day(min_timestamp)

        self.assertEqual('', stats.first_date)
        self.assertEqual('', stats.first_day)

    def test_set_start_date_and_day_previous_exists(self):
        stats = period_models.Statistics.objects.filter(user=self.period.user).first()
        min_timestamp = TIMEZONE.localize(datetime.datetime(2014, 2, 12))

        stats.set_start_date_and_day(min_timestamp)

        self.assertEqual(datetime.date(2014, 2, 12), stats.first_date)
        self.assertEqual(13, stats.first_day)

    def test_set_start_date_and_day_next_exists(self):
        stats = period_models.Statistics.objects.filter(user=self.period.user).first()
        min_timestamp = TIMEZONE.localize(datetime.datetime(2014, 1, 12))

        stats.set_start_date_and_day(min_timestamp)

        self.assertEqual(datetime.date(2014, 1, 31), stats.first_date)
        self.assertEqual(1, stats.first_day)


class TestAerisData(TestCase):
    AERIS_DATA = {'error': None, 'response': [
        {'timestamp': 1475280794, 'dateTimeISO': '2016-10-01T00:13:14+00:00', 'code': 0,
         'name': 'new moon'},
        {'timestamp': 1475987714, 'dateTimeISO': '2016-10-09T04:35:14+00:00', 'code': 1,
         'name': 'first quarter'},
        {'timestamp': 1476591907, 'dateTimeISO': '2016-10-16T04:25:07+00:00', 'code': 2,
         'name': 'full moon'},
        {'timestamp': 1477163774, 'dateTimeISO': '2016-10-22T19:16:14+00:00', 'code': 3,
         'name': 'last quarter'},
        {'timestamp': 1477849193, 'dateTimeISO': '2016-10-30T17:39:53+00:00', 'code': 0,
         'name': 'new moon'}], 'success': True}

    def setUp(self):
        self.from_date = datetime.datetime(2016, 9, 25).strftime(settings.API_DATE_FORMAT)

    @patch('requests.get')
    def test_get_from_server(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: self.AERIS_DATA)

        result = period_models.AerisData.get_from_server(self.from_date)

        self.assertEqual(self.AERIS_DATA, result)

    @patch('requests.get')
    def test_get_from_server_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError()

        result = period_models.AerisData.get_from_server(self.from_date)

        self.assertEqual({'error': 'Unable to reach Moon Phase API'}, result)

    @patch('requests.get')
    def test_get_for_date_not_cached_request_failure(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: {})
        to_date = datetime.datetime(2016, 11, 6)
        num_previous = period_models.AerisData.objects.count()

        result = period_models.AerisData.get_for_date(self.from_date, to_date)

        self.assertEqual({}, result)
        num_current = period_models.AerisData.objects.count()
        self.assertEqual(num_previous, num_current)

    @patch('requests.get')
    def test_get_for_date_not_cached_request_success(self, mock_get):
        mock_get.return_value = MagicMock(json=lambda: self.AERIS_DATA)
        to_date = datetime.datetime(2016, 11, 6)
        num_previous = period_models.AerisData.objects.count()

        result = period_models.AerisData.get_for_date(self.from_date, to_date)

        self.assertEqual(self.AERIS_DATA, result)
        num_current = period_models.AerisData.objects.count()
        self.assertEqual(num_previous + 1, num_current)

    @patch('requests.get')
    def test_get_for_date_cached(self, mock_get):
        from_date = datetime.datetime(2016, 9, 25)
        to_date = datetime.datetime(2016, 11, 6)
        period_models.AerisData.objects.create(to_date=to_date, data=self.AERIS_DATA)
        num_previous = period_models.AerisData.objects.count()

        result = period_models.AerisData.get_for_date(from_date, to_date)

        self.assertEqual(self.AERIS_DATA, result)
        num_current = period_models.AerisData.objects.count()
        self.assertEqual(num_previous, num_current)
        self.assertEqual(0, mock_get.call_count)


class TestSignals(TestCase):
    maxDiff = None

    def setUp(self):
        self.user = UserFactory()
        self.period = FlowEventFactory()

    def test_add_to_permissions_group_group_does_not_exist(self):
        self.user.groups.all().delete()

        period_models.add_to_permissions_group(period_models.User, self.user)

        groups = self.user.groups.all()
        self.assertEqual(1, groups.count())
        self.assertEqual(3, groups.first().permissions.count())
        for permission in groups.first().permissions.all():
            self.assertEqual('_flowevent', permission.codename[-10:])

    def test_add_to_permissions_group_group_exists(self):
        user = period_models.User(email='jane@jane.com',
                                  last_login=TIMEZONE.localize(datetime.datetime(2015, 2, 27)))
        user.save()
        user.groups.all().delete()
        auth_models.Group(name='users').save()

        period_models.add_to_permissions_group(period_models.User, user)

        groups = user.groups.all()
        self.assertEqual(1, groups.count())
        self.assertEqual(0, groups.first().permissions.count())

    @patch('periods.models.Statistics.save')
    def test_update_statistics_deleted_user(self, mock_save):
        self.period.user.delete()
        pre_update_call_count = mock_save.call_count

        period_models.update_statistics(period_models.FlowEvent, self.period)

        self.assertEqual(pre_update_call_count, mock_save.call_count)

    @patch('periods.models.today')
    def test_update_statistics_none_existing(self, mock_today):
        mock_today.return_value = pytz.utc.localize(datetime.datetime(2014, 4, 5))
        period = FlowEventFactory(user=self.period.user,
                                  timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 27)))

        period_models.update_statistics(period_models.FlowEvent, period)

        stats = period_models.Statistics.objects.get(user=self.period.user)
        self.assertEqual(27, stats.average_cycle_length)
        self.assertEqual(27, stats.all_time_average_cycle_length)
        self.assertEqual(37, stats.current_cycle_length)
        expected_events = [{'timestamp': datetime.date(2014, 3, 12), 'type': 'projected ovulation'},
                           {'timestamp': datetime.date(2014, 3, 26), 'type': 'projected period'},
                           {'timestamp': datetime.date(2014, 4, 8), 'type': 'projected ovulation'},
                           {'timestamp': datetime.date(2014, 4, 22), 'type': 'projected period'},
                           {'timestamp': datetime.date(2014, 5, 5), 'type': 'projected ovulation'},
                           {'timestamp': datetime.date(2014, 5, 19), 'type': 'projected period'}]
        self.assertEqual(expected_events, stats.predicted_events)

    @patch('periods.models.today')
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
        self.assertEqual(14, stats.all_time_average_cycle_length)
        self.assertEqual(22, stats.current_cycle_length)
        expected_events = [{'timestamp': datetime.date(2014, 3, 14), 'type': 'projected ovulation'},
                           {'timestamp': datetime.date(2014, 3, 28), 'type': 'projected period'},
                           {'timestamp': datetime.date(2014, 3, 28), 'type': 'projected ovulation'},
                           {'timestamp': datetime.date(2014, 4, 11), 'type': 'projected period'},
                           {'timestamp': datetime.date(2014, 4, 11), 'type': 'projected ovulation'},
                           {'timestamp': datetime.date(2014, 4, 25), 'type': 'projected period'}]
        self.assertEqual(expected_events, stats.predicted_events)
