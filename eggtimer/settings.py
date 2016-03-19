# Django settings for eggtimer project.
import dateutil.parser
import os

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

DEBUG = bool(int(os.environ.get('DJANGO_DEBUG', False)))

ALLOWED_HOSTS = ['eggtimer.herokuapp.com', 'localhost', '127.0.0.1']
CORS_ORIGIN_ALLOW_ALL = True
SECURE_SSL_REDIRECT = bool(int(os.environ.get('DJANGO_ENABLE_SSL', True)))
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
    'rest_framework',
    'rest_framework.authtoken',
    'floppyforms',
    'bootstrapform',
    'timezone_field',
    'periods',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'eggtimer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/eggtimer/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.request",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
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
    'default': dj_database_url.config(default="sqlite:///%s/eggtimer.sqlite" % HOME_DIR)
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

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_DIR + '/eggtimer/static/',
)

MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend"
)

# auth and allauth set
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
        'SCOPE': ['email', 'publish_stream'],
        'METHOD': 'oauth2',
    }
}

ACCOUNT_ACTIVATION_DAYS = 14

# If Heroku addons start using EMAIL_URL, switch to dj-email-url
DEFAULT_FROM_EMAIL = formataddr(ADMINS[0])
REPLY_TO = (
    os.environ.get('REPLY_TO_EMAIL', 'example@example.com'),
)
EMAIL_HOST = os.environ.get('MAILGUN_SMTP_SERVER')
EMAIL_PORT = os.environ.get('MAILGUN_SMTP_PORT')
EMAIL_HOST_USER = os.environ.get('MAILGUN_SMTP_LOGIN')
EMAIL_HOST_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD')
EMAIL_USE_TLS = True

if not EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '%s/Development/django_files/eggtimer/emails' % HOME_DIR

# TODO Once Ionic app is done, perhaps remove session authentication?
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


# TODO maybe this could be a django plugin?
DEPLOY_DATE = dateutil.parser.parse(os.environ.get('DEPLOY_DATE', ''))
VERSION = '0.6'
TEMPLATE_VISIBLE_SETTINGS = ['DEPLOY_DATE', 'VERSION']

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

if DEBUG:
    INSTALLED_APPS.extend([
        'django_extensions',
    ])
