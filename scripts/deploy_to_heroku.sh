#!/bin/bash

# This script will quit on the first error that is encountered.
set -e

sh .git/hooks/pre-commit

git push heroku master

python manage.py collectstatic

python manage.py syncdb
python manage.py migrate
