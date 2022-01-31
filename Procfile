release: python3 manage.py migrate
web: gunicorn mysite.wsgi --log-file -
worker2: celery -A mysite worker -l info