import datetime
import json
import pytz

from django.core.urlresolvers import reverse
from django.http import HttpRequest, QueryDict, Http404
from django.test import Client, TestCase
from mock import patch
from rest_framework.request import Request
from rest_framework.authtoken.models import Token

from periods import models as period_models, views
from periods.serializers import FlowEventSerializer
from periods.tests.factories import FlowEventFactory, UserFactory, PASSWORD


class LoggedInUserTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.login(email=self.user.email, password=PASSWORD)


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


class TestAerisView(LoggedInUserTestCase):
    maxDiff = None

    def setUp(self):
        super(TestAerisView, self).setUp()
        self.url_path = reverse('aeris')

    @patch('periods.models.AerisData.get_for_date')
    def test_get_no_data(self, mock_get_for_date):
        mock_get_for_date.return_value = {}

        response = self.client.get(self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.json())

    @patch('periods.models.AerisData.get_for_date')
    def test_get_with_data(self, mock_get_for_date):
        data = {'success': 'true'}
        mock_get_for_date.return_value = data
        to_date = datetime.date(2014, 2, 28)

        response = self.client.get(self.url_path, {'to_date': to_date})

        self.assertEqual(200, response.status_code)
        self.assertEqual(data, response.json())
        self.assertTrue(mock_get_for_date.called_once_with(None, to_date))


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


class TestFlowEventViews(LoggedInUserTestCase):
    maxDiff = None

    def setUp(self):
        super(TestFlowEventViews, self).setUp()
        self.url_path = reverse('flow_event_create')
        self.period = FlowEventFactory(user=self.user)

    @patch('periods.models.today')
    def test_create_no_parameters(self, mock_today):
        mock_today.return_value = pytz.utc.localize(datetime.datetime(2014, 2, 3))

        response = self.client.get(self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, '<input type="datetime" name="timestamp" '
                                      'value="2014-02-02 19:00:00" required')
        self.assertContains(response, 'first_day" checked')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    @patch('periods.models.today')
    def test_create_not_first_day(self, mock_today):
        mock_today.return_value = pytz.utc.localize(datetime.datetime(2014, 2, 1))

        response = self.client.get(self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, 'value="2014-01-31 19:00:00"')
        self.assertContains(response, '<input type="checkbox" name="first_day" id="id_first_day"')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    def test_create_with_timestamp(self):
        params = {'timestamp': '2015-02-25T00:00:00+00:00'}

        response = self.client.get(self.url_path, params)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, 'value="2015-02-24 19:00:00"')
        self.assertContains(response, 'first_day" checked')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    def test_update_invalid_period_id(self):
        response = self.client.get('%s9999/' % self.url_path)

        self.assertEqual(404, response.status_code)

    def test_update(self):
        response = self.client.get('%s%s/' % (self.url_path, self.period.id))

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, '<input type="datetime" name="timestamp" '
                                      'value="2014-01-31 12:00:00" required ')
        self.assertContains(response, 'first_day" checked')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')


class TestFlowEventFormSetView(LoggedInUserTestCase):
    def setUp(self):
        super(TestFlowEventFormSetView, self).setUp()
        self.url_path = reverse('flow_events')

    def test_get(self):
        response = self.client.get(self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '*Note: all times in UTC')
        self.assertContains(response, 'name="form-INITIAL_FORMS" type="hidden" value="0"')


class TestCalendarView(LoggedInUserTestCase):
    def setUp(self):
        super(TestCalendarView, self).setUp()
        self.url_path = reverse('calendar')

    def test_get(self):
        response = self.client.get(self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'initializeCalendar(')
        self.assertContains(response, 'div id=\'id_calendar\'></div>')


class TestStatisticsViewsNoData(LoggedInUserTestCase):
    def setUp(self):
        super(TestStatisticsViewsNoData, self).setUp()
        self.url_path = reverse('statistics')

    def test_cycle_length_frequency(self):
        response = self.client.get('%scycle_length_frequency/' % self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertEqual({'cycles': []}, response.json())

    def test_cycle_length_history(self):
        response = self.client.get('%scycle_length_history/' % self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertEqual({'cycles': []}, response.json())

    def test_qigong_cycles(self):
        self.user.birth_date = None
        self.user.save()

        response = self.client.get('%sqigong_cycles/' % self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertEqual({}, response.json())

    def test_statistics(self):
        response = self.client.get(self.url_path)

        self.assertContains(response, '<td>Average (Last 6 Months):</td>\n        <td>28</td>')
        self.assertContains(response, '<td>Average (All Time):</td>\n        <td>28</td>')
        self.assertContains(response, '<td>Mean:</td>\n        <td></td>')


class TestStatisticsViewsWithData(LoggedInUserTestCase):
    def setUp(self):
        super(TestStatisticsViewsWithData, self).setUp()
        FlowEventFactory(user=self.user)
        FlowEventFactory(user=self.user,
                         timestamp=pytz.utc.localize(datetime.datetime(2014, 2, 28)))
        FlowEventFactory(user=self.user,
                         timestamp=pytz.utc.localize(datetime.datetime(2014, 3, 26)))
        self.url_path = reverse('statistics')

    def test_cycle_length_frequency(self):
        response = self.client.get('%scycle_length_frequency/' % self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertEqual({'cycles': [[26, 1], [28, 1]]}, response.json())

    def test_cycle_length_history(self):
        response = self.client.get('%scycle_length_history/' % self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertEqual({'cycles': [['2014-01-31', 28], ['2014-02-28', 26]]}, response.json())

    @patch('periods.models.today')
    def test_qigong_cycles(self, mock_today):
        mock_today.return_value = pytz.utc.localize(datetime.datetime(1995, 3, 20))

        response = self.client.get('%sqigong_cycles/' % self.url_path)

        self.assertEqual(200, response.status_code)

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
        self.assertEqual(expected, response.json())

    def test_statistics(self):
        response = self.client.get(self.url_path)

        self.assertContains(response, '<td>Average (Last 6 Months):</td>\n        <td>27</td>')
        self.assertContains(response, '<td>Average (All Time):</td>\n        <td>27</td>')
        self.assertContains(response, '<td>Mean:</td>\n        <td>27.0</td>')
        self.assertContains(response, '<td>Standard Deviation:</td>\n        <td>1.414')


class TestProfileUpdateView(LoggedInUserTestCase):
    def setUp(self):
        super(TestProfileUpdateView, self).setUp()
        self.url_path = reverse('user_profile')

    def test_get(self):
        response = self.client.get(self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<h4>Account Info for Jessamyn</h4>')

    def test_post_invalid_data(self):
        data = {
            "birth_date": "blah",
        }

        response = self.client.post(self.url_path, data=data)

        self.assertEqual(200, response.status_code)
        user = period_models.User.objects.get(pk=self.user.pk)
        self.assertEqual(pytz.utc.localize(datetime.datetime(1995, 3, 1)), user.birth_date)
        self.assertContains(response, '<h4>Account Info for %s</h4>' % user.email)

    def test_post_valid_data(self):
        data = {
            "first_name": "Jess",
            "luteal_phase_length": "12",
            "_timezone": "America/New_York",
        }

        response = self.client.post(self.url_path, data=data, follow=True)

        self.assertEqual(200, response.status_code)
        self.assertEqual([('/accounts/profile/', 302)], response.redirect_chain)
        user = period_models.User.objects.get(pk=self.user.pk)
        self.assertEqual(u'Jess', user.first_name)
        self.assertEqual(12, user.luteal_phase_length)
        self.assertContains(response, '<h4>Account Info for Jess</h4>')


class TestApiInfoView(LoggedInUserTestCase):

    def setUp(self):
        super(TestApiInfoView, self).setUp()
        self.url_path = reverse('api_info')

    def test_get(self):
        response = self.client.get(self.url_path)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<h4>API Info for Jessamyn</h4>')


class RegenerateKeyView(LoggedInUserTestCase):

    def setUp(self):
        super(RegenerateKeyView, self).setUp()
        self.url_path = reverse('regenerate_key')

    def test_get(self):
        response = self.client.get(self.url_path)

        self.assertEqual(200, response.status_code)
        expected = {'message': 'Post to this endpoint to update your API key'}
        self.assertEqual(expected, response.json())

    def test_post(self):
        api_key = Token.objects.get(user=self.user).key

        response = self.client.post(self.url_path, follow=True)

        self.assertEqual(200, response.status_code)
        self.assertEqual([('/accounts/profile/api_info/', 302)], response.redirect_chain)
        user = period_models.User.objects.get(pk=self.user.pk)
        self.assertNotEquals(api_key, user.auth_token.key)
