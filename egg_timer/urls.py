from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from egg_timer.apps.api import v1 as api

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(api.PeriodResource())
v1_api.register(api.UserProfileResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'periodtracker.views.home', name='home'),
    # url(r'^periodtracker/', include('periodtracker.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
)
