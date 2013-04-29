from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.views.generic import TemplateView
from tastypie.api import Api

from egg_timer.apps.api import v1 as api
from egg_timer.apps.periods import views as period_views

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(api.PeriodResource())
v1_api.register(api.StatisticsResource())
v1_api.register(api.UserProfileResource())

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^accounts/', include('registration.backends.default.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),

    url(r'^calendar/', login_required(TemplateView.as_view(template_name='periods/calendar.html')), name='calendar'),
    url(r'^statistics/', period_views.statistics, name='statistics'),
)
