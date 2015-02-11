import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from mock import ANY, patch

from periods import models as period_models
from periods.management.commands import notify_upcoming_period


class TestModels(TestCase):

    def setUp(self):
        self.command = notify_upcoming_period.Command()
        self.user = get_user_model().objects.create_user(
            password='bogus', email='jessamyn@example.com', first_name=u'Jessamyn')
        period_models.Period(user=self.user, start_date=datetime.date(2014, 1, 31)).save()
        period_models.Period(user=self.user, start_date=datetime.date(2014, 2, 28)).save()

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_notify_upcoming_period_no_periods(self, mock_send):
        period_models.Period.objects.all().delete()

        self.command.handle()

        self.assertFalse(mock_send.called)

    @patch('periods.email_sender.send')
    @patch('periods.models._today')
    def test_notify_upcoming_period_ovulation(self, mock_today, mock_send):
        mock_today.return_value = datetime.date(2014, 3, 14)

        self.command.handle()

        mock_send.assert_called_once_with(self.user, 'Ovulation today!', ANY, None)

    @patch('periods.email_sender.send')
    @patch('periods.models._today')
    def test_notify_upcoming_period_expected_soon(self, mock_today, mock_send):
        mock_today.return_value = datetime.date(2014, 3, 25)

        self.command.handle()

        mock_send.assert_called_once_with(self.user, 'Period expected in 3 days',
                                          ANY, None)

    @patch('periods.email_sender.send')
    @patch('periods.models._today')
    def test_notify_upcoming_period_expected_today(self, mock_today, mock_send):
        mock_today.return_value = datetime.date(2014, 3, 28)

        self.command.handle()

        mock_send.assert_called_once_with(self.user, 'Period today!', ANY, None)

    @patch('periods.email_sender.send')
    @patch('periods.models._today')
    def test_notify_upcoming_period_overdue(self, mock_today, mock_send):
        mock_today.return_value = datetime.date(2014, 3, 31)

        self.command.handle()

        mock_send.assert_called_once_with(self.user, 'Period was expected 3 days ago',
                                          ANY, None)
