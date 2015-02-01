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

MEDIA_ROOT = '/tmp/media'
MEDIA_URL = ''

STATIC_ROOT = '/tmp/static'
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '%s/Development/Django/eggtimer/emails' % HOME_DIR

INSTALLED_APPS.extend([
    'django_nose',
])

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

DJANGO_ARGS = [
    '--verbosity=0',
]

NOSE_ARGS = [
    '--exclude=settings',
    '--verbosity=0',
    '--cover-branches',
    '--cover-package=eggtimer',
    '--cover-inclusive',  # Cover all files
    '--cover-html',
    '--cover-html-dir=%s/eggtimer_coverage' % os.environ.get('HOME'),
]
