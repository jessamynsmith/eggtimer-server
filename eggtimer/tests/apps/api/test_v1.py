import datetime
from django.contrib.auth import models as auth_models
from django.http import HttpRequest
from django.test import TestCase
from mock import patch

from eggtimer.apps.periods import models as period_models
from eggtimer.apps.api import v1


class TestPeriodDetailResource(TestCase):

    def setUp(self):
        self.user = auth_models.User.objects.create_user(
            username='jessamyn', password='bogus', email='jessamyn@example.com',
            first_name=u'Jessamyn')
        period_models.Period(userprofile=self.user.userprofile,
                             start_date=datetime.date(2014, 1, 31)).save()
        period_models.Period(userprofile=self.user.userprofile,
                             start_date=datetime.date(2014, 2, 28)).save()
        self.resource = v1.PeriodDetailResource()
        self.request = HttpRequest()
        self.request.user = self.user

    @patch('eggtimer.apps.periods.models._today')
    def test_create_response_no_data(self, mock_today):
        mock_today.return_value = datetime.date(2014, 3, 14)
        data = {'objects': []}
        period_models.Period.objects.all().delete()

        response = self.resource.create_response(self.request, data)

        self.assertEqual('application/json', response['Content-Type'])
        self.assertEqual(0, len(data['objects']))

    @patch('eggtimer.apps.periods.models._today')
    def test_create_response(self, mock_today):
        mock_today.return_value = datetime.date(2014, 3, 14)
        data = {'objects': []}

        response = self.resource.create_response(self.request, data)

        self.assertEqual('application/json', response['Content-Type'])
        # TODO assert on response content
        self.assertEqual(7, len(data['objects']))
        data_0 = {"start_date": datetime.date(2014, 3, 14), "text": "Day: 15", "type": "day count"}
        self.assertEqual(data_0, data['objects'][0].data)
        data_1 = {"start_date": datetime.date(2014, 5, 9), "type": "projected ovulation"}
        self.assertEqual(data_1, data['objects'][6].data)
