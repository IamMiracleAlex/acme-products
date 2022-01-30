release: python3 manage.py migrate
web: gunicorn mysite.wsgi --log-file -
worker: celery -A mysite worker -l info
