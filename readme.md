# Intro
An application to load about 500,000 rows of csv data into the database, full CRUD operations and advanced search and filters. Also solves the server timeout error when uploading via the browser on a server (By integrating with AWS)

# Local Setup
1.  clone the repository
2.  create a virtual environment running python 3.8 (or above) - and activate it
    `python3 -m venv env` to create, and `source env/bin/activate` to activate (mac and linux) or `source env/Scripts/activate` (windows with `bash`)

3.  cd into the root of the django project (i.e the path containing manage.py)
4.  install requirements `pip install -r requirements.txt`
5.  Create a local postgres instance (or use an existing one)
6.  Set your DB and make sure the environment variable names are consistent with (mirapayments/settings.py)
7.  run `python manage.py migrate` to create database tables
8.  run `python manage.py createsuperuser` to create a superuser(An initial user that has access to the admin site)
9. run `python manage.py runserver` to start the development server


# Using Celery
Please see https://docs.celeryproject.org/en/stable/index.html for more information.

-  Startup Celery worker to receive tasks:

`celery -A mysite worker -l info`
