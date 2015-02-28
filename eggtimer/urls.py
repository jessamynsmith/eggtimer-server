from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect
from rest_framework import routers

from periods import views as period_views


admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'periods', period_views.FlowEventViewSet, base_name='periods')
router.register(r'statistics', period_views.StatisticsViewSet, base_name='statistics')

urlpatterns = patterns(
    '',
    (r'^$', lambda x: HttpResponseRedirect('/calendar/')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', period_views.profile, name='user_profile'),
    url(r'^accounts/profile/regenerate_key/$', period_views.regenerate_key, name='regenerate_key'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v2/', include(router.urls)),

    url(r'^period_form/$', period_views.period_form, name='period_form'),
    url(r'^period_form/(?P<period_id>[0-9]+)/$', period_views.period_form, name='period_form'),
    url(r'^calendar/$', period_views.calendar, name='calendar'),
    url(r'^statistics/$', period_views.statistics, name='statistics'),
    url(r'^qigong/cycles/$', period_views.qigong_cycles, name='qigong_cycles'),
)
