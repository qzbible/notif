import os

from celery import Celery
from django.conf import settings
# from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notification.settings.local")

app = Celery("notification")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)



# app.conf.beat_schedule = {
#     'tache_periodique': {
#         'task': 'votre_app.tache_periodique',
#         'schedule': crontab(minute=0, hour=0),  # Exécute tous les jours à minuit
#     },
# }