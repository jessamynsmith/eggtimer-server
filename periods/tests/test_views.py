import datetime
import pytz

from django.http import HttpRequest, QueryDict, Http404
from django.test import TestCase
from django.utils import timezone
from mock import patch
from rest_framework.request import Request
from rest_framework.authtoken.models import Token

from periods import models as period_models, views
from periods.serializers import FlowEventSerializer
from periods.tests.factories import FlowEventFactory


TIMEZONE = pytz.timezone("US/Eastern")


class TestFlowEventViewSet(TestCase):

    def setUp(self):
        self.view_set = views.FlowEventViewSet()
        self.view_set.format_kwarg = ''

        self.period = FlowEventFactory()
        FlowEventFactory(timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 28)))

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
        self.period2 = FlowEventFactory(timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 28)))

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
    def test_retrieve_no_params(self, mocktoday):
        mocktoday.return_value = TIMEZONE.localize(datetime.datetime(2014, 1, 5))
        self.view_set.kwargs = {'pk': self.request.user.statistics.pk}

        response = self.view_set.retrieve(self.request)

        self.assertEqual(4, len(response.data))
        self.assertEqual(28, response.data['average_cycle_length'])
        self.assertEqual(self.period.timestamp.date(), response.data['first_date'])
        self.assertEqual(1, response.data['first_day'])

    def test_retrieve_with_min_timestamp(self):
        http_request = HttpRequest()
        http_request.GET = QueryDict(u'min_timestamp=2014-01-05')
        request = Request(http_request)
        self.view_set.kwargs = {'pk': self.request.user.statistics.pk}

        response = self.view_set.retrieve(request)

        self.assertEqual(4, len(response.data))
        self.assertEqual(28, response.data['average_cycle_length'])
        self.assertEqual(self.period.timestamp.date(), response.data['first_date'])
        self.assertEqual(1, response.data['first_day'])


class TestViews(TestCase):

    def setUp(self):
        self.period = FlowEventFactory()
        FlowEventFactory(user=self.period.user,
                         timestamp=TIMEZONE.localize(datetime.datetime(2014, 2, 28)))
        self.request = HttpRequest()
        self.request.user = self.period.user
        self.request.META['SERVER_NAME'] = 'localhost'
        self.request.META['SERVER_PORT'] = '8000'

    def test_period_form_no_parameters(self):
        response = views.period_form(self.request)

        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, '<input type="datetime" name="timestamp" required')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    def test_period_form_with_timestamp(self):
        self.request.GET = QueryDict('timestamp=2015-02-25T00:00:00+00:00')

        response = views.period_form(self.request)

        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, '<input type="datetime" name="timestamp" '
                                      'value="2015-02-25 00:00:00" required')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    def test_period_form_invalid_period_id(self):
        response = views.period_form(self.request, 9999)

        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, '<input type="datetime" name="timestamp" required')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    def test_period_form_existing_period(self):
        response = views.period_form(self.request, self.period.id)

        self.assertContains(response, '<form id="id_period_form">')
        self.assertContains(response, '<input type="datetime" name="timestamp" '
                                      'value="2014-01-31 00:00:00" required ')
        self.assertContains(response, '<select class=" form-control" id="id_level" name="level">')

    def test_calendar(self):
        response = views.calendar(self.request)

        self.assertContains(response, 'initializeCalendar(')
        self.assertContains(response, 'div id=\'id_calendar\'></div>')

    def test_statistics_no_data(self):
        period_models.FlowEvent.objects.all().delete()

        response = views.statistics(self.request)

        self.assertContains(response, 'Not enough cycle information has been entered to calculate')

    def test_statistics(self):
        response = views.statistics(self.request)

        self.assertContains(response, '<th>Average Cycle Length:</th><td>28</td>')
        self.assertContains(response, 'cycle_length_frequency([28, 29], [28]);')
        self.assertContains(response, 'cycle_length_history(')

    def test_profile_post_invalid_data(self):
        self.request.method = 'POST'
        self.request.POST = QueryDict(u'birth_date=blah')

        response = views.profile(self.request)

        user = period_models.User.objects.get(pk=self.request.user.pk)
        self.assertEqual(None, user.birth_date)
        self.assertContains(response, '<a href="/qigong/cycles/">Medical Qigong Cycles</a>')
        self.assertContains(response, '<h4>API Information</h4>')

    def test_profile_post_valid_data(self):
        self.request.method = 'POST'
        self.request.POST = QueryDict(u'first_name=Jess&luteal_phase_length=12')

        response = views.profile(self.request)

        user = period_models.User.objects.get(pk=self.request.user.pk)
        self.assertEqual(u'Jess', user.first_name)
        self.assertEqual(12, user.luteal_phase_length)
        self.assertContains(response, '<a href="/qigong/cycles/">Medical Qigong Cycles</a>')
        self.assertContains(response, '<h4>API Information</h4>')

    def test_profile_get(self):
        response = views.profile(self.request)

        self.assertContains(response, '<a href="/qigong/cycles/">Medical Qigong Cycles</a>')
        self.assertContains(response, '<h4>API Information</h4>')

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

    def test_qigong_cycles_no_data(self):
        response = views.qigong_cycles(self.request)

        self.assertContains(response, '<label for="id_birth_date">Birth Date')

    def test_qigong_cycles_post_invalid_data(self):
        self.request.method = "POST"
        self.request.POST = QueryDict(u"birth_date=bogus")

        response = views.qigong_cycles(self.request)

        self.assertContains(response, 'Please enter a date in the form YYYY-MM-DD, e.g. 1975-11-30')

    def test_qigong_cycles_post(self):
        self.request.method = "POST"
        self.request.POST = QueryDict(u"birth_date=1980-02-28")

        response = views.qigong_cycles(self.request)

        self.assertContains(response, '<td class="intellectual">Intellectual</td>')
        self.assertContains(response, 'qigong_cycles(["')
        user = period_models.User.objects.get(pk=self.request.user.pk)
        expected = pytz.timezone("US/Eastern").localize(timezone.datetime(1980, 2, 28))
        self.assertEqual(expected, user.birth_date)

    def test_qigong_cycles(self):
        self.request.user.birth_date = pytz.timezone(
            "US/Eastern").localize(timezone.datetime(1981, 3, 31))
        self.request.user.save()

        response = views.qigong_cycles(self.request)

        self.assertContains(response, '<td class="intellectual">Intellectual</td>')
        self.assertContains(response, 'qigong_cycles(["')
