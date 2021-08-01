web: daphne realtimechat.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
chatworker: python manage.py runworker --settings=realtimechat.settings -v2