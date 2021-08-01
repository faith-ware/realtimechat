release: python manage.py migrate
web: daphne realtimechat.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker --settings-realtimechat.settings -v2