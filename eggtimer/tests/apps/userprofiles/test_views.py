import datetime
from django.contrib.auth import models as auth_models
from django.http import HttpRequest
from django.test import TestCase

from eggtimer.apps.userprofiles import views


class TestViews(TestCase):

    def setUp(self):
        self.user = auth_models.User.objects.create_user(
            username='jessamyn', password='bogus', email='jessamyn@example.com',
            first_name=u'Jessamyn')
        self.request = HttpRequest()
        self.request.META['SERVER_NAME'] = 'localhost'
        self.request.META['SERVER_PORT'] = '8000'
        self.request.user = self.user

    def test_profile(self):
        response = views.profile(self.request)

        self.assertContains(response, '<a href="/qigong/cycles/">Medical Qigong Cycles</a>')
        self.assertContains(response, '<h4>API Information</h4>')

    def test_qigong_cycles_no_data(self):
        response = views.qigong_cycles(self.request)

        self.assertContains(response, '<label class="control-label" for="id_birth_date">Birth Date')

    def test_qigong_cycles(self):
        self.user.userprofile.birth_date = datetime.date(1981, 3, 31)
        self.user.userprofile.save()

        response = views.qigong_cycles(self.request)

        self.assertContains(response, '<td class="intellectual">Intellectual</td>')
        self.assertContains(response, 'qigong_cycles(["')
