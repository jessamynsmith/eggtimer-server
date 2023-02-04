# eggtimer-server

[![Build Status](https://circleci.com/gh/jessamynsmith/eggtimer-server.svg?style=shield)](https://circleci.com/gh/jessamynsmith/eggtimer-server)
[![Coverage Status](https://coveralls.io/repos/jessamynsmith/eggtimer-server/badge.svg?branch=master)](https://coveralls.io/r/jessamynsmith/eggtimer-server?branch=master)

The egg timer is an open-source tracker for menstrual periods. It provides a calendar, email notifications, statistical analysis, and an API allowing you to download all your data. Check out the live app:
https://eggtimer.herokuapp.com/


Like my work? Tip me! https://www.paypal.me/jessamynsmith


### Development

Fork the project on github and git clone your fork, e.g.:

    git clone https://github.com/<username>/eggtimer-server.git
    
You may need to set environment variables to find openssl on OSX when installing Python packages:

    export LDFLAGS="-L/usr/local/opt/openssl/lib"
    export CPPFLAGS="-I/usr/local/opt/openssl/include"

Create a virtualenv using Python 3.7 and install dependencies.

    python3 -m venv venv
    pip install -r requirements/development.txt

Ensure you have node installed (I recommend using homebrew on OSX), then use npm to install Javacript dependencies:

    npm install

Set environment variables as desired. Recommended dev settings:

    export DJANGO_DEBUG=1
    export DJANGO_ENABLE_SSL=0

Optional environment variables, generally only required in production:

    DATABASE_URL
    ADMIN_NAME
    ADMIN_EMAIL
    DJANGO_SECRET_KEY
    REPLY_TO_EMAIL
    SENDGRID_API_KEY
    DEPLOY_DATE 
    
You can add the exporting of environment variables to the virtualenv activate script so they are always available.

Set up db:

    python manage.py migrate

Run tests and view coverage:

    coverage run manage.py test
    coverage report -m

Check code style:

    flake8

(Optional) Generate graph of data models. In order to do this, you will need to install some extra requirements:

    brew install graphviz pkg-config
    pip install -r requirements/extensions.txt
    
You can then generate graphs, e.g.:

    python manage.py graph_models --pygraphviz -a -g -o all_models.png  # all models
    python manage.py graph_models periods --pygraphviz -g -o period_models.png  # period models

Run server:

    python manage.py runserver
    
Or run using gunicorn:

    gunicorn eggtimer.wsgi

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

Create a period:

curl -vk -X POST -H "Content-Type: application/json" -H 'Authorization: Token <AUTH_TOKEN>' --data '{"timestamp": "<YYYY-MM-DD>T<HH:MM:SS>"}' "https://eggtimer.herokuapp.com/api/v2/periods/" 

### Continuous Integration and Deployment

This project is already set up for continuous integration and deployment using circleci, coveralls,
and Heroku.

Make a new Heroku app, and add the following addons:

    Heroku Postgres
	SendGrid
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
    HEROKU_API_KEY <value_copied_from_heroku>

On circleci.io, under Project Settings -> Heroku Deployment, follow the steps to enable
Heroku builds. At this point, you may need to cancel any currently running builds, then run
a new build.

Once your app is deployed successfully, you can add the Scheduler task on Heroku:

    python manage.py notify_upcoming_period --settings=eggtimer.settings

You can also set up Dead Man's Snitch so you will know if the scheduled task fails.

### Ubuntu Deployment

Ssh into Ubuntu server.

Get source code:

    git clone git@github.com:jessamynsmith/eggtimer-server.git eggtimer

Copy gunicorn service file into system folder:

    sudo cp config/eggtimer.service /etc/systemd/system/eggtimer.service

After service config change:

    sudo systemctl daemon-reload

Restart eggtimer service:

    sudo systemctl restart eggtimer

View gunicorn logs:

    sudo journalctl -u eggtimer.service --no-pager -f

View Django logs:

    tail -f /home/django/log/error_eggtimer.log 

Copy nginx config into nginx directory and create symlink:

    sudo cp config/eggtimer /etc/nginx/sites-available/eggtimer
    sudo ln -s /etc/nginx/sites-available/eggtimer /etc/nginx/sites-enabled/eggtimer

Set up SSL:

    sudo certbot --nginx -d eggtimer.jessamynsmith.ca

Restart nginx:

    sudo systemctl restart nginx


Thank you to:
Emily Strickland (github.com/emilyst) for the name

