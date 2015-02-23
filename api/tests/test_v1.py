import datetime
import json
import pytz

from django.http import HttpRequest, QueryDict
from django.test import TestCase
from mock import patch
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest

from periods import models as period_models
from periods.tests.factories import FlowEventFactory
from api import v1


TIMEZONE = pytz.timezone("US/Eastern")


class TestPeriodResource(TestCase):

    def setUp(self):
        self.period1 = FlowEventFactory()
        FlowEventFactory()
        self.resource = v1.PeriodResource()
        self.request = HttpRequest()
        self.request.user = self.period1.user

    def test_get_object_list(self):
        result = self.resource.get_object_list(self.request)

        self.assertEqual(1, len(result))
        self.assertEqual(self.period1, result[0])

    def test_obj_create(self):
        bundle = Bundle(request=self.request)
        bundle.data = {'timestamp': '2015-02-17T00:00:00.000Z'}
        bundle.obj = FlowEventFactory()

        result = self.resource.obj_create(bundle, request=self.request)

        self.assertEqual(1, len(result.objects_saved))
        period = period_models.FlowEvent.objects.get(id=result.obj.id)
        self.assertEqual(self.request.user, period.user)
        self.assertEqual(bundle.obj.timestamp, period.timestamp)


class TestPeriodDetailResource(TestCase):

    def setUp(self):
        period1 = FlowEventFactory()
        FlowEventFactory(
            user=period1.user, timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 12)))
        self.resource = v1.PeriodDetailResource()
        self.request = HttpRequest()
        self.request.user = period1.user
        self.request.GET = QueryDict('timestamp__gte=2014-02-01&timestamp__lte=2014-02-28')
        self.data = {'objects': []}

    def test_create_response_no_range_specified(self):
        self.request.GET = QueryDict('')

        try:
            self.resource.create_response(self.request, self.data)
            self.fail("Should error out if no date range specified")
        except BadRequest as e:
            error = 'Must specify date range, e.g. timestamp__gte=<date>&timestamp__lte=<date>'
            self.assertEqual(error, str(e))

    @patch('periods.models._today')
    def test_create_response_no_data(self, mock_today):
        mock_today.return_value = datetime.date(2014, 2, 14)
        period_models.FlowEvent.objects.all().delete()

        response = self.resource.create_response(self.request, self.data)

        self.assertEqual('application/json', response['Content-Type'])
        content = json.loads(response.content.decode('ascii'))
        self.assertEqual('', content['first_day'])
        self.assertEqual('', content['first_date'])
        self.assertEqual(0, len(content['objects']))

    @patch('periods.models._today')
    def test_create_response_day_1(self, mock_today):
        cutoff_date = TIMEZONE.localize(datetime.datetime(2014, 1, 31))
        mock_today.return_value = cutoff_date
        period_models.FlowEvent.objects.filter(timestamp__lte=cutoff_date).delete()

        response = self.resource.create_response(self.request, self.data)

        self.assertEqual('application/json', response['Content-Type'])
        content = json.loads(response.content.decode('ascii'))

        self.assertEqual(1, content['first_day'])
        self.assertEqual('2014-02-12', content['first_date'])
        self.assertEqual(6, len(content['objects']))
        data_0 = {'timestamp': '2014-03-12', 'type': 'projected period'}
        self.assertEqual(data_0, content['objects'][0])
        data_3 = {'timestamp': '2014-02-26', 'type': 'projected ovulation'}
        self.assertEqual(data_3, content['objects'][3])

    @patch('periods.models._today')
    def test_create_response(self, mock_today):
        mock_today.return_value = TIMEZONE.localize(datetime.datetime(2014, 2, 14))

        response = self.resource.create_response(self.request, self.data)

        self.assertEqual('application/json', response['Content-Type'])
        content = json.loads(response.content.decode('ascii'))
        self.assertEqual(6, len(content['objects']))

        self.assertEqual(2, content['first_day'])
        self.assertEqual('2014-02-01', content['first_date'])
        data_0 = {'timestamp': '2014-03-12', 'type': 'projected period'}
        self.assertEqual(data_0, content['objects'][0])
        data_3 = {'timestamp': '2014-02-26', 'type': 'projected ovulation'}
        self.assertEqual(data_3, content['objects'][3])
