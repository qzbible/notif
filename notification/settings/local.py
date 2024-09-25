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


EMAIL_HOST = os.getenv(
    "EMAIL_HOST", 'smtp.gmail.com')
EMAIL_PORT = os.getenv(
    "EMAIL_PORT", 587)
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER", 'avotreecoute@klivar.com>')
EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD", '!Klivardev1')
APP_NAME = 'Klivar'
