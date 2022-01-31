release: python3 manage.py migrate
web: gunicorn mysite.wsgi --log-file - & celery -A mysite worker -l info
worker: celery -A mysite worker -l info