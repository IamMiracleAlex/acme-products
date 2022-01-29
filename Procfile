release: python3 manage.py migrate
web: gunicorn mysite.wsgi --log-file -
celery: celery -A mysite worker -l info
