eggtimer
==============

A simple tracker for menstrual periods. Check out the live app:
https://eggtimer.herokuapp.com/

[![Build Status](https://travis-ci.org/jessamynsmith/eggtimer.svg?branch=master)](https://travis-ci.org/jessamynsmith/eggtimer)


For local development, create a virtualenv:

    mkvirtualenv eggtimer

Install requirements:

    pip install -r requirements/development.txt

Use dev settings:

    export DJANGO_SETTINGS_MODULE=eggtimer.settings.development

Run tests and view coverage:

     python manage.py test --with-coverage

Check code style:

    flake8 . --max-line-length=100


Thank you to:
Emily Strickland (github.com/emilyst) for the name
