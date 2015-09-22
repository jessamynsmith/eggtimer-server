import datetime
import json
import pytz

from django.http import HttpRequest, QueryDict, Http404
from django.test import Client, TestCase
from mock import patch
from rest_framework.request import Request
from rest_framework.authtoken.models import Token

from periods import models as period_models, views
from periods.serializers import FlowEventSerializer
from periods.tests.factories import FlowEventFactory, UserFactory


class TestFlowEventViewSet(TestCase):

    def setUp(self):
        self.view_set = views.FlowEventViewSet()
        self.view_set.format_kwarg = ''

        self.period = FlowEventFactory()
        FlowEventFactory(timestamp=pytz.utc.localize(datetime.datetime(2014, 2, 28)))

        self.request = Request(HttpRequest())
        self.request.__setattr__('user', self.period.user)
        self.view_set.request = self.request

    def test_list(self):
        response = self.view_set.list(self.request)

        self.assertEqual(1, len(response.data))
        self.assertEqual(self.period.id, response.data[0]['id'])

    def test_perform_create(self):
        serializer = FlowEventSerializer(data={'timestamp': datetime.datetime(2015, 1, 1)})
        serializer.is_valid()

        self.view_set.perform_create(serializer)

        self.assertEqual(self.request.user, serializer.instance.user)


class TestStatisticsViewSet(TestCase):

    def setUp(self):
        self.view_set = views.StatisticsViewSet()
        self.view_set.format_kwarg = ''

        self.period = FlowEventFactory()
        self.period2 = FlowEventFactory(timestamp=pytz.utc.localize(datetime.datetime(2014, 2, 28)))

        self.request = Request(HttpRequest())
        self.request.__setattr__('user', self.period.user)
        self.view_set.request = self.request

    def test_retrieve_other_user(self):
        self.view_set.kwargs = {'pk': self.period2.user.statistics.pk}

        try:
            self.view_set.retrieve(self.request)
            self.fail("Should not be able to retrieve another user's statistics")
        except Http404:
            pass

    @patch('periods.models.today')
    def test_list_no_params(self, mock_today):
        mock_today.return_value = pytz.utc.localize(datetime.datetime(2014, 1, 5))
        self.view_set.kwargs = {'pk': self.request.user.statistics.pk}

        response = self.view_set.list(self.request)

        self.assertEqual(4, len(response.data))
        self.assertEqual(28, response.data['average_cycle_length'])
        self.assertEqual(self.period.timestamp.date(), response.data['first_date'])
        self.assertEqual(1, response.data['first_day'])

    def test_list_with_min_timestamp(self):
        http_request = HttpRequest()
        http_request.GET = QueryDict(u'min_timestamp=2014-01-05')
        request = Request(http_request)
        request.__setattr__('user', self.period.user)
        self.view_set.kwargs = {'pk': self.request.user.statistics.pk}

        response = self.view_set.list(request)

        self.assertEqual(4, len(response.data))
        self.assertEqual(28, response.data['average_cycle_length'])
        self.assertEqual(self.period.timestamp.date(), response.data['first_date'])
        self.assertEqual(1, response.data['first_day'])


class TestApiAuthenticate(TestCase):

    def setUp(self):
        self.client = Client()
        self.url_path = '/api/v2/authenticate/'
        self.data = {"email": "jane@jane.com", "password": "somepass"}

    def test_api_authenticate_get(self):
        response = self.client.get(self.url_path)

        self.assertEqual(405, response.status_code)

    def test_api_authenticate_not_json(self):
        response = self.client.post(self.url_path, data='', content_type='application/json')

        self.assertEqual(400, response.status_code)
        self.assertEqual(b'{"error": "Could not parse body as JSON"}', response.content)

    def test_api_authenticate_missing_fields(self):
        response = self.client.post(self.url_path, data=json.dumps({}),
                                    content_type='application/json')

        self.assertEqual(400, response.status_code)
        self.assertEqual(b'{"error": "Missing required field \'email\'"}', response.content)

    def test_api_authenticate_failure(self):
        response = self.client.post(self.url_path, data=json.dumps(self.data),
                                    content_type='application/json')

        self.assertEqual(401, response.status_code)
        self.assertEqual(b'{"error": "Invalid credentials"}', response.content)

    @patch('django.contrib.auth.authenticate')
    def test_api_authenticate_success(self, mock_authenticate):
        user = UserFactory()
        mock_authenticate.return_value = user

        response = self.client.post(self.url_path, data=json.dumps(self.data),
                                    content_type='application/json')

        self.assertContains(response, user.auth_token.key)


class TestViews(TestCase):
    maxDiff = None

    def setUp(self):
        self.period = FlowEventFactory()
        FlowEventFactory(user=self.period.user,
                         timestamp=pytz.utc.localize(datetime.datetime(2014, 2, 28)))
        self.request = HttpRequest()
        self.request.user = self.period.user
        self.request.META['SERVER_NAME'] = 'localhost'
        self.request.META['SERVER_PORT'] = '8000'

    @patch('periods.models.today')
    def test_period_form_no_parameters(self, mock_today):
        mock_today.return_value = pytz.utc.localize(datetime.datetime(2015, 7, 7))

        response = views.period_form(self.request, mock_today)

        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, '<input type="datetime" name="timestamp" '
                                      'value="2015-07-06 20:00:00" required')
        self.assertContains(response, 'first_day" checked')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    def test_period_form_with_timestamp(self):
        self.request.GET = QueryDict('timestamp=2015-02-25T00:00:00%2B00:00')

        response = views.period_form(self.request)

        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, '<input type="datetime" name="timestamp" '
                                      'value="2015-02-25 00:00:00" required')
        self.assertContains(response, 'first_day" checked')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    @patch('periods.models.today')
    def test_period_form_invalid_period_id(self, mock_today):
        mock_today.return_value = pytz.utc.localize(datetime.datetime(2015, 7, 7))

        response = views.period_form(self.request, 9999)

        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, '<input type="datetime" name="timestamp" '
                                      'value="2015-07-06 20:00:00" required')
        self.assertContains(response, 'first_day" checked')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    def test_period_form_existing_period(self):
        response = views.period_form(self.request, self.period.id)

        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, '<input type="datetime" name="timestamp" '
                                      'value="2014-01-31 12:00:00" required ')
        self.assertContains(response, 'first_day" checked')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    def test_calendar(self):
        response = views.calendar(self.request)

        self.assertContains(response, 'initializeCalendar(')
        self.assertContains(response, 'div id=\'id_calendar\'></div>')

    def test_cycle_length_frequency_no_data(self):
        period_models.FlowEvent.objects.all().delete()

        response = views.cycle_length_frequency(self.request)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual({}, result)

    def test_cycle_length_frequency(self):
        response = views.cycle_length_frequency(self.request)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual({'cycles': [[28, 1]]}, result)

    def test_cycle_length_history_no_data(self):
        period_models.FlowEvent.objects.all().delete()

        response = views.cycle_length_history(self.request)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual({}, result)

    def test_cycle_length_history(self):
        response = views.cycle_length_history(self.request)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual({'cycles': [['2014-01-31', 28]]}, result)

    def test_qigong_cycles_no_birth_date(self):
        self.request.user.birth_date = None
        self.request.user.save()

        response = views.qigong_cycles(self.request)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual({}, result)

    @patch('periods.models.today')
    def test_qigong_cycles(self, mock_today):
        mock_today.return_value = pytz.utc.localize(datetime.datetime(1995, 3, 20))

        response = views.qigong_cycles(self.request)

        result = json.loads(response.content.decode('utf-8'))

        expected = {
            'physical': [['1995-03-01T00:00:00Z', 0],
                         ['1995-03-12T12:00:00Z', 100],
                         ['1995-03-20T00:00:00Z', 27],
                         ['1995-03-24T00:00:00Z', 0],
                         ['1995-04-03T00:00:00Z', 96]],
            'emotional': [['1995-03-01T00:00:00Z', 0],
                          ['1995-03-15T00:00:00Z', 100],
                          ['1995-03-20T00:00:00Z', 72],
                          ['1995-03-29T00:00:00Z', 0],
                          ['1995-04-03T00:00:00Z', 28]],
            'intellectual': [['1995-03-01T00:00:00Z', 0],
                             ['1995-03-17T12:00:00Z', 100],
                             ['1995-03-20T00:00:00Z', 94],
                             ['1995-04-03T00:00:00Z', 0]],
        }
        self.assertEqual(expected, result)

    def test_statistics_no_data(self):
        period_models.FlowEvent.objects.all().delete()

        response = views.statistics(self.request)

        self.assertContains(response, '<td>Average (Last 6 Months):</td>\n        <td>28</td>')
        self.assertContains(response, '<td>Average (All Time):</td>\n        <td>28</td>')
        self.assertContains(response, '<td>Mean:</td>\n        <td></td>')

    def test_statistics(self):
        response = views.statistics(self.request)

        self.assertContains(response, '<td>Average (Last 6 Months):</td>\n        <td>28</td>')
        self.assertContains(response, '<td>Average (All Time):</td>\n        <td>28</td>')
        self.assertContains(response, '<td>Mean:</td>\n        <td>28.0</td>')
        self.assertContains(response, '<td>Mode:</td>\n        <td>28</td>')

    def test_profile_post_invalid_data(self):
        self.request.method = 'POST'
        self.request.POST = QueryDict(u'birth_date=blah')

        response = views.profile(self.request)

        user = period_models.User.objects.get(pk=self.request.user.pk)
        self.assertEqual(pytz.utc.localize(datetime.datetime(1995, 3, 1)), user.birth_date)
        self.assertContains(response, '<h4>Account Info for %s</h4>' % self.request.user.email)

    def test_profile_post_valid_data(self):
        self.request.method = 'POST'
        self.request.POST = QueryDict(u'first_name=Jess&luteal_phase_length=12&'
                                      u'timezone=America/New_York')

        response = views.profile(self.request)

        user = period_models.User.objects.get(pk=self.request.user.pk)
        self.assertEqual(u'Jess', user.first_name)
        self.assertEqual(12, user.luteal_phase_length)
        self.assertContains(response, '<h4>Account Info for Jess</h4>')

    def test_profile_get(self):
        response = views.profile(self.request)

        self.assertContains(response, '<h4>Account Info for Jessamyn</h4>')

    def test_api_info(self):
        response = views.api_info(self.request)

        self.assertContains(response, '<h4>API Info for Jessamyn</h4>')

    def test_regenerate_key_post(self):
        self.request.method = 'POST'
        api_key = Token.objects.get(user=self.request.user).key

        response = views.regenerate_key(self.request)

        self.assertContains(response, '', status_code=302)
        self.assertNotEquals(api_key, self.request.user.auth_token.key)

    def test_regenerate_key_get(self):
        api_key = Token.objects.get(user=self.request.user).key

        response = views.regenerate_key(self.request)

        self.assertContains(response, '', status_code=302)
        self.assertEquals(api_key, self.request.user.auth_token.key)
