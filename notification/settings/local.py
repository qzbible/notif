from .base import *
from .base import env
import os
from dotenv import load_dotenv

load_dotenv()
DEBUG = True


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-o(%d_rzzf^g01b1bm9j--$wv**&fvez9y_!bmkl(xupof2qzfj",
)

ALLOWED_HOSTS = ["*"]


CELERY_TIMEZONE ="Africa/Douala"
# CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "Africa/Douala")
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'

CELERY_CACHE_BACKEND = 'django-cache'
CELERY_TASK_TRACK_STARTED = True

CELERY_RESULT_BACKEND_DB = f'db+mysql+pymysql://root:ziyouma@db/pseudo_mysql'
# CELERY_RESULT_BACKEND_DB = os.getenv(
#     "CELERY_RESULT_BACKEND_DB", f'db+mysql+pymysql://root:ziyouma@db/pseudo_mysql')
CELERY_BROKER_URL = f'amqp://root:ziyouma@rabbitmq_mail//'
# CELERY_BROKER_URL = f'amqp://root:ziyouma@rabbitmq//'
CELERY_TASK_RESULT_EXPIRES = 18000
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_IMPORTS = ["mailing.tasks"]

EMAIL_HOST = os.getenv(
    "EMAIL_HOST", 'smtp.gmail.com')
EMAIL_PORT = os.getenv(
    "EMAIL_PORT", 587)
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER", 'landry.ziyouma@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD", 'ypsyzkiidjakjdqb')
APP_NAME = 'Klivar'
