import datetime
import pytz

from django.test import TestCase
from mock import patch

from periods import models as period_models
from periods.management.commands import email_active_users
from periods.tests.factories import FlowEventFactory

TIMEZONE = pytz.timezone("US/Eastern")


class TestCommand(TestCase):
    def setUp(self):
        self.command = email_active_users.Command()
        flow_event = FlowEventFactory()
        self.user = flow_event.user
        FlowEventFactory(user=self.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 28)))

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_email_active_users_no_periods(self, mock_send):
        period_models.FlowEvent.objects.all().delete()

        self.command.handle()

        self.assertFalse(mock_send.called)

    @patch('django.core.mail.EmailMultiAlternatives.send')
    @patch('periods.models.today')
    def test_email_active_users_send_disabled(self, mocktoday, mock_send):
        mocktoday.return_value = TIMEZONE.localize(datetime.datetime(2014, 3, 14))
        self.user.send_emails = False
        self.user.save()

        self.command.handle()

        self.assertFalse(mock_send.called)

    @patch('periods.email_sender.send')
    @patch('periods.models.today')
    def test_email_active_users(self, mocktoday, mock_send):
        mocktoday.return_value = TIMEZONE.localize(datetime.datetime(2014, 3, 15))

        self.command.handle()

        email_text = ('Hello ,\n\nThis is an important notification about the data in your '
                      'eggtimer account.\n\nUntil now, eggtimer has been storing all data in '
                      'Eastern time. As you may already be aware,\nthis creates issues for users '
                      'in other timezones. I am going to update the application so all\ndata is '
                      'stored in UTC. This may affect your data!\n\nIf you are in Eastern time, '
                      'your data will be migrated correctly, and you need do nothing.\n\nIf you '
                      'have been using eggtimer from another timezone, you have two options:\n1) '
                      'Before July 14, edit your user profile to select your timezone. When the '
                      'data migration is\nperformed, I will use the timezone on your profile.\n2) '
                      'Do nothing, and your data will be migrated '
                      'as if it is in Eastern time. This will likely\nresult in a time shift when '
                      'you view your events. If desired, you can then edit events yourself.\n\nI '
                      'apologize for the inconvenience.\n\nSincerely,\n\n')
        mock_send.assert_called_once_with(self.user, 'Important information about the data in your '
                                                     'eggtimer account', email_text, None)
