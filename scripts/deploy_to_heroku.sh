#!/bin/bash

# This script will quit on the first error that is encountered.
set -e

CIRCLE=$1

DEPLOY_DATE=`date "+%Y/%m/%d %H:%M:%S %Z"`

heroku config:set --app=eggtimer \
ADMIN_EMAIL="egg.timer.app@gmail.com" \
ADMIN_NAME="the egg timer" \
DJANGO_SETTINGS_MODULE=eggtimer.settings.production \
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY \
DEPLOY_DATE="$DEPLOY_DATE" \
> /dev/null

if [ $CIRCLE ]
then
    git push git@heroku.com:eggtimer.git $CIRCLE_SHA1:refs/heads/master
else
    git push heroku master
fi

heroku run python manage.py syncdb --noinput --app=eggtimer
heroku run python manage.py migrate --noinput --app=eggtimer
