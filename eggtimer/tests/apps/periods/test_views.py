import datetime
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase

from eggtimer.apps.periods import models as period_models
from eggtimer.apps.periods import views


class TestViews(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            password='bogus', email='jessamyn@example.com', first_name=u'Jessamyn')
        period_models.Period(user=self.user, start_date=datetime.date(2014, 1, 31)).save()
        period_models.Period(user=self.user, start_date=datetime.date(2014, 2, 28)).save()
        self.request = HttpRequest()
        self.request.user = self.user

    def test_calendar(self):
        response = views.calendar(self.request)

        self.assertContains(response, 'initializeCalendar(')
        self.assertContains(response, 'div id=\'calendar\'></div>')

    def test_statistics_no_data(self):
        period_models.Period.objects.all().delete()

        response = views.statistics(self.request)

        self.assertContains(response, 'Not enough cycle information has been entered to calculate')

    def test_statistics(self):
        response = views.statistics(self.request)

        self.assertContains(response, '<th>Average Cycle Length:</th><td>28</td>')
        self.assertContains(response, 'cycle_length_frequency([28, 29], [28]);')
        self.assertContains(response, 'cycle_length_history(')
