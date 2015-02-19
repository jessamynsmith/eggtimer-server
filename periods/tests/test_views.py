import datetime
import pytz

from django.contrib.auth import get_user_model
from django.http import HttpRequest, QueryDict
from django.test import TestCase
from django.utils import timezone
from tastypie import models as tastypie_models

from periods import models as period_models, views


class TestViews(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            password='bogus', email='jessamyn@example.com', first_name=u'Jessamyn')
        period_models.Period(user=self.user, start_date=datetime.date(2014, 1, 31)).save()
        period_models.Period(user=self.user, start_date=datetime.date(2014, 2, 28)).save()
        self.request = HttpRequest()
        self.request.user = self.user
        self.request.META['SERVER_NAME'] = 'localhost'
        self.request.META['SERVER_PORT'] = '8000'

    def test_calendar(self):
        response = views.calendar(self.request)

        self.assertContains(response, 'initializeCalendar(')
        self.assertContains(response, 'div id=\'id_calendar\'></div>')

    def test_statistics_no_data(self):
        period_models.Period.objects.all().delete()

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
        api_key = tastypie_models.ApiKey.objects.get(user=self.request.user).key

        response = views.regenerate_key(self.request)

        self.assertContains(response, '', status_code=302)
        self.assertNotEquals(api_key, self.request.user.api_key.key)

    def test_regenerate_key_get(self):
        api_key = tastypie_models.ApiKey.objects.get(user=self.request.user).key

        response = views.regenerate_key(self.request)

        self.assertContains(response, '', status_code=302)
        self.assertEquals(api_key, self.request.user.api_key.key)

    def test_qigong_cycles_no_data(self):
        response = views.qigong_cycles(self.request)

        self.assertContains(response, '<label class="control-label" for="id_birth_date">Birth Date')

    def test_qigong_cycles(self):
        self.user.birth_date = pytz.timezone("US/Eastern").localize(timezone.datetime(1981, 3, 31))
        self.user.save()

        response = views.qigong_cycles(self.request)

        self.assertContains(response, '<td class="intellectual">Intellectual</td>')
        self.assertContains(response, 'qigong_cycles(["')
