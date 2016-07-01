# -*- coding: iso-8859-15 -*-

import os

BROWSER = 'Chrome'

# Pick an environment type from the keys in BASE_URL
ENVIRONMENT_TYPE = 'dev'

BASE_URL = {
    # NOTE 'dev' is special in that tests that check email use the EMAIL_FILE_PATH
    # to retrieve emails rather than ADMIN_EMAIL
    'dev': 'http://127.0.0.1:8000/',
    'heroku-production': 'https://eggtimer.herokuapp.com/',
}

ADMIN_USERNAME = os.environ['SELENIUM_ADMIN_EMAIL']
ADMIN_PASSWORD = os.environ['SELENIUM_ADMIN_PASSWORD']

EMAIL_USERNAME = 'eggtimer.selenium@example.com'

# Required when testing locally; must match settings.py EMAIL_FILE_PATH
EMAIL_FILE_PATH = '%s/Development/django_files/eggtimer/emails' % os.environ.get('HOME')

SLEEP_INTERVAL = 0.1
MAX_SLEEP_TIME = 10
