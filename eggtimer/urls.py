from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect
from tastypie.api import Api

from eggtimer.apps.api import v1 as api
from eggtimer.apps.periods import views as period_views

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(api.PeriodResource())
v1_api.register(api.PeriodDetailResource())
v1_api.register(api.StatisticsResource())
v1_api.register(api.UserResource())

urlpatterns = patterns(
    '',
    (r'^$', lambda x: HttpResponseRedirect('/calendar/')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', period_views.profile, name='user_profile'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),

    url(r'^calendar/$', period_views.calendar, name='calendar'),
    url(r'^statistics/$', period_views.statistics, name='statistics'),
    url(r'^qigong/cycles/$', period_views.qigong_cycles, name='qigong_cycles'),
)
