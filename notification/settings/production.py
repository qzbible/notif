from .base import *
from .base import env

SECRET_KEY = env("DJANGO_SECRET_KEY",
                 default="VoQE5G62Qu1Sk8cmBMa8V8D4nYhWazjaEoH9p9wWGPF4Pv23A3M68Wtme2BpHSwt",)
# allowed host tru
ALLOWED_HOSTS =  ["*"]
ADMIN_URL = env("DJANGO_ADMIN_URL") 

# DATABASES = {"default": env.db("DATABASE_URL")}
# DATABASES["default"]["ATOMIC_REQUESTS"] = True

# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# SECURE_SSL_REDIRECT = True

# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# SECURE_HSTS_SECONDS = 60

# SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)

# SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
#     "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True
# )

# SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
#     "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
# )

# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# DEFAULT_FROM_EMAIL = env(
#     "DJANGO_DEFAULT_FROM_EMAIL",
#     default="Klivar  <avotreecoute@klivar.com>",
# )

# SITE_NAME = "Klivar "

# SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

# EMAIL_SUBJECT_PREFIX = env(
#     "DJANGO_EMAIL_SUBJECT_PREFIX",
#     default="[klivar]",
# )

# EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
# EMAIL_HOST = env("EMAIL_HOST")
# EMAIL_HOST_USER = env("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = env("SMTP_MAILGUN_PASSWORD")
# EMAIL_PORT = env("EMAIL_PORT")
# EMAIL_USE_TLS = True
# DOMAIN = env("DOMAIN")


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
    "EMAIL_HOST_USER", 'avotreecoute@klivar.com')
EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD", '!Klivardev1')
APP_NAME = 'Klivar'
