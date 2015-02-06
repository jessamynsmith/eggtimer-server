eggtimer
==============

[![Build Status](https://travis-ci.org/jessamynsmith/eggtimer.svg?branch=master)](https://travis-ci.org/jessamynsmith/eggtimer)
[![Coverage Status](https://coveralls.io/repos/jessamynsmith/eggtimer/badge.svg?branch=master)](https://coveralls.io/r/jessamynsmith/eggtimer?branch=master)

A simple tracker for menstrual periods. Check out the live app:
https://eggtimer.herokuapp.com/

Development
-----------

Fork the project on github and git clone your fork, e.g.:

    git clone https://github.com/<username>/quotations.git

Create a virtualenv and install dependencies:

    mkvirtualenv eggtimer --python=/path/to/python3
    pip install -r requirements/development.txt

Use development settings:

    export DJANGO_SETTINGS_MODULE=eggtimer.settings.development

Set up db:

    python manage.py syncdb
    python manage.py migrate

Run tests and view coverage:

     coverage run manage.py test eggtimer
     coverage report

Check code style:

    flake8

Run server:

    python manage.py runserver


Thank you to:
Emily Strickland (github.com/emilyst) for the name
