# Django settings for eggtimer project.
import os

from django.utils.dateparse import parse_datetime

import dj_database_url
from email.utils import formataddr

HOME_DIR = os.path.expanduser("~")
BASE_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.pardir))

ADMINS = (
    (os.environ.get('ADMIN_NAME', 'admin'), os.environ.get('ADMIN_EMAIL', 'example@example.com')),
)

# Export a secret value in production; for local development, the default is good enough
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY',
                            'psu&83=i(4wgd@9*go=nps9=1rw#9b_w6psy4mp6yoxqv1i5g')

# Use env setting if available, otherwise make debug false
DEBUG = bool(int(os.environ.get('DJANGO_DEBUG', '0')))

ALLOWED_HOSTS = ['eggtimer.herokuapp.com', 'localhost', '127.0.0.1']
CORS_ORIGIN_ALLOW_ALL = True

SECURE_SSL_REDIRECT = bool(int(os.environ.get('DJANGO_ENABLE_SSL', '1')))
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'custom_user',
    'settings_context_processor',
    'gunicorn',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.github',
    'rest_framework',
    'rest_framework.authtoken',
    'floppyforms',
    'bootstrapform',
    'timezone_field',
    'periods',
]

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'eggtimer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'eggtimer', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "settings_context_processor.context_processors.settings",
            ],
            'debug': DEBUG,
        },
    },
]

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'eggtimer.wsgi.application'

# Parse database configuration from $DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default="sqlite:///%s" % os.path.join(HOME_DIR, 'eggtimer', 'eggtimer.sqlite')
    )
}

SITE_ID = 1

# https://docs.djangoproject.com/en/1.8/topics/i18n/

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'bower_components'),
    os.path.join(BASE_DIR, 'eggtimer', 'static'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend"
)

# auth and allauth
AUTH_USER_MODEL = 'periods.User'
LOGIN_REDIRECT_URL = '/calendar/'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email'],
        'METHOD': 'oauth2',
    }
}

ACCOUNT_ACTIVATION_DAYS = 14

# If Heroku addons start using EMAIL_URL, switch to dj-email-url
DEFAULT_FROM_EMAIL = formataddr(ADMINS[0])
REPLY_TO = (
    os.environ.get('REPLY_TO_EMAIL', 'example@example.com'),
)
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
EMAIL_USE_TLS = True

if not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = os.path.join(HOME_DIR, 'eggtimer', 'emails')

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}

# US Navy API is used for moon phases
# http://aa.usno.navy.mil/data/docs/api.php#phase
MOON_PHASE_URL = 'http://api.usno.navy.mil'
API_DATE_FORMAT = '%Y-%m-%d'
US_DATE_FORMAT = '%-m/%-d/%Y'

# TODO maybe this could be a django plugin?
DEPLOY_DATE = parse_datetime(os.environ.get('DEPLOY_DATE', ''))
VERSION = '0.6'
TEMPLATE_VISIBLE_SETTINGS = ['DEPLOY_DATE', 'VERSION', 'ADMINS']

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# if DEBUG:
#     INSTALLED_APPS.extend([
#         'django_extensions',
#     ])
