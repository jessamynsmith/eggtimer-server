import datetime
import json

from django.contrib.auth import get_user_model
from django.http import HttpRequest, QueryDict
from django.test import TestCase
from mock import patch
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest

from periods import models as period_models
from api import v1


class TestPeriodResource(TestCase):

    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            password='bogus', email='jessamyn@example.com', first_name=u'Jessamyn')
        self.period1 = period_models.Period(user=self.user1, start_date=datetime.date(2014, 1, 15))
        self.period1.save()
        user2 = get_user_model().objects.create_user(
            password='bogus', email='colleen@example.com', first_name=u'Colleen')
        period_models.Period(user=user2, start_date=datetime.date(2014, 1, 17)).save()
        self.resource = v1.PeriodResource()
        self.request = HttpRequest()
        self.request.user = self.user1

    def test_get_object_list(self):
        result = self.resource.get_object_list(self.request)

        self.assertEqual(1, len(result))
        self.assertEqual(self.period1, result[0])

    def test_obj_create(self):
        bundle = Bundle(request=self.request)
        bundle.data = {'start_date': '2015-02-17T00:00:00.000Z'}
        bundle.obj = period_models.Period(start_date=datetime.date(2015, 2, 17))

        result = self.resource.obj_create(bundle, request=self.request)

        self.assertEqual(1, len(result.objects_saved))
        period = period_models.Period.objects.get(id=result.obj.id)
        self.assertEqual(self.request.user, period.user)
        self.assertEqual(bundle.obj.start_date, period.start_date)


class TestPeriodDetailResource(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            password='bogus', email='jessamyn@example.com', first_name=u'Jessamyn')
        period_models.Period(user=self.user, start_date=datetime.date(2014, 1, 15)).save()
        period_models.Period(user=self.user, start_date=datetime.date(2014, 2, 12)).save()
        self.resource = v1.PeriodDetailResource()
        self.request = HttpRequest()
        self.request.user = self.user
        self.request.GET = QueryDict('start_date__gte=2014-02-01&start_date__lte=2014-02-28')
        self.data = {'objects': []}

    def test_create_response_no_range_specified(self):
        self.request.GET = QueryDict('')

        try:
            self.resource.create_response(self.request, self.data)
            self.fail("Should error out if no date range specified")
        except BadRequest as e:
            error = 'Must specify date range, e.g. start_date__gte=<date>&start_date__lte=<date>'
            self.assertEqual(error, str(e))

    @patch('periods.models._today')
    def test_create_response_no_data(self, mock_today):
        mock_today.return_value = datetime.date(2014, 2, 14)
        period_models.Period.objects.all().delete()

        response = self.resource.create_response(self.request, self.data)

        self.assertEqual('application/json', response['Content-Type'])
        content = json.loads(response.content.decode('ascii'))
        self.assertEqual(0, len(content['objects']))

    @patch('periods.models._today')
    def test_create_response_day_1(self, mock_today):
        mock_today.return_value = datetime.date(2014, 2, 12)
        period_models.Period.objects.filter(start_date__lte=datetime.date(2014, 2, 1)).delete()

        response = self.resource.create_response(self.request, self.data)

        self.assertEqual('application/json', response['Content-Type'])
        content = json.loads(response.content.decode('ascii'))
        self.assertEqual(23, len(content['objects']))

        data_0 = {'start_date': '2014-03-12', 'type': 'projected period'}
        self.assertEqual(data_0, content['objects'][0])
        data_3 = {'start_date': '2014-02-26', 'type': 'projected ovulation'}
        self.assertEqual(data_3, content['objects'][3])
        data_6 = {'text': 'Day: 1', 'start_date': '2014-02-12', 'type': 'day count'}
        self.assertEqual(data_6, content['objects'][6])
        data_22 = {'text': 'Day: 17', 'start_date': '2014-02-28', 'type': 'day count'}
        self.assertEqual(data_22, content['objects'][22])

    @patch('periods.models._today')
    def test_create_response(self, mock_today):
        mock_today.return_value = datetime.date(2014, 2, 14)

        response = self.resource.create_response(self.request, self.data)

        self.assertEqual('application/json', response['Content-Type'])
        content = json.loads(response.content.decode('ascii'))
        self.assertEqual(34, len(content['objects']))

        data_0 = {'start_date': '2014-03-12', 'type': 'projected period'}
        self.assertEqual(data_0, content['objects'][0])
        data_3 = {'start_date': '2014-02-26', 'type': 'projected ovulation'}
        self.assertEqual(data_3, content['objects'][3])
        data_6 = {'text': 'Day: 17', 'start_date': '2014-02-01', 'type': 'day count'}
        self.assertEqual(data_6, content['objects'][6])
        data_17 = {'text': 'Day: 1', 'start_date': '2014-02-12', 'type': 'day count'}
        self.assertEqual(data_17, content['objects'][17])
        data_33 = {'text': 'Day: 17', 'start_date': '2014-02-28', 'type': 'day count'}
        self.assertEqual(data_33, content['objects'][33])
