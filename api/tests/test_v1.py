import datetime
import json

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from mock import patch

from periods import models as period_models
from api import v1


class TestPeriodDetailResource(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            password='bogus', email='jessamyn@example.com', first_name=u'Jessamyn')
        period_models.Period(user=self.user, start_date=datetime.date(2014, 1, 31)).save()
        period_models.Period(user=self.user, start_date=datetime.date(2014, 2, 28)).save()
        self.resource = v1.PeriodDetailResource()
        self.request = HttpRequest()
        self.request.user = self.user

    @patch('periods.models._today')
    def test_create_response_no_data(self, mock_today):
        mock_today.return_value = datetime.date(2014, 3, 14)
        data = {'objects': []}
        period_models.Period.objects.all().delete()

        response = self.resource.create_response(self.request, data)

        self.assertEqual('application/json', response['Content-Type'])
        content = json.loads(response.content.decode('ascii'))
        self.assertEqual(0, len(content['objects']))

    @patch('periods.models._today')
    def test_create_response(self, mock_today):
        mock_today.return_value = datetime.date(2014, 3, 14)
        data = {'objects': []}

        response = self.resource.create_response(self.request, data)

        self.assertEqual('application/json', response['Content-Type'])
        content = json.loads(response.content.decode('ascii'))
        self.assertEqual(7, len(content['objects']))
        data_0 = {"start_date": '2014-03-14', "text": "Day: 15", "type": "day count"}
        self.assertEqual(data_0, content['objects'][0])
        data_1 = {"start_date": '2014-05-09', "type": "projected ovulation"}
        self.assertEqual(data_1, content['objects'][6])
