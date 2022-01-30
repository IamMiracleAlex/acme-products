import os

from django.conf import settings

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite', broker=settings.CELERY_BROKER_URL)
# app.conf.update(
#     broker_url = settings.CELERY_BROKER_URL,
#     result_backend = settings.CELERY_BROKER_URL,
#     timezone='Africa/Lagos',
#     enable_utc=True,
# )
app.autodiscover_tasks()
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
print(app.conf)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

