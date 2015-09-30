from django.conf.urls import include, url
from django.contrib import admin

from periods import urls as period_urls


urlpatterns = [
        url(r'^admin/', include(admin.site.urls)),
        url(r'^', include(period_urls), name='periods'),
]
