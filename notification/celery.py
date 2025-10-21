import os

from celery import Celery
from django.conf import settings
# from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notification.settings.local")

app = Celery("notification")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# ✅ CONFIGURATION TIMEZONE CELERY
app.conf.update(
    timezone='UTC',  # ✅ Timezone par défaut
    enable_utc=True,  # ✅ Forcer UTC
    
    # Sérialisation JSON (recommendé pour eta avec datetime)
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Format de datetime dans les tâches
    task_track_started=True,
    task_time_limit=3600,  # 1h max
)

# app.conf.beat_schedule = {
#     'tache_periodique': {
#         'task': 'votre_app.tache_periodique',
#         'schedule': crontab(minute=0, hour=0),  # Exécute tous les jours à minuit
#     },
# }