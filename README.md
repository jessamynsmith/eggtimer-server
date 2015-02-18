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

Edit development settings as needed to match your environment (check DATABASES in particular),
and ensure those settings will be used automatically:

    export DJANGO_SETTINGS_MODULE=eggtimer.settings.development

Set up db:

    python manage.py syncdb
    python manage.py migrate

Run tests and view coverage:

    coverage run manage.py test
    coverage report -m

Check code style:

    flake8

Run server:

    python manage.py runserver
    
The javascript linter and tests require you to install node, then:

    npm install -g jshint mocha blanket moment

Set up your environment to know about node:

    export NODE_PATH=/path/to/node_modules/
    
Run JavaScript tests:

    mocha -R html-cov */tests/static/js/* > ~/eggtimer_javascript_coverage.html

Lint JavaScript:

    jshint */static/js


Thank you to:
Emily Strickland (github.com/emilyst) for the name
