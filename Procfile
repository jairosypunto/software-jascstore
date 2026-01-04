release: python3 manage.py migrate && python3 manage.py collectstatic --noinput
web: gunicorn JascEcommerce.wsgi:application --bind 0.0.0.0:$PORT