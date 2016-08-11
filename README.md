eggtimer-server
===============

[![Build Status](https://circleci.com/gh/jessamynsmith/eggtimer-server.svg?style=shield)](https://circleci.com/gh/jessamynsmith/eggtimer-server)
[![Coverage Status](https://coveralls.io/repos/jessamynsmith/eggtimer-server/badge.svg?branch=master)](https://coveralls.io/r/jessamynsmith/eggtimer-server?branch=master)

Open-source tracker for menstrual periods. Check out the live app:
https://eggtimer.herokuapp.com/

Note: the front end for this app is being ported to Ionic (see https://github.com/jessamynsmith/eggtimer-ui)

Development
-----------

Fork the project on github and git clone your fork, e.g.:

    git clone https://github.com/<username>/eggtimer-server.git

Ensure Graphviz is installed. I recommend getting it via [homebrew](http://brew.sh/), along with `pkg-config`: `brew install graphviz pkg-config`

Create a virtualenv using Python 3 and install dependencies. I recommend getting python3 via homebrew as well, then installing [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/install.html#basic-installation) to that python. NOTE! You must change 'path/to/python3'
to be the actual path to python3 on your system.

    mkvirtualenv eggtimer --python=/path/to/python3
    pip install -r requirements/development.txt

Ensure you have node installed, then use npm to install JavaScript dependencies:

    npm install

Set environment variables as desired. Recommended dev settings:

    DJANGO_DEBUG=1
    DJANGO_ENABLE_SSL=0

Optional environment variables, generally only required in production:

    ADMIN_NAME
    ADMIN_EMAIL
    DJANGO_SECRET_KEY
    REPLY_TO_EMAIL
    MAILGUN_SMTP_SERVER
    MAILGUN_SMTP_PORT
    MAILGUN_SMTP_LOGIN
    MAILGUN_SMTP_PASSWORD
    DEPLOY_DATE

Set up db:

    python manage.py syncdb
    python manage.py migrate

Run tests and view coverage:

    coverage run manage.py test
    coverage report -m

Check code style:

    flake8

Generate graph of data models, e.g.:

    python manage.py graph_models --pygraphviz -a -g -o all_models.png  # all models
    python manage.py graph_models periods --pygraphviz -g -o period_models.png  # period models

Run server:

    python manage.py runserver

Lint JavaScript:

    ./node_modules/jshint/bin/jshint */static/*/js

Run JavaScript tests:

    mocha --require-blanket -R html-cov */tests/static/*/js/* > ~/eggtimer_javascript_coverage.html

To run Selenium tests, you must have chromedriver installed:

     brew install chromedriver

Next you need to create a Django admin user and then export the email and password for that user as environment variables:

    export SELENIUM_ADMIN_EMAIL='<EMAIL_VALUE>'
    export SELENIUM_ADMIN_PASSWORD='<PASSWORD_VALUE>'

Finally, ensure the server is running, and run the selenium tests:

    nosetests selenium/

Retrieve data from the API with curl. <AUTH_TOKEN> can be found in your account info.

curl -vk -X GET -H "Content-Type: application/json" -H 'Authorization: Token <AUTH_TOKEN>' "https://eggtimer.herokuapp.com/api/v2/statistics/" | python -m json.tool

curl -vk -X GET -H "Content-Type: application/json" -H 'Authorization: Token <AUTH_TOKEN>' "https://eggtimer.herokuapp.com/api/v2/periods/" | python -m json.tool

You can filter based on minimum and maximum timestamp of the events:

curl -vk -X GET -H "Content-Type: application/json" -H 'Authorization: Token <AUTH_TOKEN>' "https://eggtimer.herokuapp.com/api/v2/periods/?min_timestamp=2016-01-19&max_timestamp=2016-01-20" | python -m json.tool


Continuous Integration and Deployment
-------------------------------------

This project is already set up for continuous integration and deployment using circleci, coveralls,
and Heroku.

Make a new Heroku app, and add the following addons:

    Heroku Postgres
	Mailgun
	New Relic APM
	Papertrail
	Heroku Scheduler
	Dead Man's Snitch

Add Heroku buildpacks:

    heroku buildpacks:set heroku/nodejs -i 1
    heroku buildpacks:set heroku/python -i 2

Enable the project on coveralls.io, and copy the repo token

Enable the project on circleci.io, and under Project Settings -> Environment variables, add:

    COVERALLS_REPO_TOKEN <value_copied_from_coveralls>

On circleci.io, under Project Settings -> Heroku Deployment, follow the steps to enable
Heroku builds. At this point, you may need to cancel any currently running builds, then run
a new build.

Once your app is deployed successfully, you can add the Scheduler task on Heroku:

    python manage.py notify_upcoming_period --settings=eggtimer.settings

You can also set up Dead Man's Snitch so you will know if the scheduled task fails.


Thank you to:
Emily Strickland (github.com/emilyst) for the name
