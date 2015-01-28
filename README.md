eggtimer
==============

A simple tracker for menstrual periods. Check out the live app:
https://eggtimer.herokuapp.com/


For local development, create a virtualenv:
    mkvirtualenv egg_timer

Install requirements:
    pip install -r requirements/development.txt

Use dev settings:
    export DJANGO_SETTINGS_MODULE=egg_timer.settings.development

Run tests and view coverage:

    coverage run -m nose
    coverage report

Check code style:

    flake8 . --max-line-length=100


Thank you to:
Emily Strickland (github.com/emilyst) for the name
