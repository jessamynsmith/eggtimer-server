from django.conf.urls import include, url
from django.views.generic import RedirectView
from rest_framework import routers

from periods import views as period_views


router = routers.DefaultRouter()
router.register(r'periods', period_views.FlowEventViewSet, base_name='periods')
router.register(r'statistics', period_views.StatisticsViewSet, base_name='statistics')


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='calendar/', permanent=True)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', period_views.profile, name='user_profile'),
    url(r'^accounts/profile/api_info/$', period_views.api_info, name='api_info'),
    url(r'^accounts/profile/regenerate_key/$', period_views.regenerate_key, name='regenerate_key'),

    url(r'^api/v2/', include(router.urls)),
    url(r'^api/v2/authenticate/', period_views.api_authenticate, name='authenticate'),
    url(r'^period_form/$', period_views.period_form, name='period_form'),
    url(r'^period_form/(?P<period_id>[0-9]+)/$', period_views.period_form, name='period_form'),
    url(r'^calendar/$', period_views.calendar, name='calendar'),
    url(r'^statistics/$', period_views.statistics, name='statistics'),
    url(r'^statistics/cycle_length_frequency$', period_views.cycle_length_frequency),
    url(r'^statistics/cycle_length_history$', period_views.cycle_length_history),
    url(r'^statistics/qigong_cycles', period_views.qigong_cycles),
]
