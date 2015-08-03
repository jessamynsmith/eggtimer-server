from eggtimer.settings.common import *

import os

HOME_DIR = os.path.expanduser("~")

SECRET_KEY = 'psu&amp;&amp;83=i(4wgd@9*go=nps9=1rw#9b_w6psy4mp6yoxqv1i5g'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'eggtimer',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

STATIC_ROOT = '/tmp/eggtimer/static'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_ROOT = '/tmp/eggtimer/media'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '%s/Development/Django/eggtimer/emails' % HOME_DIR

SSLIFY_DISABLE = True
ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

INSTALLED_APPS.extend([
    'django_extensions',
])
