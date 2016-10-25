web: newrelic-admin run-program gunicorn eggtimer.wsgi:application -b 0.0.0.0:$PORT -w 5

release: python manage.py migrate --noinput
