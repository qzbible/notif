#!/bin/bash
set -o errexit

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

celery -A notification worker -l DEBUG --detach
celery -A notification beat -l INFO --detach

python manage.py runserver 0.0.0.0:9081 --settings=notification.settings