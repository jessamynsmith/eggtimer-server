import datetime
import pytz

from django.test import TestCase

from periods import models as period_models
from periods.management.commands import fix_timezone_for_period_data
from periods.tests.factories import FlowEventFactory

TIMEZONE = pytz.timezone("US/Eastern")


class TestCommand(TestCase):
    def setUp(self):
        self.command = fix_timezone_for_period_data.Command()
        flow_event = FlowEventFactory(timestamp=TIMEZONE.localize(
            datetime.datetime(2014, 1, 31, 17, 0, 0)))
        self.user = flow_event.user
        FlowEventFactory(user=self.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 8, 28)))

    def test_fix_timezone_for_period_data_no_periods(self):
        period_models.FlowEvent.objects.all().delete()

        self.command.handle()

        self.assertEqual(0, period_models.FlowEvent.objects.count())

    def test_fix_timezone_for_period_data(self):
        self.command.handle()

        periods = period_models.FlowEvent.objects.all()
        self.assertEqual(2, periods.count())
        self.assertEqual(pytz.utc.localize(datetime.datetime(2014, 1, 31, 22)),
                         periods[0].timestamp)
        self.assertEqual(pytz.utc.localize(datetime.datetime(2014, 8, 28, 4)), periods[1].timestamp)
