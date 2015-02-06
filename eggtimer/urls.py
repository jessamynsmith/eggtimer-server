from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect
from tastypie.api import Api

from eggtimer.apps.api import v1 as api
from eggtimer.apps.periods import views as period_views
from eggtimer.apps.userprofiles import views as userprofile_views

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(api.PeriodResource())
v1_api.register(api.PeriodDetailResource())
v1_api.register(api.StatisticsResource())
v1_api.register(api.UserProfileResource())

urlpatterns = patterns(
    '',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^$', lambda x: HttpResponseRedirect('/calendar/')),
    url(r'^accounts/profile/$', userprofile_views.profile, name='user_profile'),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/', include('password_reset.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),

    url(r'^calendar/$', period_views.calendar, name='calendar'),
    url(r'^statistics/$', period_views.statistics, name='statistics'),

    url(r'^qigong/cycles/$', userprofile_views.qigong_cycles, name='qigong_cycles'),
)
