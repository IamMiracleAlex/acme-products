release: python3 manage.py migrate
web: gunicorn mysite.wsgi --port $PORT --bind 0.0.0.0 -v2
worker2: celery -A mysite worker -l info
