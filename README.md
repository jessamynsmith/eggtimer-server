eggtimer
==============

[![Build Status](https://travis-ci.org/jessamynsmith/eggtimer.svg?branch=master)](https://travis-ci.org/jessamynsmith/eggtimer)
[![Coverage Status](https://coveralls.io/repos/jessamynsmith/eggtimer/badge.svg?branch=master)](https://coveralls.io/r/jessamynsmith/eggtimer?branch=master)

A simple tracker for menstrual periods. Check out the live app:
https://eggtimer.herokuapp.com/

For local development, create a virtualenv:

    mkvirtualenv eggtimer

Install requirements:

    pip install -r requirements/development.txt

Use dev settings:

    export DJANGO_SETTINGS_MODULE=eggtimer.settings.development

Run tests and view coverage:

     python manage.py test --with-coverage

Check code style:

    flake8


Thank you to:
Emily Strickland (github.com/emilyst) for the name
