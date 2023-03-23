#!/bin/bash
set -o errexit

celery -A pseudonymisation worker -l DEBUG --detach
celery -A pseudonymisation beat -l INFO --detach

python manage.py runserver 0.0.0.0:9081 --settings=pseudonymisation.settings.dev



