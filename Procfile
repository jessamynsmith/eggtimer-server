web: newrelic-admin run-program gunicorn eggtimer.wsgi:application -b 0.0.0.0:$PORT -w 5

#Disabling for now while I investigate broken migrations
#release: python manage.py migrate --noinput
