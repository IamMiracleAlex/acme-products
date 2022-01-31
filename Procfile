release: python3 manage.py migrate
web: gunicorn mysite.wsgi --bind 0.0.0.0
worker: celery -A mysite worker -l info
