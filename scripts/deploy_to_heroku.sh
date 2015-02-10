#!/bin/bash

# This script will quit on the first error that is encountered.
set -e

# Runs piplint, flake8, tests
sh .git/hooks/pre-commit

heroku config:set \
ADMIN_EMAIL="egg.timer.app@gmail.com" \
ADMIN_NAME="the egg timer" \
DJANGO_SETTINGS_MODULE=eggtimer.settings.production \
SECRET_KEY=$DJANGO_SECRET_KEY \
> /dev/null

git push heroku master

python manage.py collectstatic --noinput

python manage.py syncdb --noinput
python manage.py migrate --noinput
