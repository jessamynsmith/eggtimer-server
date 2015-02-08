#!/bin/bash

# This script will quit on the first error that is encountered.
set -e

sh .git/hooks/pre-commit

heroku config:set \
ADMIN_EMAIL="egg.timer.app@gmail.com" \
ADMIN_NAME="the egg timer" \
DJANGO_SETTINGS_MODULE=eggtimer.settings.production\
> /dev/null

git push heroku master

python manage.py collectstatic --noinput

python manage.py syncdb --noinput
python manage.py migrate --noinput
