from eggtimer.settings.common import *

import dj_database_url
import os

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Parse database configuration from $DATABASE_URL
DATABASES = {
    'default': dj_database_url.config()
}

# Static asset configuration
STATIC_ROOT = 'staticfiles'

MEDIA_ROOT = 'media'

ALLOWED_HOSTS = ['eggtimer.herokuapp.com']
CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS.extend([
    'gunicorn',
])
